# utils.py
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

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

def save_to_json(decrees, filename="decrees.json"):
    """Save a list of Decree objects to a JSON file."""
    data = [d.to_dict() for d in decrees]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Arquivo JSON salvo em {filename}")

def save_to_excel(data, filename):
    """
    Salva uma lista de Decree em uma planilha Excel.
    Cada linha terá: número, data de publicação, programa, CNPJ e empresa.
    """
    rows = [d.to_row() for d in data]
    df = pd.DataFrame(rows, columns=["Número", "Data Publicação", "Programa", "Tipo", "ConcOrig", "CNPJ", "Empresa", "Link", "Ementa"])
    df.to_excel(filename, index=False)
    print(f"Arquivo EXCEL salvo em {filename}")

def save_to_csv(data, filename="decrees.csv"):
    """
    Salva uma lista de Decree em um arquivo CSV.
    Cada linha terá: número, data de publicação, programa, CNPJ e empresa.
    """
    rows = [d.to_row() for d in data]
    df = pd.DataFrame(rows, columns=["Número", "Data Publicação", "Programa", "Tipo", "ConcOrig", "CNPJ", "Empresa", "Link", "Ementa"])
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Arquivo CSV salvo em {filename}")