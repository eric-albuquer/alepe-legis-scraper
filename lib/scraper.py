# scraper.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm
import calendar, math, time
from .models import Decree
from .utils import extract_decree_number, wait_table_loaded, is_page_active, find_page_link, is_first_page_group

BASE_URL = "https://legis.alepe.pe.gov.br/"
SEARCH_URL = BASE_URL + "pesquisaAvancada.aspx"

PAGE_SIZE = 200
WAIT_TIME = 15

def setup_search(driver, MONTH = 1, YEAR = 2026):
    """Open ALEPE search page, select Decreto, set date range, and click search."""
    driver.get(SEARCH_URL)
    driver.find_element(By.ID, "cblTipoNorma_3").click()
    driver.find_element(By.ID, "li-publicacao").click()

    first_day = 1
    last_day = calendar.monthrange(YEAR, MONTH)[1]

    start_input = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.ID, "tbxDataInicialPublicacao"))
    )
    end_input = driver.find_element(By.ID, "tbxDataFinalPublicacao")

    start_date = f"{first_day:02}/{MONTH:02}/{YEAR}"
    end_date = f"{last_day:02}/{MONTH:02}/{YEAR}"

    print(f"Buscando decretos no intervalo de\n{start_date}\n{end_date}")

    start_input.clear()
    start_input.send_keys(start_date)

    end_input.clear()
    end_input.send_keys(end_date)

    driver.find_element(By.ID, "btnPesquisar").click()

def configure_page_size(driver):
    qty_label = WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.ID, "lblQtd"))
    )
    total_results = int(qty_label.text.strip())

    total_pages = 1
    if total_results > 100:
        total_pages = math.ceil(total_results / PAGE_SIZE)
        select = Select(driver.find_element(By.ID, "ddlTamPagina"))
        select.select_by_value(str(PAGE_SIZE))
        wait_table_loaded(driver, WAIT_TIME)

    print(f"Resultados: {total_results}, Páginas: {total_pages}")
    return total_pages

def extract_page_data(driver, buffer):
    """Extract all decrees on current page."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("#secResultado tbody tr")
    for row in rows:
        name_anchor = row.select_one("span.nome-norma > a")
        publish_span = row.select_one("span.publicacao")
        summary_div = row.select_one("td.ementa-norma > div.fLeft")
        if not name_anchor or not summary_div:
            continue
        number = extract_decree_number(name_anchor.get_text(strip=True))
        link = BASE_URL + name_anchor["href"]
        publish_date = publish_span.get_text(strip=True)[-10:]
        summary = summary_div.get_text(strip=True)
        buffer.append(Decree(number, publish_date, link, summary))

def scrape_all_pages(driver, total_pages):
    all_data = []
    current_page = 0
    start_time_total = time.time()

    page_iter = tqdm(range(1, total_pages + 1), desc="Coletando páginas", unit="page")

    while current_page < total_pages:
        for _ in range(5):
            current_page += 1
            if current_page > total_pages:
                return all_data
            if total_pages > 1:
                page_link = find_page_link(driver, current_page)
                if page_link:
                    driver.execute_script("arguments[0].click();", page_link)
                    WebDriverWait(driver, WAIT_TIME).until(
                        lambda d: is_page_active(d, current_page)
                    )

            extract_page_data(driver, all_data)
            page_iter.update(1)

        # Próximo grupo
        try:
            next_button = driver.find_element(By.ID, "lbtnProx")
            driver.execute_script("arguments[0].click();", next_button)
            WebDriverWait(driver, WAIT_TIME).until(lambda d: is_first_page_group(d))
        except:
            break

    page_iter.close()
    print(f"Scraping completed in {time.time() - start_time_total:.2f}s")
    return all_data