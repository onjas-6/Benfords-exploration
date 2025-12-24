#!/usr/bin/env python3
"""
Test all modules to ensure they work correctly.
"""

import sys
from pathlib import Path
from io import BytesIO
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import extractor, categorizer, checkpoint, analyzer


def test_extractor():
    """Test number extraction module."""
    print("Testing extractor module...")
    print("-" * 60)

    # Test number extraction
    test_text = "The population is 1,234,567 people. Area: 42.5 km². Founded in 1999."
    numbers = extractor.extract_numbers_from_text(test_text)

    assert len(numbers) > 0, "Should extract numbers"
    print(f"✓ Extracted {len(numbers)} numbers: {numbers}")

    # Test first/second digit extraction
    test_cases = [
        (123.456, 1, 2),
        (9999, 9, 9),
        (42, 4, 2),
        (3.14159, 3, 1),
    ]

    for number, expected_first, expected_second in test_cases:
        first, second = extractor.analyze_number(number)
        assert (
            first == expected_first
        ), f"First digit of {number} should be {expected_first}, got {first}"
        assert (
            second == expected_second
        ), f"Second digit of {number} should be {expected_second}, got {second}"

    print(f"✓ First/second digit extraction working")

    # Test quick check
    text_with_numbers = b"Population: 123456"
    text_without_numbers = b"No digits here"

    assert extractor.quick_has_numbers(text_with_numbers), "Should detect numbers"
    print(f"✓ Quick number detection working")

    print()


def test_categorizer():
    """Test domain categorization module."""
    print("Testing categorizer module...")
    print("-" * 60)

    test_cases = [
        ("{{Infobox settlement}}", "Geography"),
        ("{{Infobox person}}", "People"),
        ("{{Infobox chemical compound}}", "Science"),
        ("{{Infobox football club}}", "Sports"),
        ("{{Infobox company}}", "Business"),
        ("{{Infobox film}}", "Media"),
        ("{{Infobox military conflict}}", "Military"),
        ("{{Infobox speciesbox}}", "Biology"),
        ("{{Infobox bridge}}", "Infrastructure"),
        ("{{Infobox election}}", "Events"),
        ("Some text without infobox", "Uncategorized"),
    ]

    for wikitext, expected_domain in test_cases:
        domain = categorizer.get_domain(wikitext)
        assert domain == expected_domain, f"Expected {expected_domain}, got {domain}"
        print(f"✓ {expected_domain:15} <- {wikitext[:40]}")

    print()


def test_checkpoint():
    """Test checkpoint and state management."""
    print("Testing checkpoint module...")
    print("-" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / "test_state.json"
        manager = checkpoint.StateManager(state_path)

        # Create new state
        state = manager.load()
        state.total_chunks = 10
        manager.save(state)
        print(f"✓ Created state with {state.total_chunks} chunks")

        # Mark chunks
        manager.mark_chunk_started(0)
        manager.mark_chunk_completed(0, articles=1000, numbers=15000)
        print(f"✓ Marked chunk 0 as completed")

        manager.mark_chunk_started(1)
        manager.mark_chunk_failed(1, error="Test error", retries=1)
        print(f"✓ Marked chunk 1 as failed")

        # Reload state
        manager2 = checkpoint.StateManager(state_path)
        state2 = manager2.load()

        assert len(state2.completed_chunks) == 1, "Should have 1 completed chunk"
        assert len(state2.failed_chunks) == 1, "Should have 1 failed chunk"
        assert state2.stats["articles"] == 1000, "Should have correct article count"
        print(f"✓ State persistence working")

        # Test pending chunks (failed chunks are still pending and need retry)
        pending = manager2.get_pending_chunks()
        assert (
            len(pending) == 9
        ), f"Should have 9 pending chunks (8 not started + 1 failed), got {len(pending)}"
        print(f"✓ Pending chunk calculation working")

    print()


def test_analyzer():
    """Test analysis module."""
    print("Testing analyzer module...")
    print("-" * 60)

    import polars as pl
    import numpy as np

    # Create sample data following Benford distribution
    np.random.seed(42)
    n_samples = 10000

    benford_expected = analyzer.BENFORD_EXPECTED
    digits = np.random.choice(
        list(range(1, 10)),
        size=n_samples,
        p=[benford_expected[d] for d in range(1, 10)],
    )

    sample_df = pl.DataFrame(
        {
            "article_id": np.random.randint(1, 1000, n_samples),
            "domain": np.random.choice(["Geography", "People", "Science"], n_samples),
            "number": np.random.uniform(1, 10000, n_samples),
            "first_digit": digits,
            "second_digit": np.random.randint(0, 10, n_samples),
        }
    )

    print(f"✓ Created sample dataset with {n_samples} numbers")

    # Test frequency calculation
    freq = analyzer.calculate_frequencies(sample_df, "Geography")
    assert len(freq) == 9, "Should have frequencies for digits 1-9"
    assert abs(sum(freq.values()) - 1.0) < 0.01, "Frequencies should sum to ~1"
    print(f"✓ Frequency calculation working")

    # Test statistical tests
    chi2, p_value = analyzer.chi_square_test(
        freq, sample_df.filter(pl.col("domain") == "Geography").height
    )
    print(f"✓ Chi-square test working (χ²={chi2:.2f}, p={p_value:.4f})")

    mad = analyzer.mean_absolute_deviation(freq)
    print(f"✓ MAD calculation working (MAD={mad:.4f})")

    # Test summary generation
    summary = analyzer.generate_summary_table(sample_df)
    assert summary.height == 3, "Should have 3 domains"
    print(f"✓ Summary table generation working")

    print()


def test_integration():
    """Test that all components work together."""
    print("Testing integration...")
    print("-" * 60)

    # Simulate processing an article
    test_article = """
    {{Infobox settlement
    |name = Test City
    |population = 1234567
    |area = 42.5
    }}
    
    Test City is a city with a population of 1,234,567 people.
    The area is 42.5 square kilometers. It was founded in 1999.
    """

    # Extract domain
    domain = categorizer.get_domain(test_article)
    print(f"✓ Domain: {domain}")

    # Extract numbers
    numbers = extractor.extract_numbers_from_text(test_article)
    print(f"✓ Extracted {len(numbers)} numbers: {numbers}")

    # Analyze digits
    for number in numbers:
        first, second = extractor.analyze_number(number)
        print(f"  {number:>12} -> first: {first}, second: {second}")

    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("Module Testing Suite")
    print("=" * 80)
    print()

    try:
        test_extractor()
        test_categorizer()
        test_checkpoint()
        test_analyzer()
        test_integration()

        print("=" * 80)
        print("✓ All tests passed!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Download Wikipedia dump: python download_dump.py")
        print("  2. Run quick validation:     python process_wiki.py --test")
        print("  3. Full processing:          python process_wiki.py")
        print("  4. Analyze results:          python analyze_benford.py")
        print()

        return 0

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"✗ Test failed: {e}")
        print("=" * 80)
        return 1
    except Exception as e:
        print()
        print("=" * 80)
        print(f"✗ Unexpected error: {e}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
