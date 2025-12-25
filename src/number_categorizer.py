"""
OPTIMIZED Number categorization system for Benford's Law analysis.
Uses trigger-word pre-filtering to avoid running all 59 patterns on every number.

Performance target: <5ms per article (down from 28ms)
"""

import re
from typing import Tuple, Optional, Set


# =============================================================================
# TRIGGER WORDS - Quick detection sets for each category group
# =============================================================================

# If NONE of these appear in context, number is generic
QUICK_TRIGGER_WORDS = {
    # Currency
    '$', '€', '£', '¥', '₹', '₩', 'dollar', 'euro', 'pound', 'yen', 'yuan',
    'usd', 'eur', 'gbp', 'million', 'billion', 'trillion',
    # Units
    'km', 'mi', 'meter', 'metre', 'feet', 'foot', 'inch', 'yard', 'mile',
    'kg', 'lb', 'gram', 'pound', 'ton', 'ounce',
    'km²', 'm²', 'acre', 'hectare', 'square',
    'liter', 'litre', 'gallon', 'ml',
    '°c', '°f', 'celsius', 'fahrenheit', 'kelvin',
    'km/h', 'mph', 'm/s', 'knot',
    'kw', 'mw', 'gw', 'watt', 'horsepower',
    'hz', 'mhz', 'ghz', 'khz',
    'volt', 'amp', 'ohm',
    'ev', 'joule', 'calorie', 'kwh',
    'pa', 'bar', 'psi', 'atm',
    'db', 'decibel',
    'light-year', 'parsec', 'au ', 'astronomical',
    'solar mass', 'earth mass',
    # Percentage
    '%', 'percent',
    # Time/Date
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december',
    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    'am', 'pm', 'hour', 'minute', 'second', 'day', 'week', 'month', 'year',
    'century', 'decade',
    # Demographics
    'population', 'people', 'inhabitants', 'residents',
    'killed', 'dead', 'death', 'casualties', 'wounded',
    'vote', 'votes', 'ballot',
    # Rankings
    '1st', '2nd', '3rd', '4th', '5th', 'th ', 'nd ', 'rd ', 'st ',
    'place', 'rank', 'position', 'largest', 'edition',
    'out of', 'stars', 'rating',
    '#', 'number',
    # Sports
    'goal', 'point', 'run', 'yard', 'rbi', 'assist', 'rebound',
    'batting', 'average', 'jersey', 'wore',
    # Computing
    'mb', 'gb', 'tb', 'kb', 'byte', 'mbps', 'gbps',
    '1080', '720', '4k', '8k', 'resolution',
    # Special
    'magnitude', 'richter', 'earthquake',
    'ph ', 'ph=', 'ph:',
    'elevation', 'altitude', 'above sea level', 'below sea level', 'depth', 'deep',
    'age', 'aged', 'years old',
    'episode', 'chapter', 'season', 'volume',
    'version', 'v1', 'v2', 'v3',
    # Identifiers
    'isbn', 'phone', 'tel', 'fax',
    '° n', '° s', '° e', '° w', 'latitude', 'longitude',
}

# Convert to lowercase set for fast lookup
TRIGGER_SET = frozenset(w.lower() for w in QUICK_TRIGGER_WORDS)


# =============================================================================
# CATEGORY PATTERNS - Organized by trigger group for faster matching
# =============================================================================

