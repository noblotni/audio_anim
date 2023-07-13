"""Create an animation from an audio signal."""
import abc
import numpy as np
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import audio_anim.config as config


# Constants
T_WINDOW = 0.3
N_FFT = 3000
MAX_Y = 1000
# Number of bins for the bar style
N_BINS = 100

# Set matplotlib style
plt.style.use("dark_background")


class AudioArrayAnim(abc.ABC):
    def __init__(self, audio_array: np.ndarray, sample_rate: float, fps):
        self.audio_array = audio_array
        self.sample_rate = sample_rate
        self.fps = fps
        self.speed = int(self.sample_rate / self.fps)
        self.interval = int(1000 / self.fps)

    def animate_video(
        self,
    ) -> None:
        self.figure, self.ax = plt.subplots()
        ani = anim.FuncAnimation(
            fig=self.figure,
            func=self.animate_audio,
            init_func=self.init_animation,
            interval=self.interval,
            frames=self.audio_array.size // self.speed,
        )
        if not config.TMPDIR.exists():
            config.TMPDIR.mkdir(mode=666, parents=True, exist_ok=True)
        logging.debug("Saving animation to: %s", str(config.TMP_ANIMATION))
        writer_video = anim.FFMpegWriter(
            fps=self.fps, extra_args=["-vcodec", "libx264"]
        )
        try:
            ani.save(str(config.TMP_ANIMATION), writer=writer_video)
        except ValueError:
            pass

    def show_animation(
        self,
    ) -> None:
        self.figure, self.ax = plt.subplots()
        _ = anim.FuncAnimation(
            fig=self.figure,
            func=self.animate_audio,
            init_func=self.init_animation,
            interval=self.interval,
            frames=self.audio_array.size // self.speed,
        )
        plt.show()

    @abc.abstractclassmethod
    def animate_audio(self, i: int):
        pass

    @abc.abstractclassmethod
    def init_animation(self):
        pass


class SimpleFFTAnim(AudioArrayAnim):
    def __init__(self, audio_array: np.ndarray, sample_rate: float, fps: int) -> None:
        super().__init__(audio_array=audio_array, sample_rate=sample_rate, fps=fps)

    def init_animation(self):
        (self.fft_pos,) = self.ax.plot([], [], color="blue")
        (self.fft_neg,) = self.ax.plot([], [], color="red", alpha=0.75)
        self.ax.set_xlim(0, N_FFT // 2)
        self.ax.set_ylim(-MAX_Y, MAX_Y)
        plt.axis("off")
        return [self.fft_pos, self.fft_neg]

    def animate_audio(self, i: int):
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


class BarFFTAnim(AudioArrayAnim):
    def __init__(self, audio_array: np.ndarray, sample_rate: float, fps: int) -> None:
        super().__init__(audio_array=audio_array, sample_rate=sample_rate, fps=fps)

    def init_animation(self):
        _, _, self.bar_container = self.ax.hist(
            np.arange(0, N_FFT // 2),
            bins=N_BINS,
            color="yellow",
            edgecolor="black",
            linewidth=0.5,
        )
        self.ax.hlines(y=0, xmin=0, xmax=N_FFT // 2, colors="yellow")
        self.ax.set_xlim(0, N_FFT // 2)
        plt.axis("off")
        return self.bar_container.patches

    def animate_audio(self, i: int):
        fft = np.abs(
            np.fft.fft(
                self.audio_array[
                    self.speed * i : self.speed * i + int(T_WINDOW * self.sample_rate)
                ]
            )
        )
        self.ax.set_ylim(-np.max(fft) / 4, np.max(fft))
        x = np.arange(0, N_FFT // 2)
        _, bin_edges = np.histogram(a=x, bins=N_BINS)
        for i, rect in enumerate(self.bar_container.patches):
            rect.set_height(np.mean(fft[int(bin_edges[i]) : int(bin_edges[i + 1])]))
        return self.bar_container.patches
