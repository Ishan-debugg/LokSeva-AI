"""
preprocess.py
─────────────────────────────────────────────────────────────────────────────
Multilingual pre-processing pipeline for LokSevaAI.

Strategy:
  1. Keyword dictionary — maps Hindi/Marathi complaint words to English
     equivalents so TF-IDF sees consistent English features.
  2. Transliteration normaliser — common Romanised Hindi/Marathi spellings
     ("bijli", "paani", "kachra", "rasta") mapped to their English concepts.
  3. No external API calls → zero latency, works offline.
  4. Falls back to GoogleTranslator only when text is detected as a language
     other than English, Hindi, or Marathi (rare edge-case).
─────────────────────────────────────────────────────────────────────────────
"""

import re

# ── 1. DEVANAGARI KEYWORD → ENGLISH CONCEPT MAP ───────────────────────────
# Each entry maps a Devanagari word/phrase to one or more English words that
# the TF-IDF vectorizer already knows from KDMC training data.
# Words are intentionally repeated to boost TF weight of the target concept.

DEVANAGARI_MAP = {
    # ── Electricity / Power ───────────────────────────────────────────────
    "बिजली":       "electricity electric power light",
    "बत्ती":       "light electricity electric",
    "करंट":        "electricity electric current",
    "पावर":        "power electricity electric",
    "लाइट":        "light electricity electric",
    "अंधेरा":      "electricity light electric dark",
    "वीज":         "electricity electric power",          # Marathi
    "दिवे":        "light electricity electric",          # Marathi
    "वीजपुरवठा":   "electricity supply power electric",  # Marathi
    "विद्युत":     "electricity electric power",
    "ट्रान्सफॉर्मर": "transformer electricity electric",
    "खांब":        "pole electricity electric streetlight", # Marathi
    "स्ट्रीटलाइट": "streetlight light electricity",

    # ── Water Supply ──────────────────────────────────────────────────────
    "पानी":        "water supply drinking",
    "पाणी":        "water supply drinking",               # Marathi
    "जल":          "water supply",
    "नल":          "tap water pipe supply",
    "नळ":          "tap water pipe supply",               # Marathi
    "पाइप":        "pipe water supply leak",
    "पाईप":        "pipe water supply leak",
    "पानीपुरवठा":  "water supply drinking",
    "पाणीपुरवठा":  "water supply drinking",              # Marathi
    "पानी नहीं":   "water supply no water",
    "पानी बंद":    "water supply closed",

    # ── Roads & Traffic ───────────────────────────────────────────────────
    "सड़क":        "road street pothole traffic",
    "रस्ता":       "road street pothole",                 # Marathi
    "रास्ता":      "road street",
    "गड्ढा":       "pothole road",
    "खड्डे":       "pothole road",                        # Marathi
    "ट्रैफिक":     "traffic road signal",
    "सिग्नल":      "signal traffic road",
    "पुल":         "bridge road",
    "ब्रिज":       "bridge road",

    # ── Sewage & Drainage ─────────────────────────────────────────────────
    "नाला":        "drain sewage drainage nala",
    "नाली":        "drain sewage drainage",
    "सीवेज":       "sewage drainage",
    "ड्रेनेज":     "drainage sewage",
    "गटार":        "drain sewage drainage",               # Marathi
    "मलनिस्सारण":  "sewage drainage",                    # Marathi
    "बंद नाला":    "blocked drain sewage",
    "नाला बंद":    "blocked drain sewage",

    # ── Solid Waste / Garbage ─────────────────────────────────────────────
    "कचरा":        "garbage waste solid waste",
    "गंदगी":       "garbage filth waste",
    "सफाई":        "cleaning garbage sweeping",
    "झाडू":        "sweeping garbage cleaning",           # Marathi
    "स्वच्छता":    "cleanliness garbage waste",
    "कूड़ा":       "garbage waste",
    "डस्टबिन":     "dustbin garbage waste",

    # ── Encroachment ──────────────────────────────────────────────────────
    "अतिक्रमण":   "encroachment illegal",
    "अवैध":        "illegal encroachment",
    "कब्जा":       "encroachment illegal occupation",
    "अतिक्रमण हटाओ": "encroachment removal",
}

