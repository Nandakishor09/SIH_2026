"""
Legal Metrology Compliance Checker - Pydantic Data Models
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class StatusEnum(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"


class OverallStatusEnum(str, Enum):
    COMPLIANT = "COMPLIANT"
    FLAGGED = "FLAGGED"
    NEEDS_REVIEW = "NEEDS REVIEW"


class SingleCheckResult(BaseModel):
    requirement_name: str = Field(..., description="Display title of the requirement")
    status: StatusEnum = Field(..., description="PASS, FAIL, or UNVERIFIED")
    value: Optional[str] = Field(None, description="Extracted key information value if detected")
    evidence: Optional[str] = Field(None, description="Exact OCR line or text snippet matching the requirement")
    confidence: float = Field(0.0, description="Confidence score between 0.0 and 1.0")
    details: Optional[str] = Field(None, description="Human-readable explanation of the check outcome")


class ImageQualityResult(BaseModel):
    is_valid: bool = True
    blur_score: float = 0.0
    brightness: float = 0.0
    issues: List[str] = []
    message: Optional[str] = None


class ComplianceResponse(BaseModel):
    overall_status: OverallStatusEnum
    passed: int
    failed: int
    unverified: int
    total_checks: int = 8
    checks: Dict[str, SingleCheckResult]
    quality_report: Dict[str, ImageQualityResult]
    raw_ocr_front: List[str] = []
    raw_ocr_back: List[str] = []
    combined_text: str = ""
    disclaimer: str = (
        "This tool provides an AI-assisted preliminary compliance screening based on detected packaging declarations. "
        "It does not constitute an official Legal Metrology certificate or formal legal advice."
    )
