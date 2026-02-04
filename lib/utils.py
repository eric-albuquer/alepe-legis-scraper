# utils.py
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from datetime import date
from colorama import Fore, Style

BASE_URL = "https://legis.alepe.pe.gov.br/"

SUCCESS = Fore.GREEN + Style.BRIGHT
INFO = Fore.CYAN + Style.BRIGHT
WARN = Fore.YELLOW + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
TITLE = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL

NUMBER_REGEX = re.compile(r"\d[\d\.]*")

def extract_decree_number(text):
    """Extract decree number from a string."""
    match = NUMBER_REGEX.search(text)
    if match:
        return int(match.group().replace(".", ""))
    return -1

def wait_table_loaded(driver, wait_time):
    """Wait until results table has rows."""
    WebDriverWait(driver, wait_time).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#secResultado table tbody tr")) > 0
    )

def is_page_active(driver, page_number):
    links = driver.find_elements(By.CSS_SELECTOR, "nav.nav-pagination a")
    for link in links:
        if "active" in link.get_attribute("class") and link.text.strip() == str(page_number):
            return True
    return False

def is_first_page_group(driver):
    try:
        active = driver.find_element(By.CSS_SELECTOR, "nav.nav-pagination a.active")
        return active.get_attribute("id") == "lbtn1"
    except:
        return False

def find_page_link(driver, page_number):
    links = driver.find_elements(By.CSS_SELECTOR, "nav.nav-pagination a")
    for link in links:
        if link.text.strip() == str(page_number):
            return link
    return None

def sort_decrees(decrees):
    decrees.sort(key=lambda x: x.number)

def save_to_json(decrees, filename="decrees.json"):
    """Save a list of Decree objects to a JSON file."""
    data = [d.to_dict() for d in decrees]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_excel(data, filename):
    """
    Salva uma lista de Decree em uma planilha Excel.
    Cada linha terá: número, data de publicação, programa, CNPJ e empresa.
    """
    rows = [d.to_row() for d in data]
    df = pd.DataFrame(rows, columns=["Número", "Data Publicação", "Programa", "Tipo", "Enquadramento", "ConcOrig", "CNPJ", "Empresa", "Link", "ID", "Ementa"])
    df.to_excel(filename, index=False)

def save_to_csv(data, filename="decrees.csv"):
    """
    Salva uma lista de Decree em um arquivo CSV.
    Cada linha terá: número, data de publicação, programa, CNPJ e empresa.
    """
    rows = [d.to_row() for d in data]
    df = pd.DataFrame(rows, columns=["Número", "Data Publicação", "Programa", "Tipo", "Enquadramento", "ConcOrig", "CNPJ", "Empresa", "Link", "ID", "Ementa"])
    df.to_csv(filename, index=False, encoding="utf-8-sig")

from datetime import date

def get_previous_month_date():
    """
    Solicita ao usuário mês e ano. 
    Se não digitar nada em ambos, retorna o mês anterior e ano correto.
    Retorna: (month, year)
    """
    today = date.today()

    # Calcula mês e ano do mês anterior automaticamente
    if today.month == 1:
        default_month = 12
        default_year = today.year - 1
    else:
        default_month = today.month - 1
        default_year = today.year

    default = False

    # ---------------- MÊS ----------------
    while True:
        user_input = input(INFO + f"➡️  Digite o MÊS (ENTER = {default_month:02}/{default_year:04}): " + RESET).strip()
        if not user_input:
            return default_month, default_year, True
        try:
            month = int(user_input)
        except ValueError:
            print(ERROR + "Entrada inválida! Digite um número de 1 a 12." + RESET)
            continue

        if 1 <= month <= 12:
            break
        print(WARN + "Mês inválido! Deve ser entre 1 e 12." + RESET)

    # ---------------- ANO ----------------
    while True:
        user_input = input(INFO + f"➡️  Digite o ANO: " + RESET).strip()

        try:
            year = int(user_input)
        except ValueError:
            print(ERROR + "Entrada inválida! Digite um número para o ano." + RESET)
            continue

        if year <= 0:
            print(WARN + "Ano inválido! Deve ser maior que zero." + RESET)
            continue

        # Converte anos com 2 dígitos para 4 dígitos
        if year < 100:
            current_year = date.today().year
            if year <= current_year % 100:
                year += 2000
            else:
                year += 1900

        break

    return month, year, False