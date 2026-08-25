"""
Legal Metrology Compliance Checker - OCR Module
Uses PaddleOCR (via RapidOCR ONNX runtime) to extract text and bounding boxes with confidence scores.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Global OCR Engine instance (lazy-loaded for fast startup)
_OCR_ENGINE = None


def get_ocr_engine():
    """Initializes and returns the PaddleOCR / RapidOCR engine singleton."""
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            # Initialize with default English/Multilingual models
            _OCR_ENGINE = RapidOCR()
            logger.info("RapidOCR (PaddleOCR ONNX) engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RapidOCR: {e}")
            raise RuntimeError(f"OCR engine could not be initialized: {e}")
    return _OCR_ENGINE


class OCRResult:
    def __init__(self, raw_lines: List[str], line_details: List[Dict[str, Any]], combined_text: str, avg_confidence: float):
        self.raw_lines = raw_lines
        self.line_details = line_details
        self.combined_text = combined_text
        self.avg_confidence = avg_confidence


def extract_text_from_image(image: np.ndarray) -> OCRResult:
    """
    Extracts text lines and confidence scores from an OpenCV BGR image array.
    """
    engine = get_ocr_engine()
    
    try:
        # RapidOCR accepts numpy BGR image directly
        result, _ = engine(image)
    except Exception as e:
        logger.error(f"Error during OCR execution: {e}")
        return OCRResult(raw_lines=[], line_details=[], combined_text="", avg_confidence=0.0)

    if not result:
        return OCRResult(raw_lines=[], line_details=[], combined_text="", avg_confidence=0.0)

    raw_lines: List[str] = []
    line_details: List[Dict[str, Any]] = []
    total_conf = 0.0

    for item in result:
        # RapidOCR format: [box_coordinates, text_string, confidence_float]
        box = item[0]
        text = str(item[1]).strip()
        score = float(item[2])

        if text:
            raw_lines.append(text)
            line_details.append({
                "text": text,
                "confidence": round(score, 3),
                "box": box
            })
            total_conf += score

    avg_confidence = round(total_conf / len(raw_lines), 3) if raw_lines else 0.0
    combined_text = "\n".join(raw_lines)

    return OCRResult(
        raw_lines=raw_lines,
        line_details=line_details,
        combined_text=combined_text,
        avg_confidence=avg_confidence
    )
