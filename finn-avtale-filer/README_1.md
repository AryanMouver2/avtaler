# Finn avtale

Skrivebeskyttet søkeside for prosjektledere i Mouvers medlemsbedrifter — for å
finne hvilken leverandøravtale som gjelder når de skal bestille noe til et
prosjekt.

Viser kun: leverandørnavn, kategori/produktområde, rabatt- og
bestillingsvilkår, betalingsfrist, kontaktperson hos leverandøren og
avtalens status. Viser **aldri** bonussatser, salgstall, avtalehistorikk
eller andre finansielle/administrative detaljer — det hører til det interne
leverandøravtale-systemet, ikke dette.

Alle ni Mouver-medlemsbedrifter kan velge blant de samme leverandørene, så
det er ingen innlogging eller medlemsbedrift-filtrering i søket.

## Struktur

```
finn-avtale/
  index.html          ← selve søkesiden (statisk, ingen backend i v1)
  data/avtaler.json    ← datagrunnlaget, generert av scripts/build_data.py
  scripts/
    kilde_leverandorer.csv   ← rå kildedata (leverandørregisteret)
    build_data.py             ← bygger data/avtaler.json fra CSV-en
```

## Oppdatere leverandørdata

1. Oppdater `scripts/kilde_leverandorer.csv` med nye/endrede leverandører
2. Kjør:
   ```
   python3 scripts/build_data.py
   ```
3. Commit og push endringen i `data/avtaler.json`

## Kjøre lokalt

Siden siden bare henter en lokal JSON-fil, holder det med en enkel
lokal webserver (kan ikke åpnes direkte som `file://` i alle nettlesere):

```
python3 -m http.server 8000
```

Åpne så http://localhost:8000 i nettleseren.

## Status / videre arbeid

- **v1 (dette):** statisk side, data hentet fra CSV, "Fant du ikke det du
  lette etter"-knappen sender en e-post (midlertidig løsning inntil videre)
- **Fase 2:** egen database (planlagt: Supabase) som deles med
  leverandøravtale-systemet — én kilde til sannhet, ulike visninger for
  prosjektledere vs. forvaltning. "Fant du ikke"-loggen lagres da i en egen
  tabell og mates inn i Linns dashboard som varsel om udekkede behov.
- **Leverandører uten mottatt avtaledokument ennå:** Service Master AS,
  Arti konsult (vises med varsel-badge i registeret)
- **Bevisst holdt utenfor registeret:** Kai Hansen, HMS Prosjekt AS,
  Grønn jobb, samt en uidentifisert Fleet/Equipment-avtale
