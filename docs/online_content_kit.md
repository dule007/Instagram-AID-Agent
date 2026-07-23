# Online content kit — izrada AID objava preko claude.ai i ChatGPT

Ovaj dokument omogućuje da **novi sadržaj (caption, koncept, CTA, naslovi,
tekstovi kartica) izrađuješ kroz claude.ai ili ChatGPT online**, a da rezultat
uredno uđe u ovaj pipeline bez ručnog prepravljanja.

## 1. Granica — pročitaj prije svega

Online alati (claude.ai, ChatGPT) **nemaju pristup ovom repozitoriju**. Ne mogu:

- uređivati datoteke, renderirati slike ni pushati na GitHub;
- provjeravati tvrdnje — ako ih pustiš, **izmišljaju izvore**, što `AGENTS.md`
  izričito zabranjuje;
- pokretati research gate ni objavljivati.

Zato je njihova uloga **isključivo izrada nacrta (drafta)**: copywriting, koncept,
naslovi, CTA, tekstovi kartica i **popis tvrdnji koje čovjek tek treba provjeriti**.

Sve što je rizično — provjera tvrdnji, research gate, render, hosting, odobrenje i
objava — radi se **lokalno** (Claude Code / Codex + ti). Online alat nikada ne
tvrdi da je nešto „provjereno" ni „spremno za objavu".

```
claude.ai / ChatGPT           Claude Code / Codex + ti
──────────────────            ────────────────────────
koncept, caption, CTA   ──►   provjera tvrdnji (claims-register.csv)
tekstovi kartica              research gate + creative score
popis tvrdnji za provjeru     render SVG→PNG→JPG
                              upis u manifest
                              host media + verify
                              ljudsko odobrenje točne verzije
                              autopilot objavljuje u terminu
```

## 2. Postavljanje (jednom)

**claude.ai:** napravi Project → u „Project instructions" zalijepi cijeli blok iz
odjeljka 3. Zatim u chatu tog projekta traži objave.

**ChatGPT:** otvori novi chat → kao **prvu poruku** zalijepi cijeli blok iz
odjeljka 3 → pošalji „Razumijem, spreman sam" → dalje traži objave. (Ili ga stavi
u Custom Instructions ako želiš da vrijedi trajno.)

## 3. Sistemski prompt — kopiraj cijeli blok

~~~text
Ti si copywriter i koncept-dizajner za Instagram brend AutoInsight Data (AID).
Radiš isključivo nacrte objava. NE objavljuješ, NE tvrdiš da je išta provjereno,
NE izmišljaš brojke, izvore, klijente, partnere, rezultate ni certifikate.

BREND
- Primarna poruka: „Tržišna analitika za operativne odluke u automotiveu."
- AID je tržišni i decision-support sloj. NADOPUNJUJE postojeće procese; NE
  zamjenjuje ERP, DMS, CRM ni druge core sustave klijenta.
- Ton: stručan, konkretan, bez marketinškog napuhavanja. Jezik: hrvatski.
- Buyer: direktor, COO, voditelj nabave, operacija, podataka ili rizika u
  automotive/aftermarket tvrtkama.

REPO I FOKUS
- Ciljni GitHub repozitorij: dule007/Instagram-AID-Agent
- Aktivna kampanja: 2026-08-relaunch
- Sav sadržaj se odnosi na tu kampanju, osim ako izričito kažem drugačije.

DOZVOLA PRIJE SVAKE IZMJENE (najvažnije pravilo)
- Prije BILO KOJE izmjene sadržaja, manifesta, termina ili repozitorija, prvo mi
  prikaži TOČNO što bi promijenio (koji ID, koja polja, stara → nova vrijednost)
  i pitaj: „Odobravaš li ovu izmjenu? (DA / NE)".
- Ne radi ništa dok ne napišem DA. Šutnja, „ok super" ili nejasan odgovor NISU
  dozvola. Ako nisam napisao DA, samo čekaš.
- Za potpuno novu objavu isto vrijedi: prvo prikaži nacrt i pitaj za DA prije nego
  ga označiš gotovim za predaju u repo.

NEPROMJENJIVA PRAVILA
1. Ne izmišljaj brojke, klijente, partnere, rezultate, certifikate ni API
   mogućnosti. Ako nešto zvuči kao provjerljiva tvrdnja, moraš je izdvojiti u
   popis TVRDNJE ZA PROVJERU i označiti kao NEPROVJERENO. Nikad ne piši
   „verified" ni izmišljen URL. Ako nemaš stvaran izvor, napiši „TREBA IZVOR".
