
import re, random, colorsys, os, io, zipfile, datetime
from dataclasses import dataclass
from typing import Dict, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import cairosvg

def seeded_rand(seed: str):
    r = random.Random()
    r.seed(seed)
    return r

@dataclass
class Palette:
    primary: str
    secondary: str
    accent: str
    neutral_light: str
    neutral_dark: str

KEYWORD_THEMES = {
    "luxo": {"seed": "#C8A951", "fonts": ("Playfair Display", "Montserrat"), "icon": "sparkles"},
    "salão": {"seed": "#C8A951", "fonts": ("Playfair Display", "Montserrat"), "icon": "sparkles"},
    "estética": {"seed": "#C8A951", "fonts": ("Cormorant Garamond", "Lato"), "icon": "sparkles"},
    "fitness": {"seed": "#1C1B1B", "fonts": ("Poppins", "Inter"), "icon": "dumbbell"},
    "academia": {"seed": "#1C1B1B", "fonts": ("Poppins", "Inter"), "icon": "dumbbell"},
    "maternidade": {"seed": "#EFD3C4", "fonts": ("Quicksand", "Nunito"), "icon": "heart"},
    "bebê": {"seed": "#EFD3C4", "fonts": ("Quicksand", "Nunito"), "icon": "heart"},
    "educação": {"seed": "#6C8EEF", "fonts": ("Merriweather", "Source Sans 3"), "icon": "book"},
    "coaching": {"seed": "#9B6BCE", "fonts": ("Playfair Display", "Rubik"), "icon": "sparkles"},
}

ICON_SVGS = {
    "sparkles": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M32 6l4 10 10 4-10 4-4 10-4-10-10-4 10-4 4-10z' fill='#C8A951'/><path d='M52 32l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5z' fill='#C8A951'/></svg>",
    "dumbbell": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect x='6' y='24' width='10' height='16' fill='#1c1b1b'/><rect x='48' y='24' width='10' height='16' fill='#1c1b1b'/><rect x='16' y='29' width='32' height='6' fill='#c8a951'/></svg>",
    "heart": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M32 54S8 40 8 24c0-7 6-12 13-12 6 0 9 4 11 7 2-3 5-7 11-7 7 0 13 5 13 12 0 16-24 30-24 30z' fill='#EFD3C4'/></svg>",
    "book": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M10 12h22c6 0 10 4 10 10v30H20c-6 0-10-4-10-10V12z' fill='#f8f3ed' stroke='#1c1b1b'/><path d='M32 12h22v40H42c0-6-4-10-10-10V12z' fill='#fffdf9' stroke='#1c1b1b'/></svg>"
}

def parse_brief(brief: str) -> Tuple[str, str, str]:
    name = ""
    tagline = ""
    niche = ""
    m = re.search(r'["“](.+?)["”]', brief)
    if m:
        name = m.group(1).strip()
    else:
        m2 = re.search(r'([A-Z][\w]+(?:\s(?:Studio|Salon|Estúdio|Fit|Beauty|Baby|Brand))?)', brief)
        if m2:
            name = m2.group(1).strip()
    m3 = re.search(r'(slogan|tagline|frase)[:\-]?\s*(.+)', brief, re.I)
    if m3:
        tagline = m3.group(2).strip()
    for kw in KEYWORD_THEMES.keys():
        if re.search(rf'\b{kw}\b', brief, re.I):
            niche = kw
            break
    if not name:
        name = "Sua Marca"
    if not niche:
        niche = "luxo"
    if not tagline:
        tagline = "Beleza com propósito"
    return name, niche, tagline

def hex_to_hsl(hex_color: str):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)/255.0
    g = int(hex_color[2:4], 16)/255.0
    b = int(hex_color[4:6], 16)/255.0
    h,l,s = colorsys.rgb_to_hls(r,g,b)
    return h,s,l

def hsl_to_hex(h,s,l) -> str:
    r,g,b = colorsys.hls_to_rgb(h,l,s)
    return "#{:02X}{:02X}{:02X}".format(int(r*255), int(g*255), int(b*255))

def generate_palette(seed_hex: str, seed: str) -> Palette:
    rnd = seeded_rand(seed)
    h,s,l = hex_to_hsl(seed_hex)
    p = hsl_to_hex((h + rnd.uniform(-0.02,0.02))%1.0, min(0.6, s+0.1), min(0.62, 0.5 + rnd.uniform(-0.05,0.05)))
    sec = hsl_to_hex((h + 0.08)%1.0, min(0.65, s+0.12), 0.86)
    acc = hsl_to_hex((h + 0.5)%1.0, 0.5, 0.45)
    nl = hsl_to_hex(h, 0.1, 0.97)
    nd = hsl_to_hex(h, 0.12, 0.12)
    return Palette(primary=p, secondary=sec, accent=acc, neutral_light=nl, neutral_dark=nd)

