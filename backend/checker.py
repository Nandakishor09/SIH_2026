"""
Legal Metrology Compliance Checker - 8 Mandatory Declaration Evaluators
Implements distinct detection functions for each of the 8 Legal Metrology declarations.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from models import SingleCheckResult, StatusEnum, OverallStatusEnum
from patterns import (
    COMMODITY_PREFIX_PATTERNS, COMMON_COMMODITY_KEYWORDS,
    MFG_NAME_PATTERNS, COMPANY_SUFFIXES,
    PIN_CODE_PATTERN, INDIAN_STATES_AND_CITIES, ADDRESS_KEYWORDS,
    NET_QTY_PATTERNS, EXCLUDED_QUANTITY_PREFIXES,
    MRP_PATTERNS, CONFIGURABLE_TAX_INCLUSIVE_PATTERNS,
    DATE_DECLARATION_PATTERNS,
    CUSTOMER_CARE_KEYWORDS, PHONE_PATTERNS, EMAIL_PATTERN, CUSTOMER_CARE_PREFIX_PATTERN
)


def _clean_str(s: str) -> str:
    """Normalizes string spaces and characters."""
    return re.sub(r'\s+', ' ', s).strip()


def check_commodity_name(text: str, lines: List[str], min_conf: float = 0.5) -> SingleCheckResult:
    """
    1. Name of Commodity Check
    Identifies the commodity/product name from explicit prefixes or prominent heuristic names.
    """
    # 1. Check explicit declarations
    for line in lines:
        for pat in COMMODITY_PREFIX_PATTERNS:
            m = pat.search(line)
            if m:
                val = _clean_str(m.group(1))
                if len(val) >= 3 and not any(k in val.lower() for k in ["pack", "mrp", "net"]):
                    return SingleCheckResult(
                        requirement_name="Name of commodity",
                        status=StatusEnum.PASS,
                        value=val,
                        evidence=line,
                        confidence=0.95,
                        details="Explicit commodity declaration found."
                    )

    # 2. Heuristic check across lines
    for line in lines:
        cleaned = line.strip()
        line_lower = cleaned.lower()
        
        # Skip legal notices or nutritional tables
        if any(skip in line_lower for skip in ["rules", "ingredient", "nutrition", "store in", "keep away", "mfd by", "mrp"]):
            continue

        for kw in COMMON_COMMODITY_KEYWORDS:
            if kw in line_lower:
                # Return the line containing the commodity descriptor
                return SingleCheckResult(
                    requirement_name="Name of commodity",
                    status=StatusEnum.PASS,
                    value=cleaned,
                    evidence=cleaned,
                    confidence=0.88,
                    details=f"Identified commodity descriptor matching '{kw}'."
                )

    # 3. Fallback: If top lines exist on package that look like a brand/product title (not legal text)
    if lines:
        for line in lines[:3]:
            if len(line) >= 4 and len(line) <= 40 and not any(c in line for c in [":", "@", "₹", "Rs", "1800"]):
                if not any(k in line.lower() for k in ["nutrition", "batch", "date", "weight", "warning"]):
                    return SingleCheckResult(
                        requirement_name="Name of commodity",
                        status=StatusEnum.PASS,
                        value=line.strip(),
                        evidence=line.strip(),
                        confidence=0.75,
                        details="Detected prominent product title."
                    )

    return SingleCheckResult(
        requirement_name="Name of commodity",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Could not reliably detect commodity or product name."
    )


def check_manufacturer_name(text: str, lines: List[str]) -> SingleCheckResult:
    """
    2. Manufacturer Name Check
    Detects manufacturer prefixes like 'Manufactured by', 'Mfg. by', 'Packed by' and extracts the company name.
    """
    for i, line in enumerate(lines):
        for pat in MFG_NAME_PATTERNS:
            m = pat.search(line)
            if m:
                mfg_val = _clean_str(m.group(1))
                if len(mfg_val) >= 3:
                    return SingleCheckResult(
                        requirement_name="Manufacturer name",
                        status=StatusEnum.PASS,
                        value=mfg_val,
                        evidence=line,
                        confidence=0.92,
                        details="Manufacturer declaration detected."
                    )
                # If prefix is on this line and name is on the next line
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if len(next_line) >= 3:
                        return SingleCheckResult(
                            requirement_name="Manufacturer name",
                            status=StatusEnum.PASS,
                            value=next_line,
                            evidence=f"{line} {next_line}",
                            confidence=0.88,
                            details="Manufacturer declaration detected across lines."
                        )

    # Fallback: check for company suffixes near manufacturer keywords
    for line in lines:
        line_lower = line.lower()
        if any(p in line_lower for p in ["mfg", "mfd", "manufactur", "packed by", "pkd by", "marketed by"]):
            for suffix in COMPANY_SUFFIXES:
                if suffix in line_lower:
                    return SingleCheckResult(
                        requirement_name="Manufacturer name",
                        status=StatusEnum.PASS,
                        value=line.strip(),
                        evidence=line.strip(),
                        confidence=0.85,
                        details=f"Detected company entity with suffix '{suffix}'."
                    )

    return SingleCheckResult(
        requirement_name="Manufacturer name",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Manufacturer name declaration not detected."
    )


def check_manufacturer_address(text: str, lines: List[str]) -> SingleCheckResult:
    """
    3. Manufacturer Address Check
    Detects physical location indicators (PIN code, state/city, industrial areas, road/nagar).
    """
    matched_pieces = []
    evidence_lines = []

    # Check 1: 6-digit Indian PIN code
    pin_match = PIN_CODE_PATTERN.search(text)
    if pin_match:
        pin = pin_match.group(1)
        matched_pieces.append(f"PIN: {pin}")
        for l in lines:
            if pin in l:
                evidence_lines.append(l.strip())

    # Check 2: Indian State or City
    text_lower = text.lower()
    for loc in INDIAN_STATES_AND_CITIES:
        if loc in text_lower:
            matched_pieces.append(loc.title())
            for l in lines:
                if loc in l.lower() and l.strip() not in evidence_lines:
                    evidence_lines.append(l.strip())
            break

    # Check 3: Address keywords (Plot, Sector, Road, Nagar, Industrial Area)
    for kw in ADDRESS_KEYWORDS:
        if kw in text_lower:
            matched_pieces.append(kw.title())
            for l in lines:
                if kw in l.lower() and l.strip() not in evidence_lines:
                    evidence_lines.append(l.strip())
            break

    if len(matched_pieces) >= 1 and evidence_lines:
        combined_evidence = " | ".join(evidence_lines[:2])
        return SingleCheckResult(
            requirement_name="Manufacturer address",
            status=StatusEnum.PASS,
            value=", ".join(matched_pieces[:3]),
            evidence=combined_evidence,
            confidence=0.90,
            details="Plausible manufacturer address detected."
        )

    return SingleCheckResult(
        requirement_name="Manufacturer address",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Manufacturer address / locality details not detected."
    )


def check_net_quantity(text: str, lines: List[str]) -> SingleCheckResult:
    """
    4. Net Quantity Check
    Detects declarations such as 'Net Quantity: 500 g', 'Net Wt: 100 g', 'Net Volume: 1 L'.
    Ensures gross weight or nutritional weights are excluded.
    """
    # 1. Look for explicit Net Quantity lines first
    for line in lines:
        line_lower = line.lower()
        if any(exc in line_lower for exc in EXCLUDED_QUANTITY_PREFIXES):
            continue

        m = NET_QTY_PATTERNS[0].search(line)
        if m:
            qty_val = _clean_str(m.group(1))
            return SingleCheckResult(
                requirement_name="Net quantity",
                status=StatusEnum.PASS,
                value=qty_val,
                evidence=line.strip(),
                confidence=0.95,
                details=f"Explicit net quantity declaration detected: {qty_val}"
            )

    # 2. General metric declarations if near 'weight' or isolated measurement
    for line in lines:
        line_lower = line.lower()
        if any(exc in line_lower for exc in EXCLUDED_QUANTITY_PREFIXES):
            continue

        if "net" in line_lower or "qty" in line_lower or "weight" in line_lower or "wt" in line_lower:
            m = NET_QTY_PATTERNS[1].search(line)
            if m:
                qty_val = _clean_str(m.group(1))
                return SingleCheckResult(
                    requirement_name="Net quantity",
                    status=StatusEnum.PASS,
                    value=qty_val,
                    evidence=line.strip(),
                    confidence=0.90,
                    details=f"Net quantity measurement detected: {qty_val}"
                )

    # 3. Fallback standalone metric (e.g. '500g', '1kg', '750ml' on front panel)
    for line in lines:
        line_lower = line.lower()
        if any(exc in line_lower for exc in EXCLUDED_QUANTITY_PREFIXES):
            continue
        m = NET_QTY_PATTERNS[1].search(line)
        if m:
            qty_val = _clean_str(m.group(1))
            # Validate plausible product quantity
            if re.search(r'^\d+(\.\d+)?\s*(g|kg|ml|l|ltr|gm|gms|n|pcs)$', qty_val, re.IGNORECASE):
                return SingleCheckResult(
                    requirement_name="Net quantity",
                    status=StatusEnum.PASS,
                    value=qty_val,
                    evidence=line.strip(),
                    confidence=0.82,
                    details=f"Metric quantity detected: {qty_val}"
                )

    return SingleCheckResult(
        requirement_name="Net quantity",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Net quantity declaration not detected."
    )


def check_mrp(text: str, lines: List[str]) -> Tuple[SingleCheckResult, Optional[str]]:
    """
    5. MRP Check
    Detects MRP / Maximum Retail Price and extracts the numeric price value.
    Returns (SingleCheckResult, raw_mrp_line).
    """
    for line in lines:
        for pat in MRP_PATTERNS:
            m = pat.search(line)
            if m:
                price_str = _clean_str(m.group(1))
                # Add currency symbol formatting if needed
                formatted_price = price_str if "₹" in price_str or "rs" in price_str.lower() else f"₹{price_str}"
                return SingleCheckResult(
                    requirement_name="MRP",
                    status=StatusEnum.PASS,
                    value=formatted_price,
                    evidence=line.strip(),
                    confidence=0.95,
                    details=f"MRP declaration detected: {formatted_price}"
                ), line.strip()

    return SingleCheckResult(
        requirement_name="MRP",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Maximum Retail Price (MRP) not detected."
    ), None


def check_mrp_wording(text: str, lines: List[str], mrp_evidence: Optional[str] = None) -> SingleCheckResult:
    """
    6. MRP Wording / Format Check
    Checks whether the mandatory tax-inclusive wording ('Inclusive of all taxes' or equivalent) is present.
    Uses configurable regexes from patterns.py.
    """
    # 1. Check in the line containing MRP evidence
    if mrp_evidence:
        for pat in CONFIGURABLE_TAX_INCLUSIVE_PATTERNS:
            m = pat.search(mrp_evidence)
            if m:
                return SingleCheckResult(
                    requirement_name="MRP wording/format",
                    status=StatusEnum.PASS,
                    value=m.group(0).strip(),
                    evidence=mrp_evidence,
                    confidence=0.96,
                    details="Mandatory tax-inclusive expression detected with MRP."
                )

    # 2. Check across all OCR lines
    for line in lines:
        for pat in CONFIGURABLE_TAX_INCLUSIVE_PATTERNS:
            m = pat.search(line)
            if m:
                return SingleCheckResult(
                    requirement_name="MRP wording/format",
                    status=StatusEnum.PASS,
                    value=m.group(0).strip(),
                    evidence=line.strip(),
                    confidence=0.92,
                    details="Tax-inclusive declaration detected."
                )

    return SingleCheckResult(
        requirement_name="MRP wording/format",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="⚠️ Mandatory tax-inclusive wording (e.g. 'Inclusive of all taxes') not detected."
    )


def check_expiry(text: str, lines: List[str]) -> SingleCheckResult:
    """
    7. Best Before / Use By / Expiry Check
    Detects shelf life / date of expiry / Best Before declarations.
    """
    for line in lines:
        for pat in DATE_DECLARATION_PATTERNS:
            m = pat.search(line)
            if m:
                date_val = _clean_str(m.group(1) if m.groups() else m.group(0))
                return SingleCheckResult(
                    requirement_name="Best Before / Use By / Expiry",
                    status=StatusEnum.PASS,
                    value=date_val,
                    evidence=line.strip(),
                    confidence=0.94,
                    details="Date / shelf-life validity declaration detected."
                )

    return SingleCheckResult(
        requirement_name="Best Before / Use By / Expiry",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Best Before / Expiry declaration not detected."
    )


def check_customer_care(text: str, lines: List[str]) -> SingleCheckResult:
    """
    8. Customer-Care Details Check
    Detects customer care phrasing, helpline numbers (1800-xxx-xxxx, mobile), or email addresses.
    """
    detected_contacts = []
    evidence_lines = []

    # 1. Search for Customer Care Phrasing
    has_cc_keyword = False
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in CUSTOMER_CARE_KEYWORDS):
            has_cc_keyword = True
            evidence_lines.append(line.strip())

    # 2. Search for Phone Numbers
    for pat in PHONE_PATTERNS:
        matches = pat.findall(text)
        for ph in matches:
            ph_clean = _clean_str(ph)
            if ph_clean not in detected_contacts:
                detected_contacts.append(ph_clean)
                for l in lines:
                    if ph_clean in l and l.strip() not in evidence_lines:
                        evidence_lines.append(l.strip())

    # 3. Search for Email Addresses
    emails = EMAIL_PATTERN.findall(text)
    for em in emails:
        if em not in detected_contacts:
            detected_contacts.append(em)
            for l in lines:
                if em in l and l.strip() not in evidence_lines:
                    evidence_lines.append(l.strip())

    if detected_contacts or (has_cc_keyword and evidence_lines):
        val_str = ", ".join(detected_contacts) if detected_contacts else "Customer Care Desk"
        combined_evidence = " | ".join(evidence_lines[:2])
        return SingleCheckResult(
            requirement_name="Customer-care details",
            status=StatusEnum.PASS,
            value=val_str,
            evidence=combined_evidence,
            confidence=0.93,
            details="Customer grievance / consumer care contact information detected."
        )

    return SingleCheckResult(
        requirement_name="Customer-care details",
        status=StatusEnum.FAIL,
        value=None,
        evidence=None,
        confidence=0.0,
        details="Customer care phone number, email, or contact details not detected."
    )


def evaluate_compliance(combined_text: str, combined_lines: List[str], avg_confidence: float) -> Dict[str, Any]:
    """
    Runs all 8 detection functions on the combined front + back OCR text and computes overall status.
    """
    # 1. Commodity Name
    res_commodity = check_commodity_name(combined_text, combined_lines)

    # 2. Manufacturer Name
    res_mfg_name = check_manufacturer_name(combined_text, combined_lines)

    # 3. Manufacturer Address
    res_mfg_address = check_manufacturer_address(combined_text, combined_lines)

    # 4. Net Quantity
    res_net_qty = check_net_quantity(combined_text, combined_lines)

    # 5. MRP
    res_mrp, mrp_line = check_mrp(combined_text, combined_lines)

    # 6. MRP Wording
    res_mrp_wording = check_mrp_wording(combined_text, combined_lines, mrp_line)

    # 7. Expiry / Best Before
    res_expiry = check_expiry(combined_text, combined_lines)

    # 8. Customer Care
    res_customer_care = check_customer_care(combined_text, combined_lines)

    checks = {
        "commodity_name": res_commodity,
        "manufacturer_name": res_mfg_name,
        "manufacturer_address": res_mfg_address,
        "net_quantity": res_net_qty,
        "mrp": res_mrp,
        "mrp_wording": res_mrp_wording,
        "expiry": res_expiry,
        "customer_care": res_customer_care
    }

    # Handle UNVERIFIED status if OCR confidence is low on failed checks
    if avg_confidence < 0.48:
        for key, res in checks.items():
            if res.status == StatusEnum.FAIL:
                res.status = StatusEnum.UNVERIFIED
                res.details = f"Unverified due to low OCR confidence ({avg_confidence:.2f}). Please provide a clearer image."

    passed = sum(1 for c in checks.values() if c.status == StatusEnum.PASS)
    failed = sum(1 for c in checks.values() if c.status == StatusEnum.FAIL)
    unverified = sum(1 for c in checks.values() if c.status == StatusEnum.UNVERIFIED)

    if unverified > 0:
        overall_status = OverallStatusEnum.NEEDS_REVIEW
    elif failed == 0 and passed == 8:
        overall_status = OverallStatusEnum.COMPLIANT
    else:
        overall_status = OverallStatusEnum.FLAGGED

    return {
        "overall_status": overall_status,
        "passed": passed,
        "failed": failed,
        "unverified": unverified,
        "total_checks": 8,
        "checks": checks
    }
