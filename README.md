# Automatic YouTube subtitle generation

This repository uses `youtube-dl` and [OpenAI's Whisper](https://openai.com/blog/whisper) to generate subtitle files for any youtube video.

## Installation

To get started, you'll need Python 3.7 or newer. Install the binary by running the following command:

    pip install git+https://github.com/m1guelpf/yt-whisper.git

You'll also need to install [`ffmpeg`](https://ffmpeg.org/), which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg
```

## Usage

The following command will generate a VTT file from the specified YouTube video

    yt_whisper https://www.youtube.com/watch?v=dQw4w9WgXcQ

The default setting (which selects the `small` model) works well for transcribing English. You can optionally use a bigger model for better results (especially with other languages). The available models are `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large`.

    yt_whisper https://www.youtube.com/watch?v=dQw4w9WgXcQ --model medium

Adding `--task translate` will translate the subtitles into English:

    yt_whisper https://www.youtube.com/watch?v=dQw4w9WgXcQ --task translate

Run the following to view all available options:

    yt_whisper --help

## License

The code and the model weights of Whisper are released under the MIT License. See [LICENSE](LICENSE) for further details.
