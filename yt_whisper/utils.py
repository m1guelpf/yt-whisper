from typing import Iterator, List, TextIO


SENTENCE_END_PUNCT = ('.', '!', '?')
CLAUSE_END_PUNCT = (',', ';', ':')


def str2bool(string):
    str2val = {"True": True, "False": False}
    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"

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

def _split_words(words: List[dict], max_length: int) -> List[List[dict]]:
    """Recursively split a list of word entries into chunks, each whose joined
    text is under max_length characters when possible. Splits are chosen by
    preference: sentence-ending punctuation past the midpoint, then clause
    punctuation past the midpoint, then the latest word boundary that fits
    under the limit. Never splits mid-word."""
    text = "".join(w["word"] for w in words).strip()
    if len(text) <= max_length or len(words) <= 1:
        return [words]

    # cumulative stripped length of text up to and including word i
    cum_lengths = []
    acc = ""
    for w in words:
        acc += w["word"]
        cum_lengths.append(len(acc.strip()))
    midpoint = cum_lengths[-1] / 2

    sentence_idx = None
    clause_idx = None
    fit_idx = None

    for i in range(len(words) - 1):
        token = words[i]["word"].rstrip()
        first_len = cum_lengths[i]
        if first_len <= max_length:
            fit_idx = i
        if first_len >= midpoint:
            if sentence_idx is None and token.endswith(SENTENCE_END_PUNCT):
                sentence_idx = i
            elif clause_idx is None and token.endswith(CLAUSE_END_PUNCT):
                clause_idx = i

    if sentence_idx is not None:
        split_idx = sentence_idx
    elif clause_idx is not None:
        split_idx = clause_idx
    elif fit_idx is not None:
        split_idx = fit_idx
    else:
        # a single word already exceeds max_length; leave intact rather than
        # break mid-word
        return [words]

    return (
        _split_words(words[:split_idx + 1], max_length)
        + _split_words(words[split_idx + 1:], max_length)
    )


def split_long_segments(segments: Iterator[dict], max_length: int) -> List[dict]:
    """Split any segment whose text exceeds max_length into multiple segments,
    using word-level timestamps to assign each chunk its own start/end. Segments
    without word-level timestamps or already within the limit are passed through
    unchanged."""
    if not max_length or max_length <= 0:
        return list(segments)

    out: List[dict] = []
    for segment in segments:
        words = segment.get("words")
        text = segment.get("text", "").strip()
        if not words or len(text) <= max_length:
            out.append(segment)
            continue

        chunks = _split_words(words, max_length)
        if len(chunks) <= 1:
            out.append(segment)
            continue

        for chunk in chunks:
            chunk_text = "".join(w["word"] for w in chunk).strip()
            new_segment = dict(segment)
            new_segment["text"] = chunk_text
            new_segment["start"] = chunk[0]["start"]
            new_segment["end"] = chunk[-1]["end"]
            new_segment.pop("words", None)
            out.append(new_segment)

    return out


def process_segment(segment: dict, line_length: int = 0):
    segment["text"] = segment["text"].strip()
    if line_length > 0 and len(segment["text"]) > line_length:
        # break at N characters as per Netflix guidelines
        segment["text"] = break_line(segment["text"], line_length)
    
    return segment

def write_vtt(transcript: Iterator[dict], file: TextIO, line_length: int = 0):
    print("WEBVTT\n", file=file)
    for segment in transcript:
        segment = process_segment(segment, line_length=line_length)

        print(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def write_srt(transcript: Iterator[dict], file: TextIO, line_length: int = 0):
    for i, segment in enumerate(transcript, start=1):
        segment = process_segment(segment, line_length=line_length)

        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )

def slugify(title):
    return "".join(c if c.isalnum() else "_" for c in title).rstrip("_")