# Marathi inflections and vocabulary that do not reliably match the Hindi forms.
MARATHI_SPECIFIC = {
    # Electricity
    "रोहित्र": "transformer electricity",
    "वीजतार": "electric wire electricity",
    "लोडशेडिंग": "load shedding electricity power",
    "वीजेचा": "electricity power",
    "वीजेची": "electricity power",
    "वीजेमुळे": "electricity power",

    # Water
    "नळकांडे": "water pipe",
    "गळती": "leak water pipe",
    "दूषित": "contaminated dirty water",
    "पाण्याचा": "water supply",
    "पाण्याची": "water supply",
    "पाण्याने": "water supply",
    "पाण्यात": "water supply",

    # Drainage
    "नाले": "drain sewage nala",
    "गटारे": "drain sewage gutter",
    "तुंबलेले": "blocked clogged drain",
    "साचले": "accumulated waterlogging",
    "ओसंडून": "overflow drain sewage",
    "भुयारी": "underground drainage",
    "नाल्याची": "drain sewage",
    "नाल्यात": "drain sewage",
    "नाल्यामुळे": "drain sewage",

    # Road
    "रस्त्यावर": "road street",
    "खड्डा": "pothole road",
    "दुरुस्ती": "repair road",
    "वाहतूक": "traffic road",
    "रस्त्याची": "road street",
    "रस्त्याने": "road street",

    # Garbage
    "उचलला": "collected garbage",
    "घंटागाडी": "garbage collection vehicle",

    # Encroachment
    "अनधिकृत": "unauthorized illegal encroachment",
    "बेकायदा": "illegal unauthorized encroachment",
    "बांधकाम": "construction building",
    "काढा": "remove encroachment",
}

MARATHI_INFLECTION_MAP = {
    # Drainage
    "नाल्याची": "drain sewage",
    "नाल्याचा": "drain sewage",
    "नाल्यात": "drain sewage",
    "नाल्यामुळे": "drain sewage",
    "नाल्यावर": "drain sewage",
    "नाल्याने": "drain sewage",
    "नाल्यांची": "drain sewage",
    "गटाराची": "gutter drain sewage",
    "गटाराचा": "gutter drain sewage",
    "गटारात": "gutter drain sewage",
    "गटारामुळे": "gutter drain sewage",
    "गटारांची": "gutter drain sewage",

    # Water
    "पाण्याची": "water supply",
    "पाण्याचा": "water supply",
    "पाण्यात": "water supply",
    "पाण्यामुळे": "water supply",
    "पाण्याने": "water supply",

    # Electricity
    "वीजेची": "electricity electric",
    "वीजेचा": "electricity electric",
    "वीजेमुळे": "electricity electric",
    "वीजेत": "electricity electric",

    # Road
    "रस्त्याची": "road street",
    "रस्त्याचा": "road street",
    "रस्त्यावर": "road street",
    "रस्त्याने": "road street",
    "रस्त्यामुळे": "road street",

    # Garbage
    "कचऱ्याची": "garbage waste",
    "कचऱ्याचा": "garbage waste",
    "कचऱ्यामुळे": "garbage waste",

    # Encroachment
    "अतिक्रमणाची": "encroachment illegal",
    "अतिक्रमणाचा": "encroachment illegal",
    "अतिक्रमणामुळे": "encroachment illegal",
}

DEVANAGARI_MAP.update(MARATHI_SPECIFIC)
DEVANAGARI_MAP.update(MARATHI_INFLECTION_MAP)

MARATHI_PHRASE_MAP = {
    "पाणी साचले": "water accumulated waterlogging drainage",
    "पाणी येत नाही": "water not coming supply",
    "वीज नाही": "electricity no power",
    "नाला तुंबला": "drain blocked sewage",
    "गटार तुंबले": "drain blocked sewage gutter",
}

