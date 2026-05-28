'''
Function:
    Test search and download for PMLRPaperClient
'''
import asyncio
from pathlib import Path
from modules import PMLRPaperClient


QUERY = "diffusion"
TOTAL_RESULTS = 5
DOWNLOAD_RESULTS = 2
OUTPUT_DIR = Path("downloads/PMLRPaperClient")


async def main() -> None:
    async with PMLRPaperClient(
        concurrency=3,
        show_progress=True,
        progress_mode="auto",
        verbose=True,
    ) as client:
        paper_infos = await client.search(
            QUERY,
            total_results=TOTAL_RESULTS,
        )
        print(f"Found {len(paper_infos)} PMLR papers")
        for index, paper_info in enumerate(paper_infos, start=1):
            print(f"{index}. {paper_info.title}")

        selected_papers = paper_infos[:DOWNLOAD_RESULTS]
        if not selected_papers:
            print("No PMLR papers to download")
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
