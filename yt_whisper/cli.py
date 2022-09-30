import os
import whisper
import argparse
import warnings
import youtube_dl
from .utils import slugify, str2bool, write_vtt, youtube_dl_log
import tempfile


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", nargs="+", type=str,
                        help="video URLs to transcribe")
    parser.add_argument("--model", default="small",
                        choices=whisper.available_models(), help="name of the Whisper model to use")
    parser.add_argument("--output_dir", "-o", type=str,
                        default=".", help="directory to save the outputs")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="Whether to print out the progress and debug messages")

    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--device", choices=("cpu", "cuda"), help="device to use for PyTorch inference")

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    device: str = args.pop("device")
    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"

    model = whisper.load_model(model_name, device=device)
    audios = get_audio(args.pop("video"))

    for title, audio_path in audios.items():
        warnings.filterwarnings("ignore")
        result = model.transcribe(audio_path, **args)
        warnings.filterwarnings("default")

        vtt_path = os.path.join(output_dir, f"{slugify(title)}.vtt")
        with open(vtt_path, 'w', encoding="utf-8") as vtt:
            write_vtt(result["segments"], file=vtt)

        # print saved message with absolute path
        print("Saved VTT to", os.path.abspath(vtt_path))


def get_audio(urls):
    temp_dir = tempfile.gettempdir()

    ydl = youtube_dl.YoutubeDL({
        'quiet': True,
        'verbose': False,
        'no_warnings': True,
        'format': 'bestaudio/best',
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        'progress_hooks': [youtube_dl_log],
        'postprocessors': [{
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'key': 'FFmpegExtractAudio',
        }],
    })

    paths = {}

    for url in urls:
        result = ydl.extract_info(url, download=True)
        print(
            f"Downloaded video \"{result['title']}\". Generating subtitles..."
        )
        paths[result["title"]] = os.path.join(temp_dir, f"{result['id']}.mp3")

    return paths


if __name__ == '__main__':
    main()
