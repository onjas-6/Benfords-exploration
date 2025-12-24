#!/usr/bin/env python3
"""
Main Wikipedia processing script with parallel workers.
"""

import sys
import bz2
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import multiprocessing as mp
from multiprocessing import Pool
import psutil
import polars as pl
import orjson
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table

from src.worker import process_chunk_with_retry
from src.checkpoint import StateManager, ProcessingState


console = Console()


def parse_index_file(index_path: Path) -> List[Tuple[int, int, str]]:
    """
    Parse the multistream index file.
    
    Args:
        index_path: Path to index file
        
    Returns:
        List of tuples: (byte_offset, article_id, title)
    """
    console.print(f"[cyan]Parsing index file: {index_path}[/cyan]")
    
    entries = []
    
    with bz2.open(index_path, 'rt', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':', 2)
            if len(parts) == 3:
                try:
                    offset = int(parts[0])
                    article_id = int(parts[1])
                    title = parts[2]
                    entries.append((offset, article_id, title))
                except ValueError:
                    continue
    
    console.print(f"[green]✓ Found {len(entries):,} articles in index[/green]")
    return entries


def create_chunks(
    entries: List[Tuple[int, int, str]],
    num_chunks: int
) -> List[Dict]:
    """
    Divide articles into chunks for parallel processing.
    
    Args:
        entries: List of (offset, article_id, title) tuples
        num_chunks: Number of chunks to create
        
    Returns:
        List of chunk definitions
    """
    # Group by offset (articles in same bz2 stream)
    offset_groups = {}
    for offset, article_id, title in entries:
        if offset not in offset_groups:
            offset_groups[offset] = []
        offset_groups[offset].append(article_id)
    
    # Get unique offsets sorted
    offsets = sorted(offset_groups.keys())
    
    # Divide into chunks
    chunks_per_group = max(1, len(offsets) // num_chunks)
    
    chunks = []
    for i in range(0, len(offsets), chunks_per_group):
        chunk_offsets = offsets[i:i + chunks_per_group]
        
        if not chunk_offsets:
            continue
        
        start_offset = chunk_offsets[0]
        end_offset = chunk_offsets[-1] if i + chunks_per_group < len(offsets) else offsets[-1]
        
        # Get next offset for boundary
        next_idx = offsets.index(end_offset) + 1
        if next_idx < len(offsets):
            end_offset = offsets[next_idx]
        else:
            end_offset = -1  # Read to end
        
        # Collect all article IDs in this chunk
        article_ids = []
        for offset in chunk_offsets:
            article_ids.extend(offset_groups[offset])
        
        chunks.append({
            'chunk_id': len(chunks),
            'start_offset': start_offset,
            'end_offset': end_offset,
            'article_ids': article_ids,
            'article_count': len(article_ids)
        })
    
    console.print(f"[green]✓ Created {len(chunks)} chunks[/green]")
    return chunks


def get_optimal_workers() -> int:
    """Determine optimal number of worker processes."""
    available_ram = psutil.virtual_memory().available
    ram_per_worker = 500 * 1024 * 1024  # 500MB
    cpu_cores = psutil.cpu_count(logical=False) or 4
    
    max_by_ram = available_ram // ram_per_worker
    max_by_cpu = cpu_cores
    
    optimal = min(max_by_ram, max_by_cpu, 8)  # Cap at 8
    return max(1, optimal)


def worker_wrapper(args):
    """Wrapper for multiprocessing."""
    chunk_id, dump_path, temp_dir, start_offset, end_offset, article_ids = args
    
    try:
        return process_chunk_with_retry(
            chunk_id=chunk_id,
            dump_path=dump_path,
            temp_dir=temp_dir,
            start_offset=start_offset,
            end_offset=end_offset,
            article_ids=article_ids
        )
    except Exception as e:
        console.print(f"[red]✗ Chunk {chunk_id} failed: {e}[/red]")
        return None, 0, 0


def merge_parquet_files(temp_files: List[Path], output_path: Path):
    """
    Merge temporary parquet files into final output.
    
    Args:
        temp_files: List of temporary parquet file paths
        output_path: Final output path
    """
    console.print("[cyan]Merging temporary files...[/cyan]")
    
    # Filter out None values
    temp_files = [f for f in temp_files if f and f.exists()]
    
    if not temp_files:
        console.print("[red]✗ No data to merge[/red]")
        return
    
    # Read and concatenate
    dfs = []
    for temp_file in temp_files:
        try:
            df = pl.read_parquet(temp_file)
            dfs.append(df)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {temp_file}: {e}[/yellow]")
    
    if not dfs:
        console.print("[red]✗ No valid data files[/red]")
        return
    
    # Concatenate all dataframes
    final_df = pl.concat(dfs)
    
    # Write final file with zstd compression
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.write_parquet(output_path, compression='zstd')
    
    console.print(f"[green]✓ Merged {len(temp_files)} files into {output_path}[/green]")
    console.print(f"[green]  Total records: {final_df.height:,}[/green]")
    
    # Clean up temp files
    for temp_file in temp_files:
        try:
            temp_file.unlink()
        except Exception:
            pass


def generate_summary(data_path: Path, output_path: Path):
    """Generate summary JSON file."""
    console.print("[cyan]Generating summary...[/cyan]")
    
    df = pl.read_parquet(data_path)
    
    # Group by domain and first digit
    summary = {}
    
    for domain in df['domain'].unique().to_list():
        domain_df = df.filter(pl.col('domain') == domain)
        digit_counts = domain_df.group_by('first_digit').agg(pl.count()).sort('first_digit')
        
        summary[domain] = {}
        for row in digit_counts.iter_rows(named=True):
            summary[domain][str(row['first_digit'])] = row['count']
    
    # Write summary
    with open(output_path, 'wb') as f:
        f.write(orjson.dumps(summary, option=orjson.OPT_INDENT_2))
    
    console.print(f"[green]✓ Summary saved to {output_path}[/green]")


def display_progress_table(state: ProcessingState):
    """Display progress statistics."""
    table = Table(title="Processing Statistics")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Articles Processed", f"{state.stats['articles']:,}")
    table.add_row("Numbers Extracted", f"{state.stats['numbers']:,}")
    table.add_row("Completed Chunks", f"{len(state.completed_chunks)}/{state.total_chunks}")
    table.add_row("Failed Chunks", f"{len(state.failed_chunks)}")
    
    if state.stats['articles'] > 0:
        avg_numbers = state.stats['numbers'] / state.stats['articles']
        table.add_row("Avg Numbers/Article", f"{avg_numbers:.1f}")
    
    console.print(table)


def process_wikipedia(
    dump_path: Path,
    index_path: Path,
    output_path: Path,
    num_workers: int = None,
    num_chunks: int = 100,
    resume: bool = True
):
    """
    Main processing function.
    
    Args:
        dump_path: Path to Wikipedia dump
        index_path: Path to index file
        output_path: Output parquet file path
        num_workers: Number of parallel workers (auto if None)
        num_chunks: Number of chunks to create
        resume: Whether to resume from checkpoint
    """
    console.print("[bold cyan]Wikipedia Benford Analysis - Processing[/bold cyan]")
    console.print()
    
    # Setup paths
    data_dir = dump_path.parent
    temp_dir = data_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    state_path = data_dir / "state.json"
    state_manager = StateManager(state_path)
    
    # Load or create state
    if resume and state_path.exists():
        console.print("[yellow]Resuming from checkpoint...[/yellow]")
        state = state_manager.load()
    else:
        console.print("[cyan]Starting new processing run...[/cyan]")
        state = ProcessingState()
        state.total_chunks = num_chunks
        state_manager.save(state)
    
    # Parse index
    entries = parse_index_file(index_path)
    
    # Create chunks
    chunks = create_chunks(entries, num_chunks)
    state.total_chunks = len(chunks)
    state_manager.save(state)
    
    # Determine workers
    if num_workers is None:
        num_workers = get_optimal_workers()
    
    console.print(f"[green]Using {num_workers} parallel workers[/green]")
    console.print()
    
    # Get pending chunks
    pending = state_manager.get_pending_chunks()
    pending_chunks = [c for c in chunks if c['chunk_id'] in pending]
    
    if not pending_chunks:
        console.print("[green]✓ All chunks already processed![/green]")
        display_progress_table(state)
        return
    
    console.print(f"[cyan]Processing {len(pending_chunks)} chunks...[/cyan]")
    console.print()
    
    # Process chunks in parallel
    temp_files = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task(
            "Processing Wikipedia...",
            total=len(pending_chunks)
        )
        
        # Prepare worker arguments
        worker_args = [
            (
                chunk['chunk_id'],
                dump_path,
                temp_dir,
                chunk['start_offset'],
                chunk['end_offset'],
                chunk['article_ids']
            )
            for chunk in pending_chunks
        ]
        
        # Process with pool
        with Pool(processes=num_workers) as pool:
            for result in pool.imap_unordered(worker_wrapper, worker_args):
                temp_file, articles, numbers = result
                
                if temp_file:
                    temp_files.append(temp_file)
                    # Extract chunk_id from result
                    chunk_id = int(temp_file.stem.split('_')[1])
                    state_manager.mark_chunk_completed(chunk_id, articles, numbers)
                
                progress.advance(task)
    
    console.print()
    console.print("[green]✓ Processing complete![/green]")
    console.print()
    
    # Display final stats
    state = state_manager.load()
    display_progress_table(state)
    console.print()
    
    # Merge files
    merge_parquet_files(temp_files, output_path)
    
    # Generate summary
    if output_path.exists():
        summary_path = data_dir / "summary.json"
        generate_summary(output_path, summary_path)


def quick_validate(dump_path: Path, index_path: Path, sample_size: int = 1000):
    """
    Quick validation on a sample of articles.
    
    Args:
        dump_path: Path to Wikipedia dump
        index_path: Path to index file
        sample_size: Number of articles to sample
    """
    console.print(f"[bold cyan]Quick Validation - Testing on {sample_size} articles[/bold cyan]")
    console.print()
    
    # Parse index
    entries = parse_index_file(index_path)
    
    # Take first N articles, but also get N+1 to determine proper end offset
    sample_entries = entries[:sample_size]
    
    # Get the offset right after our sample for proper boundary
    if len(entries) > sample_size:
        next_offset = entries[sample_size][0]
        # Manually create chunk with proper end offset
        offsets = sorted(set(e[0] for e in sample_entries))
        article_ids = [e[1] for e in sample_entries]
        
        chunks = [{
            'chunk_id': 0,
            'start_offset': offsets[0],
            'end_offset': next_offset,  # Use next article's offset as boundary
            'article_ids': article_ids,
            'article_count': len(article_ids)
        }]
        console.print(f"[green]✓ Created 1 chunk with proper boundaries[/green]")
    else:
        # Fallback to original method
        chunks = create_chunks(sample_entries, num_chunks=1)
    
    if not chunks:
        console.print("[red]✗ Could not create chunks[/red]")
        return
    
    chunk = chunks[0]
    
    # Setup temp directory
    temp_dir = dump_path.parent / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Process chunk
    console.print("[cyan]Processing sample...[/cyan]")
    
    temp_file, articles, numbers = process_chunk_with_retry(
        chunk_id=0,
        dump_path=dump_path,
        temp_dir=temp_dir,
        start_offset=chunk['start_offset'],
        end_offset=chunk['end_offset'],
        article_ids=chunk['article_ids']
    )
    
    if not temp_file or not temp_file.exists():
        console.print("[red]✗ Processing failed[/red]")
        return
    
    # Load and analyze
    df = pl.read_parquet(temp_file)
    
    # Show statistics
    table = Table(title="Validation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Articles Processed", f"{articles:,}")
    table.add_row("Numbers Extracted", f"{numbers:,}")
    table.add_row("Avg Numbers/Article", f"{numbers/articles:.1f}")
    table.add_row("Domains Found", f"{df['domain'].n_unique()}")
    
    console.print(table)
    console.print()
    
    # Show first digit distribution
    digit_dist = df.group_by('first_digit').agg(pl.count()).sort('first_digit')
    
    table2 = Table(title="First Digit Distribution (Sample)")
    table2.add_column("Digit", style="cyan")
    table2.add_column("Count", style="green")
    table2.add_column("Frequency", style="yellow")
    table2.add_column("Benford", style="magenta")
    
    benford = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079, 
               6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}
    
    total = numbers
    for row in digit_dist.iter_rows(named=True):
        digit = row['first_digit']
        count = row['count']
        freq = count / total
        expected = benford.get(digit, 0)
        
        table2.add_row(
            str(digit),
            f"{count:,}",
            f"{freq:.3f}",
            f"{expected:.3f}"
        )
    
    console.print(table2)
    console.print()
    console.print("[green]✓ Validation successful! Ready for full run.[/green]")
    
    # Clean up
    temp_file.unlink()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process Wikipedia dump for Benford's Law analysis"
    )
    parser.add_argument(
        "--dump",
        type=Path,
        default=Path("data/enwiki-latest-pages-articles-multistream.xml.bz2"),
        help="Path to Wikipedia dump file"
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=Path("data/enwiki-latest-pages-articles-multistream-index.txt.bz2"),
        help="Path to index file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/numbers.parquet"),
        help="Output parquet file path"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (auto if not specified)"
    )
    parser.add_argument(
        "--chunks",
        type=int,
        default=100,
        help="Number of chunks to divide work into"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh instead of resuming"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Quick validation on 1000 articles"
    )
    parser.add_argument(
        "--quick-validate",
        action="store_true",
        help="Quick validation mode (alias for --test)"
    )
    
    args = parser.parse_args()
    
    # Check if files exist
    if not args.dump.exists():
        console.print(f"[red]✗ Dump file not found: {args.dump}[/red]")
        console.print("[yellow]Run download_dump.py first[/yellow]")
        return 1
    
    if not args.index.exists():
        console.print(f"[red]✗ Index file not found: {args.index}[/red]")
        console.print("[yellow]Run download_dump.py first[/yellow]")
        return 1
    
    # Run validation or full processing
    try:
        if args.test or args.quick_validate:
            quick_validate(args.dump, args.index)
        else:
            process_wikipedia(
                dump_path=args.dump,
                index_path=args.index,
                output_path=args.output,
                num_workers=args.workers,
                num_chunks=args.chunks,
                resume=not args.no_resume
            )
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]✗ Interrupted by user[/yellow]")
        console.print("[cyan]Run again with same arguments to resume[/cyan]")
        return 1
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