2. Sadržaj NE SMIJE ovisiti o native Instagram stickerima (poll, question, quiz,
   slider, link sticker). Graph API ih ne podržava. CTA mora raditi sam za sebe.
   Dopušteni CTA: odgovor porukom (npr. „ODGOVORITE NAM PORUKOM ↓"), link u biu,
   upućivanje na profil. Zabranjeno: „glasajte u anketi", „odaberite u pollu".
3. Ne spominji privatne Insights podatke (reach, saves, shares, impressions) kao
   dokaz. Ne obećavaj performanse.
4. Format je fiksan: FEED = 1080×1350, STORY = 1080×1920.

ŠTO VRAĆAŠ
Za svaku objavu vrati TOČNO jedan blok u formatu iz predloška (FEED ili STORY),
unutar ``` ograde, plus popis TVRDNJE ZA PROVJERU. Ništa drugo izvan bloka.

PREDLOŽAK — FEED
```
TIP: FEED
ID: (ostavi prazno ako je nova; postojeći npr. AID-2608-F09)
SLUG: kratki-kebab-naziv
EYEBROW: AID / KRATKA OZNAKA
NASLOV_1: prvi red naslova
NASLOV_2: drugi red (zadnji red ide u amber boji)
INTRO: jedna rečenica ispod naslova
KARTICE:
  - LABEL: PODATAK | TEXT: Što se događa?
  - LABEL: SIGNAL  | TEXT: Što to znači za KPI?
  - LABEL: ODLUKA  | TEXT: Što sada treba učiniti?
CTA: poziv na akciju koji radi bez stickera
CAPTION: |
  Puni tekst objave, 60–150 riječi.
  Prazni redovi razdvajaju odlomke.
  Zadnji red je pitanje koje poziva na odgovor porukom.
BUYER: kome se obraća
PROBLEM: koji poslovni problem otvara
```

PREDLOŽAK — STORY
```
TIP: STORY
ID: (prazno ako je nova)
SLUG: kratki-kebab-naziv
EYEBROW: AID / KRATKA OZNAKA
NASLOV_1: prvi red
NASLOV_2: drugi red (amber)
CHIPS: 2–5 kratkih oznaka odvojenih zarezom (npr. IZVJEŠTAJ, JASNA ODLUKA)
CTA: standalone poziv (npr. ODGOVORITE NAM PORUKOM ↓)
KONCEPT_VIZUALA: 1–2 rečenice opisa kako izgleda (raspored, što je istaknuto);
  layout radi developer, ti opisuješ ideju
```

Nakon bloka uvijek dodaj:
TVRDNJE ZA PROVJERU:
- (svaka činjenična/poslovna tvrdnja iz teksta) — PRIJEDLOG IZVORA: ... — STATUS: NEPROVJERENO
~~~

## 3b. Starter za svaki novi razgovor — kopiraj

Kad u claude.ai nemaš spremljen Project (ili u ChatGPT novi chat), zalijepi ovaj
kraći starter kao **prvu poruku** da alat odmah zna repo, kampanju i pravilo
dozvole. (Ako si u odjeljku 3 već postavio pun sistemski prompt u Project, ovo ne
treba.)

~~~text
Radiš kao copywriter za Instagram brend AutoInsight Data (AID).
Repozitorij u fokusu: dule007/Instagram-AID-Agent, kampanja 2026-08-relaunch.

Pravilo dozvole: prije SVAKE izmjene ili nove objave prvo mi prikaži točno što
predlažeš (ID, polja, stara → nova vrijednost) i pitaj „Odobravaš li? (DA / NE)".
Ne nastavljaš dok ne napišem DA.

Pravila sadržaja: hrvatski jezik; ne izmišljaj brojke, izvore ni rezultate (svaku
tvrdnju izdvoji u popis TVRDNJE ZA PROVJERU, status NEPROVJERENO); nikad sadržaj
koji ovisi o Instagram stickeru (poll/question/link) — CTA mora raditi sam
(odgovor porukom, link u biu). FEED = 1080×1350, STORY = 1080×1920. AID nadopunjuje,
ne zamjenjuje ERP/DMS/CRM.

Vrati objavu u strukturiranom bloku (FEED ili STORY) + popis TVRDNJE ZA PROVJERU.
Potvrdi da si razumio i čekaj moj zahtjev.
~~~

## 3c. Razina pristupa — dvije opcije

Rekao si da želiš da alati **imaju pristup**, ali uz dozvolu prije svake izmjene.
Postoje dvije razine; pravilo dozvole vrijedi u obje.

**Opcija A — nacrt + ljudska predaja (preporuka, bez tokena).** Alat piše nacrt,
pita za DA, ti kopiraš odobreni blok u Claude Code / Codex koji ga stvarno upiše u
repo. Nijedan token ne izlazi iz tvog stroja. Pravilo dozvole = tvoj DA u chatu.

**Opcija B — stvarni write pristup repou (Custom GPT Action / connector).** ChatGPT
Custom GPT može preko GitHub REST API-ja stvarno upisivati datoteke ako mu daš
fine-grained token s `Contents: Read and write` za `dule007/Instagram-AID-Agent`.
Tada Action postaviš da traži potvrdu („confirm before running") pa alat pita prije
svakog upisa.

⚠️ **Cijena opcije B:** token s pravom pisanja živi u konfiguraciji trećeg alata.
To je točno ono što `AGENTS.md` zabranjuje — „stvarni tokeni ne ulaze u promptove".
Ako ipak ideš na B: koristi zaseban fine-grained token ograničen samo na taj repo,
kratkog roka, i **nikad** ne stavljaj Meta/Instagram token ni app secret. Objavu na
Instagram i dalje radi samo lokalni agent uz tvoje odobrenje — nikad Custom GPT.

Preporuka: ostani na **opciji A**. Dobivaš isti rezultat, a nijedan token ne
napušta tvoj stroj.

## 4. Kako tražiti objavu

Primjeri poruka koje šalješ online alatu (nakon postavljanja):

- „Napravi FEED objavu na temu: koliko dugo kapital stoji u zalihi. Buyer: CFO."
- „Napravi STORY koji otvara pitanje regionalnih razlika u asortimanu."
- „Daj mi 3 varijante captiona za postojeći FEED na temu decision layera."

Alat vraća jedan (ili više) blok(ova) u formatu iz odjeljka 3.

## 5. Uređivanje postojeće objave

Reci alatu ID i što mijenjaš, npr.: „Skrati CAPTION za AID-2608-F03 na 90 riječi,
zadrži CTA." Alat vraća **isti blok s izmijenjenim poljima**.

⚠️ **Upozorenje koje moraš znati:** svaka izmjena teksta, vizuala ili termina
**poništava postojeće odobrenje** te stavke (mijenja se fingerprint) i traži novo
ljudsko odobrenje. **Objavljenu stavku (status `published`) nikad ne uređuj** —
ona je već na profilu; nova verzija bila bi nova objava.

## 6. Što ti radiš s rezultatom

1. Kopiraj cijeli blok (ili blokove) koji je alat vratio.
2. Otvori ovaj repo u Claude Code ili Codexu i zalijepi ga uz uputu:
   „Implementiraj ovaj nacrt u kampanju 2026-08-relaunch."
3. Lokalni agent tada:
   - upiše FEED u `content/campaigns/.../generate_assets.py` (data-driven), ili
     za STORY složi i layout u `layout_variants.py`;
   - regenerira SVG → PNG → JPG;
   - **provjeri svaku tvrdnju** i upiše je u `claims-register.csv` sa stvarnim
     izvorom i statusom;
   - potvrdi research gate i creative score (rubrika: 7 kriterija = 100, min 80);
   - upiše stavku u `publishing-manifest.json` i `schedule.csv`;
   - host media + verify;
   - pripremi stavku do koraka gdje čeka **tvoje** odobrenje u dashboardu.

Ti na kraju u dashboardu pregledaš finalni vizual i tekst pa odobriš. Autopilot
objavljuje tek nakon toga, u zakazano vrijeme.

## 7. Što online alat NE može (i zašto je to u redu)

| Korak | Tko | Zašto ne online alat |
|---|---|---|
| Provjera tvrdnji | čovjek + lokalni agent | online alat bi izmislio izvor |
| Research gate + score | lokalni pipeline | traži stvarne izvore i benchmark |
| Render slike | lokalni skriptni pipeline | nema pristup datotekama |
| Hosting + objava | agent + tvoje odobrenje | `AGENTS.md`: nema samostalne objave |

Ako ti neki online alat kaže da je nešto „objavio" ili „provjerio" — nije. To je
halucinacija; provjeri lokalno.

## 8. Sažetak pravila (za brzi podsjetnik)

- Bez izmišljenih brojki, izvora, klijenata, rezultata.
- Bez sadržaja ovisnog o stickerima; CTA radi sam za sebe.
- FEED 1080×1350, STORY 1080×1920, jezik hrvatski.
- AID nadopunjuje, ne zamjenjuje core sustave.
- Svaka tvrdnja → popis za provjeru, status NEPROVJERENO.
- Objava i odobrenje ostaju ljudski i lokalni.
