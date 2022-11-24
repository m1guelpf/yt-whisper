import os
from typing import List
import whisper
from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE
import argparse
import warnings
import yt_dlp
from .utils import slugify, str2bool, write_srt, write_vtt
import tempfile
import ffmpeg

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", nargs="+", type=str,
                        help="video URLs or files to transcribe")
    parser.add_argument("--model", default="small",
                        choices=whisper.available_models(), help="name of the Whisper model to use")
    parser.add_argument("--format", default="vtt",
                        choices=["vtt", "srt"], help="the subtitle format to output")
    parser.add_argument("--output_dir", "-o", type=str,
                        default=".", help="directory to save the outputs")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="Whether to print out the progress and debug messages")
    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--language", type=str, default=None, choices=sorted(LANGUAGES.keys()) + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]),
                        help="language spoken in the audio, skip to perform language detection")

    parser.add_argument("--break-lines", type=int, default=0, 
                        help="Whether to break lines into a bottom-heavy pyramid shape if line length exceeds N characters. 0 disables line breaking.")

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    subtitles_format: str = args.pop("format")
    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"

    model = whisper.load_model(model_name)
    with tempfile.TemporaryDirectory() as tmp_dir:
        audios = get_audio(args.pop("video"), tmp_dir)
        break_lines = args.pop("break_lines")

        for title, audio_path in audios.items():
            warnings.filterwarnings("ignore")
            result = model.transcribe(audio_path, **args)
            warnings.filterwarnings("default")

            if (subtitles_format == 'vtt'):
                vtt_path = os.path.join(output_dir, f"{slugify(title)}.vtt")
                with open(vtt_path, 'w', encoding="utf-8") as vtt:
                    write_vtt(result["segments"], file=vtt, line_length=break_lines)

                print("Saved VTT to", os.path.abspath(vtt_path))
            else:
                srt_path = os.path.join(output_dir, f"{slugify(title)}.srt")
                with open(srt_path, 'w', encoding="utf-8") as srt:
                    write_srt(result["segments"], file=srt, line_length=break_lines)

                print("Saved SRT to", os.path.abspath(srt_path))


def get_audio(video_paths:List[str], temp_dir:tempfile.TemporaryDirectory):   
    ydl = yt_dlp.YoutubeDL({
        'quiet': True,
        'verbose': False,
        'format': 'bestaudio',
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        'postprocessors': [{'preferredcodec': 'mp3', 'preferredquality': '192', 'key': 'FFmpegExtractAudio', }],
    })

    paths = {}

    for video_path in video_paths:
        if os.path.exists(video_path):
            title = os.path.basename(video_path).split(".")[0]
            audio_path = os.path.join(temp_dir, f"{title}.mp3")
            (ffmpeg
                .input(video_path)
                .audio
                .output(audio_path)
                .run()
            )
            paths[title] = audio_path
        else:
            result = ydl.extract_info(video_path, download=True)
            print(
                f"Downloaded video \"{result['title']}\". Generating subtitles..."
            )
            audio_path = os.path.join(temp_dir, f"{result['id']}.mp3")
            paths[result["title"]] = audio_path

    return paths


if __name__ == '__main__':
    main()
