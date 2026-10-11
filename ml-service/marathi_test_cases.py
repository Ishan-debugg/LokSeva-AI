"""Phrase and ambiguity regression checks (not a general accuracy set)."""

from predict import predict_category
from preprocess import keyword_department_override, preprocess_text


MARATHI_TEST_CASES = [
    ("पाणी येत नाही", "water"),
    ("नळाला पाणी नाही", "water"),
    ("नाले तुंबले आहेत पाणी साचले", "sewage"),
    ("गटार तुंबले रस्त्यावर पाणी आले", "sewage"),
    ("नाल्यामुळे पाणी साचले आहे", "sewage"),
    ("वीज नाही आमच्या भागात", "streetlight"),
    ("दिवे जळत नाहीत रात्री", "streetlight"),
    ("रस्त्यावर खड्डे आहेत", "road"),
    ("कचरा उचलला नाही घंटागाडी आली नाही", "garbage"),
    ("अतिक्रमण काढा रस्त्यावरून", "encroachment"),
    ("बेकायदा बांधकाम होत आहे", "encroachment"),
    ("पाईप फुटला पाणी वाया जात आहे", "water"),
    ("ट्रान्सफॉर्मर खराब झाला वीज नाही", "streetlight"),
    ("वाहतूक कोंडी रोज होते सिग्नल बंद", "road"),
]


def run_marathi_benchmark() -> bool:
    failures = []
    for complaint, expected in MARATHI_TEST_CASES:
        predicted = predict_category(complaint)
        if predicted != expected:
            failures.append((complaint, expected, predicted))

    ambiguity_checks = [
        "काढा",
        "gutter cleaning is requested and garbage should be collected",
        "नाल्यात कचरा साठला असून सर्व कचरा उचलावा",
        "नाला साफ",
        "नाल्याची सफाई",
        "गटाराची सफाई",
        "cleaning of septic tank",
    ]
    for complaint in ambiguity_checks:
        for text in (complaint, preprocess_text(complaint)):
            predicted = keyword_department_override(text)
            if predicted is not None:
                failures.append((complaint, None, predicted))

    for complaint, expected, predicted in failures:
        print(f"FAIL: {complaint}")
        print(f"  expected={expected!r}, predicted={predicted!r}")

    total_checks = len(MARATHI_TEST_CASES) + 2 * len(ambiguity_checks)
    passed = total_checks - len(failures)
    print(
        f"\nPhrase and ambiguity checks: {passed}/{total_checks} "
        f"({100 * passed / total_checks:.1f}%)"
    )
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if run_marathi_benchmark() else 1)
