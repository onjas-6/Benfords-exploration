"""
Test suite for number categorization system.
Tests conflict resolution and priority ordering.
"""

import sys
sys.path.insert(0, '/root/Benfords-exploration')

from src.number_categorizer import categorize_number


def test_conflict_resolution():
    """Test that conflicts are resolved correctly based on priority."""
    
    test_cases = [
        # Date vs Ranking vs Year
        ("2", "December 2nd, 1999", "date_full"),  # Full date beats everything
        ("2", "2nd place in the competition", "ranking"),  # Ranking beats generic
        ("1999", "born in 1999", "year"),  # Standalone year
        ("1999", "altitude 1999 meters", "distance"),  # Units beat year
        
        # Money vs Generic
        ("100", "$100", "money"),
        ("5", "$5 million", "money_magnitude"),
        ("100", "100 people", "population"),
        ("100", "100%", "percentage"),
        ("100", "just 100", "generic"),
        
        # Distance variations
        ("4", "4.2 light-years away", "distance_astro"),
        ("4", "4 km from here", "distance"),
        ("100", "100 feet tall", "distance"),
        
        # Temperature
        ("25", "25°C today", "temperature"),
        ("77", "77°F outside", "temperature"),
        
        # Coordinates
        ("37", "37.7749° N latitude", "coordinates"),
        
        # Time formats
        ("3", "3:45 PM", "time"),
        ("14", "14:30:00", "time"),
        ("9", "9.58 seconds world record", "time_record"),
        
        # Ordinals in different contexts
        ("19", "19th century", "century_decade"),
        ("1", "1st place", "ranking"),
        ("2", "2nd edition of the book", "ranking"),
        
        # Scientific units
        ("500", "500 kWh of energy", "energy"),
        ("100", "100 MW power plant", "power"),
        ("220", "220V electrical", "electric"),
        ("85", "85 dB noise level", "decibel"),
        ("7", "pH 7 neutral", "ph"),
        
        # Astronomical
        ("1", "1.5 solar masses", "mass_astro"),
        ("4", "magnitude 4.5 star", "magnitude_astro"),
        ("6", "magnitude 6.5 earthquake", "richter"),
        
        # Sports
        ("3", "3-2 victory", "score_sports"),
        (".300", ".300 batting average", "batting_avg"),
        ("23", "wore #23 jersey", "jersey_number"),
        ("58", "58 goals scored", "record_stat"),
        
        # Counting
        ("5", "Episode 5 of the series", "episode_chapter"),
        ("3", "3 children in family", "small_count"),
        
        # Geographic measurements
        ("8848", "8848 m above sea level", "elevation"),
        ("100", "100 m deep ocean", "depth"),
        
        # Area and volume
        ("50", "50 km² area", "area"),
        ("100", "100 acres of land", "area"),
        ("2", "2 liters of water", "volume"),
        
        # Demographics
        ("1234567", "population of 1,234,567", "population"),
        ("5000", "5,000 killed in battle", "casualties"),
        ("1000", "won by 1000 votes", "votes"),
        
        # Tech/Computing
        ("500", "500 MB file", "file_size"),
        ("100", "100 Mbps speed", "bit_rate"),
        ("1920", "1920x1080 resolution", "resolution"),
        ("3", "3.5 GHz processor", "clock_speed"),
        
        # Version numbers
        ("2", "v2.0.1 software", "version"),
        
        # Ages
        ("25", "25 years old", "age"),
        ("30", "aged 30", "age"),
        
        # Duration
        ("2", "2 hours long", "duration"),
        ("30", "30 minutes", "duration"),
        
        # Percentages (should beat generic)
        ("75", "75% approval", "percentage"),
        ("4", "4 out of 5 rating", "rating"),
        
        # Chart positions
        ("1", "#1 on Billboard", "chart_position"),
        
        # Years should NOT match when followed by units
        ("2000", "2000 km away", "distance"),
        ("1500", "1500 kg weight", "mass_weight"),
        ("1984", "published in 1984", "year"),
        
        # Decades
        ("1990", "1990s music", "century_decade"),
        
        # Edge cases - phone numbers
        ("555", "(555) 123-4567 phone", "phone"),
        
        # Edge cases - IP addresses  
        ("192", "192.168.1.1 IP address", "ip_address"),
        
        # Edge cases - postal codes
        ("90210", "ZIP code 90210", "postal_code"),
    ]
    
    passed = 0
    failed = 0
    
    print("="*80)
    print("TESTING NUMBER CATEGORIZATION")
    print("="*80)
    
    for number, context, expected_category in test_cases:
        result = categorize_number(number, context)
        
        if result == expected_category:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = f"✗ FAIL (got '{result}')"
        
        print(f"{status:15} | Number: {number:8} | Expected: {expected_category:20} | Context: {context[:50]}")
    
    print("="*80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    print("="*80)
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = test_conflict_resolution()
    
    if failed > 0:
        print(f"\n⚠️  {failed} tests failed. Review categorization patterns.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

