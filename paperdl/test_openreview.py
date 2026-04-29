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
        paper_infos = await client.search(query="diffusion", venue_id="ICLR.cc/2024/Conference", max_results=20)
        print(f"Found {len(paper_infos)} papers")
        print(random.choice(paper_infos))

asyncio.run(test_search_venue())


# async def main():
#     async with OpenReviewPaperClient() as client:
#         papers = await client.search(
#             query="language model",
#             invitation="ICLR.cc/2024/Conference/-/Submission",
#             max_results=50,
#         )

#         print(len(papers))

# asyncio.run(main())


# async def main():
#     async with OpenReviewPaperClient(
#         concurrency=5,
#         show_progress=True,
#         progress_mode="auto",
#     ) as client:
#         papers = await client.search(
#             query="multimodal",
#             venue_id="ICLR.cc/2024/Conference",
#             max_results=5,
#         )

#         paths = await client.download_many(
#             papers,
#             output_dir="downloads/openreview",
#             overwrite=False,
#         )

#         for path in paths:
#             print(path)

# asyncio.run(main())


# async def main():
#     async with OpenReviewPaperClient(
#         concurrency=5,
#         show_progress=True,
#         progress_mode="auto",
#     ) as client:
#         papers = await client.search(
#             query="multimodal",
#             venue_id="ICLR.cc/2024/Conference",
#             max_results=5,
#         )

#         paths = await client.download_many(
#             papers,
#             output_dir="downloads/openreview",
#             overwrite=False,
#         )

#         for path in paths:
#             print(path)

# asyncio.run(main())


# async with OpenReviewPaperClient(
#     username="your_email@example.com",
#     password="your_password",
# ) as client:
#     papers = await client.search(
#         venue_id="Your/Venue/ID",
#         max_results=10,
#     )

#     await client.download_paper(
#         papers[0],
#         output_dir="downloads/openreview",
#         prefer_attachment_api=True,
#     )