MARATHI_PHRASES = [
    # Drainage and waterlogging; these must win over the generic water rule.
    ("नाल्यात कचरा", "sewage"),
    ("पाणी साचले आहे", "sewage"),
    ("नाल्यामुळे पाणी", "sewage"),
    ("गटारामुळे पाणी", "sewage"),
    ("पाणी निघत नाही", "sewage"),
    ("पाणी वाहत नाही", "sewage"),
    ("पाणी तुंबले", "sewage"),
    ("नाल्याची सफाई", "sewage"),
    ("गटाराची सफाई", "sewage"),
    ("नाले तुंबले", "sewage"),
    ("गटारे तुंबले", "sewage"),
    ("नाला तुंबला", "sewage"),
    ("गटार तुंबले", "sewage"),
    ("नाली तुंबली", "sewage"),
    ("पाणी जमा", "sewage"),
    ("पाणी साचले", "sewage"),
    ("नाला साफ", "sewage"),

    # Water supply
    ("नळाला पाणी नाही", "water"),
    ("पाणीपुरवठा बंद", "water"),
    ("पाणी येत नाही", "water"),
    ("घाण पाणी येते", "water"),
    ("पाणी गळती", "water"),
    ("दूषित पाणी", "water"),
    ("पाईप फुटला", "water"),
    ("पाणी नाही", "water"),
    ("पाणी बंद", "water"),
    ("नळ बंद", "water"),

    # Electricity and streetlights
    ("दिवे जळत नाहीत", "streetlight"),
    ("स्ट्रीट लाईट बंद", "streetlight"),
    ("ट्रान्सफॉर्मर खराब", "streetlight"),
    ("रस्त्यावरील दिवे", "streetlight"),
    ("वीज खंडित", "streetlight"),
    ("वीज गेली", "streetlight"),
    ("दिवे नाहीत", "streetlight"),
    ("खांब पडला", "streetlight"),
    ("वीज नाही", "streetlight"),

    # Road and traffic
    ("रस्त्यावर खड्डे", "road"),
    ("रस्त्याची दुरुस्ती", "road"),
    ("वाहतूक कोंडी", "road"),
    ("रस्ता खराब", "road"),
    ("सिग्नल बंद", "road"),
    ("पूल खराब", "road"),

    # Garbage and cleanliness
    ("कचरा उचलला नाही", "garbage"),
    ("कचरा नाही उचलला", "garbage"),
    ("घंटागाडी आली नाही", "garbage"),
    ("कचरा साफ नाही", "garbage"),

    # Encroachment; "काढा" is intentionally not a standalone rule.
    ("अनधिकृत बांधकाम", "encroachment"),
    ("रस्त्यावर अतिक्रमण", "encroachment"),
    ("अतिक्रमण हटवा", "encroachment"),
    ("अतिक्रमण काढा", "encroachment"),
    ("बेकायदा बांधकाम", "encroachment"),
]
MARATHI_PHRASES.sort(key=lambda item: len(item[0]), reverse=True)

DRAIN_ANCHORS = {
    "drain", "drains", "drainage", "gutter", "gutters", "sewer", "sewage",
    "sewerage", "nala", "naala", "nali", "naali", "manhole", "man hole",
    "stormwater", "storm water", "underground drainage", "septic",
    "cesspool", "cesspit",
    "नाला", "नाली", "नाले", "नाल्यात", "गटार", "गटारे", "मलनिस्सारण",
    "सीवर", "सीवेज", "मैनहोल", "ड्रेनेज", "सेप्टिक",
}

CLEANING_GARBAGE_WORDS = {
    "cleaning", "clean", "safai", "lift", "lifted", "lifting", "garbage",
    "waste", "smell", "stench", "odour", "odor", "foul", "filth", "dirty",
    "blocked", "block", "overflow", "overflowing", "accumulated", "stagnant",
    "material", "debris", "sludge", "clog", "clogged", "chok", "choked",
    "logged", "logging", "water logged", "waterlogging",
    "सफाई", "कचरा", "गंदगी", "बदबू", "बंद", "जाम", "साफ", "उचलावा",
    "उचलना", "घाण", "वास",
}

COMPOUND_PATTERNS = [
    (r'\bsepti[ck]\s*tank\b', "sewage"),
    (r'\bsepitc\s*tank\b', "sewage"),
    (r'\bclean(?:ing|ign)\s+(?:of\s+)?(?:the\s+)?septi[ck]\b', "sewage"),
    (r'\b(?:foul|bad|dirty)\s+smell\b.{0,30}\b(?:drain|gutter|sewer)\w*\b', "sewage"),
    (r'\b(?:smell|odou?r|stench)\b.{0,30}\b(?:drain|gutter|sewer)\w*\b', "sewage"),
    (r'\b(?:drain|gutter|sewer)\w*\b.{0,40}\b(?:smell|odou?r|stench|foul)\b', "sewage"),
    (r'\b(?:material|debris|sludge)\b.{0,40}\b(?:gutter|drain|nala)\w*\b', "sewage"),
    (r'\b(?:gutter|drain|nala)\w*\b.{0,40}\b(?:material|debris|sludge)\b', "sewage"),
    (r'\b(?:rain\s*water|rainwater)\s+(?:log|logged|logging)\b', "sewage"),
    (r'\b(?:drain|gutter|sewer)\w*\b.{0,40}\b(?:overflow|blocked|clog|chok)\w*\b', "sewage"),
    (r'\b(?:overflow|blocked|clog|chok)\w*\b.{0,40}\b(?:drain|gutter|sewer)\w*\b', "sewage"),
]


# ── 2. ROMANISED TRANSLITERATION MAP ──────────────────────────────────────
# Covers how citizens type Hindi/Marathi using English letters (very common
# on mobile keyboards).  Sorted by length DESC so longer phrases match first.

