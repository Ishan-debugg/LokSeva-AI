"""Small Marathi phrase-rule regression benchmark (not a general accuracy set)."""

from predict import predict_category
from preprocess import keyword_department_override


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

    if keyword_department_override("काढा") is not None:
        failures.append(("काढा", None, keyword_department_override("काढा")))

    for complaint, expected, predicted in failures:
        print(f"FAIL: {complaint}")
        print(f"  expected={expected!r}, predicted={predicted!r}")

    passed = len(MARATHI_TEST_CASES) - len(failures)
    print(
        f"\nMarathi phrase-rule checks: {passed}/{len(MARATHI_TEST_CASES)} "
        f"({100 * passed / len(MARATHI_TEST_CASES):.1f}%)"
    )
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if run_marathi_benchmark() else 1)
