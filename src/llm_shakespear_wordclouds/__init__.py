from llm_shakespear_wordclouds.read_shakespear import (
    read,
    pick_longest_lines_for_each_title,
    Works,
)


def main() -> None:
    works: Works = pick_longest_lines_for_each_title(read())
    for work in works:
        print(f"{work.title}, {len(work.text)} lines")


if __name__ == "__main__":
    main()
