# filter.py
import re

# Compilando regex uma única vez
RE_DENOMINADA = re.compile(r"denominada\s+(.+)", re.IGNORECASE)
RE_EMPRESA = re.compile(r"empresa\s+(.+)", re.IGNORECASE)
RE_CONTRIBUINTE = re.compile(r"contribuinte\s+(.+)", re.IGNORECASE)
RE_ORIGINAL = re.compile(r"\d{2,3}\.\d{3}")

def filter_programs(decrees):
    """Filter decrees for PRODEPE or PROIND programs."""
    filtered = []

    for decree in decrees:
        summary = decree.summary

        if "PRODEPE" in summary:
            decree.program = "PRODEPE"

            match = RE_DENOMINADA.search(summary)
            if match:
                decree.company = match.group(1).strip()
            else:
                match = RE_EMPRESA.search(summary)
                if match:
                    decree.company = match.group(1).strip()

            if "Concede" in summary:
                decree.type = 'C'
                decree.origin_decree = [decree.number]
            else:
                if "Introduz alterações" in summary:
                    decree.type = 'A'
                elif "prorrogaç" in summary:
                    decree.type = 'P'
                elif "renovaç" in summary:
                    decree.type = 'R'
                elif "transferência" in summary:
                    decree.type = 'T'

                match = RE_ORIGINAL.findall(summary)
                if match:
                    decree.origin_decree = [int(n.replace(".", "")) for n in match]

        elif "PROIND" in summary:
            decree.program = "PROIND"

            match = RE_CONTRIBUINTE.search(summary)
            if match:
                decree.company = match.group(1).strip()

            if "Autoriza" in summary:
                decree.type = 'C'

            decree.origin_decree = [decree.number]

        if decree.program:
            filtered.append(decree)

    return filtered