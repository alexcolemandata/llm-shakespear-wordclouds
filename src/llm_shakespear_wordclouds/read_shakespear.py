from enum import Enum
from pathlib import Path
from dataclasses import dataclass

SHAKESPEAR_PATH = Path(__file__).parent / "data" / "shakespear.txt"

if not SHAKESPEAR_PATH.exists():
    raise FileNotFoundError(
        f"Could not locate shakespear at {SHAKESPEAR_PATH}, something has gone "
        + "wrong in the installation/setup!"
    )


class ParsingState(int, Enum):
    START = 0
    CONTENTS = 1
    WORKS = 2
    DONE = 3


@dataclass
class Work:
    title: str
    text: list[str]


Works = list[Work]


def pick_longest_lines_for_each_title(works: Works) -> Works:
    longest: dict[str, Work] = {}
    for work in works:
        current_longest = longest.get(work.title, None)
        if current_longest is None:
            longest_lines = 0
        else:
            longest_lines = len(current_longest.text)

        if len(work.text) > longest_lines:
            longest[work.title] = work

    return list(longest.values())


def read() -> Works:
    parsing_state = ParsingState.START
    titles: list[str] = []
    works: Works = []
    with open(SHAKESPEAR_PATH, "r") as file:
        title = ""
        text: list[str] = []
        while True:
            line = file.readline()

            stripline = line.strip()

            if parsing_state == ParsingState.START:
                if stripline == "Contents":
                    parsing_state = ParsingState.CONTENTS
            elif parsing_state == ParsingState.CONTENTS:
                if len(stripline) == 0:
                    if len(titles) > 0:
                        parsing_state = ParsingState.WORKS
                else:
                    titles.append(stripline)
            elif parsing_state == ParsingState.WORKS:
                if not line or stripline.startswith(
                    "*** END OF THE PROJECT GUTENBERG EBOOK"
                ):
                    parsing_state = ParsingState.DONE

                if (stripline in titles) or (parsing_state == ParsingState.DONE):
                    print(f"Parsed {title}, {len(text)} lines")
                    work = Work(title=title, text=text)
                    works.append(work)

                    title = stripline
                    text = []
                if parsing_state == ParsingState.DONE:
                    break
                if not line:
                    break
                elif len(stripline) == 0:
                    continue
                else:
                    text.append(line)

    return works
