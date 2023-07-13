import argparse
import logging
from pathlib import Path
import shutil
import numpy as np
import pydub
import audio_anim.config as config
from audio_anim.fft_anim import AudioArrayAnim, SimpleFFTAnim, BarFFTAnim
from audio_anim.video import make_final_video

logging.basicConfig(level=logging.INFO)


def convert_to_temporary_wav(audiofile: Path):
    audio = pydub.AudioSegment.from_file(audiofile)
    if not config.TMPDIR.exists():
        config.TMPDIR.mkdir(mode=666, parents=True)
        audiofile = config.TMP_AUDIOFILE
        audio.export(audiofile, format="wav")
    return audiofile


def load_audio(audiofile: Path, audio_format: str):
    if audio_format != "wav":
        audiofile = convert_to_temporary_wav(audiofile)
    audio = pydub.AudioSegment.from_wav(audiofile)
    # Normalization
    audio_max = audio.max_possible_amplitude / 2
    audio_array = 1 / audio_max * np.array(audio.get_array_of_samples())
    # Calculate frame rate
    frame_rate = audio_array.size / audio.duration_seconds
    return audio_array, audiofile, frame_rate


def select_animation(
    animation_type: str, audio_array: np.ndarray, sample_rate: float, fps: int
) -> AudioArrayAnim:
    if animation_type == "bar":
        return BarFFTAnim(audio_array, sample_rate, fps=fps)
    elif animation_type == "simple":
        return SimpleFFTAnim(audio_array, sample_rate, fps=fps)
    else:
        raise ValueError("Invalid animation type.")


def main(audiofile: Path, output: Path, animation_type: str, fps: int):
    # Delete temporary directory if it already exists
    if config.TMPDIR.exists():
        shutil.rmtree(config.TMPDIR)
    audio_format = audiofile.name.split(".")[1]
    audio_array, audiofile, audio_sample_rate = load_audio(
        audiofile=audiofile, audio_format=audio_format
    )
    logging.debug(f"Audio file loaded. Its shape is : {audio_array.shape}")
    anim = select_animation(
        animation_type=animation_type,
        audio_array=audio_array,
        sample_rate=audio_sample_rate,
        fps=fps,
    )
    # Make animation video
    anim.animate_video()
    # Make final video with sound
    make_final_video(
        audiofile=str(audiofile),
        videofile=str(config.TMP_ANIMATION),
        audio_sample_rate=audio_sample_rate,
        output=str((output)),
    )
    # Delete temporary files
    shutil.rmtree(config.TMPDIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Entry point of the audio animation package.")
    parser.add_argument(
        "--audiofile",
        help="Audio file to create the animation.",
        type=Path,
        required=True,
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
    parser.add_argument(
        "--fps", help="Number of frame per second. (default: 20)", type=int, default=20
    )
    args = parser.parse_args()
    main(
        audiofile=args.audiofile,
        output=args.output,
        animation_type=args.type,
        fps=args.fps,
    )
