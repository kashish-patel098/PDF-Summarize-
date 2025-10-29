"""Select or generate a simple visual for each slide.

This module creates a clean reference image per slide suitable for both
PowerPoint slides and video frames (16:9 by default).

Functions provided:
- compose_visual(...) : create a single image with headline/bullets and simple icon
- create_visuals_for_slides(...) : generate one visual per slide item and return paths
"""
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict
import hashlib
import re

FONT_PATH = None  # set to a ttf path to use a consistent font across systems


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _safe_load_font(size: int):
    """Try to load a truetype font if available, otherwise fall back to default."""
    try:
        if FONT_PATH:
            return ImageFont.truetype(FONT_PATH, size)
        # try some common fonts if available on system
        for candidate in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
    except Exception:
        pass
    return ImageFont.load_default()


def _slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        s = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return s


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    """Return (width, height) of rendered text using the best available API.

    Tries: draw.textbbox -> font.getbbox/getsize -> draw.textsize
    """
    # try ImageDraw.textbbox (Pillow 8.0+)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass
    # try font.getbbox/getsize
    try:
        if hasattr(font, 'getbbox'):
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        if hasattr(font, 'getsize'):
            return font.getsize(text)
    except Exception:
        pass
    # fallback: ImageDraw.textsize (older versions)
    try:
        return draw.textsize(text, font=font)
    except Exception:
        # ultimate fallback: estimate
        approx_w = len(text) * (getattr(font, 'size', 12) // 2)
        approx_h = getattr(font, 'size', 12)
        return approx_w, approx_h


def compose_visual(headline: str, bullets: List[str], out_path: str, size=(1280, 720), bg_color=(250, 250, 255)):
    """Compose a single visual card.

    headline: main headline text
    bullets: list of bullet strings
    out_path: output file path (directories will be created)
    size: (w, h) in pixels
    bg_color: background color tuple
    """
    ensure_dir(os.path.dirname(out_path) or '.')
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    w, h = size

    # area for left icon/graphic
    icon_w = int(w * 0.35)
    padding = int(max(12, w * 0.03))
    icon_rect = [padding, padding, icon_w - padding, h - padding]
    draw.rectangle(icon_rect, fill=(230, 240, 255))

    # draw a simple circular emblem in the icon area with initials
    cx = (icon_rect[0] + icon_rect[2]) // 2
    cy = (icon_rect[1] + icon_rect[3]) // 2
    r = int(min(icon_rect[2] - icon_rect[0], icon_rect[3] - icon_rect[1]) * 0.25)
    # draw shadowed circle and main circle for a modern emblem
    shadow_offset = max(2, int(h * 0.01))
    draw.ellipse((cx - r + shadow_offset, cy - r + shadow_offset, cx + r + shadow_offset, cy + r + shadow_offset), fill=(70, 80, 90))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 130, 200))

    # initials from headline (up to 2 letters)
    initials = ''.join([p[0].upper() for p in headline.split()[:2] if p])[:2]
    title_font = _safe_load_font(int(h * 0.07))
    tw, th = _text_size(draw, initials, title_font)
    draw.text((cx - tw // 2, cy - th // 2), initials, fill=(255, 255, 255), font=title_font)

    # prepare headline and bullets on the right side
    right_x = icon_w + padding
    right_w = w - right_x - padding

    # fonts for headline and body - slightly adjusted sizes for better hierarchy
    headline_font = _safe_load_font(int(h * 0.08))
    body_font = _safe_load_font(int(h * 0.038))

    # draw headline with wrapping
    head_lines = _wrap_text(headline, max_chars=max(10, int(right_w / (max(1, _text_size(draw, "a", headline_font)[0]) + 1))))
    y = padding
    first = True
    for line in head_lines.split('\n'):
        draw.text((right_x, y), line, fill=(18, 24, 38), font=headline_font)
        lh = int(_text_size(draw, line, headline_font)[1] * 1.15)
        y += lh

    # bullets with slightly larger spacing and softer color
    y += int(h * 0.03)
    for b in bullets:
        lines = _wrap_text(b, max_chars=max(10, int(right_w / (max(1, _text_size(draw, "a", body_font)[0]) + 1)))).split('\n')
        for ln in lines:
            draw.text((right_x + 10, y), '• ' + ln, fill=(60, 70, 85), font=body_font)
            y += int(_text_size(draw, ln, body_font)[1] * 1.3)

    # footer small credit

    img.save(out_path)
    return out_path


def _wrap_text(text: str, max_chars: int = 40) -> str:
    """A basic wrapper that breaks text into lines of up to max_chars characters.

    This is fast and deterministic; font-aware wrapping could be added later.
    """
    if not text:
        return ''
    words = text.split()
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        if cur and cur_len + 1 + len(w) > max_chars:
            lines.append(' '.join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += (0 if cur_len == 0 else 1) + len(w)
    if cur:
        lines.append(' '.join(cur))
    return '\n'.join(lines)


def create_visuals_for_slides(slide_items: List[Dict], out_dir: str, size=(1280, 720)) -> List[str]:
    """Create one visual per slide item and return list of output paths.

    slide_items: list of dicts containing at least 'headline' and optional 'bullets'
    out_dir: directory to write images into
    size: tuple for image size (defaults to 1280x720 for 16:9)
    """
    ensure_dir(out_dir)
    paths = []
    for i, item in enumerate(slide_items):
        headline = item.get('headline', f'Slide {i+1}')
        bullets = item.get('bullets', []) or []
        # deterministic filename: index + slug of headline
        slug = _slugify(headline)[:40]
        filename = f"{i+1:02d}-{slug}.png"
        out_path = os.path.join(out_dir, filename)
        try:
            compose_visual(headline, bullets, out_path, size=size)
            paths.append(out_path)
        except Exception:
            # fallback: create a very simple blank image so downstream doesn't fail
            fallback = Image.new('RGB', size, (240, 240, 240))
            fallback.save(out_path)
            paths.append(out_path)
    return paths
