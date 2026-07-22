"""Distinct visual archetypes for the AID relaunch campaign."""

from __future__ import annotations

import html


C = {
    "navy": "#0D1B2A", "navy2": "#13243A", "line": "#283C58",
    "amber": "#F5A623", "blue": "#3B9DD6", "ink": "#E8EDF4", "muted": "#94A6BE",
}


def e(value: str) -> str:
    return html.escape(value, quote=True)


def photo_path(name: str) -> str:
    return f"../../../autodijelovi/visuals/{name}"


def feed_frame(item: dict, body: str, background: str = "", photo: str | None = None) -> str:
    image = f'<image href="{photo_path(photo)}" width="1080" height="1350" preserveAspectRatio="xMidYMid slice"/>' if photo else ""
    opacity = ".76" if photo else "1"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{C['navy']}"/><stop offset="1" stop-color="{C['navy2']}"/></linearGradient>
    <pattern id="grid" width="54" height="54" patternUnits="userSpaceOnUse"><path d="M54 0H0V54" fill="none" stroke="{C['line']}" stroke-opacity=".28"/></pattern>
    <filter id="shadow"><feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#000" flood-opacity=".35"/></filter>
  </defs>
{image}
  <rect width="1080" height="1350" fill="url(#bg)" opacity="{opacity}"/><rect width="1080" height="1350" fill="url(#grid)"/>{background}
  <rect width="668" height="8" fill="{C['amber']}"/><rect x="668" width="412" height="8" fill="{C['blue']}"/>
  <g font-family="DejaVu Sans, Arial, sans-serif"><text x="76" y="86" fill="{C['ink']}" font-size="21" font-weight="800" letter-spacing="2.4">{e(item['eyebrow'])}</text>{body}
    <line x1="76" y1="1190" x2="1004" y2="1190" stroke="{C['line']}" stroke-width="2"/>
    <text x="76" y="1235" fill="{C['ink']}" font-size="21" font-weight="700">{e(item['cta'])}</text>
    <text x="76" y="1286" fill="{C['muted']}" font-size="18">autoinsightdata.com</text><text x="1004" y="1286" text-anchor="end" fill="{C['amber']}" font-size="18" font-weight="800">{e(item['id'])}</text>
  </g></svg>'''


def feed_svg_v2(item: dict) -> str:
    slug = item["slug"]
    if slug.startswith("01-"):
        body = f'''
    <text x="76" y="250" fill="{C['muted']}" font-size="30" font-weight="700" letter-spacing="5">PODATAK</text>
    <text x="72" y="425" fill="{C['ink']}" font-size="126" font-weight="800">NIJE</text>
    <rect x="68" y="468" width="620" height="178" rx="22" fill="{C['amber']}" filter="url(#shadow)"/>
    <text x="110" y="586" fill="{C['navy']}" font-size="112" font-weight="900">ODLUKA.</text>
    <path d="M760 252C912 330 824 472 952 548S893 807 991 894" fill="none" stroke="{C['blue']}" stroke-width="12"/><circle cx="760" cy="252" r="20" fill="{C['blue']}"/><circle cx="952" cy="548" r="20" fill="{C['amber']}"/><circle cx="991" cy="894" r="20" fill="{C['blue']}"/>
    <text x="76" y="760" fill="{C['ink']}" font-size="31" font-weight="700">Što se događa?</text><text x="76" y="804" fill="{C['muted']}" font-size="23">podatak</text>
    <text x="76" y="890" fill="{C['ink']}" font-size="31" font-weight="700">Što to znači za KPI?</text><text x="76" y="934" fill="{C['muted']}" font-size="23">signal</text>
    <text x="76" y="1020" fill="{C['amber']}" font-size="31" font-weight="800">Što sada treba učiniti?</text><text x="76" y="1064" fill="{C['muted']}" font-size="23">odluka</text>'''
        return feed_frame(item, body, f'<rect width="26" height="1350" fill="{C["amber"]}"/><circle cx="930" cy="400" r="250" fill="{C["blue"]}" opacity=".06"/>')

    if slug.startswith("02-"):
        coords = [(150, 500), (390, 700), (650, 500), (900, 700)]
        steps = []
        for idx, ((head, _), (x, y)) in enumerate(zip(item["cards"], coords), 1):
            color = C["amber"] if idx == 4 else C["blue"]
            steps.append(f'<circle cx="{x}" cy="{y}" r="74" fill="{C["navy2"]}" stroke="{color}" stroke-width="6"/><text x="{x}" y="{y+14}" text-anchor="middle" fill="{color}" font-size="42" font-weight="900">{idx}</text><text x="{x}" y="{y+126}" text-anchor="middle" fill="{C["ink"]}" font-size="21" font-weight="800">{e(head.split("  ")[-1])}</text>')
        body = f'''
    <text x="76" y="245" fill="{C['ink']}" font-size="63" font-weight="800">Od raspršenih izvora</text><text x="76" y="325" fill="{C['amber']}" font-size="63" font-weight="800">do jednog poteza.</text>
    <path d="M150 500C270 500 270 700 390 700S530 500 650 500S780 700 900 700" fill="none" stroke="{C['line']}" stroke-width="12" stroke-linecap="round"/>{''.join(steps)}
    <rect x="180" y="950" width="720" height="114" rx="57" fill="{C['blue']}"/><text x="540" y="1020" text-anchor="middle" fill="{C['navy']}" font-size="27" font-weight="900">SIGNAL → KONKRETAN SLJEDEĆI POTEZ</text>'''
        return feed_frame(item, body, f'<path d="M0 1020L1080 790V1350H0Z" fill="{C["blue"]}" opacity=".04"/>')

    if slug.startswith("03-"):
        body = f'''
    <rect x="70" y="180" width="650" height="330" rx="28" fill="{C['navy']}" fill-opacity=".86" stroke="{C['line']}"/>
    <text x="110" y="300" fill="{C['ink']}" font-size="86" font-weight="900">Prodaja = 0</text><text x="110" y="408" fill="{C['amber']}" font-size="86" font-weight="900">Potražnja = ?</text>
    <text x="780" y="455" fill="{C['blue']}" opacity=".72" font-size="360" font-weight="900">?</text>
    <rect x="76" y="680" width="928" height="250" rx="28" fill="{C['navy2']}" fill-opacity=".93" stroke="{C['amber']}"/>
    <text x="116" y="756" fill="{C['amber']}" font-size="23" font-weight="900" letter-spacing="2">NEVIDLJIVA POTRAŽNJA</text><text x="116" y="820" fill="{C['ink']}" font-size="34" font-weight="800">Dio nije bio dostupan.</text><text x="116" y="872" fill="{C['ink']}" font-size="34" font-weight="800">Kupac nije ostavio prodajni trag.</text>
    <path d="M116 1010H900" stroke="{C['blue']}" stroke-width="8"/><path d="M900 1010l-32-22v44z" fill="{C['blue']}"/><text x="116" y="1065" fill="{C['muted']}" font-size="23">vozni park + fitment + dostupnost = kvalitetniji signal</text>'''
        return feed_frame(item, body, photo=item.get("photo"))

    if slug.startswith("04-"):
        rows, widths = [], [610, 720, 830, 900, 760]
        for idx, ((head, body_text), width) in enumerate(zip(item["cards"], widths)):
            y, x = 420 + idx * 128, 76 + (idx % 2) * 70
            color = C["amber"] if idx in (0, 4) else C["blue"]
            rows.append(f'<rect x="{x}" y="{y}" width="{width}" height="96" rx="18" fill="{C["navy2"]}" fill-opacity=".94" stroke="{color}" stroke-width="2"/><text x="{x+28}" y="{y+42}" fill="{color}" font-size="25" font-weight="900">{e(head)}</text><text x="{x+28}" y="{y+73}" fill="{C["ink"]}" font-size="18">{e(body_text)}</text>')
        body = f'''<text x="76" y="245" fill="{C['ink']}" font-size="78" font-weight="900">Pet odluka.</text><text x="76" y="330" fill="{C['amber']}" font-size="52" font-weight="800">Ne pet novih dashboarda.</text>{''.join(rows)}'''
        return feed_frame(item, body, f'<text x="930" y="1080" text-anchor="middle" fill="{C["blue"]}" opacity=".18" font-size="420" font-weight="900">5</text>', item.get("photo"))

    if slug.startswith("05-"):
        body = f'''
    <text x="76" y="230" fill="{C['ink']}" font-size="72" font-weight="900">Ista država.</text><text x="76" y="315" fill="{C['amber']}" font-size="72" font-weight="900">Drugačiji asortiman.</text>
    <line x1="540" y1="410" x2="540" y2="985" stroke="{C['amber']}" stroke-width="5" stroke-dasharray="16 14"/>
    <circle cx="275" cy="580" r="88" fill="{C['navy2']}" stroke="{C['blue']}" stroke-width="5"/><circle cx="275" cy="580" r="30" fill="{C['blue']}"/><path d="M275 610v95" stroke="{C['blue']}" stroke-width="10"/>
    <circle cx="805" cy="580" r="88" fill="{C['navy2']}" stroke="{C['amber']}" stroke-width="5"/><circle cx="805" cy="580" r="30" fill="{C['amber']}"/><path d="M805 610v95" stroke="{C['amber']}" stroke-width="10"/>
    <text x="275" y="770" text-anchor="middle" fill="{C['ink']}" font-size="30" font-weight="900">LOKACIJA A</text><text x="805" y="770" text-anchor="middle" fill="{C['ink']}" font-size="30" font-weight="900">LOKACIJA B</text>
    <rect x="170" y="910" width="740" height="126" rx="28" fill="{C['amber']}"/><text x="540" y="965" text-anchor="middle" fill="{C['navy']}" font-size="22" font-weight="900">ODLUKA</text><text x="540" y="1005" text-anchor="middle" fill="{C['navy']}" font-size="27" font-weight="800">lokalno držati · premjestiti · centralizirati</text>'''
        bg = f'<rect y="390" width="540" height="650" fill="{C["blue"]}" opacity=".06"/><rect x="540" y="390" width="540" height="650" fill="{C["amber"]}" opacity=".06"/>'
        return feed_frame(item, body, bg, item.get("photo"))

    if slug.startswith("06-"):
        body = f'''
    <text x="76" y="250" fill="{C['ink']}" font-size="62" font-weight="900">Koliko dugo kapital</text><text x="76" y="325" fill="{C['amber']}" font-size="62" font-weight="900">čeka odluku?</text>
    <circle cx="690" cy="690" r="270" fill="{C['navy2']}" stroke="{C['line']}" stroke-width="18"/><path d="M690 690V505M690 690L840 775" stroke="{C['amber']}" stroke-width="18" stroke-linecap="round"/><circle cx="690" cy="690" r="28" fill="{C['amber']}"/><path d="M690 390A300 300 0 0 1 990 690" fill="none" stroke="{C['blue']}" stroke-width="22"/>
    <rect x="76" y="470" width="300" height="116" rx="22" fill="{C['navy2']}" stroke="{C['blue']}"/><text x="106" y="520" fill="{C['blue']}" font-size="22" font-weight="900">ZADRŽI</text><text x="106" y="556" fill="{C['ink']}" font-size="18">kada signal opravdava</text>
    <rect x="76" y="630" width="300" height="116" rx="22" fill="{C['navy2']}" stroke="{C['amber']}"/><text x="106" y="680" fill="{C['amber']}" font-size="22" font-weight="900">KORIGIRAJ</text><text x="106" y="716" fill="{C['ink']}" font-size="18">cijenu, kanal ili prioritet</text>
    <rect x="76" y="790" width="360" height="116" rx="22" fill="{C['navy2']}" stroke="{C['blue']}"/><text x="106" y="840" fill="{C['blue']}" font-size="22" font-weight="900">PREMJESTI / IZAĐI</text><text x="106" y="876" fill="{C['ink']}" font-size="18">prije skuplje korekcije</text><text x="690" y="1065" text-anchor="middle" fill="{C['muted']}" font-size="24">Vrijeme nije samo metrika. Vrijeme je signal.</text>'''
        return feed_frame(item, body, f'<circle cx="690" cy="690" r="360" fill="{C["amber"]}" opacity=".035"/>')

    if slug.startswith("07-"):
        body = f'''
    <text x="76" y="230" fill="{C['ink']}" font-size="69" font-weight="900">Vrijednost vozila</text><text x="76" y="315" fill="{C['amber']}" font-size="69" font-weight="900">nije statična.</text>
    <path d="M100 900C260 840 300 620 460 700S690 460 980 510" fill="none" stroke="{C['blue']}" stroke-width="14"/><path d="M100 900C260 840 300 620 460 700S690 460 980 510L980 1030H100Z" fill="{C['blue']}" opacity=".08"/>
    <circle cx="180" cy="850" r="28" fill="{C['amber']}"/><circle cx="460" cy="700" r="28" fill="{C['blue']}"/><circle cx="750" cy="545" r="28" fill="{C['amber']}"/><circle cx="960" cy="510" r="28" fill="{C['blue']}"/>
    <rect x="110" y="950" width="250" height="90" rx="18" fill="{C['navy2']}" stroke="{C['line']}"/><text x="235" y="1006" text-anchor="middle" fill="{C['ink']}" font-size="19" font-weight="800">USPOREDIVA JEDINICA</text>
    <rect x="415" y="950" width="250" height="90" rx="18" fill="{C['navy2']}" stroke="{C['line']}"/><text x="540" y="1006" text-anchor="middle" fill="{C['ink']}" font-size="19" font-weight="800">TRENUTAK PROCJENE</text>
    <rect x="720" y="950" width="250" height="90" rx="18" fill="{C['navy2']}" stroke="{C['amber']}"/><text x="845" y="1006" text-anchor="middle" fill="{C['amber']}" font-size="19" font-weight="800">PORTFELJNI SIGNAL</text>'''
        return feed_frame(item, body, f'<path d="M0 1100L1080 800V1350H0Z" fill="{C["blue"]}" opacity=".04"/>')

    body = f'''
    <rect x="58" y="155" width="964" height="930" rx="42" fill="{C['amber']}" filter="url(#shadow)"/><text x="110" y="280" fill="{C['navy']}" font-size="27" font-weight="900" letter-spacing="3">PILOT FIRST</text>
    <text x="110" y="420" fill="{C['navy']}" font-size="83" font-weight="900">Jedan slučaj.</text><text x="110" y="520" fill="{C['navy']}" font-size="83" font-weight="900">Jedan KPI.</text><text x="110" y="620" fill="{C['navy']}" font-size="83" font-weight="900">Jasan test.</text>
    <line x1="110" y1="690" x2="930" y2="690" stroke="{C['navy']}" stroke-opacity=".35" stroke-width="3"/><text x="110" y="770" fill="{C['navy']}" font-size="27" font-weight="800">01  problem koji danas nije dovoljno jasan</text><text x="110" y="835" fill="{C['navy']}" font-size="27" font-weight="800">02  signal vezan uz vlasnika i KPI</text><text x="110" y="900" fill="{C['navy']}" font-size="27" font-weight="800">03  usporedba sa stvarnim ishodom</text>
    <rect x="110" y="950" width="520" height="82" rx="41" fill="{C['navy']}"/><text x="370" y="1002" text-anchor="middle" fill="{C['ink']}" font-size="22" font-weight="900">DOGOVORITE POSLOVNI PRIKAZ →</text>'''
    return feed_frame(item, body, f'<circle cx="1000" cy="120" r="260" fill="{C["blue"]}" opacity=".20"/>', item.get("photo"))


def story_frame(content_id: str, eyebrow: str, body: str, photo: str | None = None, amber_bg: bool = False) -> str:
    image = f'<image href="{photo_path(photo)}" width="1080" height="1920" preserveAspectRatio="xMidYMid slice"/>' if photo else ""
    bg_color = C["amber"] if amber_bg else C["navy"]
    ink = C["navy"] if amber_bg else C["ink"]
    muted = C["navy2"] if amber_bg else C["muted"]
    overlay = f'<rect width="1080" height="1920" fill="{C["navy"]}" opacity=".74"/>' if photo else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><defs><pattern id="grid" width="54" height="54" patternUnits="userSpaceOnUse"><path d="M54 0H0V54" fill="none" stroke="{C['line']}" stroke-opacity=".28"/></pattern></defs>{image}<rect width="1080" height="1920" fill="{bg_color}"/>{overlay}<rect width="1080" height="1920" fill="url(#grid)"/><rect width="668" height="8" fill="{C['amber']}"/><rect x="668" width="412" height="8" fill="{C['blue']}"/><g font-family="DejaVu Sans, Arial, sans-serif"><text x="90" y="270" fill="{ink}" font-size="23" font-weight="800" letter-spacing="2.5">AID / {e(eyebrow)}</text>{body}<text x="90" y="1648" fill="{muted}" font-size="19">autoinsightdata.com</text><text x="990" y="1648" text-anchor="end" fill="{C['blue'] if amber_bg else C['amber']}" font-size="19" font-weight="800">{e(content_id)}</text></g></svg>'''