TRANSLITERATION_MAP = [
    # Electricity
    ("power cut",        "electricity cut power outage electric"),
    ("power outage",     "electricity outage electric"),
    ("load shedding",    "electricity power outage electric"),
    ("light nahi",       "electricity light no power"),
    ("light band",       "electricity light no power"),
    ("bijli nahi",       "electricity no power"),
    ("bijli gayi",       "electricity gone no power"),
    ("bijli cut",        "electricity cut power"),
    ("current nahi",     "electricity no current power"),
    ("current gaya",     "electricity gone no power"),
    ("batti nahi",       "electricity light no power"),
    ("batti gayi",       "electricity light gone"),
    ("andhera",          "electricity dark no light"),
    ("no electricity",   "electricity no power outage"),
    ("no current",       "electricity no power"),
    ("no power",         "electricity no power outage"),
    ("veej nahi",        "electricity no power"),           # Marathi

    # Water
    ("paani nahi",       "water supply no water"),
    ("pani nahi",        "water supply no water"),
    ("paani band",       "water supply no water closed"),
    ("nal band",         "water tap closed supply"),
    ("pipe leak",        "water pipe leak supply"),
    ("ganda paani",      "water dirty contaminated supply"),
    ("dirty water",      "water contaminated supply"),
    ("no water",         "water supply no water"),

    # Roads
    ("sadak kharab",     "road damage pothole"),
    ("rasta kharab",     "road damage pothole"),
    ("khaddha",          "pothole road"),
    ("gadha",            "pothole road"),
    ("road damage",      "road pothole damage"),
    ("road repair",      "road pothole repair"),
    ("traffic jam",      "traffic road congestion"),
    ("signal band",      "traffic signal road"),

    # Drainage / Sewage
    ("nala block",       "drain sewage blocked"),
    ("nali block",       "drain sewage blocked"),
    ("naali jam",        "drain sewage blocked"),
    ("sewage overflow",  "sewage drainage overflow"),
    ("drainage block",   "drainage sewage blocked"),
    ("ganda nala",       "sewage drain dirty"),
    ("gatar",            "drain sewage"),                  # Marathi

    # Garbage
    ("kachra",           "garbage waste solid waste"),
    ("kuda",             "garbage waste"),
    ("gandagi",          "garbage filth waste"),
    ("safai nahi",       "garbage cleaning not done"),
    ("no cleaning",      "garbage cleanliness waste"),
    ("waste not collected", "garbage waste collection"),

    # Encroachment
    ("atikraman",        "encroachment illegal"),
    ("kabja",            "encroachment illegal occupation"),
    ("avaidh",           "illegal encroachment"),
    ("illegal building",  "encroachment illegal construction"),
    ("illegal shop",      "encroachment illegal"),
]


# ── 3. DIRECT DEPARTMENT KEYWORD RULES ────────────────────────────────────
# These are high-confidence rules that bypass the ML model entirely.
# The keyword engine checks the raw (lowercased) complaint text BEFORE
# and AFTER translation.  If any rule matches, the department is returned
# directly — no ML needed.

KEYWORD_RULES = [
    # ─ Electric Department ───────────────────────────────────────────────
    {
        "department": "streetlight",
        "keywords": [
            "power cut", "power outage", "power failure", "load shedding",
            "no electricity", "no power", "no current", "electricity cut",
            "electricity gone", "electricity failure", "electric failure",
            "bijli", "batti", "bijli nahi", "batti nahi", "bijli gayi",
            "current nahi", "current gaya", "light nahi", "light band",
            "andhera", "andher", "veej nahi", "streetlight", "street light",
            "street lamp", "lamp post", "transformer", "electric pole",
            "electricity supply", "electric supply", "power supply cut",
            "बिजली", "बत्ती", "वीज", "करंट", "विद्युत",
        ],
    },
    # ─ Sewage & Drainage ─────────────────────────────────────────────────
    {
        "department": "sewage",
        "keywords": [
            "sewage", "drainage", "drain blocked", "drain overflow",
            "blocked drain", "nala", "naala", "nali", "naali",
            "gutter", "manhole", "sewer", "sewage overflow",
            "drainage problem", "nala block", "nali block", "naali jam",
            "flood water", "waterlogging", "water logging",
            "गटार", "नाला", "नाली", "मलनिस्सारण",
        ],
    },
    # ─ Water Supply Department ───────────────────────────────────────────
    {
        "department": "water",
        "keywords": [
            "no water", "water supply", "water not coming", "water cut",
            "water shortage", "water problem", "water pipe", "water leak",
            "water leakage", "drinking water", "dirty water", "contaminated water",
            "pipe burst", "water pressure", "paani nahi", "pani nahi",
            "paani band", "nal band", "पानी", "पाणी", "जल", "नल",
        ],
    },
    # ─ Road & Traffic ────────────────────────────────────────────────────
    {
        "department": "road",
        "keywords": [
            "pothole", "road damage", "road repair", "road broken",
            "road bad condition", "speed breaker", "footpath", "divider",
            "traffic signal", "traffic jam", "traffic light",
            "road accident", "road construction", "sadak", "rasta",
            "khaddha", "gadha", "road kharab",
            "सड़क", "रस्ता", "गड्ढा", "खड्डे", "ट्रैफिक",
        ],
    },
    # ─ Solid Waste / Garbage ─────────────────────────────────────────────
    {
        "department": "garbage",
        "keywords": [
            "garbage", "waste", "trash", "rubbish", "litter",
            "dustbin", "garbage collection", "waste collection",
            "no sweeping", "no cleaning", "cleanliness", "kachra",
            "kuda", "gandagi", "safai", "कचरा", "गंदगी", "सफाई",
        ],
    },
    # ─ Encroachment ──────────────────────────────────────────────────────
    {
        "department": "encroachment",
        "keywords": [
            "encroachment", "illegal construction", "illegal building",
            "illegal shop", "illegal occupation", "atikraman", "kabja",
            "avaidh", "अतिक्रमण", "अवैध", "कब्जा",
        ],
    },
]


