"""
Worker process for parallel Wikipedia processing.
Handles chunk processing with two-pass extraction and LZ4 compression.
"""

import bz2
import gc
import lz4.frame
from pathlib import Path
from typing import List, Tuple, Dict
from io import BytesIO
import mwparserfromhell
import polars as pl
from lxml import etree

from .extractor import quick_has_numbers, extract_numbers_from_bytes, analyze_number
from .categorizer import extract_infobox_type, categorize_by_infobox, strip_wikitext


class ChunkWorker:
    """Worker for processing a chunk of Wikipedia articles."""
    
    def __init__(self, dump_path: Path, temp_dir: Path):
        """
        Initialize chunk worker.
        
        Args:
            dump_path: Path to Wikipedia dump file
            temp_dir: Directory for temporary output files
        """
        self.dump_path = dump_path
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def process_chunk(
        self,
        chunk_id: int,
        start_offset: int,
        end_offset: int,
        article_ids: List[int]
    ) -> Tuple[Path, int, int]:
        """
        Process a chunk of articles and write results to temp file.
        
        Args:
            chunk_id: Chunk identifier
            start_offset: Byte offset to start reading
            end_offset: Byte offset to stop reading
            article_ids: List of article IDs in this chunk
            
        Returns:
            Tuple of (temp_file_path, articles_processed, numbers_extracted)
        """
        article_ids_set = set(article_ids) if article_ids else None
        
        records = []
        articles_processed = 0
        numbers_extracted = 0
        
        # Open dump file and seek to start
        with open(self.dump_path, 'rb') as f:
            f.seek(start_offset)
            
            # Read the chunk
            if end_offset > 0:
                chunk_size = end_offset - start_offset
                compressed_data = f.read(chunk_size)
            else:
                # For last chunk, read in manageable pieces
                # The multistream format should handle this gracefully
                max_read = 200 * 1024 * 1024  # 200MB max per chunk
                compressed_data = f.read(max_read)
            
            try:
                decompressed_data = bz2.decompress(compressed_data)
            except Exception as e:
                print(f"Warning: Could not decompress chunk {chunk_id}: {e}")
                return None, 0, 0
            
            # Parse XML
            try:
                # Wrap in root element if needed
                if not decompressed_data.startswith(b'<mediawiki'):
                    xml_data = b'<mediawiki>' + decompressed_data + b'</mediawiki>'
                else:
                    xml_data = decompressed_data
                
                # Parse with lxml
                context = etree.iterparse(
                    BytesIO(xml_data),
                    events=('end',),
                    tag='{http://www.mediawiki.org/xml/export-0.11/}page'
                )
                
                for event, elem in context:
                    try:
                        article_data = self._process_article(elem)
                        
                        if article_data:
                            # Filter by article IDs if provided
                            if article_ids_set is None or article_data['article_id'] in article_ids_set:
                                records.extend(article_data['numbers'])
                                articles_processed += 1
                                numbers_extracted += len(article_data['numbers'])
                        
                        # Clear element to free memory
                        elem.clear()
                        while elem.getprevious() is not None:
                            del elem.getparent()[0]
                            
                    except Exception as e:
                        # Skip problematic articles
                        continue
                
                # Clear context
                del context
                
            except Exception as e:
                print(f"Warning: XML parsing error in chunk {chunk_id}: {e}")
                return None, 0, 0
        
        # Write records to temp file
        if records:
            df = pl.DataFrame(records)
            temp_path = self.temp_dir / f"chunk_{chunk_id:04d}.parquet"
            
            # Write with LZ4 compression
            df.write_parquet(temp_path, compression='lz4')
            
            # Force garbage collection
            gc.collect()
            
            return temp_path, articles_processed, numbers_extracted
        
        return None, articles_processed, numbers_extracted
    
    def _process_article(self, page_elem) -> Dict:
        """
        Process a single article element.
        
        Args:
            page_elem: lxml Element for a page
            
        Returns:
            Dict with article_id and list of number records, or None
        """
        ns = '{http://www.mediawiki.org/xml/export-0.11/}'
        
        # Get namespace
        namespace_elem = page_elem.find(f'{ns}ns')
        if namespace_elem is None or namespace_elem.text != '0':
            return None  # Skip non-main namespace
        
        # Get article ID
        id_elem = page_elem.find(f'{ns}id')
        if id_elem is None:
            return None
        
        try:
            article_id = int(id_elem.text)
        except (ValueError, TypeError):
            return None
        
        # Get revision text
        revision = page_elem.find(f'{ns}revision')
        if revision is None:
            return None
        
        text_elem = revision.find(f'{ns}text')
        if text_elem is None or text_elem.text is None:
            return None
        
        wikitext = text_elem.text
        
        # Convert to bytes for fast checking
        wikitext_bytes = wikitext.encode('utf-8', errors='ignore')
        
        # PASS 1: Quick check if article has numbers
        if not quick_has_numbers(wikitext_bytes):
            return None
        
        # PASS 2: Full extraction
        try:
            # Extract domain from infobox
            infobox_type = extract_infobox_type(wikitext)
            domain = categorize_by_infobox(infobox_type)
            
            # Strip wikitext to plain text
            try:
                plain_text = strip_wikitext(wikitext)
                text_bytes = plain_text.encode('utf-8', errors='ignore')
            except Exception:
                # If stripping fails, use original
                text_bytes = wikitext_bytes
            
            # Extract numbers
            numbers = extract_numbers_from_bytes(text_bytes)
            
            if not numbers:
                return None
            
            # Create records
            records = []
            for number in numbers:
                first_digit, second_digit = analyze_number(number)
                
                # Only keep numbers with valid first digit
                if first_digit > 0:
                    records.append({
                        'article_id': article_id,
                        'domain': domain,
                        'number': number,
                        'first_digit': first_digit,
                        'second_digit': second_digit
                    })
            
            return {
                'article_id': article_id,
                'numbers': records
            }
            
        except Exception as e:
            # Skip articles with processing errors
            return None


def process_chunk_with_retry(
    chunk_id: int,
    dump_path: Path,
    temp_dir: Path,
    start_offset: int,
    end_offset: int,
    article_ids: List[int],
    max_retries: int = 3
) -> Tuple[Path, int, int]:
    """
    Process a chunk with retry logic.
    
    Args:
        chunk_id: Chunk identifier
        dump_path: Path to Wikipedia dump
        temp_dir: Temporary directory
        start_offset: Start byte offset
        end_offset: End byte offset
        article_ids: List of article IDs in chunk
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (temp_file_path, articles_processed, numbers_extracted)
    """
    import time
    
    worker = ChunkWorker(dump_path, temp_dir)
    
    for attempt in range(max_retries):
        try:
            result = worker.process_chunk(chunk_id, start_offset, end_offset, article_ids)
            return result
            
        except MemoryError:
            print(f"Memory error in chunk {chunk_id}, attempt {attempt + 1}")
            gc.collect()
            time.sleep(5)
            
        except Exception as e:
            print(f"Error in chunk {chunk_id}, attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    
    # All retries failed
    raise Exception(f"Failed to process chunk {chunk_id} after {max_retries} attempts")


# Test function
if __name__ == "__main__":
    print("Worker module loaded successfully")
    print("Use process_wiki.py to run the full pipeline")

