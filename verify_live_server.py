"""
Live Server Integration Verification Script
Tests the running FastAPI application on http://127.0.0.1:8000 across all endpoints.
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import urllib.request
import urllib.parse
import urllib.error
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


def test_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"Expected 200 for {endpoint}, got {resp.status}"
        return resp.read()


def test_multipart_check(front_filename: str, back_filename: str):
    boundary = "----WebKitFormBoundaryLegalMetrologyChecker"
    body = bytearray()

    # Front Image
    with open(SAMPLES_DIR / front_filename, "rb") as f:
        front_data = f.read()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="front_image"; filename="{front_filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(front_data)
    body.extend(b"\r\n")

    # Back Image
    with open(SAMPLES_DIR / back_filename, "rb") as f:
        back_data = f.read()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="back_image"; filename="{back_filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(back_data)
    body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{BASE_URL}/check",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        return json.loads(resp.read().decode("utf-8"))


def run_live_verification():
    print("=================================================================")
    print("  VERIFYING LIVE FASTAPI SERVER (http://127.0.0.1:8000)          ")
    print("=================================================================")

    # 1. Verify Frontend Static Files
    html = test_get("/").decode("utf-8")
    assert "Legal Metrology Compliance Checker" in html, "Header not in index.html"
    assert "Upload the front and back of a packaged product" in html, "Subtitle not in index.html"
    assert "compliance-table" in html, "Table not in index.html"
    assert 'rel="icon" type="image/svg+xml" href="favicon.svg"' in html, "Favicon SVG tag missing in index.html"
    print("[PASS] 1. GET / (Frontend HTML UI loaded successfully with Favicon tags)")

    css = test_get("/styles.css").decode("utf-8")
    assert "--bg-main" in css, "CSS variables missing"
    print("[PASS] 2. GET /styles.css (Glassmorphic stylesheet loaded)")

    js = test_get("/app.js").decode("utf-8")
    assert "DOMContentLoaded" in js, "JS file invalid"
    print("[PASS] 3. GET /app.js (Frontend controller script loaded)")

    fav_ico = test_get("/favicon.ico")
    assert len(fav_ico) > 0, "Favicon .ico is empty"
    print("[PASS] 3a. GET /favicon.ico (Multi-res browser icon served)")

    fav_svg = test_get("/favicon.svg")
    assert b"<svg" in fav_svg, "Favicon SVG invalid"
    print("[PASS] 3b. GET /favicon.svg (Scalable vector favicon served)")

    # 2. Verify Sample Catalog API
    samples_raw = test_get("/api/samples").decode("utf-8")
    samples = json.loads(samples_raw)
    assert len(samples) == 4, f"Expected 4 sample packages, got {len(samples)}"
    print(f"[PASS] 4. GET /api/samples ({len(samples)} demo products listed)")

    # 3. Verify POST /check with Compliant Package
    print("\n--- Testing Compliant Product (Front + Back) ---")
    res_compliant = test_multipart_check("sample_compliant_front.jpg", "sample_compliant_back.jpg")
    print(f"Status: {res_compliant['overall_status']}, Passed: {res_compliant['passed']}/8")
    assert res_compliant['overall_status'] == "COMPLIANT", f"Expected COMPLIANT, got {res_compliant['overall_status']}"
    assert res_compliant['passed'] == 8, "Expected 8 passed"
    print("[PASS] 5. POST /check [COMPLIANT] verified (8/8 checks passed)")

    # 4. Verify POST /check with Flagged Package (Missing MRP Tax Wording)
    print("\n--- Testing Flagged Product (Missing MRP Tax Wording) ---")
    res_flagged_mrp = test_multipart_check("sample_flagged_mrp_front.jpg", "sample_flagged_mrp_back.jpg")
    print(f"Status: {res_flagged_mrp['overall_status']}, Passed: {res_flagged_mrp['passed']}/8")
    assert res_flagged_mrp['overall_status'] == "FLAGGED", f"Expected FLAGGED, got {res_flagged_mrp['overall_status']}"
    assert res_flagged_mrp['checks']['mrp']['status'] == "PASS"
    assert res_flagged_mrp['checks']['mrp_wording']['status'] == "FAIL"
    print("[PASS] 6. POST /check [FLAGGED - Missing MRP Tax Wording] verified")

    # 5. Verify POST /check with Flagged Package (Missing Customer Care)
    print("\n--- Testing Flagged Product (Missing Customer Care) ---")
    res_flagged_care = test_multipart_check("sample_flagged_care_front.jpg", "sample_flagged_care_back.jpg")
    print(f"Status: {res_flagged_care['overall_status']}, Passed: {res_flagged_care['passed']}/8")
    assert res_flagged_care['overall_status'] == "FLAGGED", f"Expected FLAGGED, got {res_flagged_care['overall_status']}"
    assert res_flagged_care['checks']['customer_care']['status'] == "FAIL"
    print("[PASS] 7. POST /check [FLAGGED - Missing Customer Care] verified")

    # 6. Verify POST /check with Blurry Image Quality Defense
    print("\n--- Testing Blurry Image Interceptor ---")
    res_blurry = test_multipart_check("sample_blurry_front.jpg", "sample_compliant_back.jpg")
    print(f"Status: {res_blurry['overall_status']}, Unverified: {res_blurry['unverified']}/8")
    assert res_blurry['overall_status'] == "NEEDS REVIEW"
    assert res_blurry['unverified'] == 8
    print("[PASS] 8. POST /check [Blurry Quality Defense] verified")

    print("\n=================================================================")
    print("  ALL 8 LIVE ENDPOINT VERIFICATION TESTS PASSED (100%)           ")
    print("=================================================================")


if __name__ == "__main__":
    run_live_verification()
