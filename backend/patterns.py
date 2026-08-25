"""
Legal Metrology Compliance Checker - Configurable Patterns & Dictionaries
Contains all regex expressions, keyword sets, and configurable rules for the 8 mandatory declarations.
"""

import re
from typing import List, Dict, Pattern

# -----------------------------------------------------------------------------
# 1. NAME OF COMMODITY
# -----------------------------------------------------------------------------
# Heuristics for common commodity descriptors and prefixes
COMMODITY_PREFIX_PATTERNS: List[Pattern] = [
    re.compile(r'(?:name\s+of\s+(?:the\s+)?commodity|commodity(?:\s+name)?|product\s+name|product|item\s+name|item|food\s+category|goods)\s*[:\-]\s*(.+)', re.IGNORECASE),
    re.compile(r'(?:article|type\s+of\s+commodity)\s*[:\-]\s*(.+)', re.IGNORECASE),
]

# Common generic Indian FMCG product keywords for fallback heuristic detection
COMMON_COMMODITY_KEYWORDS: List[str] = [
    "biscuit", "biscuits", "cookie", "cookies", "chips", "crisps", "wafer", "wafers",
    "tea", "coffee", "juice", "drink", "beverage", "milk", "butter", "cheese", "ghee",
    "atta", "flour", "rice", "dal", "pulses", "oil", "refined oil", "mustard oil",
    "salt", "sugar", "spices", "masala", "turmeric", "chilli powder", "garam masala",
    "soap", "shampoo", "detergent", "toothpaste", "handwash", "sanitizer",
    "namkeen", "bhujia", "snack", "snacks", "noodle", "noodles", "pasta",
    "chocolate", "chocolates", "candy", "toffee", "confectionery", "sauce", "ketchup",
    "bread", "cake", "rusk", "pickle", "jam", "honey", "cereals", "cornflakes",
    "ready to eat", "energy bar", "granola", "mix", "instant mix"
]

# -----------------------------------------------------------------------------
# 2. MANUFACTURER NAME
# -----------------------------------------------------------------------------
# Prefixes indicating manufacturer identity
MFG_NAME_PATTERNS: List[Pattern] = [
    re.compile(r'(?:manufactured\s*(?:&|and)?\s*marketed\s*by|manufactured\s*by|mfg\.?\s*(?:&|and)?\s*mktg\.?\s*by|mfg\.?\s*by|mfd\.?\s*by|mfr\.?\s*by|manufacturer|producer|packed\s*by|pkd\.?\s*by|processed\s*by|bottled\s*by|imported\s*(?:&|and)?\s*marketed\s*by|manufactured\s*for)\s*[:\-]?\s*([^\n\r,]+(?:(?:pvt|private|ltd|limited|llp|corp|corporation|industries|foods|enterprises|co|company|products|laboratories|pharma|herbals)[^\n\r,]*)?)', re.IGNORECASE),
    re.compile(r'(?:marketed\s*by|mktg\.?\s*by)\s*[:\-]?\s*([^\n\r,]+(?:(?:pvt|private|ltd|limited|llp)[^\n\r,]*)?)', re.IGNORECASE)
]

COMPANY_SUFFIXES = [
    "pvt ltd", "private limited", "ltd", "limited", "llp", "corp", "corporation",
    "inc", "industries", "foods", "enterprises", "company", "co.", "products", "works"
]

# -----------------------------------------------------------------------------
# 3. MANUFACTURER ADDRESS
# -----------------------------------------------------------------------------
# Indian 6-digit PIN code regex (PIN: 110001, PIN - 600040, Pin Code: 560001, etc.)
PIN_CODE_PATTERN = re.compile(r'(?:pin(?:\s*code)?\s*[:\-]?)?\s*\b([1-9][0-9]{2}\s?[0-9]{3})\b', re.IGNORECASE)

