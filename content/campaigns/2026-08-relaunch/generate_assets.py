#!/usr/bin/env python3
"""Generate editable SVG sources, PNG previews are rendered separately."""

from __future__ import annotations

import html
import json
from pathlib import Path

from layout_variants import feed_svg_v2, story_svg_v2


ROOT = Path(__file__).resolve().parent
VISUALS = ROOT.parents[1] / "autodijelovi" / "visuals"
RESEARCH_GATE = json.loads((ROOT / "research-gate.json").read_text(encoding="utf-8"))

COLORS = {
    "navy": "#0D1B2A",
    "navy2": "#13243A",
    "line": "#283C58",
    "amber": "#F5A623",
    "blue": "#3B9DD6",
    "ink": "#E8EDF4",
    "muted": "#94A6BE",
}


FEED = [
    {
        "id": "AID-2608-F01",
        "slug": "01-podatak-nije-odluka",
        "eyebrow": "AID / DECISION LAYER",
        "title": ["Podatak nije", "odluka."],
        "accent_line": 1,
        "intro": "Vrijednost nastaje tek kada signal vodi prema jasnom sljedećem potezu.",
        "cards": [
            ("PODATAK", "Što se događa?"),
            ("SIGNAL", "Što to znači za KPI?"),
            ("ODLUKA", "Što sada treba učiniti?"),
        ],
        "cta": "Prepoznajete li izvještaj koji još čeka odluku?",
        "caption": """Podatak sam po sebi nije odluka.\n\nTim može imati tablice, dashboarde i izvještaje, a i dalje ne znati što treba korigirati, zadržati, nabaviti ili zaustaviti.\n\nZato AID povezuje tri razine:\n\n– podatak: što se događa\n– signal: što to znači za konkretni KPI\n– odluka: koji je sljedeći operativni potez\n\nAID je tržišni i decision-support sloj. Nadopunjuje postojeće procese; ne zamjenjuje ERP, DMS, CRM ili drugi core sustav.\n\nImate li izvještaj koji još uvijek čeka nečiju interpretaciju?""",
        "buyer": "direktor, COO, voditelj podataka ili operacija",
        "problem": "Podaci postoje, ali nisu prevedeni u operativni potez.",
        "source": "autoinsightdata.com; docs/brand_positioning.md",
    },
    {
        "id": "AID-2608-F02",
        "slug": "02-cetiri-koraka-do-poteza",
        "eyebrow": "AID / KAKO RADI",
        "title": ["Od raspršenih izvora", "do jednog poteza."],
        "accent_line": 1,
        "intro": "Decision layer spaja kontekst, standardizira usporedbu i vraća operativni signal.",
        "cards": [
            ("01  SPOJI", "tržišne, tehničke i dogovorene operativne izvore"),
            ("02  STANDARDIZIRAJ", "istu jedinicu i istu logiku usporedbe"),
            ("03  SIGNAL", "veži nalaz uz konkretni KPI"),
            ("04  ODLUKA", "definiraj jasan sljedeći korak"),
        ],
        "cta": "Pogledajte signal za jedan poslovni slučaj →",
        "caption": """Kako raspršeni podaci postaju operativna odluka?\n\n1. Spoje se tržišni, tehnički i dogovoreni operativni izvori.\n2. Standardizira se usporedba — da ista jedinica zaista znači isto.\n3. Nalaz se veže uz konkretni KPI.\n4. Signal završava jasnim sljedećim potezom.\n\nIzlaz nije još jedan izvještaj. Izlaz je odgovor na pitanje što korigirati, zadržati, nabaviti, premjestiti ili dodatno provjeriti.\n\nKoji biste jedan poslovni slučaj prvo pretvorili u signal?""",
        "buyer": "voditelji operacija, nabave, prodaje i rizika",
        "problem": "Raspršeni izvori i različite definicije usporavaju odluku.",
        "source": "autoinsightdata.com; docs/brand_positioning.md",
    },
    {
        "id": "AID-2608-F03",
        "slug": "03-prodaja-nula-potražnja-upitnik",
        "eyebrow": "AID / PARTS INTELLIGENCE",
        "title": ["Prodaja = 0", "Potražnja = ?"],
        "accent_line": 1,
        "intro": "Nedostupan dio ne ostavlja prodajni trag.",
        "cards": [
            ("DIO NIJE BIO NA POLICI", "kupac odlazi, prodaja ostaje nula"),
            ("REORDER VIDI SAMO NULU", "i može ponoviti istu odluku"),
            ("TRŽIŠNI SIGNAL", "dodaje vozni park, fitment i dostupnost"),
        ],
        "cta": "Odaberite jednu grupu dijelova i jednu regiju →",
        "photo": "warehouse-brake-parts.png",
        "caption": """Prodaja je nula. Ali je li i potražnja bila nula?\n\nAko dio nije bio dostupan, povijest prodaje ne vidi kupca koji je otišao drugdje. Reorder tada može ponoviti istu odluku: nije se prodavalo, zato ponovno ne nabavljamo.\n\nZa kvalitetniju odluku treba povezati:\n\n– lokalni vozni park\n– tehničku aplikaciju i fitment\n– OE/AM reference\n– raspoloživu zalihu\n– prodaju, lead time i pravila nabave\n\nCilj nije više dijelova na polici. Cilj je pravi dio na pravoj lokaciji.\n\nOdaberite jednu grupu dijelova i jednu regiju za početni pregled.""",
        "buyer": "voditelj nabave i category manager",
        "problem": "Povijest prodaje ne vidi potražnju izgubljenu zbog nedostupnosti.",
        "source": "inputs_docuemtns/AID_Inteligentna_nabavka_autodijelova_BiH.pdf",
    },
    {
        "id": "AID-2608-F04",
        "slug": "04-pet-odluka-po-artiklu",
        "eyebrow": "AID / PARTS INTELLIGENCE",
        "title": ["Pet odluka", "po artiklu."],
        "accent_line": 1,
        "intro": "Analitika ima vrijednost kada završava jasnom akcijom za nabavu i zalihu.",
        "cards": [
            ("NABAVI", "pokriće je prenisko"),
            ("ZADRŽI", "aplikacija i rotacija su zdrave"),
            ("PREBACI", "zaliha je na pogrešnoj lokaciji"),
            ("CENTRALIZIRAJ", "spor ili skup dio ne treba svugdje"),
            ("ZAUSTAVI", "ulaz više nema opravdanje"),
        ],
        "cta": "Koja odluka danas najčešće ostaje na osjećaj?",
        "photo": "category-parts-flatlay.png",
        "caption": """Dobar signal za autodijelove ne završava ocjenom. Završava odlukom po artiklu.\n\nNABAVI — pokriće je prenisko za prepoznatu potrebu.\nZADRŽI — aplikacija i rotacija opravdavaju zalihu.\nPREBACI — dio postoji, ali na pogrešnoj lokaciji.\nCENTRALIZIRAJ — spor ili skup dio ne treba držati u svakoj poslovnici.\nZAUSTAVI — novi ulaz više nema poslovno opravdanje.\n\nPragovi se ne postavljaju generički. Vežu se uz kategoriju, lokaciju, lead time i pravila poslovanja.\n\nKoja od ovih odluka u vašem timu najčešće još ostaje na osjećaj?""",
        "buyer": "direktor nabave, category manager, CFO",
        "problem": "Analitika bez jasne akcije ne mijenja zalihu.",
        "source": "inputs_docuemtns/AID_Inteligentna_nabavka_autodijelova_BiH.pdf",
    },
    {
        "id": "AID-2608-F05",
        "slug": "05-ista-drzava-drugaciji-asortiman",
        "eyebrow": "AID / REGIONALNI SIGNAL",
        "title": ["Ista država.", "Drugačiji asortiman."],
        "accent_line": 1,
        "intro": "Jedinstvena lista za sve lokacije može sakriti lokalnu strukturu voznog parka.",
        "cards": [
            ("VOZNI PARK", "koja vozila stvarno dominiraju u zoni"),
            ("LOKACIJA", "gdje dio treba biti dostupan"),
            ("ASORTIMAN", "što držati lokalno, a što centralno"),
        ],
        "cta": "Zatražite lokalni pregled jedne kategorije →",
        "photo": "regional-distribution.png",
        "caption": """Jedna država ne znači jedan aftermarket.\n\nStruktura voznog parka razlikuje se po lokaciji. Zato identičan asortiman u svakoj poslovnici može istodobno stvarati višak na jednom mjestu i nedostupnost na drugom.\n\nRegionalni signal povezuje:\n\n– vozila koja stvarno postoje u servisnoj zoni\n– tehničke aplikacije dijelova\n– lokalnu prodaju i dostupnost\n– pravila centralnog i lokalnog lagera\n\nRezultat nije veći katalog. Rezultat je jasnija odluka što držati lokalno, što premjestiti i što centralizirati.\n\nKoju biste kategoriju prvo pregledali po lokacijama?""",
        "buyer": "voditelj mreže poslovnica, nabava i logistika",
        "problem": "Isti asortiman po svim lokacijama ignorira lokalni vozni park.",
        "source": "inputs_docuemtns/AID_Inteligentna_nabavka_autodijelova_BiH.pdf",
    },
    {
        "id": "AID-2608-F06",
        "slug": "06-koliko-dugo-kapital-ceka",
        "eyebrow": "AID / STOCK AGING SIGNAL",
        "title": ["Koliko dugo", "kapital čeka odluku?"],
        "accent_line": 1,
        "intro": "Vrijeme je signal: artikl ili vozilo koje stoji traži novi pregled cijene, lokacije ili izlaza.",
        "cards": [
            ("ZADRŽI", "ako tržišni i operativni kontekst to opravdava"),
            ("KORIGIRAJ", "cijenu, prioritet ili kanal"),
            ("PREMJESTI / IZAĐI", "kada druga odluka bolje štiti obrt"),
        ],
        "cta": "Gdje vam odluka najduže čeka?",
        "caption": """Kapital ne stoji samo u robi. Stoji i u odluci koja kasni.\n\nArtikl, vozilo ili portfeljna pozicija koja predugo čeka ne traži automatski popust. Prvo traži novi pregled konteksta:\n\n– postoji li lokalna potražnja\n– je li cijena još tržišno pozicionirana\n– treba li promijeniti lokaciju ili kanal\n– postoji li jasniji trenutak izlaza\n\nSignal ne donosi odluku umjesto tima. On pokazuje gdje odluku treba otvoriti prije nego problem postane skuplji.\n\nU kojem dijelu procesa kod vas odluka najduže čeka?""",
        "buyer": "CFO, voditelj zaliha, fleet i remarketing manager",
        "problem": "Stock aging postaje vidljiv tek kada je korekcija skuplja.",
        "source": "autoinsightdata.com/solutions; docs/content_strategy.md",
    },
    {
        "id": "AID-2608-F07",
        "slug": "07-vrijednost-nije-staticna",
        "eyebrow": "AID / VALUE & RISK SIGNAL",
        "title": ["Vrijednost vozila", "nije statična."],
        "accent_line": 1,
        "intro": "Procjena treba tržišni kontekst, usporedivu jedinicu i jasno vrijeme promatranja.",
        "cards": [
            ("TRŽIŠTE", "kako se mijenja relevantan segment"),
            ("VOZILO", "što je doista usporediva jedinica"),
            ("PORTFELJ", "gdje odluka traži dodatnu kontrolu"),
        ],
        "cta": "Dogovorite tržišni pregled jednog segmenta →",
        "caption": """Vrijednost vozila nije broj koji jednom upišemo i zaboravimo.\n\nZa leasing, flote i financiranje važan je tržišni kontekst u kojem se procjena koristi:\n\n– što je doista usporedivo vozilo\n– kako se mijenja relevantan tržišni segment\n– gdje procjena odstupa od aktualnog signala\n– koja pozicija portfelja traži dodatnu kontrolu\n\nAID dodaje vanjski tržišni sloj postojećem procesu procjene. Ne zamjenjuje risk, underwriting ili internu odluku.\n\nKoji biste segment portfelja prvi stavili pod tržišni pregled?""",
        "buyer": "leasing risk, fleet, remarketing i auto-finance",
        "problem": "Procjena bez aktualnog tržišnog konteksta brzo gubi operativnu vrijednost.",
        "source": "autoinsightdata.com; docs/brand_positioning.md",
    },
    {
        "id": "AID-2608-F08",
        "slug": "08-jedan-slucaj-jedan-kpi",
        "eyebrow": "AID / PILOT FIRST",
        "title": ["Jedan slučaj.", "Jedan KPI.", "Jasan test."],
        "accent_line": 2,
        "intro": "Prvi korak nije veliki IT projekt nego ograničen prikaz koji provjerava mijenja li signal odluku.",
        "cards": [
            ("1  PROBLEM", "odaberite odluku koja danas nije dovoljno jasna"),
            ("2  SIGNAL", "dogovorite izvore, prag i vlasnika odluke"),
            ("3  TEST", "usporedite signal sa stvarnim poslovnim ishodom"),
        ],
        "cta": "Dogovorite poslovni prikaz → autoinsightdata.com/contact",
        "photo": "procurement-pilot.png",
        "caption": """Prvi korak ne mora biti veliki IT projekt.\n\nDobar početak je mali i provjerljiv:\n\n1. jedan poslovni problem\n2. jedan KPI koji je važan vlasniku odluke\n3. jasno definiran tržišni signal\n4. dogovoreno razdoblje i način usporedbe\n5. odluka hoće li se sustav širiti\n\nTako se prvo provjerava mijenja li signal stvarnu odluku. Tek zatim se razgovara o širem procesu i integraciji.\n\nOdaberite jedan slučaj. Dogovorite poslovni prikaz: https://www.autoinsightdata.com/contact""",
        "buyer": "donositelj odluke s konkretnim problemom i KPI-jem",
        "problem": "Preširok početni projekt otežava dokaz poslovne vrijednosti.",
        "source": "autoinsightdata.com; docs/brand_positioning.md",
    },
]


