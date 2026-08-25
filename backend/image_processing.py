"""
Legal Metrology Compliance Checker - Image Processing & Quality Assessment
Uses OpenCV to evaluate image quality (blur, darkness, brightness, glare, resolution)
and preprocess package images for optimal OCR detection.
"""

import cv2
import numpy as np
from typing import Tuple, List, Dict
from models import ImageQualityResult


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Decodes raw uploaded image bytes into an OpenCV BGR numpy array."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes. Unsupported or corrupted format.")
    return img


def check_image_quality(image: np.ndarray, image_label: str = "Image") -> ImageQualityResult:
    """
    Evaluates image quality metrics to determine if the photo is usable for OCR.
    Checks:
    - Resolution / Dimensions
    - Blur (Laplacian variance)
    - Excessive darkness or excessive brightness (Mean luminance)
    - Severe glare / Over-exposure hotspot
    """
    h, w = image.shape[:2]
    issues: List[str] = []
    
    # 1. Resolution Check
    if w < 180 or h < 180 or (w * h) < 40000:
        issues.append(f"Very low resolution ({w}x{h} px). Text may be unreadable.")

    # Convert to grayscale for metric calculations
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Blur Check using Laplacian Variance
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if blur_score < 25.0:
        issues.append(f"Image is significantly blurred (Sharpness score: {blur_score:.1f} < 25.0).")

    # 3. Brightness / Darkness Check
    brightness = float(np.mean(gray))
    if brightness < 20.0:
        issues.append(f"Image is excessively dark (Average brightness: {brightness:.1f}/255).")
    elif brightness > 248.0:
        issues.append(f"Image is excessively overexposed (Average brightness: {brightness:.1f}/255).")

    # 4. Glare Check (severe localized blowout where text is erased)
    # Severe glare is characterized by almost 100% white saturated pixels (> 253) covering more than 40% of the image
    glare_mask = gray >= 253
    glare_pct = float(np.sum(glare_mask) / (h * w)) * 100.0
    if glare_pct > 40.0:
        issues.append(f"Severe flash glare detected ({glare_pct:.1f}% washed out area).")

    is_valid = len(issues) == 0
    message = None
    if not is_valid:
        message = f"⚠️ {image_label} quality is insufficient for reliable analysis: " + "; ".join(issues)

    return ImageQualityResult(
        is_valid=is_valid,
        blur_score=round(blur_score, 2),
        brightness=round(brightness, 2),
        issues=issues,
        message=message
    )


def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Applies image preprocessing tailored for packaged product OCR:
    - Optimal scaling
    - Contrast Limited Adaptive Histogram Equalization (CLAHE)
    """
    h, w = image.shape[:2]

    # Resize if very large (downscale for speed) or very small (upscale for legibility)
    target_img = image.copy()
    max_dim = max(h, w)
    if max_dim > 2000:
        scale = 2000.0 / max_dim
        target_img = cv2.resize(target_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    elif max_dim < 800:
        scale = 800.0 / max_dim
        target_img = cv2.resize(target_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # Convert to LAB to equalize luminance without color distortion
    lab = cv2.cvtColor(target_img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    merged_lab = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

    return enhanced_bgr
