"""
Complete unit reference for number categorization.
Contains 300+ units across all measurement domains.
"""

# Distance Units
DISTANCE_UNITS = {
    # SI metric
    'km', 'kilometer', 'kilometers', 'kilometre', 'kilometres',
    'm', 'meter', 'meters', 'metre', 'metres',
    'cm', 'centimeter', 'centimeters', 'centimetre', 'centimetres',
    'mm', 'millimeter', 'millimeters', 'millimetre', 'millimetres',
    'μm', 'um', 'micrometer', 'micrometers', 'micrometre', 'micrometres',
    'nm', 'nanometer', 'nanometers', 'nanometre', 'nanometres',
    
    # Imperial
    'mi', 'mile', 'miles',
    'yd', 'yard', 'yards',
    'ft', 'foot', 'feet',
    'in', 'inch', 'inches',
    
    # Nautical
    'nmi', 'nautical mile', 'nautical miles',
    
    # Historical/other
    'league', 'leagues', 'furlong', 'furlongs', 'fathom', 'fathoms',
}

# Astronomical distance units
DISTANCE_ASTRO_UNITS = {
    'AU', 'astronomical unit', 'astronomical units',
    'light-year', 'light-years', 'lightyear', 'lightyears', 'ly',
    'parsec', 'parsecs', 'pc',
    'kpc', 'kiloparsec', 'kiloparsecs',
    'Mpc', 'megaparsec', 'megaparsecs',
    'Gpc', 'gigaparsec', 'gigaparsecs',
}

# Area units
AREA_UNITS = {
    # Metric
    'km²', 'km2', 'square kilometer', 'square kilometers', 'square kilometre', 'square kilometres',
    'm²', 'm2', 'square meter', 'square meters', 'square metre', 'square metres',
    'cm²', 'cm2', 'square centimeter', 'square centimeters',
    'mm²', 'mm2', 'square millimeter', 'square millimeters',
    'ha', 'hectare', 'hectares',
    
    # Imperial
    'mi²', 'mi2', 'square mile', 'square miles',
    'ft²', 'ft2', 'square foot', 'square feet',
    'in²', 'in2', 'square inch', 'square inches',
    'acre', 'acres',
    
    # Abbreviations
    'sq km', 'sq mi', 'sq ft', 'sq m', 'sq in',
    
    # Historical
    'dunam', 'dunams',
}

# Volume units
VOLUME_UNITS = {
    # Metric
    'm³', 'm3', 'cubic meter', 'cubic meters', 'cubic metre', 'cubic metres',
    'L', 'l', 'liter', 'liters', 'litre', 'litres',
    'mL', 'ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres',
    'cL', 'cl', 'centiliter', 'centiliters', 'centilitre', 'centilitres',
    'μL', 'ul', 'microliter', 'microliters',
    
    # Imperial
    'gal', 'gallon', 'gallons',
    'qt', 'quart', 'quarts',
    'pt', 'pint', 'pints',
    'fl oz', 'fluid ounce', 'fluid ounces',
    'cup', 'cups',
    'tbsp', 'tablespoon', 'tablespoons',
    'tsp', 'teaspoon', 'teaspoons',
    
    # Industrial
    'barrel', 'barrels', 'bbl',
    'acre-foot', 'acre-feet',
    
    # Scientific
    'cc', 'cm³', 'cm3', 'cubic centimeter', 'cubic centimeters',
}

# Mass/Weight units
MASS_UNITS = {
    # SI metric
    'kg', 'kilogram', 'kilograms',
    'g', 'gram', 'grams',
    'mg', 'milligram', 'milligrams',
    'μg', 'ug', 'microgram', 'micrograms',
    'tonne', 'tonnes', 'metric ton', 'metric tons',
    
    # Imperial
    'lb', 'lbs', 'pound', 'pounds',
    'oz', 'ounce', 'ounces',
    'ton', 'tons', 'short ton', 'short tons',
    'long ton', 'long tons',
    'st', 'stone', 'stones',
    'grain', 'grains',
    
    # Scientific
    'Da', 'dalton', 'daltons',
    'amu', 'atomic mass unit', 'atomic mass units',
    'u',
}

# Astronomical mass units
MASS_ASTRO_UNITS = {
    'M☉', 'solar mass', 'solar masses',
    'M⊕', 'Earth mass', 'Earth masses',
    'M♃', 'Jupiter mass', 'Jupiter masses',
    'lunar mass', 'lunar masses',
}

# Temperature units
TEMP_UNITS = {
    '°C', '°F', 'K', '°R',
    'degrees Celsius', 'degrees C', 'Celsius',
    'degrees Fahrenheit', 'degrees F', 'Fahrenheit',
    'Kelvin', 'Kelvins',
    'Rankine',
}

# Speed units
SPEED_UNITS = {
    'km/h', 'kph', 'kmph', 'kilometers per hour', 'kilometres per hour',
    'mph', 'miles per hour',
    'm/s', 'meters per second', 'metres per second',
    'ft/s', 'feet per second',
    'knot', 'knots', 'kn', 'kt',
    'Mach',
    'c',  # speed of light
}

