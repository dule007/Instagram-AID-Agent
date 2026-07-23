# AID Instagram Agent — zajedničke upute za AI agente

Ove upute vrijede za Codex, Claude Code i druge agente koji rade u ovom repozitoriju. `AGENTS.md` je kanonski izvor pravila suradnje. Agent-specifične datoteke, poput `CLAUDE.md`, ne smiju mu proturječiti.

## 1. Svrha projekta

AID Instagram Growth Agent je content engine za stvaranje kvalificiranih B2B leadova za AutoInsight Data. Primarni cilj nije rast broja pratitelja, nego relevantni poslovni razgovori.

Prva verzija koristi obavezno ljudsko odobrenje. Nijedan agent nema ovlast samostalno objaviti sadržaj, mijenjati stvarni Instagram profil ili aktivirati vanjsku automatizaciju.

## 2. Obavezni izvori prije rada

Prije sadržajnih ili arhitekturnih izmjena pročitaj relevantne izvore ovim redom:

1. `coordination/CURRENT_HANDOFF.md`;
2. `coordination/OWNERSHIP.md`;
3. `coordination/DECISIONS.md`;
4. relevantne dokumente u `docs/`;
5. relevantne izvorne dokumente u `inputs_docuemtns/`.

Za aktualno pozicioniranje počni s:

- `docs/brand_positioning.md`;
- `docs/business_rules.md`;
- `docs/content_strategy.md`;
- `docs/architecture.md`.

### Obavezni research gate za svaki feed i Story

Prije izrade ili materijalne izmjene bilo kojeg feed posta, carousela, Reela ili
Storyja agent mora izvršiti `Content Benchmark Super Task` iz
`docs/content_research_gate.md`.

- Istraživanje mora biti aktualno, vezano uz istu nišu, buyer problem i format.
- Za isti sadržaj može se koristiti benchmark star najviše sedam dana. Nakon
  isteka mora se ponovno pregledati aktualno stanje.
- Obavezno je evidentirati najmanje tri provjerljiva izvora ili javna primjera.
- Javno vidljivi lajkovi, komentari i pregledi su samo kreativni signal. Ne
  predstavljaj ih kao privatne Insights metrike ili dokaz konverzije.
- Ne koristi formulaciju „najbolja objava” bez usporedivih i provjerljivih
  podataka. Koristi „javno uočeni benchmark” ili „interno najbolje ocijenjena
  varijanta”.
- Ne kopiraj tuđi tekst, vizual ili prepoznatljivu kreativnu izvedbu. Izdvoji
  princip i izradi originalnu AID varijantu.
- Svaki sadržaj mora imati interni creative score najmanje `80/100`, bez
  blokirajuće neprovjerene tvrdnje, prije slanja na ručno odobrenje.
- Benchmark zapis i score moraju biti povezani s točnim content ID-om. Izmjena
  hooka, formata, glavne poruke, CTA-a ili vizuala zahtijeva novu ocjenu.

## 3. Nepromjenjiva poslovna pravila

- Primarna poruka je: **Tržišna analitika za operativne odluke u automotiveu.**
- AID je tržišni i decision-support sloj, a ne zamjena za core sustave klijenta.
- Ne izmišljaj brojke, klijente, partnere, rezultate, certifikate ni API mogućnosti.
- Svaka brojka i provjerljiva poslovna tvrdnja mora imati izvor i status provjere.
- Svaka objava zahtijeva ručno odobrenje točne verzije teksta i vizuala.
- Svaka objava zahtijeva valjan research gate i creative score prije odobrenja.
- Neposredno prije evidentiranja approvala agent mora prikazati puni paket za
  pregled: finalni vizual, caption ili Story uputu, termin, research score,
  tvrdnje, upozorenja i zaključani hash. Zatim mora stati i zatražiti izričito
  ljudsko odobrenje; izostanak odgovora nikada nije odobrenje.
- Izmjena nakon odobrenja poništava odobrenje.
- **Sadržaj ne smije ovisiti o native Instagram stickerima.** Poll, question,
  quiz, slider i link sticker ne postoje u Graph API-ju, pa svaka stavka koja ih
  traži zahtijeva ručno dovršavanje u aplikaciji i time izlazi iz autopilota.
  Zabranjeno je i da vizual upućuje na sticker kojeg neće biti — CTA tipa
  „odaberite u pollu ↓" nad praznim mjestom je pokvarena objava. Dopušteni
  zamjenski pozivi na akciju: odgovor porukom (nativni story reply), link u biu
  i upućivanje na profil. Iznimka je moguća samo uz izričitu korisničku odluku i
  oznaku `manual_only: true` u manifestu.
