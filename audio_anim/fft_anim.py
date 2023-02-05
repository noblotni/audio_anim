"""Create an animation from an audio signal."""
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import audio_anim.config as config

plt.style.use("dark_background")
# Constants
T_WINDOW = 0.3
N_FFT = 3000
MAX_Y = 1000
FPS = 20
# Time between two frames (ms)
INTERVAL = int(1000 / FPS)


class AudioArrayAnim:
    def __init__(self, audio_array: np.ndarray, sample_rate: float) -> None:
        self.audio_array = audio_array
        self.sample_rate = sample_rate
        self.speed = int(self.sample_rate / FPS)
        self.figure, self.ax = plt.subplots()
        self.ani = anim.FuncAnimation(
            fig=self.figure,
            func=self.anim_audio,
            init_func=self.init_anim,
            interval=INTERVAL,
            frames=self.audio_array.size // self.speed,
        )
        if not config.TMPDIR.exists():
            config.TMPDIR.mkdir(mode=666, parents=True, exist_ok=True)
        self.ani.save(str(config.TMP_ANIMATION), fps=FPS)

    def init_anim(self):
        (self.fft_pos,) = self.ax.plot([], [], color="blue")
        (self.fft_neg,) = self.ax.plot([], [], color="red", alpha=0.75)
        self.ax.set_xlim(0, N_FFT // 2)
        self.ax.set_ylim(-MAX_Y, MAX_Y)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        return [self.fft_pos, self.fft_neg]

    def anim_audio(self, i: int):
        fft = np.fft.fft(
            self.audio_array[
                self.speed * i : self.speed * i + int(T_WINDOW * self.sample_rate)
            ]
        )
        x = np.arange(0, N_FFT // 2)
        y_pos = np.abs(fft[: N_FFT // 2])
        y_neg = -np.abs(fft[: N_FFT // 2])
        self.fft_neg.set_data(x, y_neg)
        self.fft_pos.set_data(x, y_pos)
        return [self.fft_pos, self.fft_neg]