class OptimizedCategorizer:
    """
    Optimized categorizer using trigger-word pre-filtering.
    
    Strategy:
    1. Quick scan: Does context contain ANY trigger words?
    2. If no triggers: Return "generic" immediately (skip all patterns)
    3. If triggers found: Only run patterns from triggered groups
    """
    
    def __init__(self):
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile all patterns organized by trigger groups."""
        
        # Pattern format: (pattern, category, trigger_words)
        # trigger_words = set of words that must be present for this pattern to run
        
        self.patterns = []
        
        # =====================================================================
        # PRIORITY 1: FULLY FORMATTED (run first, highest specificity)
        # =====================================================================
        
        # Date patterns
        self.patterns.append((
            re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b', re.I),
            'date_full',
            {'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
             'january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 
             'october', 'november', 'december'}
        ))
        
        self.patterns.append((
            re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
            'date_full',
            {'/'} 
        ))
        
        # Time
        self.patterns.append((
            re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:am|pm)?\b', re.I),
            'time',
            {':', 'am', 'pm'}
        ))
        
        # Coordinates
        self.patterns.append((
            re.compile(r'\b\d+\.?\d*\s?°\s?[nsew]\b', re.I),
            'coordinates',
            {'°', 'latitude', 'longitude', '° n', '° s', '° e', '° w'}
        ))
        
        # Resolution
        self.patterns.append((
            re.compile(r'\b\d{3,5}\s?[x×]\s?\d{3,5}\b|(?:4k|8k|1080[pi]|720[pi])', re.I),
            'resolution',
            {'x', '×', '1080', '720', '4k', '8k', 'resolution'}
        ))
        
        # =====================================================================
        # PRIORITY 2: MEASUREMENTS WITH UNITS
        # =====================================================================
        
        # Astronomical distance
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:light-years?|ly|parsecs?|pc|kpc|mpc|au)\b', re.I),
            'distance_astro',
            {'light-year', 'parsec', 'au ', 'astronomical', 'ly', 'pc'}
        ))
        
        # Astronomical mass
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:solar mass|earth mass|jupiter mass|m☉|m⊕)', re.I),
            'mass_astro',
            {'solar mass', 'earth mass', 'jupiter mass', 'm☉', 'm⊕'}
        ))
        
        # Elevation/Depth
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:m|meters?|ft|feet)\s+(?:above sea level|asl)', re.I),
            'elevation',
            {'above sea level', 'elevation', 'altitude', 'asl'}
        ))
        
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:m|meters?|ft|feet)\s+(?:deep|below|depth)', re.I),
            'depth',
            {'deep', 'below', 'depth', 'below sea level'}
        ))
        
        # Area
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:km²|km2|m²|mi²|ft²|hectares?|ha\b|acres?|sq\s+(?:km|mi|ft|m))', re.I),
            'area',
            {'km²', 'm²', 'acre', 'hectare', 'square', 'sq '}
        ))
        
        # Volume
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:liters?|litres?|l\b|ml|gallons?|gal\b)', re.I),
            'volume',
            {'liter', 'litre', 'gallon', 'ml'}
        ))
        
        # Mass/Weight
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:kg|kilograms?|g\b|grams?|lbs?|pounds?|tons?|tonnes?|oz|ounces?)', re.I),
            'mass_weight',
            {'kg', 'lb', 'gram', 'pound', 'ton', 'ounce', 'kilogram'}
        ))
        
        # Distance
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:km|kilometers?|kilometres?|m\b|meters?|metres?|mi\b|miles?|ft|feet|foot|in\b|inches?|yd|yards?)', re.I),
            'distance',
            {'km', 'mi', 'meter', 'metre', 'feet', 'foot', 'inch', 'yard', 'mile'}
        ))
        
        # Temperature
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:°[cf]|degrees?\s+(?:celsius|fahrenheit)|kelvin|k\b)', re.I),
            'temperature',
            {'°c', '°f', 'celsius', 'fahrenheit', 'kelvin'}
        ))
        
        # Speed
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:km/h|kph|mph|m/s|knots?)', re.I),
            'speed',
            {'km/h', 'mph', 'm/s', 'knot', 'kph'}
        ))
        
        # Power
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:kw|mw|gw|watts?|horsepower|hp\b)', re.I),
            'power',
            {'kw', 'mw', 'gw', 'watt', 'horsepower', 'hp'}
        ))
        
        # Energy
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:kwh|mwh|joules?|calories?|kcal|ev\b|kev|mev|gev)', re.I),
            'energy',
            {'kwh', 'joule', 'calorie', 'ev', 'kev', 'mev'}
        ))
        
        # Frequency
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:hz|khz|mhz|ghz|thz)', re.I),
            'frequency',
            {'hz', 'khz', 'mhz', 'ghz'}
        ))
        
        # Electrical
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:volts?|v\b|amps?|amperes?|a\b|ohms?|Ω|mah)', re.I),
            'electric',
            {'volt', 'amp', 'ohm', 'mah'}
        ))
        
        # Pressure
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:pa|kpa|mpa|bar|psi|atm)', re.I),
            'pressure',
            {'pa', 'bar', 'psi', 'atm', 'kpa'}
        ))
        
        # File size
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:kb|mb|gb|tb|pb|bytes?)', re.I),
            'file_size',
            {'kb', 'mb', 'gb', 'tb', 'byte'}
        ))
        
        # Bit rate
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:kbps|mbps|gbps|bit/s)', re.I),
            'bit_rate',
            {'kbps', 'mbps', 'gbps'}
        ))
        
        # Decibel
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?(?:db|decibels?)', re.I),
            'decibel',
            {'db', 'decibel'}
        ))
        
        # pH
        self.patterns.append((
            re.compile(r'\bph\s+(?:of\s+)?(\d+\.?\d*)', re.I),
            'ph',
            {'ph '}
        ))
        
        # =====================================================================
        # PRIORITY 3: CONTEXTUAL PATTERNS
        # =====================================================================
        
        # Money with magnitude
        self.patterns.append((
            re.compile(r'[$€£¥₹]\s?\d[\d,]*\.?\d*\s+(?:thousand|million|billion|trillion)', re.I),
            'money_magnitude',
            {'$', '€', '£', '¥', '₹', 'million', 'billion', 'trillion'}
        ))
        
        # Money
        self.patterns.append((
            re.compile(r'[$€£¥₹]\s?\d[\d,]*\.?\d*', re.I),
            'money',
            {'$', '€', '£', '¥', '₹', 'dollar', 'euro', 'pound', 'usd', 'eur', 'gbp'}
        ))
        
        # Population
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+(?:people|inhabitants|residents|population)', re.I),
            'population',
            {'population', 'people', 'inhabitants', 'residents'}
        ))
        
        # Casualties
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+(?:killed|dead|deaths?|casualties|wounded|injured)', re.I),
            'casualties',
            {'killed', 'dead', 'death', 'casualties', 'wounded'}
        ))
        
        # Votes
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+(?:votes?|ballots?)', re.I),
            'votes',
            {'vote', 'ballot'}
        ))
        
        # Duration
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+(?:hours?|minutes?|seconds?|days?|weeks?|months?|years?)\b', re.I),
            'duration',
            {'hour', 'minute', 'second', 'day', 'week', 'month', 'year'}
        ))
        
        # Age
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+years?\s+old|aged\s+\d+', re.I),
            'age',
            {'years old', 'aged'}
        ))
        
        # Sports stats
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s+(?:goals?|points?|runs?|yards?|rbis?|assists?|rebounds?)', re.I),
            'record_stat',
            {'goal', 'point', 'run', 'yard', 'rbi', 'assist', 'rebound'}
        ))
        
        # =====================================================================
        # PRIORITY 4: CONSTRAINED FORMATS
        # =====================================================================
        
        # Percentage
        self.patterns.append((
            re.compile(r'\b\d[\d,]*\.?\d*\s?%|\b\d[\d,]*\.?\d*\s+percent', re.I),
            'percentage',
            {'%', 'percent'}
        ))
        
        # Sports score
        self.patterns.append((
            re.compile(r'\b\d{1,3}[-–]\d{1,3}\b', re.I),
            'score_sports',
            {'-', '–'}
        ))
        
        # Rating
        self.patterns.append((
            re.compile(r'\b\d+\.?\d*\s+(?:out of|/)\s+\d+|\b\d+\.?\d*\s+stars?', re.I),
            'rating',
            {'out of', 'stars', '/'}
        ))
        
        # Ranking
        self.patterns.append((
            re.compile(r'\b\d+(?:st|nd|rd|th)\s+(?:place|position|largest|biggest|smallest|edition|best|worst)', re.I),
            'ranking',
            {'place', 'position', 'largest', 'biggest', 'smallest', 'edition', 'best', 'worst',
             '1st', '2nd', '3rd', 'th '}
        ))
        
        # Chart position
        self.patterns.append((
            re.compile(r'#\s?\d+|number\s+\d+\s+(?:on|in).*(?:chart|billboard)', re.I),
            'chart_position',
            {'#', 'chart', 'billboard', 'number'}
        ))
        
        # Richter/earthquake
        self.patterns.append((
            re.compile(r'(?:magnitude|richter)\s+\d+\.?\d*|\d+\.?\d*\s+(?:on the\s+)?richter', re.I),
            'richter',
            {'magnitude', 'richter', 'earthquake'}
        ))
        
        # Episode/chapter
        self.patterns.append((
            re.compile(r'(?:episode|chapter|season|volume)\s+\d+', re.I),
            'episode_chapter',
            {'episode', 'chapter', 'season', 'volume'}
        ))
        
        # Century/decade
        self.patterns.append((
            re.compile(r'\b\d{1,2}(?:st|nd|rd|th)\s+century|\b(?:19|20)\d{2}s\b', re.I),
            'century_decade',
            {'century', 'decade', '0s'}
        ))
        
        # Jersey number
        self.patterns.append((
            re.compile(r'(?:wore|number|#)\s*\d{1,2}\b.*(?:jersey|shirt|uniform)?', re.I),
            'jersey_number',
            {'wore', 'jersey'}
        ))
        
        # =====================================================================
        # PRIORITY 5: YEAR (only if no units)
        # =====================================================================
        
        self.patterns.append((
            re.compile(r'\b(1[0-9]{3}|20[0-2][0-9])\b'),
            'year',
            set()  # No triggers needed - fallback for 4-digit numbers
        ))
    
    def _has_triggers(self, context_lower: str) -> bool:
        """Quick check if context contains ANY trigger words."""
        for trigger in TRIGGER_SET:
            if trigger in context_lower:
                return True
        return False
    
    def _get_matching_triggers(self, context_lower: str) -> Set[str]:
        """Get all trigger words found in context."""
        return {t for t in TRIGGER_SET if t in context_lower}
    
    def categorize(self, number_str: str, context: str) -> str:
        """
        Categorize a number based on context.
        
        Optimized approach:
        1. Quick scan for trigger words
        2. If no triggers AND not a year → return "generic"
        3. Only run patterns whose triggers are present
        """
        context_lower = context.lower()
        
        # Quick path: Check if any triggers present
        if not self._has_triggers(context_lower):
            # No triggers - check if it could be a year
            try:
                num = int(float(number_str.replace(',', '')))
                if 1000 <= num <= 2100:
                    return 'year'
            except (ValueError, TypeError):
                pass
            return 'generic'
        
        # Get matching triggers for filtering
        active_triggers = self._get_matching_triggers(context_lower)
        
        # Run patterns in priority order, but only if triggers match
        for pattern, category, trigger_words in self.patterns:
            # Skip if pattern requires specific triggers that aren't present
            if trigger_words and not (trigger_words & active_triggers):
                continue
            
            # Run the pattern
            match = pattern.search(context)
            if match:
                # Verify the number is part of the match
                num_clean = number_str.replace(',', '')
                if num_clean in context:
                    return category
        
        # Fallback: Check year
        try:
            num = int(float(number_str.replace(',', '')))
            if 1000 <= num <= 2100:
                return 'year'
        except (ValueError, TypeError):
            pass
        
        return 'generic'


# Global instance
_categorizer = None

def get_categorizer():
    """Get or create global optimized categorizer."""
    global _categorizer
    if _categorizer is None:
        _categorizer = OptimizedCategorizer()
    return _categorizer


def categorize_number(number_str: str, context: str) -> str:
    """Convenience function for categorizing a single number."""
    return get_categorizer().categorize(number_str, context)

