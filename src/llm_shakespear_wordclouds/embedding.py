from itertools import batched
from rich.progress import (
    Progress,
    TaskID,
    MofNCompleteColumn,
    TimeElapsedColumn,
)
import chromadb

from llm_shakespear_wordclouds.read_shakespear import (
    read,
    pick_longest_lines_for_each_title,
    Work,
    Works,
)
from random import sample


BATCH_SIZE = 3

MAX_WORKS = 10
MAX_LINES = 100
MIN_WORDS_FOR_LINE = 4


def embed_work(
    work: Work, collection: chromadb.Collection, progress: Progress, task: TaskID
) -> None:
    progress.start_task(task)
    title = work.title
    text = work.text
    count = 0
    for lines in batched(text, BATCH_SIZE):
        numlines = len(lines)
        collection.add(
            documents=list([line.lower().strip() for line in lines]),
            metadatas=[{"title": title}] * numlines,
            ids=[f"{title}-{n}" for n in range(count, count + numlines)],
        )
        count += numlines
        progress.update(task, advance=numlines)


def embed_works(works: Works, collection: chromadb.Collection):
    with Progress(
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        MofNCompleteColumn(),
        refresh_per_second=60,
    ) as progress:
        tasks: list[TaskID] = []
        total_task = progress.add_task(
            "Generating Embeddings for Works",
            total=sum([len(work.text) for work in works]),
        )
        for work in works:
            tasks.append(
                progress.add_task(work.title, total=len(work.text), start=False)
            )

        for work, task in zip(works, tasks, strict=True):
            embed_work(work=work, collection=collection, progress=progress, task=task)
            progress.update(total_task, advance=len(work.text))


def main():
    works = pick_longest_lines_for_each_title(read())
    if MAX_WORKS:
        works = sample(works, k=MAX_WORKS)

    if MIN_WORDS_FOR_LINE:
        for work in works:
            work.text = [
                line for line in work.text if len(line.split()) > MIN_WORDS_FOR_LINE
            ]

    if MAX_LINES:
        for work in works:
            work.text = sample(work.text, k=min(MAX_LINES, len(work.text)))

    client = chromadb.Client()
    collection = client.create_collection(name="shakespear")

    embed_works(works, collection=collection)

    for theme in ["War", "Love", "Greed", "Lust"]:
        print(f"\n\n{theme}")
        result = collection.query(query_texts=[theme], n_results=5)
        for title, text in zip(result["ids"][0], result["documents"][0], strict=True):
            print(f"\t{title}:\t{text}")


if __name__ == "__main__":
    main()
