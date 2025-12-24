"""
Domain categorization based on Wikipedia Infobox types.
Maps infobox templates to broad domain categories.
"""

import re
from typing import Optional
import mwparserfromhell


# Infobox to domain mapping
INFOBOX_MAPPINGS = {
    "Geography": [
        "settlement",
        "country",
        "city",
        "region",
        "body of water",
        "mountain",
        "island",
        "river",
        "lake",
        "sea",
        "ocean",
        "valley",
        "desert",
        "forest",
        "park",
        "protected area",
        "place",
        "location",
        "administrative division",
        "municipality",
        "province",
        "state",
        "territory",
        "continent",
    ],
    "People": [
        "person",
        "officeholder",
        "scientist",
        "artist",
        "writer",
        "musician",
        "athlete",
        "actor",
        "politician",
        "military person",
        "biography",
        "sportsperson",
        "football biography",
        "basketball biography",
        "baseball biography",
        "ice hockey player",
        "cricketer",
        "tennis biography",
        "royalty",
        "noble",
        "philosopher",
        "economist",
        "engineer",
    ],
    "Science": [
        "element",
        "planet",
        "star",
        "chemical compound",
        "mineral",
        "disease",
        "drug",
        "medication",
        "medical condition",
        "anatomy",
        "constellation",
        "galaxy",
        "nebula",
        "astronomical object",
        "particle",
        "molecule",
        "isotope",
        "ion",
    ],
    "Sports": [
        "sports team",
        "stadium",
        "tournament",
        "football club",
        "basketball team",
        "baseball team",
        "ice hockey team",
        "sports season",
        "sports league",
        "racing driver",
        "cyclist",
        "olympian",
        "sports competition",
        "football club season",
    ],
    "Business": [
        "company",
        "organization",
        "university",
        "college",
        "school",
        "corporation",
        "airline",
        "bank",
        "brand",
        "product",
        "software",
        "website",
        "nonprofit",
        "NGO",
    ],
    "Media": [
        "film",
        "television",
        "album",
        "single",
        "song",
        "video game",
        "book",
        "magazine",
        "newspaper",
        "TV channel",
        "radio station",
        "musical artist",
        "band",
        "podcast",
        "television episode",
        "television season",
        "anime",
        "manga",
    ],
    "Military": [
        "military conflict",
        "weapon",
        "aircraft",
        "ship",
        "military unit",
        "battle",
        "war",
        "military structure",
        "military vehicle",
        "submarine",
        "warship",
        "tank",
        "gun",
        "missile",
        "military operation",
    ],
    "Biology": [
        "taxobox",
        "speciesbox",
        "automatic taxobox",
        "subspeciesbox",
        "virus",
        "bacteria",
        "fungus",
        "plant",
        "animal",
        "insect",
        "bird",
        "fish",
        "mammal",
        "reptile",
        "amphibian",
    ],
    "Infrastructure": [
        "bridge",
        "building",
        "station",
        "airport",
        "road",
        "highway",
        "railway",
        "tunnel",
        "dam",
        "power station",
        "lighthouse",
        "skyscraper",
        "tower",
        "shopping mall",
        "hotel",
    ],
    "Events": [
        "election",
        "event",
        "disaster",
        "earthquake",
        "hurricane",
        "tornado",
        "flood",
        "fire",
        "accident",
        "festival",
        "ceremony",
        "conference",
        "summit",
    ],
}

# Compile regex patterns for each domain (case insensitive)
# Use word boundaries to avoid partial matches (e.g., "element" in "election")
DOMAIN_PATTERNS = {}
for domain, keywords in INFOBOX_MAPPINGS.items():
    # Create pattern that matches any of the keywords with word boundaries
    pattern = "|".join(r"\b" + re.escape(kw) + r"\b" for kw in keywords)
    DOMAIN_PATTERNS[domain] = re.compile(pattern, re.IGNORECASE)


def extract_infobox_type(wikitext: str) -> Optional[str]:
    """
    Extract the infobox type from Wikipedia wikitext.

    Args:
        wikitext: Raw Wikipedia markup

    Returns:
        Infobox type string (e.g., "settlement", "person") or None
    """
    try:
        # Parse wikitext
        parsed = mwparserfromhell.parse(wikitext)

        # Find templates that look like infoboxes
        for template in parsed.filter_templates():
            name = str(template.name).strip().lower()

            # Check if it's an infobox
            if name.startswith("infobox"):
                # Extract the type after "infobox "
                infobox_type = name[7:].strip()  # Remove "infobox" prefix
                if infobox_type:
                    return infobox_type

        return None

    except Exception:
        # If parsing fails, return None
        return None


def categorize_by_infobox(infobox_type: Optional[str]) -> str:
    """
    Map an infobox type to a broad domain category.

    Args:
        infobox_type: The infobox type string

    Returns:
        Domain category string (e.g., "Geography", "People", "Uncategorized")
    """
    if not infobox_type:
        return "Uncategorized"

    # Check each domain's patterns
    for domain, pattern in DOMAIN_PATTERNS.items():
        if pattern.search(infobox_type):
            return domain

    return "Uncategorized"


def get_domain(wikitext: str) -> str:
    """
    Get the domain category for a Wikipedia article.

    Args:
        wikitext: Raw Wikipedia markup

    Returns:
        Domain category string
    """
    infobox_type = extract_infobox_type(wikitext)
    return categorize_by_infobox(infobox_type)


def strip_wikitext(wikitext: str) -> str:
    """
    Strip Wikipedia markup to get plain text for number extraction.

    Args:
        wikitext: Raw Wikipedia markup

    Returns:
        Plain text with markup removed
    """
    try:
        parsed = mwparserfromhell.parse(wikitext)
        return parsed.strip_code()
    except Exception:
        # If parsing fails, return original text
        return wikitext


# Test function
if __name__ == "__main__":
    # Test categorization
    test_cases = [
        ("infobox settlement", "Geography"),
        ("infobox person", "People"),
        ("infobox chemical compound", "Science"),
        ("infobox football club", "Sports"),
        ("infobox company", "Business"),
        ("infobox film", "Media"),
        ("infobox military conflict", "Military"),
        ("infobox speciesbox", "Biology"),
        ("infobox bridge", "Infrastructure"),
        ("infobox election", "Events"),
        ("infobox something random", "Uncategorized"),
    ]

    print("Testing infobox categorization:")
    print("-" * 60)
    for infobox, expected in test_cases:
        result = categorize_by_infobox(infobox)
        status = "✓" if result == expected else "✗"
        print(f"{status} {infobox:30} -> {result:15} (expected: {expected})")