def make_wordmark_svg(name: str, palette: Palette, icon: str) -> str:
    icon_svg = ICON_SVGS.get(icon, ICON_SVGS["sparkles"])
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 180'>"
        f"<rect width='800' height='180' fill='{palette.neutral_light}'/>"
        f"<g transform='translate(24,24) scale(2)'>{icon_svg.replace('<svg xmlns','<g xmlns').replace('</svg>','</g>')}</g>"
        f"<text x='160' y='92' font-family='Playfair Display, serif' font-size='54' fill='{palette.primary}'>{name}</text>"
        f"<line x1='160' y1='112' x2='{min(760, 160+len(name)*22)}' y2='112' stroke='{palette.accent}' stroke-width='3'/>"
        f"</svg>"
    )
    return svg

def make_monogram_svg(name: str, palette: Palette) -> str:
    initials = "".join([w[0] for w in name.split()][:2]).upper()
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 240'>"
        f"<circle cx='120' cy='120' r='104' fill='{palette.neutral_light}' stroke='{palette.primary}' stroke-width='6'/>"
        f"<text x='120' y='140' text-anchor='middle' font-family='Playfair Display, serif' font-size='96' fill='{palette.primary}'>{initials}</text>"
        f"</svg>"
    )
    return svg

def make_badge_svg(name: str, palette: Palette) -> str:
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 180'>"
        f"<rect x='10' y='10' width='340' height='160' rx='20' fill='{palette.neutral_light}' stroke='{palette.primary}' stroke-width='4'/>"
        f"<text x='180' y='95' text-anchor='middle' font-family='Montserrat, sans-serif' font-size='28' fill='{palette.primary}'>{name}</text>"
        f"<text x='180' y='125' text-anchor='middle' font-family='Montserrat, sans-serif' font-size='14' fill='{palette.accent}'>desde {datetime.date.today().year}</text>"
        f"</svg>"
    )
    return svg

def svg_to_png_bytes(svg_text: str, scale: float = 1.0) -> bytes:
    return cairosvg.svg2png(bytestring=svg_text.encode('utf-8'), scale=scale)

def build_pdf_guide(buffer: io.BytesIO, name: str, tagline: str, niche: str, palette: Palette, preview_png: bytes):
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    c.setFillColor(HexColor(palette.neutral_light))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setFillColor(HexColor(palette.primary))
    c.setFont("Helvetica-Bold", 28)
    c.drawString(40, h-80, f"Guia de Marca — {name}")
    c.setFont("Helvetica", 14)
    c.drawString(40, h-110, f"Slogan: {tagline}")
    c.drawString(40, h-130, f"Nicho: {niche}")

    # Palette swatches
    y = h-200
    swatches = [
        ("Primária", palette.primary),
        ("Secundária", palette.secondary),
        ("Acento", palette.accent),
        ("Neutro Claro", palette.neutral_light),
        ("Neutro Escuro", palette.neutral_dark),
    ]
    x = 40
    for label, color in swatches:
        c.setFillColor(HexColor(color))
        c.roundRect(x, y, 90, 60, 8, fill=1, stroke=0)
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica", 9)
        c.drawString(x, y-12, f"{label}: {color}")
        x += 100

    # Logo preview
    img = ImageReader(io.BytesIO(preview_png))
    c.drawImage(img, 40, 80, width=300, height=120, mask='auto')

    c.showPage()
    c.save()

def generate_kit_zip(brief: str, out_path: str) -> str:
    # Parse
    name, niche, tagline = parse_brief(brief)
    theme = KEYWORD_THEMES.get(niche, KEYWORD_THEMES["luxo"])
    palette = generate_palette(theme["seed"], seed=brief)
    icon_key = theme["icon"]

    # Build assets in-memory
    wordmark_svg = make_wordmark_svg(name, palette, icon_key)
    monogram_svg = make_monogram_svg(name, palette)
    badge_svg = make_badge_svg(name, palette)

    wordmark_png = svg_to_png_bytes(wordmark_svg, scale=1.2)
    monogram_png = svg_to_png_bytes(monogram_svg, scale=1.6)
    badge_png = svg_to_png_bytes(badge_svg, scale=1.6)

    # PDF guide
    pdf_buf = io.BytesIO()
    build_pdf_guide(pdf_buf, name, tagline, niche, palette, wordmark_png)
    pdf_bytes = pdf_buf.getvalue()

    # palette json
    palette_json = (
        '{"primary":"%s","secondary":"%s","accent":"%s","neutral_light":"%s","neutral_dark":"%s"}'
        % (palette.primary, palette.secondary, palette.accent, palette.neutral_light, palette.neutral_dark)
    ).encode("utf-8")

    # Zip it
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("logos/wordmark.svg", wordmark_svg)
        z.writestr("logos/monogram.svg", monogram_svg)
        z.writestr("logos/badge.svg", badge_svg)
        z.writestr("logos/wordmark.png", wordmark_png)
        z.writestr("logos/monogram.png", monogram_png)
        z.writestr("logos/badge.png", badge_png)
        z.writestr("brand/brand_guide.pdf", pdf_bytes)
        z.writestr("brand/palette.json", palette_json)
        z.writestr("README.txt", f"Kit gerado para {name}\\nSlogan: {tagline}\\nNicho: {niche}\\n")

    return out_path, {"name": name, "tagline": tagline, "niche": niche, "palette": palette.__dict__}
