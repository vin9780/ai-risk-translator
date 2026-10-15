import asyncio
import time


async def fetch_book_risk(book: str) -> str:
    print(f"start {book}")
    await asyncio.sleep(1)          # simulates a 1-second API call
    print(f"done  {book}")
    return f"{book}: ok"


async def sequential():
    results = []
    for book in ["RATES", "CREDIT", "FX"]:
        results.append(await fetch_book_risk(book))
    return results


async def concurrent():
    return await asyncio.gather(
        fetch_book_risk("RATES"),
        fetch_book_risk("CREDIT"),
        fetch_book_risk("FX"),
    )


if __name__ == "__main__":
    start = time.perf_counter()
    print(asyncio.run(sequential()))
    print(f"sequential: {time.perf_counter() - start:.1f}s\n")

    start = time.perf_counter()
    print(asyncio.run(concurrent()))
    print(f"concurrent: {time.perf_counter() - start:.1f}s")