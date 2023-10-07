# Audio Anim

A package to animate audio files.

![](./docs/imgs/fft_color_example.svg)

# Installation 

`audio_anim` requires Python 3.9 or higher.

1. Clone this repository
   ```shell
   git clone https://github.com/noblotni/audio_anim
   ```
2. Change the directory
   ```shell
   cd audio_anim
   ```
3. Install the dependencies
    ```shell
    pip install .
    ```

You will also need `fmpeg`. On Linux install it with : 
```shell
sudo apt install ffmpeg
```
# Usage

Once installed, you can run the `audio-anim` command :
```shell
 Usage: audio-anim [OPTIONS] AUDIOFILE                                                                           
                                                                                                                 
 Convert an audio file into a video animation.
 *    audiofile      PATH  Path to the audio file [default: None] [required]
 --output                  PATH          Path to the output file [default: final.mp4]
 --animation-type          [simple|bar]  Type of animation [default: AnimationType.SIMPLE]
 --fps                     INTEGER       Frames per second [default: 20]
 --verbose         -v      INTEGER       Verbosity [default: 0] 
 --help                                  Show this message and exit.       
```

# TODO

- Add a config file to set fft colors
- Improve the resolution of the output video
- Improve fft bar style
