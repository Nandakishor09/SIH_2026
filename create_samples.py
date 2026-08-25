"""
Sample Package Image Generator
Creates realistic synthetic packaged product images for testing all 8 Legal Metrology requirements,
flags, and image quality defenses.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def draw_styled_package(
    filename: str,
    bg_gradient: tuple,
    title_text: str,
    subtitle_text: str,
    lines_of_text: list,
    is_front: bool = False,
    is_blurry: bool = False
):
    width, height = 750, 950
    # Create canvas
    img = Image.new("RGB", (width, height), bg_gradient[0])
    draw = ImageDraw.Draw(img)

    # Draw subtle gradient background
    for y in range(height):
        r = int(bg_gradient[0][0] + (bg_gradient[1][0] - bg_gradient[0][0]) * (y / height))
        g = int(bg_gradient[0][1] + (bg_gradient[1][1] - bg_gradient[0][1]) * (y / height))
        b = int(bg_gradient[0][2] + (bg_gradient[1][2] - bg_gradient[0][2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Outer packaging border / foil edge
    draw.rectangle([15, 15, width - 15, height - 15], outline=(220, 220, 230), width=4)
    draw.rectangle([25, 25, width - 25, height - 25], outline=(170, 170, 180), width=1)

    # Font setup
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_subtitle = ImageFont.truetype("arial.ttf", 22)
        font_body = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_small = ImageFont.load_default()

    card_bg = (248, 249, 250)

    if is_front:
        # Top banner / Brand Header
        draw.rectangle([35, 45, width - 35, 120], fill=(20, 20, 25))
        draw.text((width // 2, 80), "PREMIUM QUALITY FOODS", fill=(255, 215, 0), font=font_subtitle, anchor="mm")

        # Main Product Title Card
        draw.rounded_rectangle([50, 180, width - 50, 360], radius=15, fill=card_bg, outline=(220, 38, 38), width=3)
        draw.text((width // 2, 235), title_text, fill=(185, 28, 28), font=font_title, anchor="mm")
        draw.text((width // 2, 290), subtitle_text, fill=(30, 41, 59), font=font_subtitle, anchor="mm")

        # Visual illustration block
        draw.rounded_rectangle([70, 400, width - 70, 720], radius=12, fill=(235, 240, 245), outline=(203, 213, 225), width=2)
        draw.ellipse([width // 2 - 100, 460, width // 2 + 100, 660], fill=(218, 225, 235), outline=(148, 163, 184), width=3)
        draw.text((width // 2, 560), "★ 100% VEGETARIAN ★", fill=(22, 101, 52), font=font_bold, anchor="mm")

        # Front panel declarations (Net Quantity & Highlight)
        draw.rounded_rectangle([60, 760, width - 60, 880], radius=10, fill=card_bg, outline=(15, 23, 42), width=2)
        for idx, line in enumerate(lines_of_text):
            draw.text((width // 2, 800 + idx * 35), line, fill=(15, 23, 42), font=font_bold, anchor="mm")

    else:
        # Back panel: Legal Declarations & Regulatory Information Box
        draw.rectangle([35, 40, width - 35, 95], fill=(30, 41, 59))
        draw.text((width // 2, 68), "MANDATORY CONSUMER DECLARATIONS", fill=(248, 250, 252), font=font_bold, anchor="mm")

        # Main Info Box
        box_top = 115
        draw.rounded_rectangle([45, box_top, width - 45, height - 60], radius=8, fill=card_bg, outline=(51, 65, 85), width=2)

        cur_y = box_top + 25
        for item in lines_of_text:
            if item.startswith("HEADER:"):
                hdr = item.replace("HEADER:", "").strip()
                draw.rectangle([55, cur_y - 5, width - 55, cur_y + 25], fill=(230, 235, 242))
                draw.text((65, cur_y), hdr, fill=(30, 41, 59), font=font_bold)
                cur_y += 38
            elif item.startswith("DIVIDER"):
                draw.line([(55, cur_y), (width - 55, cur_y)], fill=(203, 213, 225), width=1)
                cur_y += 15
            else:
                # Regular text line
                draw.text((65, cur_y), item, fill=(15, 23, 42), font=font_body)
                cur_y += 28

        # Simulated Barcode at bottom
        barcode_y = height - 130
        draw.rectangle([width - 240, barcode_y, width - 65, barcode_y + 55], fill=card_bg, outline=(0, 0, 0), width=1)
        for bx in range(width - 230, width - 75, 4):
            bar_w = 2 if (bx % 3 == 0) else 1
            draw.line([(bx, barcode_y + 5), (bx, barcode_y + 40)], fill=(0, 0, 0), width=bar_w)
        draw.text((width - 150, barcode_y + 42), "8 901030 001234", fill=(0, 0, 0), font=font_small, anchor="mm")

    # Apply severe blur if requested
    if is_blurry:
        img = img.filter(ImageFilter.GaussianBlur(radius=16.0))

    dest_path = SAMPLES_DIR / filename
    img.save(dest_path, "JPEG", quality=92)
    print(f"Generated sample image: {dest_path}")


def generate_all_samples():
    print("Generating synthetic sample package images...")

    # 1. Compliant Sample (All 8 declarations present)
    draw_styled_package(
        filename="sample_compliant_front.jpg",
        bg_gradient=((245, 235, 235), (240, 220, 220)),
        title_text="ABC DELIGHT BISCUITS",
        subtitle_text="Crispy Butter Cookies with Choco Cream",
        lines_of_text=[
            "Commodity: ABC Biscuits",
            "Net Quantity: 200 g"
        ],
        is_front=True
    )

    draw_styled_package(
        filename="sample_compliant_back.jpg",
        bg_gradient=((235, 240, 245), (230, 235, 240)),
        title_text="",
        subtitle_text="",
        lines_of_text=[
            "HEADER: PRODUCT & MANUFACTURING DETAILS",
            "Name of Commodity: ABC Biscuits",
            "Manufactured by: ABC Foods Pvt Ltd",
            "Address: Plot 45, Phase 2, GIDC Industrial Estate, Ahmedabad - 380015, Gujarat",
            "DIVIDER",
            "HEADER: WEIGHT & PRICING (LEGAL METROLOGY)",
            "Net Quantity: 200 g",
            "MRP: Rs. 40.00 (Inclusive of all taxes)",
            "DIVIDER",
            "HEADER: DATES & STORAGE",
            "Best Before 6 Months From Packaging",
            "Date of Packaging: 15/05/2026",
            "DIVIDER",
            "HEADER: CONSUMER GRIEVANCE & SUPPORT",
            "Customer Care: 1800-123-4567",
            "Email: care@abcfoods.com",
            "Reach us at: ABC Foods Consumer Redressal Cell, Ahmedabad"
        ],
        is_front=False
    )

    # 2. Flagged Sample: Missing MRP Tax Wording (Has MRP but lacks "Inclusive of all taxes")
    draw_styled_package(
        filename="sample_flagged_mrp_front.jpg",
        bg_gradient=((245, 240, 200), (240, 230, 180)),
        title_text="CRUNCHY POTATO WAFERS",
        subtitle_text="Classic Salted Potato Chips",
        lines_of_text=[
            "Commodity: Potato Wafers",
            "Net Weight: 100 g"
        ],
        is_front=True
    )

    draw_styled_package(
        filename="sample_flagged_mrp_back.jpg",
        bg_gradient=((235, 240, 245), (230, 235, 240)),
        title_text="",
        subtitle_text="",
        lines_of_text=[
            "HEADER: PRODUCT INFORMATION",
            "Name of Commodity: Potato Wafers",
            "Manufactured by: Crispy Snacks India Pvt Ltd",
            "Address: Sector 18, Udyog Vihar, Gurugram - 122015, Haryana",
            "DIVIDER",
            "HEADER: WEIGHT & PRICE",
            "Net Quantity: 100 g",
            "MRP: Rs. 30.00",  # MISSING "(Inclusive of all taxes)" !
            "DIVIDER",
            "HEADER: SHELF LIFE",
            "Best Before: 12/2026",
            "DIVIDER",
            "HEADER: CONSUMER SERVICE",
            "Customer Care Helpline: 1800-222-3344",
            "Email: feedback@crispysnacks.in"
        ],
        is_front=False
    )

    # 3. Flagged Sample: Missing Customer Care (No helpline/phone/email/desk)
    draw_styled_package(
        filename="sample_flagged_care_front.jpg",
        bg_gradient=((230, 235, 250), (220, 225, 245)),
        title_text="GOLDEN SNACK MIX",
        subtitle_text="Authentic Indian Spiced Namkeen",
        lines_of_text=[
            "Commodity: Namkeen Mix",
            "Net Quantity: 150 g"
        ],
        is_front=True
    )

    draw_styled_package(
        filename="sample_flagged_care_back.jpg",
        bg_gradient=((235, 240, 245), (230, 235, 240)),
        title_text="",
        subtitle_text="",
        lines_of_text=[
            "HEADER: PRODUCT DETAILS",
            "Name of Commodity: Namkeen Mix",
            "Manufactured by: Royal Foods & Spices Ltd",
            "Address: 12 Anna Salai, Guindy, Chennai - 600032, Tamil Nadu",
            "DIVIDER",
            "HEADER: WEIGHT & PRICING",
            "Net Quantity: 150 g",
            "MRP: Rs. 50.00 (Inclusive of all taxes)",
            "DIVIDER",
            "HEADER: EXPIRY DETAILS",
            "Best Before 9 Months From Packaging",
            "Date of Mfg: 01/06/2026"
            # MISSING CUSTOMER CARE HELPLINE / EMAIL !
        ],
        is_front=False
    )

    # 4. Blurry Image Test
    draw_styled_package(
        filename="sample_blurry_front.jpg",
        bg_gradient=((245, 235, 235), (240, 220, 220)),
        title_text="ABC DELIGHT BISCUITS",
        subtitle_text="Crispy Butter Cookies",
        lines_of_text=["Commodity: ABC Biscuits", "Net Qty: 200 g"],
        is_front=True,
        is_blurry=True
    )

    print("All sample images generated successfully.")


if __name__ == "__main__":
    generate_all_samples()
