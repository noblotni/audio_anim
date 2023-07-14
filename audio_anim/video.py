"""Make video."""
from pathlib import Path
from moviepy.editor import AudioFileClip, VideoFileClip


def make_final_video(
    audiofile: Path,
    videofile: Path,
    audio_sample_rate: float,
    output: Path,
):
    # Load video clip
    video = VideoFileClip(videofile.as_posix())
    # Load audio clip
    audio = AudioFileClip(audiofile.as_posix(), fps=int(audio_sample_rate))
    # Check duration of audio and video
    audio_duration = audio.duration
    video_duration = video.duration

    # If audio longer than video, then cut audio
    if audio_duration > video_duration:
        audio = audio.subclip(0, video_duration)
    # If video longer than audio, then cut video
    elif video_duration > audio_duration:
        video = video.subclip(0, audio_duration)

    # Add music to video
    final_clip = video.set_audio(audio)

    # Save final clip
    final_clip.write_videofile(output.as_posix())

    # Close the files
    audio.close()
    video.close()
    final_clip.close()
