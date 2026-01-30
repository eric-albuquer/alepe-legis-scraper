# main.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from lib.scraper import setup_search, configure_page_size, scrape_all_pages
from lib.filter import filter_programs
from lib.utils import save_to_excel, save_to_json, save_to_csv, get_month_input, get_year_input
from lib.extract import populate_cnpjs_parallel
import time
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

    service = Service(executable_path="chromedriver.exe")

    driver = webdriver.Chrome(options=chrome_options, service=service)

    driver.implicitly_wait(0)

    return driver

def main():
    print("\n=== Alepe Legis Scraper ===")
    print("Autor: Eric Gonçalves Albuquerque")
    print("GitHub: https://github.com/eric-albuquer/alepe-legis-scraper\n")

    start_month = get_month_input("➡️  Digite o Mês de início (1-12): ")
    start_year = get_year_input("➡️  Digite o Ano de início (ex: 2026): ")

    only_start = input("📌  Deseja pesquisar apenas este mês? (aperte Enter para não, qualquer tecla para sim): ")

    end_month, end_year = None, None
    if only_start:
        end_month = get_month_input("➡️  Digite o Mês de fim (1-12): ")
        end_year = get_year_input("➡️  Digite o Ano de fim (ex: 2026): ")

    print("\n🔎  Iniciando pesquisa...\n")

    driver = create_driver()

    try:
        start_time = time.time()
        t = start_time

        print("🔎 Configurando parâmetros de pesquisa...")
        setup_search(driver, start_month, start_year, end_month, end_year)
        
        total_pages = configure_page_size(driver)
        print(f"✅ Parâmetros de pesquisa configurados em {time.time() - t:.2f}s\n")

        t = time.time()
        print(f"📄 Coletando decretos de {total_pages} página(s)...")
        decrees = scrape_all_pages(driver, total_pages)
        print(f"✅ Coleta de decretos concluída em {time.time() - t:.2f}s\n")

        result = filter_programs(decrees)
        print(f"📊 Total de decretos encontrados: {len(decrees)}")
        print(f"💼 Total de decretos PRODEPE/PROIND: {len(result)}\n")

        t = time.time()
        print("🔍 Extraindo CNPJs das empresas associadas aos decretos...")
        result = populate_cnpjs_parallel(result)
        print(f"✅ Extração de CNPJs concluída em {time.time() - t:.2f}s\n")

        t = time.time()
        os.makedirs("./output", exist_ok=True)
        print("💾 Salvando resultados nos formatos JSON, XLSX e CSV...")
        save_to_excel(result, "./output/programas.xlsx")
        save_to_json(result, "./output/programas.json")
        save_to_csv(result, "./output/programas.csv")
        print(f"✅ Gravação concluída em {time.time() - t:.2f}s\n")

        print(f"⏱️ Tempo total de execução: {time.time() - start_time:.2f}s")
        print("🎉 Processo finalizado com sucesso!")

    finally:
        driver.quit()
        input("Pressione ENTER para encerrar o programa")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn")

    main()