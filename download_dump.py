#!/usr/bin/env python3
"""
Download Wikipedia dump and index files with resume capability.
"""

import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm


DUMP_URL = "https://dumps.wikimedia.your.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"
INDEX_URL = "https://dumps.wikimedia.your.org/enwiki/latest/enwiki-latest-pages-articles-multistream-index.txt.bz2"

DATA_DIR = Path(__file__).parent / "data"


def download_with_resume(url: str, output_path: Path, chunk_size: int = 8192) -> bool:
    """
    Download a file with resume capability and progress bar.
    
    Args:
        url: URL to download from
        output_path: Where to save the file
        chunk_size: Download chunk size in bytes
        
    Returns:
        True if successful, False otherwise
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if output_path.exists():
        existing_size = output_path.stat().st_size
        print(f"Found existing file: {output_path.name} ({existing_size:,} bytes)")
    else:
        existing_size = 0
    
    # Get total file size
    try:
        headers = {}
        if existing_size > 0:
            headers['Range'] = f'bytes={existing_size}-'
        
        response = requests.head(url, allow_redirects=True)
        total_size = int(response.headers.get('content-length', 0))
        
        # Check if already complete
        if existing_size == total_size and total_size > 0:
            print(f"✓ {output_path.name} already downloaded completely")
            return True
        
        # Download with resume
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get actual content length (may differ if Range is used)
        content_length = int(response.headers.get('content-length', 0))
        
        mode = 'ab' if existing_size > 0 else 'wb'
        desc = f"Downloading {output_path.name}"
        
        if existing_size > 0:
            desc += f" (resuming from {existing_size:,} bytes)"
            
        with open(output_path, mode) as f:
            with tqdm(
                total=total_size,
                initial=existing_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=desc,
                ncols=100
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"✓ Downloaded {output_path.name}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {output_path.name}: {e}", file=sys.stderr)
        return False
    except KeyboardInterrupt:
        print(f"\n✗ Download interrupted. Run again to resume.", file=sys.stderr)
        return False


def verify_file_size(file_path: Path, expected_min_size: int) -> bool:
    """Verify that downloaded file is at least the expected size."""
    if not file_path.exists():
        return False
    
    actual_size = file_path.stat().st_size
    if actual_size < expected_min_size:
        print(f"✗ {file_path.name} seems incomplete: {actual_size:,} bytes")
        return False
    
    return True


def main():
    """Download both the Wikipedia dump and index file."""
    print("=" * 80)
    print("Wikipedia Dump Downloader")
    print("=" * 80)
    print()
    
    # File paths
    dump_path = DATA_DIR / "enwiki-latest-pages-articles-multistream.xml.bz2"
    index_path = DATA_DIR / "enwiki-latest-pages-articles-multistream-index.txt.bz2"
    
    # Download index file first (smaller, faster)
    print("Step 1/2: Downloading index file (~250 MB)")
    print("-" * 80)
    if download_with_resume(INDEX_URL, index_path):
        print()
    else:
        print("Failed to download index file. Please check your connection and try again.")
        return 1
    
    # Download main dump file
    print("Step 2/2: Downloading Wikipedia dump (~22 GB)")
    print("-" * 80)
    print("Note: This will take 1-2 hours depending on your connection speed.")
    print("      You can interrupt (Ctrl+C) and resume later.")
    print()
    
    if download_with_resume(DUMP_URL, dump_path):
        print()
    else:
        print("Failed to download dump file. Please check your connection and try again.")
        return 1
    
    # Verify downloads
    print("=" * 80)
    print("Download Complete!")
    print("=" * 80)
    print(f"Dump file:  {dump_path}")
    print(f"Index file: {index_path}")
    print()
    print("Next steps:")
    print("  1. Run test: python process_wiki.py --test")
    print("  2. Full run: python process_wiki.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

