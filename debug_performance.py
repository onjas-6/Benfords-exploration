#!/usr/bin/env python3
"""
Performance debugging script - identifies bottlenecks in processing pipeline.
"""

import time
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, '/root/Benfords-exploration')

from collections import Counter
from src.extractor import extract_numbers_from_bytes, extract_categorized_numbers
from src.categorizer import strip_wikitext
from src.number_categorizer_optimized import categorize_number_optimized
import mwparserfromhell
import re


# Sample Wikipedia article (realistic size)
SAMPLE_ARTICLE = """
{{Infobox settlement
|name = San Francisco
|population = 873,965
|area_total_km2 = 121.4
|elevation_m = 16
|coordinates = {{coord|37.7749|N|122.4194|W}}
}}
'''San Francisco''' is a city in [[California]], [[United States]]. As of the [[2020 United States census|2020 census]], the city had a population of 873,965, making it the 17th most populous city in the United States. The city covers an area of {{convert|121.4|km2|sqmi}}.

== History ==
Founded in 1776, San Francisco has a rich history spanning over 200 years. The [[California Gold Rush]] of 1849 brought rapid growth, with the population increasing from 1,000 to 25,000 in just two years. By 1900, the population had reached 342,782.

== Geography ==
San Francisco is located at {{coord|37.7749|N|122.4194|W|display=inline}}. The city sits on the tip of the [[San Francisco Peninsula]], with an elevation ranging from sea level to 282 meters (925 feet) at [[Twin Peaks]]. The total area is 600.6 km² (231.9 sq mi), of which 121.4 km² (46.9 sq mi) is land.

== Climate ==
The average temperature is 14°C (57°F), with summer highs around 21°C (70°F) and winter lows around 8°C (46°F). Annual rainfall averages 583 mm (23 inches).

== Economy ==
San Francisco's GDP is approximately $500 billion. The median household income is $112,449, with a poverty rate of 10.3%. Major employers include technology companies with revenues exceeding $10 billion annually.

== Transportation ==
The city has 1,200 km of streets and 80 km of bicycle lanes. [[San Francisco International Airport]] (SFO) handles 58 million passengers per year. The [[BART]] system covers 180 km and serves 400,000 riders daily.

== Demographics ==
{| class="wikitable"
|-
! Year !! Population
|-
| 1900 || 342,782
|-
| 1950 || 775,357
|-
| 2000 || 776,733
|-
| 2020 || 873,965
|}

As of 2020, the city had:
* Population density: 7,200 per km²
* Median age: 38.5 years
* 48.5% male, 51.5% female
* Per capita income: $68,883

[[Category:Cities in California]]
[[Category:Populated places established in 1776]]
"""