STORIES = [
    ("AID-2608-S01", "01-izvjestaj-ili-odluka", "PITANJE ZA TIM", ["Što vam danas", "češće stiže?"], ["IZVJEŠTAJ", "JASNA ODLUKA"], ""),
    ("AID-2608-S02", "02-cetiri-koraka", "KAKO RADI", ["Četiri koraka", "do jednog poteza"], ["SPOJI", "STANDARDIZIRAJ", "SIGNAL", "ODLUKA"], ""),
    ("AID-2608-S03", "03-sto-je-izlaz", "DECISION LAYER", ["Izlaz nije", "još jedan dashboard."], ["KORIGIRAJ", "ZADRŽI", "(NE) NABAVI", "KONTROLIRAJ"], ""),
    ("AID-2608-S04", "04-prodaja-nula", "PARTS INTELLIGENCE", ["Prodaja = 0", "Potražnja = ?"], ["Dio nije bio dostupan", "Kupac nije ostavio prodajni trag"], ""),
    ("AID-2608-S05", "05-gdje-je-dio", "ZALIHA × LOKACIJA", ["Dio postoji.", "Ali gdje?"], ["PRAVA POSLOVNICA", "CENTRALNI LAGER", "POGREŠNA REGIJA"], ""),
    ("AID-2608-S06", "06-pet-odluka", "ODLUKA PO ARTIKLU", ["Što signal", "mora vratiti?"], ["NABAVI", "ZADRŽI", "PREBACI", "CENTRALIZIRAJ", "ZAUSTAVI"], ""),
    ("AID-2608-S07", "07-ista-drzava", "REGIONALNI SIGNAL", ["Ista država.", "Isti asortiman?"], ["LOKALNI VOZNI PARK", "FITMENT", "DOSTUPNOST"], ""),
    ("AID-2608-S08", "08-kapital-ceka", "STOCK AGING", ["Gdje vam kapital", "najduže čeka?"], ["ARTIKL", "VOZILO", "PORTFELJ"], ""),
    ("AID-2608-S09", "09-vrijeme-je-signal", "EARLY WARNING", ["Vrijeme je", "operativni signal."], ["ZADRŽI", "KORIGIRAJ", "PREMJESTI / IZAĐI"], ""),
    ("AID-2608-S10", "10-vrijednost-se-mijenja", "VALUE SIGNAL", ["Vrijednost se", "mijenja s tržištem."], ["USPOREDIVA JEDINICA", "TRENUTAK PROCJENE", "PORTFELJNI KONTEKST"], ""),
    ("AID-2608-S11", "11-jedan-kpi", "PILOT FIRST", ["Koji jedan KPI", "želite razjasniti?"], ["OBRT", "DOSTUPNOST", "VRIJEDNOST", "RIZIK"], ""),
    ("AID-2608-S12", "12-dogovorite-prikaz", "SLJEDEĆI KORAK", ["Jedan slučaj.", "Jedan signal.", "Jasan test."], ["DOGOVORITE POSLOVNI PRIKAZ"], ""),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def photo_data(name: str) -> str:
    return f"../../../autodijelovi/visuals/{name}"


def research_section(content_id: str) -> str:
    record = RESEARCH_GATE["items"][content_id]
    labels = {
        "buyer_relevance": "Relevantnost za buyer problem i odluku",
        "hook": "Snaga hooka / stopping power",
        "specificity": "Specifičnost i praktična vrijednost",
        "evidence": "Dokazivost i povjerenje",
        "differentiation": "Originalnost i vizualna diferencijacija",
        "cta": "CTA i potencijal za poslovni razgovor",
        "format_fit": "Izvedba prilagođena formatu",
    }
    rows = []
    for (key, maximum), score in zip(RESEARCH_GATE["rubric"].items(), record["scorecard"], strict=True):
        rows.append(f"| {labels[key]} | {score}/{maximum} |")
    score = sum(record["scorecard"])
    benchmark = (Path("..") / RESEARCH_GATE["benchmark_file"]).as_posix()
    patterns = "; ".join(record["patterns"])
    return f'''## Research gate

- Status: `{record['status']}`
- Benchmark: [`{benchmark}`]({benchmark})
- Istraženo: `{RESEARCH_GATE['researched_at']}`
- Vrijedi do: `{RESEARCH_GATE['expires_at']}`
- Interni creative score: **{score}/100**
- Odabrani obrasci: {patterns}
- Odbijena alternativa: {record['rejected']}
- Očekivani kvalificirani signal: {record['expected_signal']}
- Ograničenje: javni signali nisu privatni Instagram Insights ni dokaz buduće izvedbe.

| Kriterij | Score |
|---|---:|
{chr(10).join(rows)}
'''


def feed_svg(item: dict) -> str:
    c = COLORS
    photo = item.get("photo")
    image = ""
    opacity = ".79"
    if photo:
        image = f'<image href="{photo_data(photo)}" width="1080" height="1350" preserveAspectRatio="xMidYMid slice"/>'
        opacity = ".82"

    title = []
    y = 290
    for idx, line in enumerate(item["title"]):
        fill = c["amber"] if idx == item.get("accent_line") else c["ink"]
        size = 74 if len(line) < 24 else 62
        title.append(f'<text x="76" y="{y}" fill="{fill}" font-size="{size}" font-weight="800">{esc(line)}</text>')
        y += 88

    intro_y = y + 24
    cards_y = intro_y + 90
    cards = item["cards"]
    card_h = 102 if len(cards) >= 5 else 128
    gap = 13
    usable = 430 if len(cards) >= 5 else 430
    card_h = min(card_h, int((usable - gap * (len(cards) - 1)) / len(cards)))
    card_elements = []
    for idx, (head, body) in enumerate(cards):
        cy = cards_y + idx * (card_h + gap)
        stroke = c["amber"] if idx == len(cards) - 1 else c["line"]
        head_color = c["amber"] if idx == len(cards) - 1 else c["blue"]
        card_elements.append(f'<rect x="76" y="{cy}" width="928" height="{card_h}" rx="22" fill="{c["navy2"]}" fill-opacity=".96" stroke="{stroke}"/>')
        card_elements.append(f'<text x="108" y="{cy + 42}" fill="{head_color}" font-size="20" font-weight="800" letter-spacing="1.5">{esc(head)}</text>')
        if body:
            card_elements.append(f'<text x="108" y="{cy + 76}" fill="{c["ink"]}" font-size="21">{esc(body)}</text>')

    cta_y = 1234
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['navy']}"/><stop offset="1" stop-color="{c['navy2']}"/></linearGradient>
    <pattern id="grid" width="54" height="54" patternUnits="userSpaceOnUse"><path d="M54 0H0V54" fill="none" stroke="{c['line']}" stroke-opacity=".34"/></pattern>
  </defs>
{image}
  <rect width="1080" height="1350" fill="url(#bg)" opacity="{opacity}"/>
  <rect width="1080" height="1350" fill="url(#grid)"/>
  <rect width="668" height="8" fill="{c['amber']}"/><rect x="668" width="412" height="8" fill="{c['blue']}"/>
  <circle cx="982" cy="122" r="165" fill="none" stroke="{c['blue']}" stroke-opacity=".16" stroke-width="40"/>
  <g font-family="DejaVu Sans, Arial, sans-serif">
    <text x="76" y="92" fill="{c['ink']}" font-size="23" font-weight="800" letter-spacing="2.4">{esc(item['eyebrow'])}</text>
    <rect x="76" y="126" width="142" height="36" rx="18" fill="{c['amber']}"/><text x="147" y="151" text-anchor="middle" fill="{c['navy']}" font-size="15" font-weight="800">MARKET SIGNAL</text>
    {''.join(title)}
    <text x="76" y="{intro_y}" fill="{c['muted']}" font-size="23">{esc(item['intro'])}</text>
    {''.join(card_elements)}
    <line x1="76" y1="1188" x2="1004" y2="1188" stroke="{c['line']}" stroke-width="2"/>
    <text x="76" y="{cta_y}" fill="{c['ink']}" font-size="22" font-weight="700">{esc(item['cta'])}</text>
    <text x="76" y="1286" fill="{c['muted']}" font-size="18">autoinsightdata.com</text>
    <text x="1004" y="1286" text-anchor="end" fill="{c['amber']}" font-size="18" font-weight="800">{esc(item['id'])}</text>
  </g>