- Ne implementiraj Meta objavljivanje, ManyChat automatizaciju ili produkcijske integracije bez novog izričitog korisničkog zahtjeva.
- Instagram lozinka se nikada ne zapisuje, koristi ni prenosi. Za buduću
  integraciju koristi se službena Meta autorizacija. Automatizacija preko
  preglednika (Selenium, Playwright i slično) nad Instagram sučeljem je
  zabranjena: traži lozinku, krši Instagramove uvjete i riskira gubitak
  Business računa, a time i službenog Graph API pristupa.
- Scouting preko Instagram računa smije biti samo read-only i preko službenog
  Meta API-ja. Ne zaobilazi login zid, ne scrapea privatne profile i ne
  predstavlja javne metrike drugih računa kao njihove privatne Insights podatke.
- Stvarni API ključevi, tokeni i tajne ne ulaze u Git, dokumentaciju, promptove ni audit zapise.

## 4. Pravila suradnje Codex ↔ Claude Code

### Prije izmjene

1. Pokreni `git status --short --branch`.
2. Pročitaj aktualni handoff i ownership tablicu.
3. Provjeri postoje li korisničke ili agentske izmjene u ciljanim datotekama.
4. U `coordination/OWNERSHIP.md` zapiši koje datoteke preuzimaš, svrhu i vrijeme.
5. Ako je ciljanu datoteku preuzeo drugi aktivni agent, ne mijenjaj je. Radi na odvojenoj datoteci ili čekaj novi handoff.

### Tijekom rada

- Jedan agent smije biti urednik pojedine datoteke u jednom trenutku.
- Ne prepisuj ili briši tuđe promjene da bi pojednostavio vlastiti zadatak.
- Drži izmjene usko vezane uz korisnički zahtjev.
- Za lokalne izmjene koristi uređive izvore; PNG se generira iz pripadajućeg SVG-a.
- Ne predstavljaj specifikaciju kao implementirani n8n workflow.
- Ne predstavljaj javno dostupne Instagram podatke kao privatne Insights metrike.
- Ako pronađeš kontradikciju, zapiši je u `coordination/DECISIONS.md` i zaustavi rizičnu odluku dok je korisnik ne potvrdi.

### Nakon rada

1. Pokreni provjere primjerene izmjenama.
2. Ažuriraj `coordination/CURRENT_HANDOFF.md` sa stvarnim stanjem, promijenjenim datotekama i preostalim koracima.
3. Dodaj važnu trajnu odluku u `coordination/DECISIONS.md`.
4. Oslobodi ownership redove koje više ne držiš.
5. U završnoj poruci jasno odvoji: dovršeno, provjereno, nije implementirano i blokirano.

## 5. Struktura projekta

- `docs/` — kanonska arhitektura, poslovna pravila, pozicioniranje, strategija, baza i workflow specifikacije;
- `docs/online_content_kit.md` — kanonske upute i sistemski prompt za izradu
  sadržaja preko claude.ai/ChatGPT online; online alat radi samo nacrte, uz
  obaveznu dozvolu prije svake izmjene i bez samostalne objave;
- `inputs_docuemtns/` — korisnički izvorni dokumenti; ne uređivati bez izričitog zahtjeva;
- `workflows/n8n/specs/` — specifikacije i Mermaid vizuali; nisu n8n import JSON datoteke;
- `content/objave/` — feed SVG, PNG i sadržajni briefovi;
- `content/storiji/` — Story SVG, PNG i izvedbene upute;
- `coordination/` — stanje suradnje, ownership, odluke i handoff.

## 6. Minimalna provjera

Za svaku promjenu:

```bash
git status --short --branch
rg -n "[[:blank:]]+$" docs content workflows coordination AGENTS.md CLAUDE.md
```

Za SVG/PNG assete dodatno provjeri:

- feed: 1080 × 1350;
- Story: 1080 × 1920;
- SVG se može parsirati;
- PNG postoji i odgovara istoj verziji SVG-a;
- sav tekst je čitljiv i unutar sigurnih zona.

Za n8n dokumentaciju provjeri da svaka specifikacija ima točno jedan Mermaid blok i da status ne sugerira aktivnu produkcijsku automatizaciju.

## 7. Komunikacija

Piši korisniku na hrvatskom/BHS jeziku osim ako zatraži drugo. Budi izravan, navedi točne putanje i ne tvrdi da je vanjska akcija izvršena ako je izrađen samo lokalni prijedlog.
