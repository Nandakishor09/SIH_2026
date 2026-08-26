import os
from PIL import Image, ImageDraw

def create_favicon_svg():
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b2545" />
      <stop offset="100%" stop-color="#07172c" />
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#d97706" />
    </linearGradient>
    <filter id="dropShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Base Badge Squircle -->
  <rect x="2" y="2" width="60" height="60" rx="14" fill="url(#bgGrad)" stroke="#1e3a8a" stroke-width="1.5"/>

  <!-- Tricolor Accent Dash at Top -->
  <rect x="22" y="6" width="7" height="2.5" rx="1.2" fill="#ff9933" />
  <rect x="30" y="6" width="4" height="2.5" rx="1.2" fill="#ffffff" />
  <rect x="35" y="6" width="7" height="2.5" rx="1.2" fill="#138808" />

  <!-- Metrology Scales -->
  <!-- Central Beam & Finial -->
  <path d="M14 22 C23 20 41 20 50 22" fill="none" stroke="url(#goldGrad)" stroke-width="3" stroke-linecap="round"/>
  <line x1="32" y1="16" x2="32" y2="46" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="16" r="3" fill="#f59e0b" stroke="#ffffff" stroke-width="1"/>
  <path d="M22 46 L42 46" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>

  <!-- Left Scale Pan -->
  <line x1="17" y1="23" x2="11" y2="33" stroke="#94a3b8" stroke-width="1.6"/>
  <line x1="17" y1="23" x2="23" y2="33" stroke="#94a3b8" stroke-width="1.6"/>
  <path d="M10 33 Q17 39 24 33 Z" fill="#38bdf8"/>

  <!-- Right Scale Pan -->
  <line x1="47" y1="23" x2="41" y2="33" stroke="#94a3b8" stroke-width="1.6"/>
  <line x1="47" y1="23" x2="53" y2="33" stroke="#94a3b8" stroke-width="1.6"/>
  <path d="M40 33 Q47 39 54 33 Z" fill="#38bdf8"/>

  <!-- Verification Badge -->
  <g filter="url(#dropShadow)">
    <circle cx="47" cy="47" r="11" fill="#16a34a" stroke="#ffffff" stroke-width="2.2"/>
    <path d="M42.5 47 L45.8 50.3 L51.8 43.8" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
'''
    return svg_content

def draw_raster_icon(size=512):
    # High resolution master image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    scale = size / 64.0

    # Rounded rectangle background
    # Colors: Deep navy #0b2545 -> (11, 37, 69)
    pad = 2 * scale
    radius = int(14 * scale)
    draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=radius, fill=(11, 37, 69, 255), outline=(30, 58, 138, 255), width=max(1, int(1.5 * scale)))

    # Tricolor accent top
    draw.rounded_rectangle([22 * scale, 6 * scale, 29 * scale, 8.5 * scale], radius=int(1.2*scale), fill=(255, 153, 51, 255))
    draw.rounded_rectangle([30 * scale, 6 * scale, 34 * scale, 8.5 * scale], radius=int(1.2*scale), fill=(255, 255, 255, 255))
    draw.rounded_rectangle([35 * scale, 6 * scale, 42 * scale, 8.5 * scale], radius=int(1.2*scale), fill=(19, 136, 8, 255))

    # Center beam (White pillar)
    draw.line([(32 * scale, 16 * scale), (32 * scale, 46 * scale)], fill=(255, 255, 255, 255), width=max(1, int(3 * scale)))
    # Pillar base
    draw.line([(22 * scale, 46 * scale), (42 * scale, 46 * scale)], fill=(255, 255, 255, 255), width=max(1, int(3.5 * scale)))

    # Center finial
    top_r = 3.2 * scale
    draw.ellipse([32 * scale - top_r, 16 * scale - top_r, 32 * scale + top_r, 16 * scale + top_r], fill=(245, 158, 11, 255), outline=(255, 255, 255, 255), width=max(1, int(scale)))

    # Cross beam (Gold/Amber)
    draw.line([(14 * scale, 22 * scale), (50 * scale, 22 * scale)], fill=(245, 158, 11, 255), width=max(1, int(3 * scale)))

    # Left Pan strings
    draw.line([(17 * scale, 23 * scale), (11 * scale, 33 * scale)], fill=(148, 163, 184, 255), width=max(1, int(1.6 * scale)))
    draw.line([(17 * scale, 23 * scale), (23 * scale, 33 * scale)], fill=(148, 163, 184, 255), width=max(1, int(1.6 * scale)))
    # Left Pan (Sky Blue bowl)
    draw.chord([10 * scale, 28 * scale, 24 * scale, 38 * scale], start=0, end=180, fill=(56, 189, 248, 255), outline=(56, 189, 248, 255))

    # Right Pan strings
    draw.line([(47 * scale, 23 * scale), (41 * scale, 33 * scale)], fill=(148, 163, 184, 255), width=max(1, int(1.6 * scale)))
    draw.line([(47 * scale, 23 * scale), (53 * scale, 33 * scale)], fill=(148, 163, 184, 255), width=max(1, int(1.6 * scale)))
    # Right Pan (Sky Blue bowl)
    draw.chord([40 * scale, 28 * scale, 54 * scale, 38 * scale], start=0, end=180, fill=(56, 189, 248, 255), outline=(56, 189, 248, 255))

    # Verification Badge (Bottom Right)
    badge_cx, badge_cy = 47 * scale, 47 * scale
    badge_r = 11 * scale
    # Shadow/Border
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r], fill=(22, 163, 74, 255), outline=(255, 255, 255, 255), width=max(1, int(2.2 * scale)))
    
    # Checkmark inside badge
    chk_w = max(2, int(2.6 * scale))
    draw.line([(42.5 * scale, 47 * scale), (45.8 * scale, 50.3 * scale)], fill=(255, 255, 255, 255), width=chk_w)
    draw.line([(45.8 * scale, 50.3 * scale), (51.8 * scale, 43.8 * scale)], fill=(255, 255, 255, 255), width=chk_w)

    return img

if __name__ == "__main__":
    frontend_dir = os.path.abspath("frontend")
    os.makedirs(frontend_dir, exist_ok=True)
    
    # 1. Write SVG Favicon
    svg_data = create_favicon_svg()
    with open(os.path.join(frontend_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg_data)
    print("Saved favicon.svg")

    # 2. Master Raster (512x512)
    master = draw_raster_icon(512)
    master.save(os.path.join(frontend_dir, "favicon-512.png"), "PNG")
    
    # 192x192 for PWA/Android
    icon_192 = master.resize((192, 192), Image.Resampling.LANCZOS)
    icon_192.save(os.path.join(frontend_dir, "favicon-192.png"), "PNG")

    # 180x180 for Apple Touch Icon
    icon_180 = master.resize((180, 180), Image.Resampling.LANCZOS)
    icon_180.save(os.path.join(frontend_dir, "apple-touch-icon.png"), "PNG")

    # 32x32 & 16x16 PNGs
    icon_32 = master.resize((32, 32), Image.Resampling.LANCZOS)
    icon_32.save(os.path.join(frontend_dir, "favicon-32x32.png"), "PNG")

    icon_16 = master.resize((16, 16), Image.Resampling.LANCZOS)
    icon_16.save(os.path.join(frontend_dir, "favicon-16x16.png"), "PNG")

    # Favicon.ico with multi-resolutions
    master.save(
        os.path.join(frontend_dir, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
    )
    print("Saved favicon.ico and PNG assets")
