import asyncio
import os
import pandas as pd


async def count_datasize():
    try:
        directories = os.listdir("ticker_quotes")
        directories.sort()

        total = 0
        for idx, d in enumerate(directories):
            df = pd.read_csv(f"ticker_quotes/{d}")

            total += len(df)

            if idx % 1000 == 0 and idx != 0:
                print(f"Processed {idx} files, current total: {total}")

        print(f"Total Rows: {total}")

    except Exception as e:
        print(f"Error in count_datasize: {e}")
        return None
    

if __name__ == "__main__":
    asyncio.run(count_datasize())