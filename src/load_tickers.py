import os
import asyncio

import aiocsv
import aiofiles
import pandas as pd


async def load_tickers():
    try:
        directories = os.listdir("country_sector")
        directories.sort()

        countries = {}
        for directory in directories:
            files = os.listdir(f"country_sector/{directory}")
            files.sort()

            countries[directory] = files

        total = 0
        tickers: list[dict[str, str]] = []
        for country, files in countries.items():
            for file in files:
                local_total = 0

                async with aiofiles.open(f"country_sector/{country}/{file}", "r") as f:
                    reader = aiocsv.AsyncReader(f)

                    await reader.__anext__()

                    async for row in reader:
                        local_total += 1
                        tickers.append(
                            {
                                "ticker": row[0],
                                "name": row[1],
                                "country": country,
                                "sector": file.replace(f"{country}_", "").replace(
                                    "_tickers.csv", ""
                                ),
                            }
                        )

                total += local_total

        print(f"Total Rows: {total}")

        df = pd.DataFrame(tickers)
        df.to_csv("all_tickers/tickers.csv", index=False)
    except Exception as e:
        print(f"Error in load_tickers: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(load_tickers())
