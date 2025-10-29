# PDF Summarizer

## Overview
This project is an advanced AI-powered tool designed to automate the process of transforming PDF documents into engaging video presentations. By leveraging state-of-the-art natural language processing, text-to-speech, and visual selection technologies, it streamlines content summarization, slide creation, and video generation. This makes it an excellent solution for educators, content creators, and professionals who want to quickly convert written material into dynamic multimedia content.

### Why This Project is Great
- **End-to-End Automation:** Converts PDFs into summarized slides, selects relevant visuals, generates voiceovers, and produces complete videos—all in one pipeline.
- **Customizable Summarization:** Allows users to specify the number of summary slides, tailoring the output to their needs.
- **Modular Design:** Each component (summarization, TTS, visual selection, video making) is modular, making it easy to extend or replace parts of the pipeline.
- **Time-Saving:** Automates hours of manual work, enabling rapid content repurposing.

## File Structure
```
cli.py                  # Main command-line interface for running the pipeline
Example.pdf             # Example pdf for summarize
requirements.txt        # Python dependencies
output/
    tts/                # Generated audio files
    visuals/            # Selected or generated visuals for slides.pptx         # Example ppt
    video.mp4           # Example Video 
src/
    pdf_ingest.py       # PDF ingestion and text extraction
    slide_builder.py    # Slide creation from summaries
    summarizer.py       # Summarization logic
    tts.py              # Text-to-speech generation
    video_maker.py      # Video assembly from slides and audio
    visual_selector.py  # Visual selection for slides
    __pycache__/        # Python cache files
```

## Usage Instructions
1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Run the CLI tool:**
   ```powershell
   python cli.py -i <input_pdf> -s <num_slides> -o <output_directory>
   ```
   - `<input_pdf>`: Path to the PDF file you want to convert.
   - `<num_slides>`: Number of summary slides to generate (e.g., 5).
   - `<output_directory>`: Path to be the output Store.

   **Example:**
   ```powershell
   python cli.py -i "ConceptNote.pdf" -s 5 -o "output"
   ```

3. **Output:**
   - Audio files will be saved in `output/tts/`
   - Visuals will be saved in `output/visuals/`
   - The final video will be saved in the `output/` directory.
   - The final PPT will be saved in the `output/` directory.


## How the Pipeline Works
The project follows a modular, end-to-end pipeline to convert a PDF into a summarized video presentation:

1. **PDF Ingestion** (`src/pdf_ingest.py`):
   - Extracts sections from the PDF using heading heuristics.
   - Each section contains a title, text, and page number.

2. **Summarization** (`src/summarizer.py`):
   - Summarizes each section using extractive summarization.
   - Produces a headline, bullet points, and a note for each slide.

3. **Visual Selection** (`src/visual_selector.py`):
   - Generates a simple, clean visual for each slide (headline, bullets, and icon) as a PNG image.

4. **Slide Building** (`src/slide_builder.py`):
   - Assembles the headlines, bullets, and visuals into a PowerPoint presentation (`slides.pptx`).

5. **Text-to-Speech (TTS)** (`src/tts.py`):
   - Converts slide notes or headlines into audio files (one per slide) using offline TTS.

6. **Video Creation** (`src/video_maker.py`):
   - Combines slide images and audio into a final MP4 video.
   - Optionally adds background music.

**All steps are orchestrated by the CLI (`cli.py`), which manages the flow and output directories.**

