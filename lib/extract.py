#extract.py
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from os import cpu_count
from lib.utils import BASE_URL

workers = min(32, (cpu_count() or 1) * 5)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 Chrome/121 Safari/537.36",
    "Connection": "keep-alive"
})
retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(
    pool_connections=workers * 2,
    pool_maxsize=workers * 2,
    max_retries=retries
)
session.mount("http://", adapter)
session.mount("https://", adapter)

CNPJ_REGEX = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")

INDUSTRIAL_REGEX = re.compile(
    r"(agrupamento\s+industrial\s+prioritário|atividade\s+industrial\s+relevante)",
    re.IGNORECASE
)
CENTRAL_REGEX = re.compile(
    r"central\s+de\s+distribui[cç][aã]o",
    re.IGNORECASE
)

IMPORTADOR_REGEX = re.compile(
    r"com[eé]rcio\s+importador\s+atacadista",
    re.IGNORECASE
)

LINK_REGEX = re.compile(r"/\?de\d+")

def extract_link(link, search_framing = True):
    r = session.get(link, timeout=(5, 30))
    r.raise_for_status()

    text = r.text

    cnpj = None
    framing = None

    # Extrai CNPJ
    match_cnpj = CNPJ_REGEX.search(text)
    if match_cnpj:
        cnpj = match_cnpj.group()

    if search_framing:
        if INDUSTRIAL_REGEX.search(text):
            framing = "I"

        elif CENTRAL_REGEX.search(text):
            framing = "C"

        elif IMPORTADOR_REGEX.search(text):
            framing = "P"

    return cnpj, framing, text

def extract_cnpj(decree):
    search_framing = decree.program == "PRODEPE" and decree.type == "C"
    try:
        cnpj, framing, text = extract_link(decree.link, search_framing)
        decree.cnpj = cnpj

        if not framing:
            match = LINK_REGEX.search(text)
            if match:
                link = BASE_URL + match.group()
                _, framing, _ = extract_link(link, True)

        decree.framing = framing

    except Exception as e:
        print(f"[ERROR] Decree {decree.number}: {e}")

    return decree

def populate_cnpjs_parallel(decrees):
    """
    Popula os CNPJs de uma lista de decretos em paralelo com barra de progresso.
    """
    updated_decrees = []

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
            dynamic_ncols=True):
                updated_decrees.append(future.result())

    return updated_decrees