def story_svg_v2(item: tuple[str, str, str, list[str], list[str], str]) -> str:
    content_id, slug, eyebrow, title, chips, sticker = item
    n = int(content_id[-2:])
    if n == 1:
        body = f'''<text x="90" y="430" fill="{C['ink']}" font-size="70" font-weight="900">Što vam danas</text><text x="90" y="515" fill="{C['amber']}" font-size="70" font-weight="900">češće stiže?</text><rect x="70" y="700" width="455" height="470" rx="34" fill="{C['navy2']}" stroke="{C['line']}"/><text x="298" y="860" text-anchor="middle" fill="{C['muted']}" font-size="27" font-weight="800">A</text><text x="298" y="970" text-anchor="middle" fill="{C['ink']}" font-size="42" font-weight="900">IZVJEŠTAJ</text><rect x="555" y="700" width="455" height="470" rx="34" fill="{C['amber']}"/><text x="782" y="860" text-anchor="middle" fill="{C['navy']}" font-size="27" font-weight="800">B</text><text x="782" y="955" text-anchor="middle" fill="{C['navy']}" font-size="42" font-weight="900">JASNA</text><text x="782" y="1015" text-anchor="middle" fill="{C['navy']}" font-size="42" font-weight="900">ODLUKA</text><text x="540" y="1450" text-anchor="middle" fill="{C['blue']}" font-size="25" font-weight="800">ODABERITE U POLLU ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 2:
        nodes = []
        for idx, chip in enumerate(chips):
            y = 560 + idx * 235
            nodes.append(f'<circle cx="180" cy="{y}" r="62" fill="{C["navy2"]}" stroke="{C["amber"] if idx == 3 else C["blue"]}" stroke-width="6"/><text x="180" y="{y+13}" text-anchor="middle" fill="{C["ink"]}" font-size="36" font-weight="900">{idx+1}</text><text x="290" y="{y+13}" fill="{C["ink"]}" font-size="36" font-weight="900">{e(chip)}</text>')
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="70" font-weight="900">Četiri koraka.</text><text x="90" y="505" fill="{C['amber']}" font-size="70" font-weight="900">Jedan potez.</text><path d="M180 560V1265" stroke="{C['line']}" stroke-width="10"/>{''.join(nodes)}<text x="540" y="1500" text-anchor="middle" fill="{C['blue']}" font-size="25" font-weight="800">GDJE VAŠ PROCES ZAPINJE? ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 3:
        body = f'''<text x="90" y="470" fill="{C['muted']}" font-size="42" font-weight="800">IZLAZ NIJE</text><text x="90" y="610" fill="{C['ink']}" font-size="92" font-weight="900">JOŠ JEDAN</text><text x="90" y="720" fill="{C['amber']}" font-size="92" font-weight="900">DASHBOARD.</text><rect x="90" y="850" width="900" height="320" rx="32" fill="{C['navy2']}" stroke="{C['line']}"/><path d="M150 1100L300 970L440 1030L620 910L800 980L930 900" fill="none" stroke="{C['blue']}" stroke-width="12"/><line x1="120" y1="820" x2="960" y2="1210" stroke="{C['amber']}" stroke-width="18"/><rect x="180" y="1360" width="720" height="110" rx="55" fill="{C['blue']}"/><text x="540" y="1428" text-anchor="middle" fill="{C['navy']}" font-size="27" font-weight="900">POGLEDAJTE KONKRETAN POTEZ →</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 4:
        body = f'''<rect x="70" y="390" width="940" height="370" rx="34" fill="{C['navy']}" fill-opacity=".86"/><text x="110" y="540" fill="{C['ink']}" font-size="82" font-weight="900">Prodaja = 0</text><text x="110" y="650" fill="{C['amber']}" font-size="82" font-weight="900">Potražnja = ?</text><text x="120" y="950" fill="{C['ink']}" font-size="40" font-weight="800">Ako dio nije bio dostupan,</text><text x="120" y="1010" fill="{C['ink']}" font-size="40" font-weight="800">kupac ne ostavlja prodajni trag.</text><rect x="110" y="1340" width="860" height="120" rx="60" fill="{C['amber']}"/><text x="540" y="1414" text-anchor="middle" fill="{C['navy']}" font-size="28" font-weight="900">DEAD STOCK ILI LOST SALES? ↓</text>'''
        return story_frame(content_id, eyebrow, body, "warehouse-brake-parts.png")
    if n == 5:
        body = f'''<text x="90" y="440" fill="{C['ink']}" font-size="76" font-weight="900">Dio postoji.</text><text x="90" y="530" fill="{C['amber']}" font-size="76" font-weight="900">Ali gdje?</text><circle cx="250" cy="850" r="105" fill="{C['navy2']}" stroke="{C['blue']}" stroke-width="6"/><circle cx="250" cy="850" r="34" fill="{C['blue']}"/><circle cx="830" cy="1050" r="105" fill="{C['navy2']}" stroke="{C['amber']}" stroke-width="6"/><circle cx="830" cy="1050" r="34" fill="{C['amber']}"/><path d="M340 885C500 900 580 1020 725 1035" fill="none" stroke="{C['muted']}" stroke-width="12" stroke-dasharray="18 14"/><text x="250" y="1030" text-anchor="middle" fill="{C['ink']}" font-size="26" font-weight="900">POSLOVNICA</text><text x="830" y="1230" text-anchor="middle" fill="{C['ink']}" font-size="26" font-weight="900">CENTRALNI LAGER</text><text x="540" y="1480" text-anchor="middle" fill="{C['blue']}" font-size="25" font-weight="900">GDJE DIO TREBA BITI? ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 6:
        bars = []
        for idx, chip in enumerate(chips):
            y = 600 + idx * 150
            bars.append(f'<rect x="{90 + (idx%2)*70}" y="{y}" width="{820 - idx*55}" height="112" rx="22" fill="{C["amber"] if idx==4 else C["navy2"]}" stroke="{C["blue"] if idx<4 else C["amber"]}"/><text x="{130 + (idx%2)*70}" y="{y+70}" fill="{C["navy"] if idx==4 else C["ink"]}" font-size="30" font-weight="900">{e(chip)}</text>')
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="68" font-weight="900">Što signal</text><text x="90" y="505" fill="{C['amber']}" font-size="68" font-weight="900">mora vratiti?</text>{''.join(bars)}'''
        return story_frame(content_id, eyebrow, body)
    if n == 7:
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="73" font-weight="900">Ista država.</text><text x="90" y="510" fill="{C['amber']}" font-size="73" font-weight="900">Isti asortiman?</text><line x1="540" y1="620" x2="540" y2="1300" stroke="{C['amber']}" stroke-width="6" stroke-dasharray="18 14"/><text x="280" y="850" text-anchor="middle" fill="{C['blue']}" font-size="38" font-weight="900">REGIJA A</text><text x="800" y="850" text-anchor="middle" fill="{C['amber']}" font-size="38" font-weight="900">REGIJA B</text><text x="280" y="950" text-anchor="middle" fill="{C['ink']}" font-size="25">vozni park</text><text x="800" y="950" text-anchor="middle" fill="{C['ink']}" font-size="25">drugačija potreba</text><rect x="130" y="1370" width="820" height="110" rx="55" fill="{C['blue']}"/><text x="540" y="1438" text-anchor="middle" fill="{C['navy']}" font-size="27" font-weight="900">ISTI ASORTIMAN? DA / NE ↓</text>'''
        return story_frame(content_id, eyebrow, body, "regional-distribution.png")
    if n == 8:
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="66" font-weight="900">Gdje vam kapital</text><text x="90" y="505" fill="{C['amber']}" font-size="66" font-weight="900">najduže čeka?</text><circle cx="540" cy="930" r="320" fill="{C['navy2']}" stroke="{C['line']}" stroke-width="24"/><path d="M540 930V690M540 930L760 1035" stroke="{C['amber']}" stroke-width="24" stroke-linecap="round"/><circle cx="540" cy="930" r="35" fill="{C['amber']}"/><text x="540" y="1370" text-anchor="middle" fill="{C['blue']}" font-size="28" font-weight="900">ARTIKL · VOZILO · PORTFELJ</text><text x="540" y="1480" text-anchor="middle" fill="{C['ink']}" font-size="25">ODGOVORITE ISPOD ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 9:
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="74" font-weight="900">Vrijeme je</text><text x="90" y="510" fill="{C['amber']}" font-size="74" font-weight="900">operativni signal.</text><path d="M150 900H930" stroke="{C['line']}" stroke-width="16"/><circle cx="210" cy="900" r="64" fill="{C['blue']}"/><circle cx="540" cy="900" r="64" fill="{C['amber']}"/><circle cx="870" cy="900" r="64" fill="{C['blue']}"/><text x="210" y="1030" text-anchor="middle" fill="{C['ink']}" font-size="27" font-weight="900">ZADRŽI</text><text x="540" y="1030" text-anchor="middle" fill="{C['ink']}" font-size="27" font-weight="900">KORIGIRAJ</text><text x="870" y="1030" text-anchor="middle" fill="{C['ink']}" font-size="27" font-weight="900">IZAĐI</text><rect x="190" y="1370" width="700" height="110" rx="55" fill="{C['blue']}"/><text x="540" y="1438" text-anchor="middle" fill="{C['navy']}" font-size="26" font-weight="900">POGLEDAJTE CIJELU OBJAVU →</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 10:
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="68" font-weight="900">Vrijednost se</text><text x="90" y="505" fill="{C['amber']}" font-size="68" font-weight="900">mijenja s tržištem.</text><path d="M100 1230C260 1130 330 830 500 940S720 620 980 690" fill="none" stroke="{C['blue']}" stroke-width="18"/><circle cx="180" cy="1170" r="32" fill="{C['amber']}"/><circle cx="500" cy="940" r="32" fill="{C['blue']}"/><circle cx="800" cy="700" r="32" fill="{C['amber']}"/><text x="180" y="1330" text-anchor="middle" fill="{C['ink']}" font-size="22">vozilo</text><text x="500" y="1070" text-anchor="middle" fill="{C['ink']}" font-size="22">segment</text><text x="800" y="830" text-anchor="middle" fill="{C['ink']}" font-size="22">portfelj</text><text x="540" y="1500" text-anchor="middle" fill="{C['blue']}" font-size="25" font-weight="900">PRATITE LI TO RUČNO? ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    if n == 11:
        cells = []
        for idx, chip in enumerate(chips):
            x, y = 90 + (idx % 2) * 465, 650 + (idx // 2) * 300
            cells.append(f'<rect x="{x}" y="{y}" width="435" height="250" rx="32" fill="{C["navy2"]}" stroke="{C["amber"] if idx==3 else C["blue"]}"/><text x="{x+218}" y="{y+142}" text-anchor="middle" fill="{C["ink"]}" font-size="35" font-weight="900">{e(chip)}</text>')
        body = f'''<text x="90" y="420" fill="{C['ink']}" font-size="63" font-weight="900">Koji jedan KPI</text><text x="90" y="505" fill="{C['amber']}" font-size="63" font-weight="900">želite razjasniti?</text>{''.join(cells)}<text x="540" y="1435" text-anchor="middle" fill="{C['blue']}" font-size="25" font-weight="900">ODABERITE JEDAN ↓</text>'''
        return story_frame(content_id, eyebrow, body)
    body = f'''<text x="90" y="450" fill="{C['navy']}" font-size="85" font-weight="900">Jedan slučaj.</text><text x="90" y="555" fill="{C['navy']}" font-size="85" font-weight="900">Jedan signal.</text><text x="90" y="660" fill="{C['navy']}" font-size="85" font-weight="900">Jasan test.</text><circle cx="870" cy="950" r="240" fill="none" stroke="{C['blue']}" stroke-width="52"/><path d="M710 950H1020" stroke="{C['navy']}" stroke-width="20"/><path d="M1020 950l-70-50v100z" fill="{C['navy']}"/><rect x="90" y="1300" width="900" height="130" rx="65" fill="{C['navy']}"/><text x="540" y="1380" text-anchor="middle" fill="{C['ink']}" font-size="29" font-weight="900">DOGOVORITE POSLOVNI PRIKAZ →</text>'''
    return story_frame(content_id, eyebrow, body, amber_bg=True)
