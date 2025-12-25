"""
Random sampling utilities for Wikipedia article processing.
"""

import random
from typing import List, Tuple, Optional


class WikipediaSampler:
    """
    Handles random sampling of Wikipedia articles from the index.
    """
    
    def __init__(self, seed: Optional[int] = 42):
        """
        Initialize sampler.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def parse_index(self, index_path: str) -> List[Tuple[int, int, str]]:
        """
        Parse the Wikipedia multistream index file.
        
        Args:
            index_path: Path to the index file (*.bz2)
            
        Returns:
            List of (offset, article_id, title) tuples
        """
        import bz2
        
        entries = []
        with bz2.open(index_path, 'rt', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split(':', 2)
                if len(parts) >= 3:
                    try:
                        offset = int(parts[0])
                        article_id = int(parts[1])
                        title = parts[2]
                        entries.append((offset, article_id, title))
                    except ValueError:
                        continue
        
        return entries
    
    def sample_entries(
        self,
        entries: List[Tuple[int, int, str]],
        sample_rate: Optional[float] = None,
        sample_count: Optional[int] = None
    ) -> List[Tuple[int, int, str]]:
        """
        Randomly sample entries.
        
        Args:
            entries: List of (offset, article_id, title) tuples
            sample_rate: Fraction to sample (e.g., 0.01 for 1%)
            sample_count: Absolute number to sample
            
        Returns:
            Sampled list of entries
            
        Note:
            Exactly one of sample_rate or sample_count must be provided.
        """
        if sample_rate is None and sample_count is None:
            raise ValueError("Must provide either sample_rate or sample_count")
        
        if sample_rate is not None and sample_count is not None:
            raise ValueError("Cannot provide both sample_rate and sample_count")
        
        total = len(entries)
        
        if sample_rate is not None:
            if not 0 < sample_rate <= 1.0:
                raise ValueError(f"sample_rate must be between 0 and 1, got {sample_rate}")
            sample_count = int(total * sample_rate)
        
        if sample_count > total:
            raise ValueError(f"sample_count ({sample_count}) exceeds total entries ({total})")
        
        # Random sampling without replacement
        sampled = random.sample(entries, sample_count)
        
        # Sort by offset for efficient sequential disk access
        sampled.sort(key=lambda x: x[0])
        
        return sampled
    
    def group_by_offset(
        self,
        entries: List[Tuple[int, int, str]]
    ) -> List[Tuple[int, List[Tuple[int, str]]]]:
        """
        Group entries by BZ2 block offset.
        
        Multiple articles can share the same BZ2 block offset.
        This groups them together for efficient decompression.
        
        Args:
            entries: List of (offset, article_id, title) tuples
            
        Returns:
            List of (offset, [(article_id, title), ...]) tuples
        """
        from collections import defaultdict
        
        offset_map = defaultdict(list)
        
        for offset, article_id, title in entries:
            offset_map[offset].append((article_id, title))
        
        # Return as sorted list
        return sorted(offset_map.items())
    
    def estimate_processing_time(
        self,
        num_articles: int,
        time_per_article_ms: float = 3.5,
        num_workers: int = 60
    ) -> dict:
        """
        Estimate processing time.
        
        Args:
            num_articles: Number of articles to process
            time_per_article_ms: Processing time per article in milliseconds
            num_workers: Number of parallel workers
            
        Returns:
            Dictionary with time estimates in various units
        """
        total_ms_single = num_articles * time_per_article_ms
        total_ms_parallel = total_ms_single / num_workers
        
        return {
            'num_articles': num_articles,
            'time_per_article_ms': time_per_article_ms,
            'num_workers': num_workers,
            'single_threaded': {
                'milliseconds': total_ms_single,
                'seconds': total_ms_single / 1000,
                'minutes': total_ms_single / 1000 / 60,
                'hours': total_ms_single / 1000 / 60 / 60,
            },
            'parallel': {
                'milliseconds': total_ms_parallel,
                'seconds': total_ms_parallel / 1000,
                'minutes': total_ms_parallel / 1000 / 60,
                'hours': total_ms_parallel / 1000 / 60 / 60,
            }
        }
    
    def print_estimate(self, estimate: dict):
        """Pretty print time estimate."""
        print(f"\n{'='*60}")
        print(f"PROCESSING TIME ESTIMATE")
        print(f"{'='*60}")
        print(f"Articles:           {estimate['num_articles']:>12,}")
        print(f"Workers:            {estimate['num_workers']:>12}")
        print(f"Time/article:       {estimate['time_per_article_ms']:>12.2f} ms")
        print(f"\nSingle-threaded:    {estimate['single_threaded']['minutes']:>12.1f} minutes")
        print(f"                    {estimate['single_threaded']['hours']:>12.1f} hours")
        print(f"\nParallel ({estimate['num_workers']} workers):")
        
        parallel = estimate['parallel']
        if parallel['seconds'] < 60:
            print(f"                    {parallel['seconds']:>12.1f} seconds")
        elif parallel['minutes'] < 60:
            print(f"                    {parallel['minutes']:>12.1f} minutes")
        else:
            print(f"                    {parallel['hours']:>12.1f} hours")
        
        print(f"{'='*60}\n")


def create_sample(
    index_path: str,
    sample_rate: Optional[float] = None,
    sample_count: Optional[int] = None,
    seed: int = 42
) -> List[Tuple[int, int, str]]:
    """
    Convenience function to create a random sample.
    
    Args:
        index_path: Path to Wikipedia index file
        sample_rate: Fraction to sample (e.g., 0.01 for 1%)
        sample_count: Absolute number to sample
        seed: Random seed
        
    Returns:
        Sampled list of (offset, article_id, title) tuples
    """
    sampler = WikipediaSampler(seed=seed)
    
    print("Parsing index file...")
    entries = sampler.parse_index(index_path)
    print(f"Found {len(entries):,} total articles")
    
    print("Sampling articles...")
    sampled = sampler.sample_entries(entries, sample_rate, sample_count)
    
    if sample_rate:
        print(f"Sampled {len(sampled):,} articles ({sample_rate*100:.2f}%)")
    else:
        print(f"Sampled {len(sampled):,} articles")
    
    return sampled


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m src.sampler <index_path> <sample_rate|sample_count>")
        print("  sample_rate: float between 0-1 (e.g., 0.01 for 1%)")
        print("  sample_count: integer (e.g., 10000 for 10k articles)")
        sys.exit(1)
    
    index_path = sys.argv[1]
    
    # Parse second argument as rate or count
    try:
        value = float(sys.argv[2])
        if 0 < value < 1:
            sampled = create_sample(index_path, sample_rate=value)
        else:
            sampled = create_sample(index_path, sample_count=int(value))
    except ValueError:
        print("Error: Second argument must be a number")
        sys.exit(1)
    
    # Print estimate
    sampler = WikipediaSampler()
    estimate = sampler.estimate_processing_time(len(sampled))
    sampler.print_estimate(estimate)

