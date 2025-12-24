"""
Statistical analysis and visualization for Benford's Law validation.
"""

import polars as pl
import numpy as np
from scipy import stats
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# Use non-interactive backend for headless systems
matplotlib.use('Agg')

# Benford's Law expected distribution
BENFORD_EXPECTED = {
    1: 0.301,
    2: 0.176,
    3: 0.125,
    4: 0.097,
    5: 0.079,
    6: 0.067,
    7: 0.058,
    8: 0.051,
    9: 0.046
}


def load_data(parquet_path: Path) -> pl.DataFrame:
    """Load the numbers parquet file."""
    return pl.read_parquet(parquet_path)


def calculate_frequencies(df: pl.DataFrame, domain: str = None) -> Dict[int, float]:
    """
    Calculate observed first digit frequencies.
    
    Args:
        df: DataFrame with number data
        domain: Optional domain filter
        
    Returns:
        Dict mapping digit (1-9) to frequency (0-1)
    """
    if domain:
        df = df.filter(pl.col("domain") == domain)
    
    # Count first digits
    counts = df.group_by("first_digit").agg(pl.count()).sort("first_digit")
    
    total = counts["count"].sum()
    frequencies = {}
    
    for row in counts.iter_rows(named=True):
        digit = row["first_digit"]
        if 1 <= digit <= 9:
            frequencies[digit] = row["count"] / total
    
    # Fill in missing digits with 0
    for d in range(1, 10):
        if d not in frequencies:
            frequencies[d] = 0.0
    
    return frequencies


def chi_square_test(observed: Dict[int, float], n_samples: int) -> Tuple[float, float]:
    """
    Perform chi-square goodness of fit test.
    
    Args:
        observed: Observed frequencies
        n_samples: Total number of samples
        
    Returns:
        Tuple of (chi_square_statistic, p_value)
    """
    observed_counts = np.array([observed.get(d, 0) * n_samples for d in range(1, 10)])
    expected_counts = np.array([BENFORD_EXPECTED[d] * n_samples for d in range(1, 10)])
    
    # Chi-square test
    chi2, p_value = stats.chisquare(observed_counts, expected_counts)
    
    return chi2, p_value


def mean_absolute_deviation(observed: Dict[int, float]) -> float:
    """
    Calculate Mean Absolute Deviation from Benford distribution.
    
    Args:
        observed: Observed frequencies
        
    Returns:
        MAD value
    """
    deviations = []
    for d in range(1, 10):
        expected = BENFORD_EXPECTED[d]
        obs = observed.get(d, 0)
        deviations.append(abs(obs - expected))
    
    return np.mean(deviations)


def kolmogorov_smirnov_test(observed: Dict[int, float]) -> Tuple[float, float]:
    """
    Perform Kolmogorov-Smirnov test.
    
    Args:
        observed: Observed frequencies
        
    Returns:
        Tuple of (KS_statistic, p_value)
    """
    obs_values = [observed.get(d, 0) for d in range(1, 10)]
    exp_values = [BENFORD_EXPECTED[d] for d in range(1, 10)]
    
    # Cumulative distributions
    obs_cum = np.cumsum(obs_values)
    exp_cum = np.cumsum(exp_values)
    
    ks_stat = np.max(np.abs(obs_cum - exp_cum))
    
    # For discrete case, approximate p-value
    n = sum(obs_values)
    p_value = stats.kstest(obs_values, exp_values).pvalue
    
    return ks_stat, p_value


