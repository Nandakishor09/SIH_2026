"""
Automated Test Suite for Legal Metrology Compliance Checker
Tests OCR extraction, 8 compliance checks, and API responses for sample packages.
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

import cv2
from image_processing import decode_image_bytes, check_image_quality, preprocess_for_ocr
from ocr import extract_text_from_image
from checker import evaluate_compliance
from models import StatusEnum, OverallStatusEnum


def run_tests():
    samples_dir = Path(__file__).resolve().parent / "samples"
    print("=" * 70)
    print("STARTING LEGAL METROLOGY OCR & COMPLIANCE TESTS")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: Compliant Package (Front + Back)
    # -------------------------------------------------------------
    print("\n--- [TEST 1] Testing Compliant Biscuit Package ---")
    img_front = cv2.imread(str(samples_dir / "sample_compliant_front.jpg"))
    img_back = cv2.imread(str(samples_dir / "sample_compliant_back.jpg"))
    
    assert img_front is not None, "Failed to read front image"
    assert img_back is not None, "Failed to read back image"

    q_front = check_image_quality(img_front, "Front")
    q_back = check_image_quality(img_back, "Back")
    assert q_front.is_valid, f"Front image quality failed: {q_front.issues}"
    assert q_back.is_valid, f"Back image quality failed: {q_back.issues}"

    ocr_front = extract_text_from_image(preprocess_for_ocr(img_front))
    ocr_back = extract_text_from_image(preprocess_for_ocr(img_back))

    combined_lines = ocr_front.raw_lines + ocr_back.raw_lines
    combined_text = (ocr_front.combined_text + "\n" + ocr_back.combined_text).strip()
    avg_conf = (ocr_front.avg_confidence + ocr_back.avg_confidence) / 2.0

    print(f"Front OCR extracted {len(ocr_front.raw_lines)} lines.")
    print(f"Back OCR extracted {len(ocr_back.raw_lines)} lines.")

    res = evaluate_compliance(combined_text, combined_lines, avg_conf)
    print(f"Overall Status: {res['overall_status'].value} ({res['passed']}/8 passed)")
    for k, c in res['checks'].items():
        print(f"  * {c.requirement_name:32}: [{c.status.value}] val='{c.value}'")

    assert res['overall_status'] == OverallStatusEnum.COMPLIANT, f"Expected COMPLIANT but got {res['overall_status']}"
    assert res['passed'] == 8, f"Expected 8 passed but got {res['passed']}"
    print("TEST 1 PASSED: Compliant package verified successfully!")

    # -------------------------------------------------------------
    # TEST 2: Flagged Package - Missing MRP Tax Wording
    # -------------------------------------------------------------
    print("\n--- [TEST 2] Testing Flagged Package (Missing MRP Tax Wording) ---")
    img_f2 = cv2.imread(str(samples_dir / "sample_flagged_mrp_front.jpg"))
    img_b2 = cv2.imread(str(samples_dir / "sample_flagged_mrp_back.jpg"))

    ocr_f2 = extract_text_from_image(preprocess_for_ocr(img_f2))
    ocr_b2 = extract_text_from_image(preprocess_for_ocr(img_b2))

    res2 = evaluate_compliance(
        ocr_f2.combined_text + "\n" + ocr_b2.combined_text,
        ocr_f2.raw_lines + ocr_b2.raw_lines,
        (ocr_f2.avg_confidence + ocr_b2.avg_confidence) / 2.0
    )

    print(f"Overall Status: {res2['overall_status'].value} ({res2['passed']}/8 passed)")
    print(f"MRP Status: {res2['checks']['mrp'].status.value} (Value: {res2['checks']['mrp'].value})")
    print(f"MRP Wording Status: {res2['checks']['mrp_wording'].status.value}")

    assert res2['checks']['mrp'].status == StatusEnum.PASS, "Expected MRP to pass"
    assert res2['checks']['mrp_wording'].status == StatusEnum.FAIL, "Expected MRP Wording to fail"
    assert res2['overall_status'] == OverallStatusEnum.FLAGGED, f"Expected FLAGGED but got {res2['overall_status']}"
    print("TEST 2 PASSED: Missing MRP wording correctly flagged!")

    # -------------------------------------------------------------
    # TEST 3: Flagged Package - Missing Customer Care
    # -------------------------------------------------------------
    print("\n--- [TEST 3] Testing Flagged Package (Missing Customer Care) ---")
    img_f3 = cv2.imread(str(samples_dir / "sample_flagged_care_front.jpg"))
    img_b3 = cv2.imread(str(samples_dir / "sample_flagged_care_back.jpg"))

    ocr_f3 = extract_text_from_image(preprocess_for_ocr(img_f3))
    ocr_b3 = extract_text_from_image(preprocess_for_ocr(img_b3))

    res3 = evaluate_compliance(
        ocr_f3.combined_text + "\n" + ocr_b3.combined_text,
        ocr_f3.raw_lines + ocr_b3.raw_lines,
        (ocr_f3.avg_confidence + ocr_b3.avg_confidence) / 2.0
    )

    print(f"Overall Status: {res3['overall_status'].value} ({res3['passed']}/8 passed)")
    print(f"Customer Care Status: {res3['checks']['customer_care'].status.value}")

    assert res3['checks']['customer_care'].status == StatusEnum.FAIL, "Expected Customer Care to fail"
    assert res3['overall_status'] == OverallStatusEnum.FLAGGED, f"Expected FLAGGED but got {res3['overall_status']}"
    print("TEST 3 PASSED: Missing customer care correctly flagged!")

    # -------------------------------------------------------------
    # TEST 4: Blurry Image Quality Defense
    # -------------------------------------------------------------
    print("\n--- [TEST 4] Testing Blurry Image Quality Defense ---")
    img_blur = cv2.imread(str(samples_dir / "sample_blurry_front.jpg"))
    q_blur = check_image_quality(img_blur, "Front Image")
    print(f"Blur check is_valid={q_blur.is_valid}, issues={q_blur.issues}")
    assert not q_blur.is_valid, "Expected blurry image to fail quality check"
    print("TEST 4 PASSED: Low quality blurry image successfully intercepted!")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY (4/4)!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