# Energy units
ENERGY_UNITS = {
    'J', 'joule', 'joules',
    'kJ', 'kilojoule', 'kilojoules',
    'MJ', 'megajoule', 'megajoules',
    'GJ', 'gigajoule', 'gigajoules',
    
    'cal', 'calorie', 'calories',
    'kcal', 'kilocalorie', 'kilocalories', 'Cal', 'Calorie', 'Calories',
    
    'kWh', 'kilowatt-hour', 'kilowatt-hours',
    'MWh', 'megawatt-hour', 'megawatt-hours',
    'GWh', 'gigawatt-hour', 'gigawatt-hours',
    'TWh', 'terawatt-hour', 'terawatt-hours',
    
    'eV', 'electron volt', 'electron volts', 'electronvolt', 'electronvolts',
    'keV', 'MeV', 'GeV', 'TeV',
    
    'BTU', 'British thermal unit', 'British thermal units',
    'erg', 'ergs',
    'toe', 'tonne of oil equivalent', 'tonnes of oil equivalent',
}

# Power units
POWER_UNITS = {
    'W', 'watt', 'watts',
    'mW', 'milliwatt', 'milliwatts',
    'kW', 'kilowatt', 'kilowatts',
    'MW', 'megawatt', 'megawatts',
    'GW', 'gigawatt', 'gigawatts',
    'TW', 'terawatt', 'terawatts',
    
    'hp', 'horsepower', 'bhp', 'whp',
    
    'VA', 'kVA', 'MVA', 'volt-ampere', 'volt-amperes',
    'BTU/h', 'BTU per hour',
}

# Force units
FORCE_UNITS = {
    'N', 'newton', 'newtons',
    'kN', 'kilonewton', 'kilonewtons',
    'MN', 'meganewton', 'meganewtons',
    'lbf', 'pound-force',
    'dyn', 'dyne', 'dynes',
}

# Pressure units
PRESSURE_UNITS = {
    'Pa', 'pascal', 'pascals',
    'kPa', 'kilopascal', 'kilopascals',
    'MPa', 'megapascal', 'megapascals',
    'GPa', 'gigapascal', 'gigapascals',
    'hPa', 'hectopascal', 'hectopascals',
    
    'bar', 'bars', 'mbar', 'millibar', 'millibars',
    'atm', 'atmosphere', 'atmospheres',
    'psi', 'pounds per square inch',
    'torr', 'mmHg', 'millimeters of mercury',
    'inHg', 'inches of mercury',
}

# Frequency units
FREQUENCY_UNITS = {
    'Hz', 'hertz',
    'kHz', 'kilohertz',
    'MHz', 'megahertz',
    'GHz', 'gigahertz',
    'THz', 'terahertz',
    
    'rpm', 'RPM', 'revolutions per minute', 'rev/min',
    'bpm', 'BPM', 'beats per minute',
}

# Wavelength units (often used in astronomy/physics)
WAVELENGTH_UNITS = {
    'nm', 'nanometer', 'nanometers', 'nanometre', 'nanometres',
    'μm', 'um', 'micrometer', 'micrometers', 'micrometre', 'micrometres',
    'Å', 'angstrom', 'angstroms',
}

# Electrical units
ELECTRIC_UNITS = {
    # Voltage
    'V', 'volt', 'volts',
    'kV', 'kilovolt', 'kilovolts',
    'mV', 'millivolt', 'millivolts',
    'μV', 'microvolt', 'microvolts',
    
    # Current
    'A', 'amp', 'amps', 'ampere', 'amperes',
    'mA', 'milliamp', 'milliamps', 'milliampere', 'milliamperes',
    'μA', 'microamp', 'microamps',
    
    # Resistance
    'Ω', 'ohm', 'ohms',
    'kΩ', 'kilohm', 'kilohms',
    'MΩ', 'megohm', 'megohms',
    
    # Capacitance
    'F', 'farad', 'farads',
    'μF', 'microfarad', 'microfarads',
    'nF', 'nanofarad', 'nanofarads',
    'pF', 'picofarad', 'picofarads',
    
    # Inductance
    'H', 'henry', 'henries', 'henrys',
    'mH', 'millihenry', 'millihenries',
    'μH', 'microhenry', 'microhenries',
    
    # Charge
    'C', 'coulomb', 'coulombs',
    'Ah', 'ampere-hour', 'ampere-hours',
    'mAh', 'milliampere-hour', 'milliampere-hours',
    
    # Conductance
    'S', 'siemens',
}

# Magnetic units
MAGNETIC_UNITS = {
    'T', 'tesla', 'teslas',
    'G', 'gauss',
    'Wb', 'weber', 'webers',
}

# Radiation units
RADIATION_UNITS = {
    'Bq', 'becquerel', 'becquerels',
    'Ci', 'curie', 'curies',
    'Sv', 'sievert', 'sieverts',
    'mSv', 'millisievert', 'millisieverts',
    'Gy', 'gray', 'grays',
    'rad', 'rads',
    'rem', 'rems',
}