def plot_domain_comparison(df: pl.DataFrame, output_dir: Path):
    """
    Create bar chart comparing observed vs expected for each domain.
    
    Args:
        df: DataFrame with number data
        output_dir: Directory to save plots
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get unique domains
    domains = df["domain"].unique().to_list()
    
    # Create subplot for each domain
    n_domains = len(domains)
    n_cols = 3
    n_rows = (n_domains + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
    if n_domains == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    digits = list(range(1, 10))
    expected = [BENFORD_EXPECTED[d] for d in digits]
    
    for idx, domain in enumerate(sorted(domains)):
        ax = axes[idx]
        
        # Calculate observed frequencies
        freq = calculate_frequencies(df, domain)
        observed = [freq[d] for d in digits]
        
        # Count samples
        n_samples = df.filter(pl.col("domain") == domain).height
        
        # Plot
        x = np.arange(len(digits))
        width = 0.35
        
        ax.bar(x - width/2, observed, width, label='Observed', alpha=0.8)
        ax.bar(x + width/2, expected, width, label='Benford', alpha=0.8)
        
        ax.set_xlabel('First Digit')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{domain} (n={n_samples:,})')
        ax.set_xticks(x)
        ax.set_xticklabels(digits)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    # Hide empty subplots
    for idx in range(n_domains, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'domain_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_dir / 'domain_comparison.png'}")


def plot_deviation_heatmap(df: pl.DataFrame, output_dir: Path):
    """
    Create heatmap showing deviation from Benford's Law.
    
    Args:
        df: DataFrame with number data
        output_dir: Directory to save plots
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    domains = sorted(df["domain"].unique().to_list())
    digits = list(range(1, 10))
    
    # Calculate deviations
    deviation_matrix = []
    for domain in domains:
        freq = calculate_frequencies(df, domain)
        deviations = [freq[d] - BENFORD_EXPECTED[d] for d in digits]
        deviation_matrix.append(deviations)
    
    deviation_matrix = np.array(deviation_matrix)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, len(domains) * 0.5 + 2))
    
    im = ax.imshow(deviation_matrix, cmap='RdBu_r', aspect='auto', vmin=-0.1, vmax=0.1)
    
    ax.set_xticks(np.arange(len(digits)))
    ax.set_yticks(np.arange(len(domains)))
    ax.set_xticklabels(digits)
    ax.set_yticklabels(domains)
    
    ax.set_xlabel('First Digit')
    ax.set_ylabel('Domain')
    ax.set_title('Deviation from Benford\'s Law\n(Observed - Expected)')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Deviation', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(len(domains)):
        for j in range(len(digits)):
            text = ax.text(j, i, f'{deviation_matrix[i, j]:.3f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'deviation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_dir / 'deviation_heatmap.png'}")


def generate_summary_table(df: pl.DataFrame) -> pl.DataFrame:
    """
    Generate summary statistics table for all domains.
    
    Args:
        df: DataFrame with number data
        
    Returns:
        Summary DataFrame
    """
    domains = sorted(df["domain"].unique().to_list())
    
    results = []
    for domain in domains:
        domain_df = df.filter(pl.col("domain") == domain)
        n_samples = domain_df.height
        
        if n_samples == 0:
            continue
        
        freq = calculate_frequencies(df, domain)
        chi2, p_value = chi_square_test(freq, n_samples)
        mad = mean_absolute_deviation(freq)
        
        results.append({
            "Domain": domain,
            "Samples": n_samples,
            "Chi-Square": chi2,
            "P-Value": p_value,
            "MAD": mad,
            "Follows Benford": "Yes" if p_value > 0.05 else "No"
        })
    
    return pl.DataFrame(results)


def analyze(parquet_path: Path, output_dir: Path):
    """
    Main analysis function.
    
    Args:
        parquet_path: Path to numbers.parquet file
        output_dir: Directory for output files
    """
    print("=" * 80)
    print("Benford's Law Analysis")
    print("=" * 80)
    print()
    
    # Load data
    print(f"Loading data from {parquet_path}...")
    df = load_data(parquet_path)
    print(f"✓ Loaded {df.height:,} numbers from {df['domain'].n_unique()} domains")
    print()
    
    # Generate summary table
    print("Calculating statistics...")
    summary = generate_summary_table(df)
    print()
    print(summary)
    print()
    
    # Save summary
    summary_path = output_dir / "summary_statistics.csv"
    summary.write_csv(summary_path)
    print(f"✓ Saved: {summary_path}")
    print()
    
    # Generate visualizations
    print("Generating visualizations...")
    plot_domain_comparison(df, output_dir)
    plot_deviation_heatmap(df, output_dir)
    print()
    
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print(f"Results saved to: {output_dir}")
    print()


if __name__ == "__main__":
    # Test with sample data
    print("Testing analyzer module...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 10000
    
    # Generate Benford-distributed data
    digits = np.random.choice(
        list(range(1, 10)),
        size=n_samples,
        p=[BENFORD_EXPECTED[d] for d in range(1, 10)]
    )
    
    sample_df = pl.DataFrame({
        "article_id": np.random.randint(1, 1000, n_samples),
        "domain": np.random.choice(["Geography", "People", "Science"], n_samples),
        "number": np.random.uniform(1, 10000, n_samples),
        "first_digit": digits,
        "second_digit": np.random.randint(0, 10, n_samples)
    })
    
    # Test frequency calculation
    freq = calculate_frequencies(sample_df, "Geography")
    print("\nSample frequencies (Geography):")
    for d in range(1, 10):
        print(f"  {d}: {freq[d]:.3f} (expected: {BENFORD_EXPECTED[d]:.3f})")
    
    # Test statistical tests
    chi2, p = chi_square_test(freq, sample_df.filter(pl.col("domain") == "Geography").height)
    mad = mean_absolute_deviation(freq)
    print(f"\nChi-square: {chi2:.2f}, p-value: {p:.4f}")
    print(f"MAD: {mad:.4f}")

