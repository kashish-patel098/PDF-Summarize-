"""Combine slide images and audio into a final MP4 using moviepy.
"""
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
import os


def make_video(slide_images, audio_files, music_file, out_path: str, per_slide_duration=6):
    assert len(slide_images) == len(audio_files)
    clips = []
    for img, audio in zip(slide_images, audio_files):
        # if audio exists, use its duration; else use default
        if os.path.exists(audio):
            a = AudioFileClip(audio)
            duration = a.duration
        else:
            a = None
            duration = per_slide_duration
        # moviepy version in this environment uses `with_duration` and
        # attaching audio by setting the `audio` attribute.
        clip = ImageClip(img).with_duration(duration)
        if a:
            clip.audio = a
        clips.append(clip)
    final = concatenate_videoclips(clips, method='compose')
    # add background music if provided
    if music_file and os.path.exists(music_file):
        bg = AudioFileClip(music_file)
        bg = bg.audio_loop(duration=final.duration).volumex(0.08)
        # mix
        final_audio = CompositeAudioClip([final.audio, bg]) if final.audio else bg
        final = final.set_audio(final_audio)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac')
    return out_path