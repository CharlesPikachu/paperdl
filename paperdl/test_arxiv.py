'''
Function:
    Implementation of Testing ArxivPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import random
import asyncio
from modules import ArxivPaperClient


'''test search function'''
async def test_search():
    async with ArxivPaperClient(show_progress=True, progress_mode="auto", verbose=True) as client:
        paper_infos = await client.search("large language model", categories=["cs.CV", "cs.CL"], total_results=100, page_size=25)
        print(f"Found {len(paper_infos)} papers")
        print(random.choice(paper_infos))

asyncio.run(test_search())


'''test download function'''
async def test_download():
    async with ArxivPaperClient(concurrency=5, show_progress=True, progress_mode="auto", max_detail_tasks=10, verbose=True) as client:
        paper_infos = await client.querypage("vision language model", categories=["cs.CV"], max_results=8)
        save_paths = await client.download(paper_infos, output_dir="downloads/ArxivPaperClient", overwrite=False)
        print('\n'.join([str(p) for p in save_paths]))

asyncio.run(test_download())