# Benford's Law Wikipedia Analysis

A high-performance pipeline to validate Benford's Law using Wikipedia data across different domains. Uses parallel processing, modern Python libraries (Polars, lxml), and robust crash recovery for processing the full English Wikipedia dump.

## Features

- **Parallel Processing**: 6 worker processes for fast processing (~30-60 minutes for full Wikipedia)
- **Crash Recovery**: Automatic checkpointing and resume capability
- **Memory Efficient**: Streaming decompression, ~4GB peak memory usage
- **Domain Categorization**: Automatically categorizes articles by Infobox type
- **Statistical Analysis**: Chi-Square, Mean Absolute Deviation, visualizations
- **Rich UI**: Beautiful terminal progress bars and statistics

## Requirements

- Python 3.8+
- macOS/Linux (tested on Apple Silicon M3 Pro)
- 55GB+ free disk space
- 4GB+ RAM (18GB recommended)

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Download Wikipedia Dump

Download the Wikipedia dump and index files (~22GB total, 1-2 hours):

```bash
python download_dump.py
```

The script supports resume if interrupted (Ctrl+C). Just run it again.

### Step 2: Quick Validation (Optional)

Test the pipeline on 1,000 articles before the full run:

```bash
python process_wiki.py --test
```

This validates that extraction and categorization are working correctly.

### Step 3: Full Processing

Process the entire Wikipedia dump (30-60 minutes):

```bash
python process_wiki.py
```

**Options:**
- `--workers N`: Number of parallel workers (default: auto-detect)
- `--chunks N`: Number of chunks to divide work into (default: 100)
- `--no-resume`: Start fresh instead of resuming from checkpoint

The script will:
- Process ~6.8 million articles
- Extract numbers and categorize by domain
- Save results to `data/numbers.parquet` (~500MB)
- Generate `data/summary.json` with aggregated counts

**To resume after interruption:**
Just run the same command again. It will automatically resume from the last checkpoint.

### Step 4: Analyze Results

Generate statistical analysis and visualizations:

```bash
python analyze_benford.py
```

This creates:
- `output/domain_comparison.png`: Bar charts comparing observed vs expected distributions
- `output/deviation_heatmap.png`: Heatmap showing deviations from Benford's Law
- `output/summary_statistics.csv`: Statistical test results per domain

## Output Files

```
data/
├── numbers.parquet          # Detailed number records (~500MB)
│   ├── article_id          # Wikipedia page ID
│   ├── domain              # Category (Geography, People, etc.)
│   ├── number              # The extracted number
│   ├── first_digit         # Leading digit (1-9)
│   └── second_digit        # Second digit (0-9)
├── summary.json            # Aggregated counts per domain/digit
└── state.json              # Processing checkpoint (for resume)

output/
├── domain_comparison.png   # Visualization: observed vs Benford
├── deviation_heatmap.png   # Visualization: deviations heatmap
└── summary_statistics.csv  # Chi-Square, MAD, p-values per domain
```

## Domain Categories

Articles are automatically categorized into:

- **Geography**: Countries, cities, mountains, rivers, etc.
- **People**: Biographies, scientists, artists, athletes, etc.
- **Science**: Elements, planets, compounds, diseases, etc.
- **Sports**: Teams, stadiums, tournaments, athletes, etc.
- **Business**: Companies, universities, organizations, etc.
- **Media**: Films, TV shows, albums, video games, books, etc.
- **Military**: Conflicts, weapons, aircraft, ships, etc.
- **Biology**: Species, animals, plants, insects, etc.
- **Infrastructure**: Bridges, buildings, airports, roads, etc.
- **Events**: Elections, disasters, festivals, etc.
- **Uncategorized**: Articles without recognized infoboxes

## How It Works

### Architecture

1. **Download**: Fetch Wikipedia dump and index file
2. **Chunk Creation**: Divide 6.8M articles into ~100 chunks
3. **Parallel Processing**: 6 workers process chunks simultaneously
4. **Number Extraction**: Two-pass algorithm (fast check + full parse)
5. **Domain Categorization**: Map Infobox types to broad categories
6. **Merge**: Combine chunk results into final Parquet file
7. **Analysis**: Statistical tests and visualizations

### Two-Pass Extraction

**Pass 1 (Fast)**: Quick regex scan on raw bytes
- Checks if article contains numbers
- ~0.1ms per article
- Filters out ~20% of articles

**Pass 2 (Full)**: Parse wikitext with mwparserfromhell
- Extract infobox type → map to domain
- Strip markup → extract all numbers
- ~5ms per article

### Number Extraction

- Pattern: `(?<![0-9])[1-9][0-9]{0,15}(?:\.[0-9]+)?(?![0-9])`
- Captures integers and decimals
- No filtering applied (to see what follows/doesn't follow Benford's Law)

## Performance

| Step | Duration | Notes |
|------|----------|-------|
| Download | 1-2 hours | Depends on internet speed |
| Test | ~2 minutes | Validates on 1000 articles |
| Full Processing | 30-60 minutes | 6 workers on M3 Pro |
| Analysis | ~1 minute | Statistical tests + plots |

**Memory Usage**: ~3.7GB peak (6 workers × 500MB + overhead)

**Disk Space**:
- Wikipedia dump: 22GB (can delete after processing)
- Index file: 250MB (can delete after processing)
- Output data: ~500MB (numbers.parquet)
- Temp files: ~2GB (deleted after merge)

## Benford's Law

Benford's Law states that in many naturally occurring datasets, the leading digit follows a specific distribution:

| Digit | Expected Frequency |
|-------|-------------------|
| 1 | 30.1% |
| 2 | 17.6% |
| 3 | 12.5% |
| 4 | 9.7% |
| 5 | 7.9% |
| 6 | 6.7% |
| 7 | 5.8% |
| 8 | 5.1% |
| 9 | 4.6% |

This project tests whether Wikipedia numbers follow Benford's Law and whether the conformance differs across domains.

## Statistical Tests

### Chi-Square Test
Tests if observed distribution differs significantly from expected (Benford).
- **Null hypothesis**: Data follows Benford's Law
- **p > 0.05**: Consistent with Benford's Law
- **p < 0.05**: Significantly different from Benford's Law

### Mean Absolute Deviation (MAD)
Average of absolute deviations from Benford distribution.
- **MAD < 0.006**: Close conformity
- **MAD 0.006-0.012**: Acceptable conformity
- **MAD 0.012-0.015**: Marginal conformity
- **MAD > 0.015**: Non-conformity

## Troubleshooting

### Out of Memory
- Reduce workers: `python process_wiki.py --workers 4`
- Close other applications
- Check available RAM: The script auto-detects optimal worker count

### Disk Full
- Delete dump file after processing to free 22GB
- Reduce chunk size (edit `process_wiki.py`)

### Resume After Crash
Just run the same command again:
```bash
python process_wiki.py
```

The script automatically resumes from the last checkpoint.

### Force Fresh Start
```bash
rm data/state.json
python process_wiki.py
```

## License

MIT License - see LICENSE file

## Citation

If you use this in your research, please cite:
```
Benford's Law Wikipedia Analysis
GitHub: [Your Repository URL]
```

## References

- Benford, F. (1938). "The law of anomalous numbers". Proceedings of the American Philosophical Society. 78 (4): 551–572.
- Wikipedia Dumps: https://dumps.wikimedia.org/
