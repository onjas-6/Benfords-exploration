"""
Comprehensive number categorization system for Benford's Law analysis.
Implements 59 categories with priority-based pattern matching.
"""

import re
from typing import Tuple, Optional
from .units import *


class NumberCategorizer:
    """
    Categorizes numbers based on context and format.
    
    Priority system ensures correct resolution of ambiguous cases:
    - Priority 1 (highest): Fully formatted identifiers
    - Priority 2: Measurements with explicit units
    - Priority 3: Contextual patterns
    - Priority 4: Constrained formats
    - Priority 5: Constrained ranges
    - Priority 6 (lowest): Generic fallback
    """
    
    def __init__(self):
        """Initialize and compile all regex patterns."""
        self.patterns = self._build_patterns()
        
    def _build_patterns(self):
        """
        Build all 59 category patterns with priorities.
        Returns list of (compiled_pattern, category_name, priority, requires_number).
        """
        patterns = []
        
        # ===================================================================
        # PRIORITY 1: FULLY FORMATTED IDENTIFIERS (Most Specific)
        # ===================================================================
        
        # 1. date_full - Complete dates with month/day/year
        patterns.append((
            re.compile(
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|'
                r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)'
                r'\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b|'  # "December 25, 2025"
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'  # "12/25/2025"
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # "2025-12-25"
                re.IGNORECASE
            ),
            'date_full',
            1,
            False  # Pattern already matches the number
        ))
        
        # 2. time - Clock times
        patterns.append((
            re.compile(
                r'\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm|a\.m\.|p\.m\.)?\b',
                re.IGNORECASE
            ),
            'time',
            1,
            False
        ))
        
        # 3. phone - Phone numbers
        patterns.append((
            re.compile(
                r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|'
                r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                re.IGNORECASE
            ),
            'phone',
            1,
            False
        ))
        
        # 4. isbn - ISBN numbers
        patterns.append((
            re.compile(
                r'\bISBN[-\s]?(?:97[89][-\s]?)?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d{1}\b',
                re.IGNORECASE
            ),
            'isbn',
            1,
            False
        ))
        
        # 5. ip_address - IPv4 addresses
        patterns.append((
            re.compile(
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ),
            'ip_address',
            1,
            False
        ))
        
        # 6. coordinates - Geographic coordinates
        patterns.append((
            re.compile(
                r'\b\d+\.?\d*\s?°\s?[NSEW]\b',
                re.IGNORECASE
            ),
            'coordinates',
            1,
            False
        ))
        
        # 7. postal_code - US ZIP codes (5 or 9 digits)
        patterns.append((
            re.compile(
                r'\b\d{5}(?:-\d{4})?\b'
            ),
            'postal_code',
            1,
            False
        ))
        
        # 8. version - Software versions
        patterns.append((
            re.compile(
                r'\b[vV]?\d+\.\d+(?:\.\d+)?(?:\.\d+)?\b'
            ),
            'version',
            1,
            False
        ))
        
        # 9. resolution - Display resolutions
        patterns.append((
            re.compile(
                r'\b\d{3,5}\s?[x×]\s?\d{3,5}\b|'
                r'\b(?:4K|8K|1080[pi]|720[pi]|480[pi]|360[pi])\b',
                re.IGNORECASE
            ),
            'resolution',
            1,
            False
        ))
        
        # ===================================================================
        # PRIORITY 2: MEASUREMENTS WITH EXPLICIT UNITS
        # ===================================================================
        
        # Helper function to build unit pattern
        def unit_pattern(units_set, category, priority=2):
            # Escape special regex chars and sort by length (longest first)
            sorted_units = sorted(units_set, key=len, reverse=True)
            escaped_units = [re.escape(u) for u in sorted_units]
            pattern_str = r'\b([0-9,]+\.?\d*)\s?(?:' + '|'.join(escaped_units) + r')\b'
            return (re.compile(pattern_str, re.IGNORECASE), category, priority, True)
        
        # 10. distance_astro - Astronomical distances
        patterns.append(unit_pattern(DISTANCE_ASTRO_UNITS, 'distance_astro', 2))
        
        # 11. mass_astro - Astronomical masses
        patterns.append(unit_pattern(MASS_ASTRO_UNITS, 'mass_astro', 2))
        
        # 12. magnitude_astro - Stellar magnitudes
        patterns.append((
            re.compile(
                r'\b(?:apparent|absolute)?\s?magnitude\s+([+-]?\d+\.?\d*)\b|'
                r'\bmagnitude\s+(?:of\s+)?([+-]?\d+\.?\d*)\b',
                re.IGNORECASE
            ),
            'magnitude_astro',
            2,
            True
        ))
        
        # 13. elevation - Height above sea level
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s?(?:m|meters?|metres?|ft|feet)\s+(?:above sea level|asl|a\.s\.l\.|elevation|altitude)\b|'
                r'\b(?:elevation|altitude)\s+(?:of\s+)?([0-9,]+\.?\d*)\s?(?:m|meters?|metres?|ft|feet)\b',
                re.IGNORECASE
            ),
            'elevation',
            2,
            True
        ))
        
        # 14. depth - Depth below sea level
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s?(?:m|meters?|metres?|ft|feet)\s+(?:below sea level|deep|depth|bsl|b\.s\.l\.)\b|'
                r'\bdepth\s+(?:of\s+)?([0-9,]+\.?\d*)\s?(?:m|meters?|metres?|ft|feet)\b',
                re.IGNORECASE
            ),
            'depth',
            2,
            True
        ))
        
        # 15-28. Standard measurement units
        patterns.append(unit_pattern(AREA_UNITS, 'area', 2))
        patterns.append(unit_pattern(VOLUME_UNITS, 'volume', 2))
        patterns.append(unit_pattern(MASS_UNITS, 'mass_weight', 2))
        patterns.append(unit_pattern(DISTANCE_UNITS, 'distance', 2))
        patterns.append(unit_pattern(TEMP_UNITS, 'temperature', 2))
        patterns.append(unit_pattern(SPEED_UNITS, 'speed', 2))
        patterns.append(unit_pattern(PRESSURE_UNITS, 'pressure', 2))
        patterns.append(unit_pattern(ENERGY_UNITS, 'energy', 2))
        patterns.append(unit_pattern(POWER_UNITS, 'power', 2))
        patterns.append(unit_pattern(FORCE_UNITS, 'force', 2))
        patterns.append(unit_pattern(FREQUENCY_UNITS, 'frequency', 2))
        patterns.append(unit_pattern(WAVELENGTH_UNITS, 'wavelength', 2))
        patterns.append(unit_pattern(ELECTRIC_UNITS, 'electric', 2))
        patterns.append(unit_pattern(MAGNETIC_UNITS, 'magnetic', 2))
        
        # 29-32. Scientific units
        patterns.append(unit_pattern(RADIATION_UNITS, 'radiation', 2))
        patterns.append(unit_pattern(CONCENTRATION_UNITS, 'concentration', 2))
        patterns.append(unit_pattern(DENSITY_UNITS, 'density', 2))
        
        # 33-34. Computing units
        patterns.append(unit_pattern(FILE_SIZE_UNITS, 'file_size', 2))
        patterns.append(unit_pattern(BIT_RATE_UNITS, 'bit_rate', 2))
        
        # 35. clock_speed - Processor speeds (more specific than general frequency)
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s?(?:GHz|MHz|THz)\b(?!.*(?:radio|frequency|wave))',
                re.IGNORECASE
            ),
            'clock_speed',
            2,
            True
        ))
        
        # 36. decibel - Sound levels
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s?(?:dB|decibel|decibels)\b',
                re.IGNORECASE
            ),
            'decibel',
            2,
            True
        ))
        
        # 37. ph - pH levels
        patterns.append((
            re.compile(
                r'\bpH\s+(?:of\s+)?([0-9,]+\.?\d*)\b',
                re.IGNORECASE
            ),
            'ph',
            2,
            True
        ))
        
        # ===================================================================
        # PRIORITY 3: CONTEXTUAL PATTERNS
        # ===================================================================
        
        # Helper for context patterns
        def context_pattern(context_words, category, priority=3):
            words = '|'.join(re.escape(w) for w in sorted(context_words, key=len, reverse=True))
            # Number before or after context
            pattern_str = (
                r'\b([0-9,]+\.?\d*)\s+(?:' + words + r')\b|'
                r'\b(?:' + words + r')\s+(?:of\s+)?([0-9,]+\.?\d*)\b'
            )
            return (re.compile(pattern_str, re.IGNORECASE), category, priority, True)
        
        # 38. money_magnitude - Money with magnitude words
        patterns.append((
            re.compile(
                r'(?:\$|€|£|¥|₹|USD|EUR|GBP)\s?([0-9,]+\.?\d*)\s+(?:thousand|million|billion|trillion)\b|'
                r'\b([0-9,]+\.?\d*)\s+(?:thousand|million|billion|trillion)\s+(?:dollars?|euros?|pounds?|yen|yuan)\b',
                re.IGNORECASE
            ),
            'money_magnitude',
            3,
            True
        ))
        
        # 39. money - Currency amounts
        currency_symbols = '|'.join(re.escape(s) for s in sorted(CURRENCY_SYMBOLS, key=len, reverse=True))
        patterns.append((
            re.compile(
                r'(?:' + currency_symbols + r')\s?([0-9,]+\.?\d*)\b',
                re.IGNORECASE
            ),
            'money',
            3,
            True
        ))
        
        # 40-42. Demographic contexts
        patterns.append(context_pattern(POPULATION_CONTEXT, 'population', 3))
        patterns.append(context_pattern(CASUALTY_CONTEXT, 'casualties', 3))
        patterns.append(context_pattern(VOTE_CONTEXT, 'votes', 3))
        
        # 43. duration - Time durations
        patterns.append(context_pattern(DURATION_UNITS, 'duration', 3))
        
        # 44. age - Ages
        patterns.append(context_pattern(AGE_CONTEXT, 'age', 3))
        
        # 45. time_record - Sports/race times
        patterns.append((
            re.compile(
                r'\b([0-9]+:[0-5][0-9](?:\.[0-9]{1,3})?)\b(?:.*(?:record|time|race|finish))?',
                re.IGNORECASE
            ),
            'time_record',
            3,
            False
        ))
        
        # 46. batting_avg - Baseball batting averages
        patterns.append((
            re.compile(
                r'\b(\.[0-9]{3})\b(?:.*(?:batting|average|avg))?',
                re.IGNORECASE
            ),
            'batting_avg',
            3,
            False
        ))
        
        # 47. record_stat - Sports statistics
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s+(?:goals?|points?|runs?|yards?|RBIs?|assists?|rebounds?|touchdowns?|home runs?)\b',
                re.IGNORECASE
            ),
            'record_stat',
            3,
            True
        ))
        
        # ===================================================================
        # PRIORITY 4: CONSTRAINED FORMATS
        # ===================================================================
        
        # 48. percentage - Percentages
        patterns.append((
            re.compile(
                r'\b([0-9,]+\.?\d*)\s?%|'
                r'\b([0-9,]+\.?\d*)\s+percent\b',
                re.IGNORECASE
            ),
            'percentage',
            4,
            True
        ))
        
        # 49. score_sports - Sports scores
        patterns.append((
            re.compile(
                r'\b(\d{1,3})[-–—]\d{1,3}\b(?:.*(?:won|lost|score|final|defeat|victory))?',
                re.IGNORECASE
            ),
            'score_sports',
            4,
            False
        ))
        
        # 50. rating - Ratings
        patterns.append((
            re.compile(
                r'\b([0-9]+\.?\d*)\s+(?:out of|/)\s+[0-9]+\b|'
                r'\b([0-9]+\.?\d*)\s+stars?\b',
                re.IGNORECASE
            ),
            'rating',
            4,
            True
        ))
        
        # 51. ranking - Rankings and ordinals
        patterns.append((
            re.compile(
                r'\b(\d+)(?:st|nd|rd|th)\s+(?:place|position|largest|biggest|smallest|tallest|edition|best|worst)\b',
                re.IGNORECASE
            ),
            'ranking',
            4,
            True
        ))
        
        # 52. chart_position - Chart positions
        patterns.append((
            re.compile(
                r'\b#\s?(\d+)\b(?:.*(?:chart|Billboard|hit))?|'
                r'\bnumber\s+(\d+)\s+(?:on|in).*(?:chart|Billboard)\b',
                re.IGNORECASE
            ),
            'chart_position',
            4,
            True
        ))
        
        # 53. richter - Earthquake magnitudes
        patterns.append((
            re.compile(
                r'\b(?:magnitude|Richter)\s+([0-9]+\.?\d*)\b.*(?:earthquake|seismic|tremor)?|'
                r'\b([0-9]+\.?\d*)\s+(?:on the\s+)?(?:Richter|moment magnitude)\s+scale\b',
                re.IGNORECASE
            ),
            'richter',
            4,
            True
        ))
        
        # 54. jersey_number - Jersey/uniform numbers
        patterns.append((
            re.compile(
                r'\b(?:number|#)\s?(\d{1,3})\b(?:.*(?:jersey|uniform|shirt|wore))?|'
                r'\bwore\s+(?:number\s+)?(\d{1,3})\b',
                re.IGNORECASE
            ),
            'jersey_number',
            4,
            True
        ))
        
        # 55. episode_chapter - Episode/chapter/season numbers
        patterns.append((
            re.compile(
                r'\b(?:episode|chapter|season|volume|book|part|series)\s+(\d+)\b',
                re.IGNORECASE
            ),
            'episode_chapter',
            4,
            True
        ))
        
        # 56. flight_number - Flight numbers
        patterns.append((
            re.compile(
                r'\b[A-Z]{2}\s?\d{1,4}\b(?:.*flight)?',
                re.IGNORECASE
            ),
            'flight_number',
            4,
            False
        ))
        
        # 57. century_decade - Centuries and decades
        patterns.append((
            re.compile(
                r'\b(\d{1,2})(?:st|nd|rd|th)\s+century\b|'
                r'\b(1[0-9]{3}|20[0-2][0-9])s\b',  # 1920s, 2020s
                re.IGNORECASE
            ),
            'century_decade',
            4,
            False
        ))
        
        # ===================================================================
        # PRIORITY 5: CONSTRAINED RANGES
        # ===================================================================
        
        # 58. year - Years (but NOT if followed by units!)
        patterns.append((
            re.compile(
                r'\b(1[0-9]{3}|20[0-2][0-9])\b(?!\s*(?:' +
                '|'.join(re.escape(u) for u in list(ALL_UNITS)[:50]) +  # Sample of units
                r'))',
                re.IGNORECASE
            ),
            'year',
            5,
            True
        ))
        
        # 59. small_count - Small counting numbers (1-20)
        patterns.append((
            re.compile(
                r'\b([1-9]|1[0-9]|20)\s+(?:children|albums?|books?|songs?|siblings?|rooms?|floors?|stories)\b',
                re.IGNORECASE
            ),
            'small_count',
            5,
            True
        ))
        
        return patterns
    
    def categorize(self, number_str: str, context: str) -> str:
        """
        Categorize a number based on its surrounding context.
        
        Args:
            number_str: The extracted number as a string (e.g., "1234")
            context: Surrounding text (typically ±30 characters)
            
        Returns:
            Category name (one of 59 categories, or 'generic')
        """
        # Sort by priority (lower number = higher priority)
        sorted_patterns = sorted(self.patterns, key=lambda x: x[2])
        
        for pattern, category, priority, requires_number in sorted_patterns:
            match = pattern.search(context)
            if match:
                # For patterns that require extracting the number from context,
                # verify it matches our target number
                if requires_number:
                    # Extract number from match groups
                    for group in match.groups():
                        if group:
                            # Clean the matched number (remove commas)
                            clean_matched = group.replace(',', '')
                            clean_target = number_str.replace(',', '')
                            # Check if this is our number
                            if clean_matched == clean_target or clean_target in clean_matched:
                                return category
                else:
                    # Pattern matches the full context, number is included
                    return category
        
        # No pattern matched - return generic
        return 'generic'
    
    def categorize_batch(self, numbers_with_context):
        """
        Categorize a batch of numbers for efficiency.
        
        Args:
            numbers_with_context: List of (number_str, context) tuples
            
        Returns:
            List of (number_str, category) tuples
        """
        results = []
        for num_str, context in numbers_with_context:
            category = self.categorize(num_str, context)
            results.append((num_str, category))
        return results


# Global instance for reuse
_categorizer = None

def get_categorizer() -> NumberCategorizer:
    """Get or create the global categorizer instance."""
    global _categorizer
    if _categorizer is None:
        _categorizer = NumberCategorizer()
    return _categorizer


def categorize_number(number_str: str, context: str) -> str:
    """
    Convenience function to categorize a single number.
    
    Args:
        number_str: The number as a string
        context: Surrounding context text
        
    Returns:
        Category name
    """
    categorizer = get_categorizer()
    return categorizer.categorize(number_str, context)