</svg>'''


def feed_brief(item: dict) -> str:
    return f'''# {item['id']} — {item['title'][0]} {' '.join(item['title'][1:])}

- Status: `draft`
- Format: feed 1080 × 1350
- Buyer: {item['buyer']}
- Problem: {item['problem']}
- Izvor: `{item['source']}`
- Vizual: `{item['slug']}.png`

## Caption

{item['caption']}

{research_section(item['id'])}

## Provjera prije odobrenja

- potvrditi da caption i PNG odgovaraju ovoj verziji;
- potvrditi CTA i planirani termin iz `../schedule.csv`;
- provjeriti povezane retke u `../claims-register.csv`;
- nema vanjskih brojki, klijentskog rezultata ni privatnih Insights podataka.
'''


def story_svg(item: tuple[str, str, str, list[str], list[str], str]) -> str:
    content_id, _, eyebrow, title_lines, chips, sticker = item
    c = COLORS
    if sticker.startswith("Poll"):
        sticker_cta = "ODABERITE ODGOVOR ↓"
    elif sticker.startswith("Question"):
        sticker_cta = "DODAJTE SVOJ ODGOVOR ↓"
    else:
        sticker_cta = "POGLEDAJTE VIŠE ↓"
    title = []
    y = 490
    for idx, line in enumerate(title_lines):
        fill = c["amber"] if idx == len(title_lines) - 1 else c["ink"]
        title.append(f'<text x="90" y="{y}" fill="{fill}" font-size="72" font-weight="800">{esc(line)}</text>')
        y += 92
    chip_elements = []
    chip_y = 850
    for idx, chip in enumerate(chips):
        cy = chip_y + idx * 112
        color = c["amber"] if idx == len(chips) - 1 else c["blue"]
        chip_elements.append(f'<rect x="90" y="{cy}" width="900" height="86" rx="22" fill="{c["navy2"]}" stroke="{color}" stroke-width="2"/>')
        chip_elements.append(f'<text x="540" y="{cy + 54}" text-anchor="middle" fill="{c["ink"]}" font-size="25" font-weight="800" letter-spacing="1.2">{esc(chip)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['navy']}"/><stop offset="1" stop-color="{c['navy2']}"/></linearGradient><pattern id="grid" width="54" height="54" patternUnits="userSpaceOnUse"><path d="M54 0H0V54" fill="none" stroke="{c['line']}" stroke-opacity=".35"/></pattern></defs>
  <rect width="1080" height="1920" fill="url(#bg)"/><rect width="1080" height="1920" fill="url(#grid)"/>
  <rect width="668" height="8" fill="{c['amber']}"/><rect x="668" width="412" height="8" fill="{c['blue']}"/>
  <circle cx="945" cy="360" r="240" fill="none" stroke="{c['blue']}" stroke-opacity=".16" stroke-width="64"/>
  <circle cx="130" cy="1570" r="250" fill="none" stroke="{c['amber']}" stroke-opacity=".10" stroke-width="54"/>
  <g font-family="DejaVu Sans, Arial, sans-serif">
    <text x="90" y="278" fill="{c['ink']}" font-size="24" font-weight="800" letter-spacing="2.6">AID / {esc(eyebrow)}</text>
    <rect x="90" y="316" width="150" height="38" rx="19" fill="{c['amber']}"/><text x="165" y="342" text-anchor="middle" fill="{c['navy']}" font-size="15" font-weight="800">MARKET SIGNAL</text>
    {''.join(title)}
    {''.join(chip_elements)}
    <rect x="90" y="1480" width="900" height="128" rx="28" fill="{c['blue']}"/>
    <text x="540" y="1554" text-anchor="middle" fill="{c['navy']}" font-size="24" font-weight="800">{esc(sticker_cta)}</text>
    <text x="90" y="1648" fill="{c['muted']}" font-size="19">autoinsightdata.com</text>
    <text x="990" y="1648" text-anchor="end" fill="{c['amber']}" font-size="19" font-weight="800">{esc(content_id)}</text>
  </g>
</svg>'''


