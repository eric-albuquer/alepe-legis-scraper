#extract.py
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from os import cpu_count

CNPJ_REGEX = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")

session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

def extract_cnpj(decree):
    """
    Dado um decreto (objeto com atributo .link), baixa o HTML e extrai o CNPJ.
    Retorna o decreto atualizado.
    """
    try:
        response = session.get(decree.link, timeout=120)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Busca todos os <p> do documento
        paragraphs = soup.find_all("p")
        cnpj_found = None

        for p in paragraphs:
            text = p.get_text()
            match = CNPJ_REGEX.search(text)
            if match:
                cnpj_found = match.group()
                break  # Pega o primeiro CNPJ encontrado

        if cnpj_found:
            decree.cnpj = cnpj_found

    except Exception as e:
        print(f"[ERROR] Decree {decree.number}: {e}")

    return decree  # Retorna o objeto atualizado

def populate_cnpjs_parallel(decrees):
    """
    Popula os CNPJs de uma lista de decretos em paralelo com barra de progresso.
    """
    updated_decrees = []

    workers = min((cpu_count() or 1) + 4, 15)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(extract_cnpj, d) for d in decrees]
        for future in tqdm(
            as_completed(futures),
            total=len(decrees),
            desc="📝 Extraindo CNPJs",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            colour="green",
            ncols=120,
            unit="decreto",
            dynamic_ncols=True,
        ):
            updated_decrees.append(future.result())

    return updated_decrees
