"""Orchestration CLI: run the pipeline end-to-end.
"""
import argparse
import os
from src.pdf_ingest import extract_sections
from src.summarizer import make_slide_text, extractive_summary
from src.visual_selector import compose_visual
from src.slide_builder import build_pptx
from src.tts import synthesize_texts
from src.video_maker import make_video


def render_slide_images(slide_items, visuals_dir):
    # In this skeleton we assume visuals produced are already full-slide images.
    return [os.path.join(visuals_dir, f'slide_{i+1:02d}.png') for i in range(len(slide_items))]


def run(input_pdf, outdir, slides=8):
    os.makedirs(outdir, exist_ok=True)
    sections = extract_sections(input_pdf)
    if not sections:
        raise SystemExit('No sections extracted from PDF')
    selected = sections[:slides]
    slide_items = [make_slide_text(s) for s in selected]
    visuals_dir = os.path.join(outdir, 'visuals')
    os.makedirs(visuals_dir, exist_ok=True)
    visual_paths = []
    for i, s in enumerate(slide_items, start=1):
        out = os.path.join(visuals_dir, f'slide_{i:02d}.png')
        compose_visual(s['headline'], s.get('bullets', []), out)
        visual_paths.append(out)
    pptx_path = os.path.join(outdir, 'slides.pptx')
    build_pptx(slide_items, visual_paths, pptx_path)
    # tts
    tts_outdir = os.path.join(outdir, 'tts')
    texts = [s.get('note') or s.get('headline') for s in slide_items]
    audio_files = synthesize_texts(texts, tts_outdir)
    # make video
    video_path = os.path.join(outdir, 'video.mp4')
    make_video(visual_paths, audio_files, music_file=None, out_path=video_path)
    print('Outputs:')
    print(' PPTX:', pptx_path)
    print(' Video:', video_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='input PDF path')
    parser.add_argument('--outdir', '-o', default='output', help='output directory')
    parser.add_argument('--slides', '-s', type=int, default=6, help='number of slides')
    args = parser.parse_args()
    run(args.input, args.outdir, slides=args.slides)

