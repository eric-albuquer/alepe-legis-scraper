# main.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lib.scraper import setup_search, configure_page_size, scrape_all_pages
from lib.filter import filter_programs
from lib.utils import save_to_excel, save_to_json, save_to_csv
from lib.extract import populate_cnpjs_parallel
import time
from datetime import date
import os

def create_driver():
    chrome_options = Options()

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=800,600")

    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    prefs = {
        "profile.default_content_setting_values.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.default_content_setting_values.fonts": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream": 2,
    }

    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(0)

    return driver

def main():
    MONTH = 0
    while True:
        MONTH = int(input("Mês: "))
        if MONTH >= 1 and MONTH <= 12:
            break
        print("Mês inválido")

    YEAR = 0
    while True:
        YEAR = int(input("Ano: "))
        if YEAR > 0:
            break
        print("Ano inválido")

    if YEAR < 100:
        if YEAR <= date.today().year:
            YEAR += 2000
        else:
            YEAR += 1900

    driver = create_driver()

    try:
        start_time = time.time()
        t = start_time
        print("Inciando pesquisa...")
        setup_search(driver, MONTH, YEAR)
        
        total_pages = configure_page_size(driver)
        print(f"Parâmetros de pesquisa concluídos em {time.time() - t:.2f}s\n")

        t = time.time()
        decrees = scrape_all_pages(driver, total_pages)
        print(f"Coleta de decretos concluída em {time.time() - t:.2f}s\n")

        result = filter_programs(decrees)
        print("Total de decretos encontrados:", len(decrees))
        print("Total de decretos PRODEPE/PROIND:", len(result), "\n")

        t = time.time()
        result = populate_cnpjs_parallel(result)
        print(f"Extração de CNPJ concluída em {time.time() - t:.2f}s\n")

        t = time.time()
        os.makedirs("./output", exist_ok=True)
        save_to_excel(result, "./output/programas.xlsx")
        save_to_json(result, "./output/programas.json")
        save_to_csv(result, "./output/programas.csv")
        print(f"Gravação concluida em {time.time() - t:.2f}s\n")

        print(f"Tempo total de execução {time.time() - start_time:.2f}s")
        print("Terminou!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
