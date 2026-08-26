"""
Legal Metrology Compliance Checker - FastAPI Main Server
Provides /check endpoint, sample product feeds, and hosts the frontend UI.
"""

import os
import io
import shutil
import logging
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from models import (
    ComplianceResponse, SingleCheckResult, ImageQualityResult,
    StatusEnum, OverallStatusEnum
)
from image_processing import decode_image_bytes, check_image_quality, preprocess_for_ocr
from ocr import extract_text_from_image
from checker import evaluate_compliance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LegalMetrologyApp")

app = FastAPI(
    title="Legal Metrology Product Compliance Checker",
    description="Automated OCR and rule-based verification for 8 mandatory Legal Metrology declarations on packaged goods.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve project directories
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SAMPLES_DIR = BASE_DIR / "samples"


@app.post("/check", response_model=ComplianceResponse)
async def check_compliance(
    front_image: UploadFile = File(..., description="Image of the front side of the packaged product"),
    back_image: UploadFile = File(..., description="Image of the back side of the packaged product")
):
    """
    Main compliance checker endpoint.
    Accepts front and back images, checks quality, executes PaddleOCR,
    evaluates the 8 Legal Metrology declarations, and returns structured results.
    """
    if not front_image or not back_image:
        raise HTTPException(
            status_code=400,
            detail="Please upload both the front and back images."
        )

    # 1. Read uploaded image bytes
    try:
        front_bytes = await front_image.read()
        back_bytes = await back_image.read()
        
        if len(front_bytes) == 0 or len(back_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Please upload both the front and back images."
            )

        img_front = decode_image_bytes(front_bytes)
        img_back = decode_image_bytes(back_bytes)
    except Exception as e:
        logger.error(f"Image decode failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to read image files: {str(e)}")

    # 2. Check image quality for both sides
    quality_front = check_image_quality(img_front, "Front Image")
    quality_back = check_image_quality(img_back, "Back Image")

    quality_reports = {
        "front": quality_front,
        "back": quality_back
    }

    # If any image is critically unreadable (e.g. extreme blur, severe darkness)
    if not quality_front.is_valid or not quality_back.is_valid:
        error_msgs = []
        if not quality_front.is_valid and quality_front.message:
            error_msgs.append(quality_front.message)
        if not quality_back.is_valid and quality_back.message:
            error_msgs.append(quality_back.message)

        # Return a structured response flagging UNVERIFIED / NEEDS REVIEW with quality alerts
        empty_checks = {
            k: SingleCheckResult(
                requirement_name=req_name,
                status=StatusEnum.UNVERIFIED,
                value=None,
                evidence=None,
                confidence=0.0,
                details="Analysis aborted due to insufficient image quality."
            )
            for k, req_name in [
                ("commodity_name", "Name of commodity"),
                ("manufacturer_name", "Manufacturer name"),
                ("manufacturer_address", "Manufacturer address"),
                ("net_quantity", "Net quantity"),
                ("mrp", "MRP"),
                ("mrp_wording", "MRP wording/format"),
                ("expiry", "Best Before / Use By / Expiry"),
                ("customer_care", "Customer-care details")
            ]
        }

        return ComplianceResponse(
            overall_status=OverallStatusEnum.NEEDS_REVIEW,
            passed=0,
            failed=0,
            unverified=8,
            checks=empty_checks,
            quality_report=quality_reports,
            raw_ocr_front=[],
            raw_ocr_back=[],
            combined_text="",
            disclaimer="⚠️ Image quality is insufficient for reliable analysis. Please upload a clearer image."
        )

    # 3. Preprocess images for OCR
    preprocessed_front = preprocess_for_ocr(img_front)
    preprocessed_back = preprocess_for_ocr(img_back)

    # 4. Run OCR extraction
    ocr_front = extract_text_from_image(preprocessed_front)
    ocr_back = extract_text_from_image(preprocessed_back)

    # 5. Combine front and back OCR results
    combined_lines = ocr_front.raw_lines + ocr_back.raw_lines
    combined_text = (ocr_front.combined_text + "\n" + ocr_back.combined_text).strip()
    
    # Calculate overall OCR confidence
    all_confs = [item["confidence"] for item in (ocr_front.line_details + ocr_back.line_details)]
    avg_confidence = sum(all_confs) / len(all_confs) if all_confs else 0.0

    # 6. Evaluate all 8 Legal Metrology requirements
    evaluation = evaluate_compliance(combined_text, combined_lines, avg_confidence)

    return ComplianceResponse(
        overall_status=evaluation["overall_status"],
        passed=evaluation["passed"],
        failed=evaluation["failed"],
        unverified=evaluation["unverified"],
        checks=evaluation["checks"],
        quality_report=quality_reports,
        raw_ocr_front=ocr_front.raw_lines,
        raw_ocr_back=ocr_back.raw_lines,
        combined_text=combined_text
    )


@app.get("/api/samples")
async def list_sample_packages():
    """
    Returns available demo packaged products for 1-click testing.
    """
    return [
        {
            "id": "compliant_biscuits",
            "name": "ABC Delight Biscuits (100% Compliant)",
            "description": "Contains all 8 mandatory declarations including tax-inclusive MRP wording and customer care helpline.",
            "expected_status": "COMPLIANT",
            "front_file": "/api/sample-image/sample_compliant_front.jpg",
            "back_file": "/api/sample-image/sample_compliant_back.jpg"
        },
        {
            "id": "flagged_missing_mrp_wording",
            "name": "Crunchy Wafers (Missing MRP Tax Wording)",
            "description": "Missing the mandatory '(Inclusive of all taxes)' declaration under Legal Metrology rules.",
            "expected_status": "FLAGGED",
            "front_file": "/api/sample-image/sample_flagged_mrp_front.jpg",
            "back_file": "/api/sample-image/sample_flagged_mrp_back.jpg"
        },
        {
            "id": "flagged_missing_customer_care",
            "name": "Golden Snack Mix (Missing Customer Care)",
            "description": "Missing consumer grievance redressal / customer care helpline contact details.",
            "expected_status": "FLAGGED",
            "front_file": "/api/sample-image/sample_flagged_care_front.jpg",
            "back_file": "/api/sample-image/sample_flagged_care_back.jpg"
        },
        {
            "id": "blurry_unverified",
            "name": "Blurry Package Photo (Image Quality Test)",
            "description": "Simulates out-of-focus camera capture to test automatic image quality defense.",
            "expected_status": "NEEDS REVIEW",
            "front_file": "/api/sample-image/sample_blurry_front.jpg",
            "back_file": "/api/sample-image/sample_compliant_back.jpg"
        }
    ]


@app.get("/api/sample-image/{filename}")
async def get_sample_image(filename: str):
    """Serves sample image files."""
    file_path = SAMPLES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(file_path)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serves standard browser favicon."""
    ico_path = FRONTEND_DIR / "favicon.ico"
    if ico_path.exists():
        return FileResponse(ico_path, media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")


# Mount frontend static directory
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
