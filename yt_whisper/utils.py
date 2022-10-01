from typing import Iterator, TextIO


def str2bool(string):
    str2val = {"True": True, "False": False}
    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    return (f"{hours}:" if hours > 0 else "") + f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def break_line(line: str, length: int):
    break_index = min(len(line)//2, length) # split evenly or at maximum length

    # work backwards from that guess to split between words
    # if break_index <= 1, we've hit the beginning of the string and can't split
    while break_index > 1:
        if line[break_index - 1] == " ":
            break # break at space
        else:
            break_index -= 1
    if break_index > 1:
        # split the line, not including the space at break_index
        return line[:break_index - 1] + "\n" + line[break_index:]
    else:
        return line


def write_vtt(transcript: Iterator[dict], file: TextIO, line_length: int = 0):
    print("WEBVTT\n", file=file)
    for segment in transcript:
        if line_length > 0 and len(segment["text"]) > line_length:
            # break at N characters as per Netflix guidelines
            segment["text"] = break_line(segment["text"], line_length)

        print(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{segment['text'].replace('-->', '->')}\n",
            file=file,
            flush=True,
        )

def slugify(title):
    return "".join(c if c.isalnum() else "_" for c in title).rstrip("_")


def youtube_dl_log(d):
    if d['status'] == 'downloading':
        print("Downloading video: " +
              str(round(float(d['downloaded_bytes'])/float(d['total_bytes'])*100, 1))+"%")
