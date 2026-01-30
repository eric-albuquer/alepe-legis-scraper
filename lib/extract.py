#extract.py
import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

CNPJ_REGEX = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")

def extract_cnpj(decree):
    """
    Dado um decreto (objeto com atributo .link), baixa o HTML e extrai o CNPJ.
    Retorna o decreto atualizado.
    """
    try:
        response = requests.get(decree.link, timeout=10)
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

def populate_cnpjs_parallel(decrees, num_workers=None):
    """
    Popula os CNPJs de uma lista de decretos em paralelo com barra de progresso.
    """
    if num_workers is None:
        num_workers = min(len(decrees), cpu_count())

    updated_decrees = []

    with Pool(num_workers) as pool:
        for decree in tqdm(
            pool.imap_unordered(extract_cnpj, decrees),
            total=len(decrees),
            desc="📝 Extraindo CNPJs",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            colour="green",
            ncols=120,
            unit="decreto",
            dynamic_ncols=True,
        ):
            updated_decrees.append(decree)

    return updated_decrees
