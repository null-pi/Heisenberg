import asyncio
from playwright.async_api import async_playwright


async def scrape_proxy_servers() -> list[dict[str, str]]:
    try:
        proxies = []

        async with async_playwright() as p:
            browser = await p.firefox.launch(
                headless=True
            )
            page = await browser.new_page()

            x = await page.goto("https://www.proxynova.com/proxy-server-list/elite-proxies/")
        
            if x.status != 200:
                raise Exception(f"Failed to load page, status code: {x.status}")

            rows = await page.locator("table#tbl_proxy_list tbody tr").all()

            for row in rows:
                ip = await row.locator("td:nth-child(1)").inner_text()
                port = await row.locator("td:nth-child(2)").inner_text()
                last_checked = (await row.locator("td:nth-child(3)").inner_text()).split(" ")[0]
                speed = (await row.locator("td:nth-child(4)").inner_text()).split(" ")[0]
                uptime = (await row.locator("td:nth-child(5)").inner_text()).split(" ")[0].replace("%", "")

                proxies.append({
                    "ip": ip,
                    "port": port,
                    "speed": speed,
                    "uptime": uptime,
                    "last_checked": last_checked
                })

        best_proxies = sorted(proxies, key=lambda x: (float(x["uptime"]) * float(x["speed"])), reverse=True)[:10]
        
        return best_proxies
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        await browser.close()
    

if __name__ == "__main__":
    asyncio.run(scrape_proxy_servers())