# ── HELPERS ────────────────────────────────────────────────────────────────

def _apply_devanagari_map(text: str) -> str:
    """Replace Devanagari words with English concepts."""
    for deva_word in sorted(DEVANAGARI_MAP, key=len, reverse=True):
        english_expansion = DEVANAGARI_MAP[deva_word]
        if deva_word in text:
            text = text.replace(deva_word, " " + english_expansion + " ")
    return text


def _apply_transliteration_map(text: str) -> str:
    """Replace Romanised Hindi/Marathi phrases with English equivalents."""
    for romanised, english_expansion in TRANSLITERATION_MAP:
        # whole-word boundary match to avoid partial replacements
        pattern = r'(?<!\w)' + re.escape(romanised) + r'(?!\w)'
        if re.search(pattern, text):
            text = re.sub(pattern, " " + english_expansion + " ", text)
    return text


def keyword_department_override(text: str):
    """
    Check the complaint text against high-confidence keyword rules.
    Returns the department key string if a match is found, else None.
    The caller should use this BEFORE falling back to the ML model.
    """
    lower = text.lower()
    for phrase, department in MARATHI_PHRASES:
        if department == "sewage" and phrase in lower:
            return department

    for phrase, department in MARATHI_PHRASES:
        if department != "sewage" and phrase in lower:
            return department

    if _drain_anchor_check(lower):
        return "sewage"

    for pattern, department in COMPOUND_PATTERNS:
        if re.search(pattern, lower, re.IGNORECASE):
            return department

    for rule in KEYWORD_RULES:
        for kw in rule["keywords"]:
            if kw.lower() in lower:
                return rule["department"]
    return None


def _drain_anchor_check(text: str):
    lower = text.lower()
    has_anchor = any(
        _contains_term(lower, anchor) for anchor in DRAIN_ANCHORS
    )
    has_cleaning_or_garbage_context = any(
        _contains_term(lower, term) for term in CLEANING_GARBAGE_WORDS
    )
    if has_anchor and has_cleaning_or_garbage_context:
        return "sewage"
    return None


def _contains_term(text: str, term: str) -> bool:
    if re.search(r'[a-z]', term, re.IGNORECASE):
        pattern = r'(?<!\w)' + re.escape(term) + r'(?!\w)'
        return re.search(pattern, text, re.IGNORECASE) is not None
    return term in text


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline:
      1. Devanagari keyword expansion (Hindi + Marathi script)
      2. Romanised transliteration expansion
      3. Lowercase normalisation
      4. Extra whitespace removed
    No external API calls — fully offline.
    """
    if not text or not isinstance(text, str):
        return ""

    # Expand full Marathi phrases before replacing their component words.
    for phrase, expansion in MARATHI_PHRASE_MAP.items():
        text = text.replace(phrase, " " + expansion + " ")

    # Step 1 — Devanagari → English concept expansion
    text = _apply_devanagari_map(text)

    # Step 2 — Romanised transliteration → English concept expansion
    text = _apply_transliteration_map(text.lower())

    # Step 3 — Lowercase and strip extra spaces
    text = re.sub(r'\s+', ' ', text.lower()).strip()

    return text