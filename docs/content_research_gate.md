# Content Benchmark Super Task

Ovaj workflow obavezan je prije svake nove ili materijalno izmijenjene feed ili
Story objave. Cilj nije imitirati popularan sadržaj, nego prije izrade razumjeti
što je aktualno, što buyeru zaustavlja pažnju i kako AID može ponuditi jasniju,
originalnu i dokazivu poslovnu vrijednost.

## 1. Definiraj zadatak

Zapiši:

- content ID i kanal;
- ciljnu nišu i buyer ulogu;
- poslovni problem i odluku koju sadržaj treba otvoriti;
- fazu interesa: awareness, problem recognition, consideration ili conversion;
- predloženi format i očekivani kvalificirani signal.

## 2. Aktualno istraživanje

Pregledaj najmanje tri provjerljiva izvora ili javna primjera:

1. službene Instagram/Meta smjernice za odabrani format;
2. jedan aktualni automotive ili market-intelligence benchmark;
3. jedan primjer iz konkretne niše, kada je javno dostupan.

Za svaki izvor zapiši datum pristupa, URL, format, hook, vizualni obrazac, CTA i
javno vidljiv signal. Ako privatne metrike nisu dostupne, napiši
`private_insights_unavailable`.

Benchmark vrijedi sedam dana. Ako Instagram profil vraća login zid, to se
evidentira; agent ne pokušava zaobići prijavu i ne traži korisničku lozinku.

## 3. Razdvoji dokaz od dojma

- Javni signal: objavljeni format, datum, vidljivi lajkovi, komentari, pregledi
  ili repostovi.
- Privatni Insights: reach, impressions, saves, shares, non-follower reach,
  Story taps, link klikovi, retention, profilne radnje, DM-ovi i leadovi.
- Interni creative score: AID procjena kvalitete koncepta; nije Instagram ocjena
  ni obećanje performansi.

Ne rangiraj račune samo po sirovim lajkovima jer nisu usporedivi po veličini
publike, starosti objave, plaćenoj distribuciji ni buyer kvaliteti.

## 4. Izdvoji prenosive obrasce

Za svaki sadržaj odaberi dva do četiri principa, primjerice:

- problem ili napetost u prvoj sekundi / na naslovnici;
- jedna poslovna odluka umjesto popisa značajki;
- konkretan datum, mjera, dokaz ili metodološko ograničenje;
- format prilagođen složenosti: carousel za korake, Reel za demonstraciju,
  Story za pitanje ili kvalifikaciju interesa;
- CTA vezan uz buyer odluku, DM, spremanje ili poslovni prikaz.

Princip se smije primijeniti. Tekst, kadar, raspored i prepoznatljiva izvedba
moraju biti originalni za AID.

## 5. Izradi najmanje dvije varijante

Prije finalizacije izradi najmanje dvije različite hook/layout varijante.
Odaberi onu s većim internim scoreom i zapiši zašto je druga odbijena.

## 6. Creative score — 100 bodova

| Kriterij | Maksimum |
|---|---:|
| Relevantnost za buyer problem i odluku | 20 |
| Snaga hooka / stopping power | 15 |
| Specifičnost i praktična vrijednost | 15 |
| Dokazivost i povjerenje | 15 |
| Originalnost i vizualna diferencijacija | 10 |
| CTA i potencijal za poslovni razgovor | 15 |
| Izvedba prilagođena formatu | 10 |
| **Ukupno** | **100** |

Minimalni prolaz je `80/100`. Bez obzira na zbroj, sadržaj je blokiran ako ima
neprovjerenu tvrdnju, generički CTA, kopiranu izvedbu, nečitljiv vizual,
nedostatak izvora ili istekli benchmark.

## 7. Izlaz Super Taska

Svaki content brief mora sadržavati:

- benchmark datoteku i datum;
- odabrane obrasce i odbijenu alternativu;
- score po kriterijima i ukupni score;
- status `pass` ili `blocked`;
- popis tvrdnji i izvora;
- očekivani signal uspjeha;
- napomenu o ograničenju javnih metrika.

Tehnička provjera pokreće se naredbom:

```bash
python3 instagram_agent/research_gate.py \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json
```

Tek nakon prolaza sadržaj ide na provjeru tvrdnji i ručno odobrenje.
