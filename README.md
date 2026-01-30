# Alepe Legis Scraper

Automated web scraper for collecting public legislative data from the ALEPE website and exporting results to JSON, XLSX, and CSV formats.

---

## 🔹 Overview

This project automates the extraction of decrees from [ALEPE](https://legis.alepe.pe.gov.br) related to incentive programs **PRODEPE** and **PROIND**. It combines dynamic interaction with Selenium, static scraping with BeautifulSoup, and parallel processing using `multiprocessing` for high-speed data collection.

The scraper performs three main stages:

1. **Search Automation**
   - Opens the advanced search page.
   - Inserts standardized search terms (specific to PRODEPE and PROIND).
   - Allows the user to set a search period.
   - Automates form submission on the dynamic ASPX website using Selenium.
   - Iterates through multiple pages of the results table, collecting:
     - Decree number
     - Date
     - Summary (ementa)
     - Links to detailed decree pages
     - Company names
     - Related decrees

2. **Data Extraction**
   - Opens each decree detail link.
   - Extracts company CNPJs and other detailed information.
   - Uses **BeautifulSoup** for static page parsing.
   - Speeds up the process with a **multiprocessing pool**.

3. **Filtering and Export**
   - Further processes the decree summaries to extract additional insights.
   - Exports the final dataset in **JSON**, **XLSX**, and **CSV** formats.

---

## 🔹 Features

- Automated search on ALEPE advanced search.
- Extracts multiple pages of results automatically.
- Retrieves decree number, date, summary, company names, related decrees, and CNPJs.
- Parallelized extraction using multiprocessing for improved performance.
- Saves output in three formats: JSON, XLSX, CSV.
- Configurable search period.

---

## 🔹 Installation

1. Clone the repository:

```bash
git clone https://github.com/seuusuario/alepe-legis-scraper.git
cd alepe-legis-scraper
```

2. Install dependencies (recommended in a virtual environment):

```bash
pip install -r requirements.txt
```

Dependencies:
- selenium
- beautifulsoup4
- pandas
- openpyxl (for XLSX support)
- requests

## 🔹 Usage

```bash
python main.py
```

Outputs will be saved in the output/ folder as:
- programas.json
- programas.xlsx
- programas.csv

## 🔹 Folder Structure

```text
alepe-legis-scraper/
│
├─ lib/                # scraping source code
│   ├─ __init__.py
│   ├─ extract.py
│   ├─ filter.py
│   ├─ models.py
│   ├─ scraper.py
│   └─ utils.py
│
├─ output/             # automatically generated output files
│   ├─ programas.csv
│   ├─ programas.json
│   └─ programas.xlsx
│
├─ main.py             # main script
├─ requirements.txt    # Python dependencies
├─ README.md
└─ .gitignore
```

## 🔹 Notes

- Make sure to have the correct WebDriver installed for Selenium (e.g., ChromeDriver or GeckoDriver) compatible with your browser version.

- The scraper was designed for public data. Ensure ethical use and compliance with website terms of use.

- The output/ folder is ignored in Git via .gitignore.

## 🔹 License

MIT License © [Eric Gonçalves Albuquerque]