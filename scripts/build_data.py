#!/usr/bin/env python3
"""
Bygger data/avtaler.json for Finn avtale fra kildefilen scripts/kilde_leverandorer.csv.

Kjør på nytt hver gang leverandørregisteret oppdateres:
    python3 scripts/build_data.py

Prinsipp: kun feltene prosjektledere faktisk trenger tas med (leverandørnavn,
kategori, produkttyper, bestillings-/rabattvilkår i fritekst, betalingsfrist,
kontaktpersoner). Ingen finansielle detaljer utover det som allerede lå i
kildefilen som fritekst-vilkår.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

HER = Path(__file__).parent
KILDE = HER / "kilde_leverandorer.csv"
UT = HER.parent / "data" / "avtaler.json"


_TRANSLITERASJON = str.maketrans({
    "æ": "ae", "Æ": "AE",
    "ø": "o", "Ø": "O",
    "å": "a", "Å": "A",
})


def slugify(navn: str) -> str:
    s = navn.translate(_TRANSLITERASJON).lower()
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def del_opp_kontakter(raw: str):
    """Splitter en fritekst-kontaktblokk i én eller flere regionale kontakter.

    Kildedataene er ustrukturerte (kopiert fra e-post/Excel), så dette er en
    beste-innsats-parsing: vi leter etter regionnavn (Rogaland, Agder, osv.)
    som seksjonsoverskrifter, og samler resten som fritekst per seksjon.
    """
    if not raw:
        return []
    raw = raw.strip()
    regioner = [
        "Rogaland", "Agder", "Vestland", "Vestlandet", "Bergen", "Hordaland",
        "Sogn & Fjordane", "Sogn og Fjordane", "Sørlandet",
    ]
    pattern = re.compile(
        r"^\s*(" + "|".join(re.escape(r) for r in regioner) + r")\s*:?\s*",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(pattern.finditer(raw))
    if not matches:
        # Ingen regionsoverskrifter funnet - én samlet kontaktblokk
        tekst = re.sub(r"\s+", " ", raw).strip()
        return [{"region": None, "tekst": tekst}] if tekst else []

    kontakter = []
    for i, m in enumerate(matches):
        region = m.group(1)
        start = m.end()
        slutt = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        tekst = re.sub(r"\s+", " ", raw[start:slutt]).strip(" :\n")
        if tekst:
            kontakter.append({"region": region, "tekst": tekst})
    return kontakter


# Leverandører uten mottatt/signert avtaledokument ennå (holdes i registeret,
# men markert slik at Finn avtale kan vise dem annerledes eller utelate dem).
MANGLER_AVTALEDOKUMENT = {"service-master-as", "arti-konsult"}


def parse_rad(rad):
    navn, kategori, produkttyper, vilkar, frist, kontakt_raw = (
        (f or "").strip() for f in rad
    )
    if not navn:
        return None
    id_ = slugify(navn)
    return {
        "id": id_,
        "leverandornavn": navn,
        "kategori": kategori or None,
        "produkttyper": produkttyper or None,
        "rabatt_og_bestillingsvilkar": vilkar or None,
        "betalingsfrist": frist or None,
        "kontakter": del_opp_kontakter(kontakt_raw),
        "gyldig_til": None,  # fylles inn etter hvert som avtaledatoer verifiseres mot kontraktene
        "sist_oppdatert": None,
        "status": "mangler_avtaledokument" if id_ in MANGLER_AVTALEDOKUMENT else "har_avtale",
    }


def main():
    with open(KILDE, encoding="utf-8") as f:
        reader = csv.reader(f)
        rader = list(reader)

    header, *datarader = rader
    avtaler = []
    for rad in datarader:
        # pad ut rader som mangler kolonner
        rad = rad + [""] * (6 - len(rad))
        parsed = parse_rad(rad[:6])
        if parsed:
            avtaler.append(parsed)

    UT.parent.mkdir(parents=True, exist_ok=True)
    with open(UT, "w", encoding="utf-8") as f:
        json.dump(avtaler, f, ensure_ascii=False, indent=2)

    print(f"Skrev {len(avtaler)} avtaler til {UT}")


if __name__ == "__main__":
    main()
