# Potrebni n8n workflowi

## 1. Načela izvedbe

Svaki workflow mora:

- imati stabilan naziv i verziju;
- zapisati `workflow_runs` zapis s korelacijskim ID-em;
- sigurno podnijeti ponovni pokušaj bez dupliranja rezultata;
- jasno razlikovati tehničku pogrešku od poslovne blokade;
- čitati i zapisivati status u PostgreSQL;
- ne spremati tajne u payload, log ili audit;
- završiti u predvidivom statusu i poslati upozorenje kada je potrebna ljudska radnja.

Workflowi su ovdje opisani kao specifikacija. U prvoj fazi ne implementiraju se stvarna Meta objava ni ManyChat automatizacija.

## 2. MVP workflowi

### WF-01 — Generiranje mjesečne strategije

**Okidač:** ručni poziv ili raspored prije početka mjeseca.

**Ulazi:** razdoblje, odobrena verzija poslovnog konteksta, ciljni segmenti, prethodni uvidi, dostupni izvori i poslovni prioritet.

**Koraci:**

1. provjeri postoje li obavezni ulazi;
2. učitaj prethodne rezultate i samo odobrene uvide;
3. sastavi strukturirani OpenAI zahtjev;
4. validiraj format odgovora;
5. spremi novu `strategy_version` kao nacrt;
6. postavi strategiju u `review_required`;
7. pošalji obavijest vlasniku strategije.

**Izlaz:** nova verzija strategije spremna za ljudski pregled.

**Blokade:** nedostaje poslovni cilj, ciljni segment ili važeći poslovni kontekst.

### WF-02 — Pregled i odobrenje strategije

**Okidač:** siguran obrazac, interna aplikacija ili odobreni webhook nakon akcije korisnika.

**Koraci:**

1. autentificiraj korisnika i ovlast;
2. učitaj točnu verziju strategije;
3. spremi odluku i komentar;
4. za `approved` postavi važeću verziju i status strategije;
5. za `changes_requested` vrati je u ciklus dorade;
6. zapiši audit događaj.

**Izlaz:** odobrena, vraćena ili odbijena strategija.

### WF-03 — Izrada plana objava iz odobrene strategije

**Okidač:** odobrenje strategije ili ručni poziv.

**Ulazi:** odobrena verzija strategije, željeni kapacitet i kalendarska ograničenja.

**Koraci:** predloži teme, format, ciljnu personu, hipotezu, CTA smjer i okvirne datume; spremi svaki prijedlog kao `content_item` u statusu `idea`.

**Izlaz:** urednički backlog, bez automatskog objavljivanja.

### WF-04 — Generiranje pojedinačne objave

**Okidač:** ručni odabir odobrene ideje.

**Ulazi:** `content_item`, odobrena strategija, poslovni kontekst, format, prompt predložak i odobreni izvori.

**Koraci:**

1. provjeri da je strategija odobrena;
2. generiraj strukturirani nacrt;
3. spremi novu `content_version`;
4. spremi hook, caption ili scenarij, CTA, hashtagove i Canva brief;
5. izdvoji modelom prijavljene tvrdnje;
6. postavi sadržaj u `verification_required`.

**Izlaz:** verzionirani nacrt s popisom tvrdnji.

### WF-05 — Ekstrakcija i preliminarna provjera tvrdnji

**Okidač:** stvaranje nove verzije sadržaja.

**Ulazi:** finalni tekst verzije i povezani izvori.

**Koraci:**

1. izdvoji brojke, usporedbe, superlative i poslovne tvrdnje;
2. dedupliciraj tvrdnje već prijavljene pri generiranju;
3. poveži dostupne izvore;
4. označi nejasne ili nepodržane tvrdnje kao `pending`;
5. pripremi paket za ljudskog provjeravatelja.

**Izlaz:** kompletan registar tvrdnji za verziju.

AI procjena nije finalna verifikacija.

### WF-06 — Ljudska verifikacija tvrdnji

**Okidač:** odluka provjeravatelja u internom sučelju ili sigurnom obrascu.

**Koraci:** spremi status, izvor, bilješku, korisnika i vrijeme za svaku tvrdnju; nakon zadnje odluke izračunaj je li verzija podobna za `verified` ili mora u `changes_requested`.

**Izlaz:** verificirana verzija ili zahtjev za ispravak.

### WF-07 — Priprema Canva paketa

**Okidač:** verzija sadržaja ima riješene tvrdnje.

**Ulazi:** format, tekst, odobrene tvrdnje, vizualni brief, brand smjernice i dimenzije.

**Koraci:** pripremi strukturirani brief po slajdovima ili kadrovima; stvori zadatak za ručnu Canva izradu ili, nakon potvrde mogućnosti integracije, nacrt dizajna; spremi referencu bez označavanja asseta finalnim.

**Izlaz:** Canva radni paket povezan s verzijom sadržaja.

### WF-08 — Finalni pregled i ručno odobrenje objave

**Okidač:** tekst je verificiran i finalni vizual je priložen.

**Ulazi:** točan `content_version_id`, finalni asseti, izvori, planirani termin i pregled captiona.

**Koraci:**

1. ponovi provjeru statusa svih tvrdnji;
2. prikaži kompletan paket odobravatelju;
3. spremi odluku vezanu uz verziju;
4. za odobrenje postavi sadržaj u `approved`;
5. za izmjene postavi `changes_requested` i poništi planiranje;
6. zapiši audit.

**Izlaz:** eksplicitno odobrena ili vraćena verzija.

### WF-09 — Paket za ručnu objavu