# Indian States and Major Union Territories
INDIAN_STATES_AND_CITIES: List[str] = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
    "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh",
    "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
    "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh",
    "uttarakhand", "west bengal", "delhi", "new delhi", "mumbai", "bengaluru", "bangalore",
    "chennai", "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur", "surat", "noida",
    "gurugram", "gurgaon", "chandigarh", "coimbatore", "kochi", "indore", "lucknow"
]

ADDRESS_KEYWORDS: List[str] = [
    "plot no", "survey no", "sy no", "sy. no", "phase", "sector", "industrial area", "indl area",
    "gidc", "midc", "sidco", "kiadb", "estate", "road", "rd", "street", "st", "lane",
    "nagar", "colony", "taluk", "dist", "district", "village", "po", "post", "near"
]

# -----------------------------------------------------------------------------
# 4. NET QUANTITY
# -----------------------------------------------------------------------------
# Recognized units of measurement under Legal Metrology (Weights & Measures) Rules
LEGAL_UNITS: List[str] = [
    r'kg', r'g', r'gm', r'gms', r'mg',
    r'l', r'ltr', r'ltrs', r'liter', r'liters', r'litre', r'litres', r'ml', r'milli\s*litre',
    r'm', r'meter', r'meters', r'metre', r'metres', r'cm', r'mm',
    r'n', r'unit', r'units', r'piece', r'pieces', r'pcs', r'count', r'u'
]

UNITS_REGEX_STR = r'|'.join(LEGAL_UNITS)

NET_QTY_PATTERNS: List[Pattern] = [
    # Explicit prefix: "Net Quantity / Net Qty / Net Weight / Net Wt / Net Vol: 500 g"
    re.compile(
        rf'(?:net\s*(?:quantity|qty|weight|wt|volume|vol|content|contents))\s*[:\-]?\s*(\d+(?:\.\d+)?\s*(?:{UNITS_REGEX_STR}))\b',
        re.IGNORECASE
    ),
    # Standalone metric declarations like "500 g", "1 kg", "750 ml", "1 L", "10 N"
    re.compile(
        rf'\b(\d+(?:\.\d+)?\s*(?:{UNITS_REGEX_STR}))\b',
        re.IGNORECASE
    )
]

# Negative checks: exclude "Gross Wt", "Tare Wt", "Fat: 20g", "Protein: 5g", etc.
EXCLUDED_QUANTITY_PREFIXES = [
    "gross", "tare", "fat", "protein", "carbohydrate", "sugar", "sodium", "calcium",
    "energy", "serving", "per 100g", "per 100ml", "cholesterol", "fiber"
]

# -----------------------------------------------------------------------------
# 5. MRP (MAXIMUM RETAIL PRICE)
# -----------------------------------------------------------------------------
MRP_PATTERNS: List[Pattern] = [
    re.compile(
        r'(?:m\.?r\.?p\.?|maximum\s+retail\s+price|max\.?\s*retail\s*price)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:/-\s*)?',
        re.IGNORECASE
    ),
    re.compile(
        r'(?:rs\.?|inr|₹)\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:/-\s*)?\s*(?:\(?(?:m\.?r\.?p\.?|maximum\s+retail\s+price)\)?)',
        re.IGNORECASE
    ),
    re.compile(
        r'\b(?:m\.?r\.?p\.?|maximum\s+retail\s+price)\s*[:\-]?\s*([₹Rs\.]*\s*[0-9]+(?:\.[0-9]{1,2})?)',
        re.IGNORECASE
    )
]

# -----------------------------------------------------------------------------
# 6. MRP WORDING / FORMAT (TAX INCLUSIVE DECLARATION)
# -----------------------------------------------------------------------------
# Under Legal Metrology (Packaged Commodities) Rules:
# The declaration of MRP must be accompanied by the expression "(inclusive of all taxes)" or equivalent.
CONFIGURABLE_TAX_INCLUSIVE_PATTERNS: List[Pattern] = [
    re.compile(r'\(?\s*incl(?:usive)?\.?\s*of\s*all\s*taxes\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*incl(?:usive)?\.?\s*all\s*taxes\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*incl(?:usive)?\.?\s*taxes\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*all\s*taxes\s*included\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*inclusive\s*of\s*taxes\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*tax\s*included\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*taxes\s*included\s*\)?', re.IGNORECASE),
    re.compile(r'\(?\s*incl\.?\s*of\s*taxes\s*\)?', re.IGNORECASE)
]