def benchmark_operation(name, func, iterations=100):
    """Benchmark a function multiple times."""
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    avg = sum(times) / len(times)
    median = sorted(times)[len(times) // 2]
    p95 = sorted(times)[int(len(times) * 0.95)]
    max_time = max(times)
    
    print(f"\n{name}:")
    print(f"  Mean:   {avg:>8.2f} ms")
    print(f"  Median: {median:>8.2f} ms")
    print(f"  P95:    {p95:>8.2f} ms")
    print(f"  Max:    {max_time:>8.2f} ms")
    
    return avg, result


def main():
    print("="*70)
    print("PERFORMANCE DEBUGGING - Identifying Bottlenecks")
    print("="*70)
    print(f"\nSample article size: {len(SAMPLE_ARTICLE):,} bytes")
    print(f"Running 100 iterations per test...")
    
    # Prepare data
    article_bytes = SAMPLE_ARTICLE.encode('utf-8')
    
    # Test 1: Parse wikitext with mwparserfromhell
    print("\n" + "="*70)
    print("TEST 1: Parse Wikitext (mwparserfromhell)")
    print("="*70)
    
    def test_parse():
        parsed = mwparserfromhell.parse(SAMPLE_ARTICLE)
        return parsed
    
    parse_time, parsed = benchmark_operation("mwparserfromhell.parse", test_parse, 100)
    
    # Test 2: Strip wikitext to plain text
    print("\n" + "="*70)
    print("TEST 2: Strip Wikitext to Plain Text")
    print("="*70)
    
    def test_strip():
        return strip_wikitext(SAMPLE_ARTICLE)
    
    strip_time, plain_text = benchmark_operation("strip_wikitext", test_strip, 100)
    plain_bytes = plain_text.encode('utf-8')
    
    # Test 3: Simple number extraction (old method)
    print("\n" + "="*70)
    print("TEST 3: Simple Number Extraction (No Categories)")
    print("="*70)
    
    def test_simple_extract():
        return extract_numbers_from_bytes(plain_bytes)
    
    simple_time, simple_numbers = benchmark_operation("extract_numbers_from_bytes", test_simple_extract, 100)
    print(f"  Numbers found: {len(simple_numbers)}")
    
    # Test 4: Categorized extraction (new method)
    print("\n" + "="*70)
    print("TEST 4: Categorized Number Extraction (With Categories)")
    print("="*70)
    
    def test_categorized_extract():
        return extract_categorized_numbers(plain_bytes)
    
    categorized_time, categorized_numbers = benchmark_operation("extract_categorized_numbers", test_categorized_extract, 100)
    print(f"  Numbers found: {len(categorized_numbers)}")
    
    # Show category breakdown
    if categorized_numbers:
        categories = Counter(cat for _, cat in categorized_numbers[:20])
        print(f"\n  Sample categories:")
        for cat, count in categories.most_common(10):
            print(f"    {cat:20} {count:>3}")
    
    # Test 5: OPTIMIZED Categorized extraction
    print("\n" + "="*70)
    print("TEST 5: OPTIMIZED Categorized Extraction (With Trigger Pre-filtering)")
    print("="*70)
    
    NUMBER_PATTERN = re.compile(r'(?<![0-9])[1-9][0-9]{0,15}(?:\.[0-9]+)?(?![0-9])')
    
    def test_optimized_extract():
        results = []
        for match in NUMBER_PATTERN.finditer(plain_text):
            num_str = match.group(0)
            start_pos = match.start()
            end_pos = match.end()
            context_start = max(0, start_pos - 30)
            context_end = min(len(plain_text), end_pos + 30)
            context = plain_text[context_start:context_end]
            
            category = categorize_number_optimized(num_str, context)
            results.append((float(num_str.replace(',', '')), category))
        return results
    
    optimized_time, optimized_numbers = benchmark_operation("extract_categorized_OPTIMIZED", test_optimized_extract, 100)
    print(f"  Numbers found: {len(optimized_numbers)}")
    
    if optimized_numbers:
        categories = Counter(cat for _, cat in optimized_numbers[:20])
        print(f"\n  Sample categories:")
        for cat, count in categories.most_common(10):
            print(f"    {cat:20} {count:>3}")
    
    speedup = categorized_time / optimized_time if optimized_time > 0 else 0
    print(f"\n  🚀 SPEEDUP: {speedup:.1f}x faster than original!")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - Time Breakdown Per Article")
    print("="*70)
    
    total_simple = parse_time + strip_time + simple_time
    total_categorized = parse_time + strip_time + categorized_time
    total_optimized = parse_time + strip_time + optimized_time
    overhead = categorized_time - simple_time
    overhead_opt = optimized_time - simple_time
    
    print(f"\nSIMPLE PIPELINE (no categorization):")
    print(f"  1. mwparserfromhell:  {parse_time:>8.2f} ms  ({parse_time/total_simple*100:.1f}%)")
    print(f"  2. strip_wikitext:    {strip_time:>8.2f} ms  ({strip_time/total_simple*100:.1f}%)")
    print(f"  3. extract_numbers:   {simple_time:>8.2f} ms  ({simple_time/total_simple*100:.1f}%)")
    print(f"  {'─'*40}")
    print(f"  TOTAL:                {total_simple:>8.2f} ms")
    
    print(f"\nORIGINAL CATEGORIZED PIPELINE (59 patterns on every number):")
    print(f"  1. mwparserfromhell:  {parse_time:>8.2f} ms  ({parse_time/total_categorized*100:.1f}%)")
    print(f"  2. strip_wikitext:    {strip_time:>8.2f} ms  ({strip_time/total_categorized*100:.1f}%)")
    print(f"  3. extract+categorize:{categorized_time:>8.2f} ms  ({categorized_time/total_categorized*100:.1f}%)")
    print(f"  {'─'*40}")
    print(f"  TOTAL:                {total_categorized:>8.2f} ms")
    print(f"  Overhead: {overhead:.2f}ms")
    
    print(f"\n🚀 OPTIMIZED CATEGORIZED PIPELINE (trigger pre-filtering):")
    print(f"  1. mwparserfromhell:  {parse_time:>8.2f} ms  ({parse_time/total_optimized*100:.1f}%)")
    print(f"  2. strip_wikitext:    {strip_time:>8.2f} ms  ({strip_time/total_optimized*100:.1f}%)")
    print(f"  3. extract+categorize:{optimized_time:>8.2f} ms  ({optimized_time/total_optimized*100:.1f}%)")
    print(f"  {'─'*40}")
    print(f"  TOTAL:                {total_optimized:>8.2f} ms")
    print(f"  Overhead: {overhead_opt:.2f}ms")
    print(f"\n  ✅ SPEEDUP: {total_categorized/total_optimized:.1f}x faster than original!")
    
    # Extrapolate to full dataset
    print("\n" + "="*70)
    print("EXTRAPOLATION - Processing Time Estimates")
    print("="*70)
    
    articles_22m = 22_000_000
    workers = 60
    
    print(f"\nWith ORIGINAL categorizer ({total_categorized:.1f}ms/article):")
    for sample_pct, desc in [(0.001, "0.1%"), (0.01, "1%"), (0.05, "5%"), (1.0, "100%")]:
        sample_size = int(articles_22m * sample_pct)
        time_single = sample_size * total_categorized / 1000 / 60  # minutes
        time_parallel = time_single / workers
        
        if time_parallel < 1:
            time_str = f"{time_parallel * 60:.0f} seconds"
        else:
            time_str = f"{time_parallel:.1f} minutes"
        
        print(f"  {desc:5} ({sample_size:>10,} articles): {time_str}")
    
    print(f"\n🚀 With OPTIMIZED categorizer ({total_optimized:.1f}ms/article):")
    for sample_pct, desc in [(0.001, "0.1%"), (0.01, "1%"), (0.05, "5%"), (1.0, "100%")]:
        sample_size = int(articles_22m * sample_pct)
        time_single = sample_size * total_optimized / 1000 / 60  # minutes
        time_parallel = time_single / workers
        
        if time_parallel < 1:
            time_str = f"{time_parallel * 60:.0f} seconds"
        else:
            time_str = f"{time_parallel:.1f} minutes"
        
        print(f"  {desc:5} ({sample_size:>10,} articles): {time_str}")
    
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    
    speedup_factor = total_categorized / total_optimized
    
    if speedup_factor > 2:
        print(f"\n✅ OPTIMIZATION SUCCESSFUL!")
        print(f"   Original: {total_categorized:.1f}ms/article")
        print(f"   Optimized: {total_optimized:.1f}ms/article")
        print(f"   Speedup: {speedup_factor:.1f}x faster!")
    else:
        print(f"\n⚠️  Optimization had limited effect")
        print(f"   Speedup: only {speedup_factor:.1f}x")
    
    time_1pct_opt = articles_22m * 0.01 * total_optimized / 1000 / workers
    if time_1pct_opt < 60:
        print(f"\n   1% sample: ~{time_1pct_opt:.0f} seconds")
    else:
        print(f"\n   1% sample: ~{time_1pct_opt/60:.1f} minutes")
    
    time_100pct = articles_22m * total_optimized / 1000 / workers / 60
    print(f"   100% sample: ~{time_100pct:.0f} minutes")
    print("="*70)


if __name__ == '__main__':
    main()