def story_brief(item: tuple[str, str, str, list[str], list[str], str]) -> str:
    content_id, slug, eyebrow, title_lines, chips, sticker = item
    return f'''# {content_id} — {' '.join(title_lines)}

- Status: `draft`
- Format: Story 1080 × 1920
- Tema: {eyebrow}
- Vizual: `{slug}.png`
- Interaktivni element: `nema — story je samodostatan`

{research_section(content_id)}

## Uputa

Objaviti u terminu iz `../schedule.csv`. Story ne koristi native poll, question
ni link sticker, pa ga agent objavljuje kroz Graph API bez ručnog dovršavanja u
aplikaciji. CTA upućuje na odgovor porukom ili na link u biu; oboje je nativno i
ne treba sticker. Prije objave potvrditi PNG, CTA tekst i točan termin.
'''


def main() -> None:
    for item in FEED:
        base = ROOT / "posts" / item["slug"]
        base.with_suffix(".svg").write_text(feed_svg_v2(item), encoding="utf-8")
        base.with_suffix(".md").write_text(feed_brief(item), encoding="utf-8")
    for item in STORIES:
        base = ROOT / "stories" / item[1]
        base.with_suffix(".svg").write_text(story_svg_v2(item), encoding="utf-8")
        base.with_suffix(".md").write_text(story_brief(item), encoding="utf-8")


if __name__ == "__main__":
    main()
