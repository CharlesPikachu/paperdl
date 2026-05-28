'''
Function:
    Test search and download for OpenReviewPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import asyncio
from pathlib import Path
from modules import OpenReviewPaperClient


QUERY = "language model"
VENUE_ID = "ICLR.cc/2024/Conference"
TOTAL_RESULTS = 5
DOWNLOAD_RESULTS = 2
OUTPUT_DIR = Path("downloads/OpenReviewPaperClient")


async def main() -> None:
    async with OpenReviewPaperClient(
        concurrency=3,
        show_progress=True,
        progress_mode="auto",
        verbose=True,
    ) as client:
        paper_infos = await client.search(
            query=QUERY,
            venue_id=VENUE_ID,
            total_results=TOTAL_RESULTS,
        )
        print(f"Found {len(paper_infos)} OpenReview papers")
        for index, paper_info in enumerate(paper_infos, start=1):
            print(f"{index}. {paper_info.title}")

        selected_papers = paper_infos[:DOWNLOAD_RESULTS]
        if not selected_papers:
            print("No OpenReview papers to download")
            return

        save_paths = await client.download(
            selected_papers,
            output_dir=OUTPUT_DIR,
            overwrite=False,
            return_exceptions=True,
        )
        for result in save_paths:
            if isinstance(result, Exception):
                print(f"[FAILED] {type(result).__name__}: {result}")
            else:
                print(f"[OK] {result}")


if __name__ == "__main__":
    asyncio.run(main())