# Concentration units
CONCENTRATION_UNITS = {
    'M', 'mol/L', 'molar',
    'mM', 'millimolar',
    'μM', 'micromolar',
    'ppm', 'parts per million',
    'ppb', 'parts per billion',
    'ppt', 'parts per trillion',
    'mg/dL', 'mg/L', 'g/L', 'μg/mL',
    '%', 'percent',
}

# Density units
DENSITY_UNITS = {
    'g/cm³', 'g/cm3', 'grams per cubic centimeter',
    'kg/m³', 'kg/m3', 'kilograms per cubic meter',
    'lb/ft³', 'lb/ft3', 'pounds per cubic foot',
    'g/mL', 'grams per milliliter',
}

# Data/file size units
FILE_SIZE_UNITS = {
    'bit', 'bits', 'b',
    'byte', 'bytes', 'B',
    'KB', 'kilobyte', 'kilobytes', 'kB',
    'MB', 'megabyte', 'megabytes',
    'GB', 'gigabyte', 'gigabytes',
    'TB', 'terabyte', 'terabytes',
    'PB', 'petabyte', 'petabytes',
    'EB', 'exabyte', 'exabytes',
    'KiB', 'MiB', 'GiB', 'TiB', 'PiB',  # Binary units
}

# Bit rate units
BIT_RATE_UNITS = {
    'bps', 'bit/s', 'bits per second',
    'Kbps', 'kbit/s', 'kilobits per second',
    'Mbps', 'Mbit/s', 'megabits per second',
    'Gbps', 'Gbit/s', 'gigabits per second',
    'Tbps', 'Tbit/s', 'terabits per second',
}

# Currency symbols and codes
CURRENCY_SYMBOLS = {
    '$', 'US$', 'USD', 'dollar', 'dollars', 'US dollar', 'US dollars',
    '€', 'EUR', 'euro', 'euros',
    '£', 'GBP', 'pound', 'pounds', 'pound sterling', 'pounds sterling',
    '¥', 'JPY', 'CNY', 'yen', 'yuan', 'renminbi',
    '₹', 'INR', 'rupee', 'rupees',
    '₩', 'KRW', 'won',
    '₽', 'RUB', 'ruble', 'rubles', 'rouble', 'roubles',
    'CHF', 'Swiss franc', 'Swiss francs',
    'AUD', 'CAD', 'NZD', 'HKD', 'SGD',
    'kr', 'SEK', 'NOK', 'DKK', 'krona', 'kronor', 'krone', 'kroner',
    'R$', 'BRL', 'real', 'reais',
    'ZAR', 'rand',
    'MXN', 'peso', 'pesos',
}

# Magnitude words (for money, population, etc.)
MAGNITUDE_WORDS = {
    'thousand', 'thousands',
    'million', 'millions',
    'billion', 'billions',
    'trillion', 'trillions',
    'quadrillion', 'quadrillions',
}

# Time duration units
DURATION_UNITS = {
    'second', 'seconds', 'sec', 'secs', 's',
    'minute', 'minutes', 'min', 'mins',
    'hour', 'hours', 'hr', 'hrs', 'h',
    'day', 'days', 'd',
    'week', 'weeks', 'wk', 'wks',
    'month', 'months', 'mo', 'mos',
    'year', 'years', 'yr', 'yrs', 'y',
    'decade', 'decades',
    'century', 'centuries',
    'millennium', 'millennia', 'millenniums',
}

# Context words for specific categories
POPULATION_CONTEXT = {
    'population', 'people', 'inhabitants', 'residents', 'citizens',
    'capita', 'persons', 'individuals',
}

CASUALTY_CONTEXT = {
    'killed', 'dead', 'deaths', 'casualties', 'wounded', 'injured',
    'victims', 'fatalities', 'died', 'perished',
}

VOTE_CONTEXT = {
    'vote', 'votes', 'ballot', 'ballots', 'voter', 'voters',
    'electoral', 'election',
}

AGE_CONTEXT = {
    'years old', 'year old', 'aged', 'age', 'years of age',
}

ELEVATION_CONTEXT = {
    'above sea level', 'elevation', 'altitude', 'height above',
    'asl', 'a.s.l.',
}

DEPTH_CONTEXT = {
    'below sea level', 'depth', 'deep', 'below',
    'bsl', 'b.s.l.',
}

# Compile all units for quick lookup
ALL_UNITS = (
    DISTANCE_UNITS | DISTANCE_ASTRO_UNITS | AREA_UNITS | VOLUME_UNITS |
    MASS_UNITS | MASS_ASTRO_UNITS | TEMP_UNITS | SPEED_UNITS |
    ENERGY_UNITS | POWER_UNITS | FORCE_UNITS | PRESSURE_UNITS |
    FREQUENCY_UNITS | WAVELENGTH_UNITS | ELECTRIC_UNITS | MAGNETIC_UNITS |
    RADIATION_UNITS | CONCENTRATION_UNITS | DENSITY_UNITS |
    FILE_SIZE_UNITS | BIT_RATE_UNITS | CURRENCY_SYMBOLS | DURATION_UNITS
)

