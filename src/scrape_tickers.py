import asyncio
from playwright.async_api import async_playwright, Page
import aiofiles
from aiocsv import AsyncWriter
import json


async def write_file_async(filename: str, data_rows: list[list[str]], type: str):
    try:
        async with aiofiles.open(filename, mode='w', encoding='utf-8', newline='') as afp:
            if type == "csv":
                writer = AsyncWriter(afp)
                await writer.writerows(data_rows)
            elif type == "json":
                await afp.write(json.dumps(data_rows, indent=4))

    except (IOError, OSError) as e:
        print(f"Error writing to file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def find_and_click_button(page: Page, css_locator: str):
    try:
        buttons_to_click = await page.locator(css_locator).all()

        if len(buttons_to_click) == 0:
            raise Exception("No buttons found with the specified CSS selector.")
        
        if len(buttons_to_click) > 1:
            raise Exception("Multiple buttons found with the specified CSS selector.")
        
        if await buttons_to_click[0].is_enabled():
            await buttons_to_click[0].click()
            return True
        else:
            False

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    

async def select_option(page: Page, button_css_locator: str, option_css_locator: str, submit_css_locator: str, option: str):
    try:
        await find_and_click_button(page, button_css_locator)

        options = await page.locator(option_css_locator).all()

        for option_element in options:
            option_text = await option_element.locator("span").inner_text()
            option_checked = await option_element.locator("input[type='checkbox']").is_checked()

            if option_text == option and not option_checked:
                await option_element.click()
            elif option_text != option and option_checked:
                await option_element.click()

        button_clicked = await find_and_click_button(page, submit_css_locator)

        if not button_clicked:
            await find_and_click_button(page, button_css_locator)

        await asyncio.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    

async def retrieve_options(page: Page, button_css_locator: str, option_css_locator: str):
    try:
        option_labels = []

        await find_and_click_button(page, button_css_locator)

        options = await page.locator(option_css_locator).all()

        for option in options:
            option_text = await option.inner_text()
            option_labels.append(option_text)

        await find_and_click_button(page, button_css_locator)

        return option_labels

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    

async def table_pagination(page: Page, tickers: list[tuple[str, str]], country: str, sector: str):
    try:
        rows = await page.locator("table tbody tr").all()

        for row in rows:
            tickers.append([(await row.locator("td:nth-child(2)").inner_text()).split("\n")[-1], 
                            await row.locator("td:nth-child(3)").inner_text()])
            
        next_button = await page.locator("button[aria-label='Goto next page']").all()
        
        if len(next_button) > 1:
            raise Exception("Multiple next buttons found with the specified CSS selector.")

        await write_file_async(f"{country}_{sector}_tickers.csv", tickers, "csv")

        if len(next_button) == 1 and await next_button[0].is_enabled():
            await next_button[0].click()
            await asyncio.sleep(5)

            return True
        else:
            print("Next button is disabled." if len(next_button) == 1 else "Next button not found.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    

async def generate_country_sector():
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(
                headless=False,
            )
            page = await browser.new_page()
            x = await page.goto("https://finance.yahoo.com/research-hub/screener/equity/?start=0&count=100")

            if x.status != 200:
                raise Exception(f"Failed to load page, status code: {x.status}")

            await asyncio.sleep(3)

            await find_and_click_button(page, "span:text('Explore and add more filters') button")

            await asyncio.sleep(2)

            countries_text = await retrieve_options(page, "button:has(div:text('Region'))", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] label span")

            await asyncio.sleep(2)

            sectors_text = await retrieve_options(page, "button:has(div:text('Sector'))", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] label span")

            country_sector = {}
            for country in countries_text:
                for sector in sectors_text:
                    country_sector[f"{country}_{sector}"] = False

            return country_sector
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    finally:
        await browser.close()


async def scrape_tickers():
    try:
        country_sector_list: dict[str, bool] = await generate_country_sector()

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(
                    headless=False,
                )
                page = await browser.new_page()
                x = await page.goto("https://finance.yahoo.com/research-hub/screener/equity/?start=0&count=100", timeout=1000000)

                if x.status != 200:
                    raise Exception(f"Failed to load page, status code: {x.status}")

                await asyncio.sleep(3)

                await find_and_click_button(page, "span:text('Explore and add more filters') button")
                await asyncio.sleep(2)

                for country_sector, _ in country_sector_list.items():
                    country = country_sector.split("_")[0]
                    sector = country_sector.split("_")[1]
                        
                    await select_option(page, "button:has(div:text('Region'))", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] label", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] .submit button", country)

                    await select_option(page, "button:has(div:text('Sector'))", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] label", ".dialog-container.menu-surface-dialog.modal[aria-hidden='false'] .submit button", sector)

                    tickers = [["Ticker", "Name"]]

                    print(f"Scraping tickers for {country} - {sector}")
                    next_button_enabled = True
                    while next_button_enabled:
                        next_button_enabled = await table_pagination(page, tickers, country, sector)
                    print(f"Finished scraping tickers for {country} - {sector} with {len(tickers) - 1} tickers")

                    country_sector_list[country_sector] = True

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            await browser.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

if __name__ == "__main__":

    asyncio.run(scrape_tickers())