# -----------------------------------------------------------------------------
# 7. BEST BEFORE / USE BY / EXPIRY
# -----------------------------------------------------------------------------
DATE_DECLARATION_PATTERNS: List[Pattern] = [
    # Best Before durations: "Best Before 6 Months From Packaging", "Best Before 12 Months"
    re.compile(
        r'(?:best\s+before|use\s+by|expiry\s+date|expiry|exp\.?\s*date|exp\.?|date\s+of\s+expiry|mfg\s+date|pkd\s+date)\s*[:\-]?\s*([0-9]{1,2}\s*(?:months?|days?|years?|weeks?)[^\n\r.,;]*)',
        re.IGNORECASE
    ),
    # Explicit dates: "EXP: 12/2026", "USE BY: 15/08/2027", "EXP 08/27", "BEST BEFORE: 24/11/2026"
    re.compile(
        r'(?:best\s+before|use\s+by|expiry\s+date|expiry|exp\.?\s*date|exp\.?|date\s+of\s+expiry)\s*[:\-]?\s*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4}|[0-9]{1,2}[\/\-\.][0-9]{2,4}|[A-Za-z]{3}[\s\-\.\/][0-9]{2,4}|[0-9]{1,2}\s+[A-Za-z]{3}\s+[0-9]{2,4})',
        re.IGNORECASE
    ),
    # General "Best Before X Months from ..." phrase
    re.compile(
        r'\b(best\s+before\s+[0-9]{1,2}\s+(?:months?|days?|years?)[^\n\r]*)',
        re.IGNORECASE
    ),
    # Expiry phrase followed by code/date
    re.compile(
        r'\b(use\s+by\s*[:\-]?\s*[^\n\r]+)',
        re.IGNORECASE
    ),
    re.compile(
        r'\b(expiry\s*(?:date)?\s*[:\-]?\s*[^\n\r]+)',
        re.IGNORECASE
    )
]

# -----------------------------------------------------------------------------
# 8. CUSTOMER-CARE DETAILS
# -----------------------------------------------------------------------------
CUSTOMER_CARE_KEYWORDS: List[str] = [
    "customer care", "consumer care", "customer service", "consumer service",
    "contact us", "reach us at", "helpline", "toll free", "toll-free", "help desk",
    "feedback", "queries", "complaints", "write to us", "customer support"
]

# Regex for Phone numbers (Toll-Free 1800, Landline with STD code, or 10-digit Indian Mobile)
PHONE_PATTERNS: List[Pattern] = [
    re.compile(r'\b(1800[- ]?[0-9]{3}[- ]?[0-9]{3,4})\b', re.IGNORECASE),  # Indian 1800 toll free
    re.compile(r'(?:ph(?:one)?|tel|mob|call|contact|toll\s*free|helpline)\s*[:\-.]?\s*(\+?91[- ]?[6-9][0-9]{9}|[0-9]{3,5}[- ]?[0-9]{6,8}|[6-9][0-9]{9})\b', re.IGNORECASE),
    re.compile(r'\b(\+?91[- ]?[6-9][0-9]{9})\b')  # +91 mobile
]

# Regex for Email Addresses
EMAIL_PATTERN: Pattern = re.compile(
    r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
)

# Combined Customer Care Prefix
CUSTOMER_CARE_PREFIX_PATTERN = re.compile(
    r'(?:for\s+feedback|for\s+queries|for\s+complaints|consumer\s+care|customer\s+care|customer\s+service|contact\s+us|write\s+to\s+us|reach\s+us|helpline)\s*[:\-]?\s*(.+)',
    re.IGNORECASE
)