**Okidač:** odobrena verzija dosegne planirano vrijeme ili urednik ručno zatraži paket.

**Koraci:** neposredno prije pripreme ponovno provjeri važeće odobrenje, status i točnu verziju; generiraj paket s finalnim captionom, assetima i checklistom; evidentiraj da je paket preuzet.

**Izlaz:** paket za ručnu objavu na Instagramu.

Ovaj workflow ne poziva Meta API.

### WF-10 — Evidentiranje ručno objavljene objave

**Okidač:** korisnik unese Instagram URL/ID i vrijeme objave.

**Koraci:** validiraj da je unesena objava povezana s odobrenom verzijom, spriječi duplikat, stvori `publication` zapis i postavi sadržaj u `published`.

**Izlaz:** pouzdana veza interne verzije i vanjske objave.

### WF-11 — Ručni ili uvozni unos metrika

**Okidač:** vremenski raspored nakon objave ili ručni upload/unos dok Meta API nije implementiran.

**Preporučeni prozori:** 24 sata, 72 sata, 7 dana i 30 dana, uz mogućnost prilagodbe.

**Koraci:** validiraj publikaciju i mjerni trenutak, spremi nepromjenjivi snapshot te označi nedostajuće vrijednosti kao nedostupne, ne kao nulu.

**Izlaz:** vremenska serija rezultata objave.

### WF-12 — Analiza rezultata i prijedlog uvida

**Okidač:** pristigne definirani metrički snapshot ili završi mjesečni ciklus.

**Ulazi:** strategija, hipoteza objave, metrike, kvalitativne interakcije i eventualna atribucija leadova.

**Koraci:** izračunaj determinističke pokazatelje, zatim zatraži od modela sažetak i hipoteze; spremi ih kao `content_insights` u statusu za ljudski pregled.

**Izlaz:** dokazima povezani prijedlozi za zadržavanje, promjenu ili novi test.

### WF-13 — Odobrenje uvida za sljedeći ciklus

**Okidač:** strateg pregleda predložene uvide.

**Koraci:** prihvati, odbij ili doradi svaki uvid; samo prihvaćeni uvidi postaju ulaz u WF-01.

**Izlaz:** kontrolirana memorija performansi sadržaja.

### WF-14 — Operativni monitoring i obavijesti

**Okidač:** raspored svakih nekoliko minuta ili događaj neuspjeha.

**Provjere:** workflowi u grešci, zapisi zaglavljeni u prijelaznom statusu, objave kojima istječe rok bez odobrenja, objave bez metrika i neuobičajen broj retryja.

**Izlaz:** obavijest odgovornoj osobi s `run_id`, entitetom, uzrokom i preporučenom ljudskom radnjom.

## 3. Workflowi nakon MVP-a

### WF-15 — Meta objava

Objavljuje samo važeću odobrenu verziju, koristi `idempotency_key`, ponovno provjerava status neposredno prije poziva i sprema rezultat. Implementirati tek nakon testiranja Meta ovlasti i sandbox scenarija.

### WF-16 — Meta dohvat metrika

Periodično dohvaća dopuštene metrike, sprema sirovi payload i normalizirani snapshot te detektira opozvane ovlasti ili nedostupne metrike.

### WF-17 — ManyChat komentar/DM ulaz

Prima dopuštene događaje, povezuje ih s objavom, primjenjuje odobreni razgovorni tok i po potrebi eskalira čovjeku. Ne generira proizvoljne odgovore bez granica.

### WF-18 — Kvalifikacija i predaja leada

Prikuplja minimalne dopuštene podatke, predlaže kvalifikaciju, omogućuje ručnu potvrdu te šalje lead prema dogovorenom CRM ili prodajnom procesu.

### WF-19 — Sinkronizacija Canva asseta

Nakon potvrde Canva API mogućnosti sinkronizira nacrt i finalni export, provjerava verziju i checksum te ne zamjenjuje finalni odobreni asset bez novog odobrenja.

## 4. Zajednički podworkflowi

Preporučeni reusable workflowi:

- `SUB-01 Validate Entity State` — provjera statusa, verzije i vlasništva;
- `SUB-02 Start Workflow Run` — stvaranje `workflow_runs` i korelacijskog ID-a;
- `SUB-03 Finish Workflow Run` — standardizirani uspjeh, blokada ili greška;
- `SUB-04 OpenAI Structured Call` — poziv sa schema validacijom, timeoutom i sigurnim logiranjem;
- `SUB-05 Notify Human` — standardna obavijest bez tajni;
- `SUB-06 Write Audit Event` — append-only audit događaj;
- `SUB-07 Verify Approval Gate` — provjera odobrenja konkretne verzije;
- `SUB-08 Safe Retry` — ograničeni exponential backoff za tehničke pogreške;
- `SUB-09 Redact Secrets` — uklanjanje osjetljivih vrijednosti prije logiranja.

## 5. Preporučeni redoslijed izrade

1. zajednički workflowi za run log, audit, validaciju stanja i obavijesti;
2. WF-01 i WF-02 za strategiju;
3. WF-03 do WF-06 za sadržaj i tvrdnje;
4. WF-07 do WF-10 za vizual, odobrenje i ručnu objavu;
5. WF-11 do WF-14 za metrike, učenje i monitoring;
6. WF-15 i WF-16 tek nakon Meta integracijskog dizajna i testnog računa;
7. WF-17 i WF-18 u kasnijoj ManyChat/CRM fazi;
8. WF-19 nakon provjere stvarnih Canva API mogućnosti i licencnih uvjeta.

