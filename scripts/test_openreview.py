'''
Function:
    Implementation of Testing OpenReviewPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import random
import asyncio
from modules import OpenReviewPaperClient


'''test search function'''
async def test_search_venue():
    async with OpenReviewPaperClient(show_progress=True, progress_mode="auto", verbose=True) as client:
        paper_infos = await client.search(query="diffusion", venue_id="ICLR.cc/2024/Conference", total_results=20)
        print(f"Found {len(paper_infos)} papers")
        print(random.choice(paper_infos))

async def test_search_invitation():
    async with OpenReviewPaperClient() as client:
        paper_infos = await client.search(query="language model", invitation="ICLR.cc/2024/Conference/-/Submission", total_results=50)
        print(f"Found {len(paper_infos)} papers")
        print(random.choice(paper_infos))

asyncio.run(test_search_venue())
asyncio.run(test_search_invitation())


'''test download function'''
async def test_download():
    async with OpenReviewPaperClient(concurrency=5, show_progress=True, progress_mode="auto") as client:
        paper_infos = await client.search(query="multimodal", venue_id="ICLR.cc/2024/Conference", total_results=5)
        save_paths = await client.download(paper_infos, output_dir="downloads/OpenReviewPaperClient", overwrite=False)
        print('\n'.join([str(p) for p in save_paths]))

async def test_download_with_account():
    async with OpenReviewPaperClient(concurrency=5, show_progress=True, progress_mode="auto", username="your_email@example.com", password="your_password") as client:
        paper_infos = await client.search(query="multimodal", venue_id="ICLR.cc/2024/Conference", total_results=5)
        save_paths = await client.download(paper_infos, output_dir="downloads/OpenReviewPaperClient", overwrite=False)
        print('\n'.join([str(p) for p in save_paths]))

asyncio.run(test_download())
asyncio.run(test_download_with_account())