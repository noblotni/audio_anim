"""Convert an audiofile into a video."""
from enum import Enum
import logging
from pathlib import Path
import shutil
import numpy as np
import pydub
import typer
import structlog
from typing_extensions import Annotated
import audio_anim.config as config
from audio_anim.fft_anim import AudioArrayAnim, SimpleFFTAnim, BarFFTAnim
from audio_anim.video import make_final_video


class AnimationType(str, Enum):
    SIMPLE = "simple"
    BAR = "bar"


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


def main(
    audiofile: Annotated[Path, typer.Argument(help="Path to the audio file")],
    output: Annotated[Path, typer.Option(help="Path to the output file")] = Path(
        "./final.mp4"
    ),
    animation_type: Annotated[
        AnimationType, typer.Option(help="Type of animation", case_sensitive=False)
    ] = AnimationType.SIMPLE,
    fps: Annotated[int, typer.Option(help="Frames per second")] = 20,
    verbose: Annotated[int, typer.Option(help="Verbosity")] = 0,
):
    """Convert an audio file into a video animation."""

    # Handle log level
    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )
    log = structlog.get_logger()
    # Delete temporary directory if it already exists
    if config.TMPDIR.exists():
        shutil.rmtree(config.TMPDIR)
    audio_format = audiofile.name.split(".")[1]
    audio_array, audiofile, audio_sample_rate = load_audio(
        audiofile=audiofile, audio_format=audio_format
    )
    log.debug("Audio file loaded. Its shape is: ", shape=audio_array.shape)
    anim = select_animation(
        animation_type=animation_type,
        audio_array=audio_array,
        sample_rate=audio_sample_rate,
        fps=fps,
    )
    log.info("Making animation")
    # Make animation video
    anim.animate_video()
    # Make final video with sound
    log.info("Making video")
    make_final_video(
        audiofile=audiofile,
        videofile=config.TMP_ANIMATION,
        audio_sample_rate=audio_sample_rate,
        output=output,
    )
    # Delete temporary files
    shutil.rmtree(config.TMPDIR)


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
