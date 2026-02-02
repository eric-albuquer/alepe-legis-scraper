# main.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from lib.scraper import setup_search, configure_page_size, scrape_all_pages
from lib.filter import filter_programs, filter_not_find
from lib.utils import *
from lib.extract import populate_cnpjs_parallel
import time
import os
from colorama import init

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
    init()

    print(TITLE + "\n========================================")
    print("🚀  ALEPE LEGIS SCRAPER")
    print("========================================")
    print(INFO + "Autor: Eric Gonçalves Albuquerque")
    print(INFO + "GitHub: https://github.com/eric-albuquer/alepe-legis-scraper\n" + RESET)

    print(TITLE + "📅 DEFINA O PERÍODO DE PESQUISA\n" + RESET)

    start_month, start_year, default = get_previous_month_date()
    end_month, end_year = None, None

    if not default:
        only_start = input(WARN + "📌  Deseja pesquisar apenas este mês? (aperte Enter para sim, qualquer tecla para não): " + RESET)
        
        if only_start:
            end_month, end_year, _ = get_previous_month_date()

    print(RESET, end="")

    driver = create_driver()

    try:
        start_time = time.time()

        print(INFO, end="")
        setup_search(driver, start_month, start_year, end_month, end_year)
        print(RESET, end="")
        
        total_pages = configure_page_size(driver)

        decrees = scrape_all_pages(driver, total_pages)

        result = filter_programs(decrees)

        print(INFO + f"\n📊 Total de decretos encontrados: {len(decrees)}")
        print(f"💼 Total de decretos PRODEPE/PROIND: {len(result)}" + RESET)
        
        not_find = filter_not_find(decrees)

        if not_find:
            print(ERROR + "\n" + "!" * 65)
            print("⚠️  ATENÇÃO — DECRETOS NÃO ENCONTRADOS")
            print("!" * 65)

            for start, end in not_find:
                if start == end:
                    print(f"❌ NÃO FOI ENCONTRADO O DECRETO: {start}")
                else:
                    print(f"❌ NÃO FORAM ENCONTRADOS DECRETOS NO INTERVALO: {start} ATÉ {end}")

            print("!" * 65 + "\n" + RESET)

        result = populate_cnpjs_parallel(result)

        sort_decrees(result)

        os.makedirs("./output", exist_ok=True)
        print(INFO + "\n💾 Salvando resultados nos formatos JSON, XLSX e CSV na pasta ./output" + RESET)
        save_to_excel(result, "./output/decretos.xlsx")
        save_to_json(result, "./output/decretos.json")
        save_to_csv(result, "./output/decretos.csv")

        print(SUCCESS + "GRAVAÇÃO CONCLUIDA" + RESET)

        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        print(INFO + f"\n⏱️  TEMPO TOTAL DE EXECUÇÃO: {mins:02}:{secs:02}" + RESET)
        print(SUCCESS + "🎉 PROCESSO FINALIZADO COM SUCESSO!" + RESET)

    finally:
        driver.quit()
        input(WARN + "\nPressione ENTER para encerrar o programa" + RESET)

if __name__ == "__main__":
    import sys
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    main()