import argparse
from pathlib import Path
import shutil
import numpy as np
import pydub
from moviepy.editor import AudioFileClip, VideoFileClip
import audio_anim.config as config
from audio_anim.fft_anim import SimpleFFTAnim, BarFFTAnim


def convert_to_temporary_wav(audiofile: Path):
    audio = pydub.AudioSegment.from_file(audiofile)
    if not config.TMPDIR.exists():
        config.TMPDIR.mkdir(mode=666, parents=True)
        audiofile = config.TMP_AUDIOFILE
        audio.export(audiofile, format="wav")
    return audiofile


def load_audio(audiofile: Path, format: str):
    if format != ".wav":
        audiofile = convert_to_temporary_wav(audiofile)
    audio = pydub.AudioSegment.from_wav(audiofile)
    # Normalization
    audio_max = audio.max_possible_amplitude / 2
    audio_array = 1 / audio_max * np.array(audio.get_array_of_samples())
    # Calculate frame rate
    frame_rate = audio_array.size / audio.duration_seconds
    return audio_array, audiofile, frame_rate


def select_animation(
    animation_type: str, audio_array: np.ndarray, sample_rate: float
) -> None:
    if animation_type == "bar":
        BarFFTAnim(audio_array, sample_rate)
    elif animation_type == "simple":
        SimpleFFTAnim(audio_array, sample_rate)


def main(audiofile: Path, format: str, output: Path, animation_type: str):
    # Delete temporary directory if it already exists
    if config.TMPDIR.exists():
        shutil.rmtree(config.TMPDIR)
    audio_array, audiofile, sample_rate = load_audio(audiofile=audiofile, format=format)
    select_animation(
        animation_type=animation_type, audio_array=audio_array, sample_rate=sample_rate
    )
    # Load video clip
    video = VideoFileClip(str(config.TMP_ANIMATION))
    # Load audio clip
    audio = AudioFileClip(str(audiofile))
    # Clip audio
    music_time = int(audio_array.size / sample_rate)
    audio = audio.subclip(0, music_time)
    # Add music to video
    final_clip = video.set_audio(audio)
    # Save final clip
    final_clip.write_videofile(str(output))
    # Close files
    audio.close()
    video.close()
    final_clip.close()
    # Delete temporary files
    shutil.rmtree(config.TMPDIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Entry point of the audio animation package.")
    parser.add_argument(
        "audiofile", help="Audio file to create the animation.", type=Path
    )
    parser.add_argument(
        "--format", help="Audio file format (default: .wav).", type=str, default=".wav"
    )
    parser.add_argument(
        "--type",
        help="Type of animation (default: simple).",
        type=str,
        default="simple",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output path (default: ./final.mp4).",
        type=Path,
        default=Path("./final.mp4"),
    )
    args = parser.parse_args()
    main(
        audiofile=args.audiofile,
        format=args.format,
        output=args.output,
        animation_type=args.type,
    )
