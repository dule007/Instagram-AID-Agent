# Arhitektura AID Instagram Growth Agenta

## 1. Svrha sustava

AID Instagram Growth Agent je content engine za stvaranje kvalificiranih B2B leadova za AutoInsight Data. Primarni cilj nije rast broja pratitelja, nego pretvaranje relevantne publike iz autoindustrije u mjerljive poslovne razgovore.

Prva verzija sustava radi uz obavezno ljudsko odobrenje. Nijedan sadržaj ne smije biti objavljen samo zato što ga je model generirao.

## 2. Opseg prve verzije

Prva verzija obuhvaća:

- generiranje mjesečne strategije;
- izradu nacrta pojedinačnih objava;
- evidenciju izvora, brojki i poslovnih tvrdnji;
- automatske i ručne provjere sadržaja;
- ručno odobrenje prije objave;
- pripremu uputa i sadržaja za Canva vizual;
- planiranje objave nakon odobrenja;
- dohvat i spremanje rezultata objava;
- korištenje rezultata kao ulaza za sljedeći ciklus strategije.

Izvan opsega prve verzije su:

- produkcijska konfiguracija/deployment Meta OAutha i hosting medijskih datoteka;
- autonomno objavljivanje bez ručnog approval zapisa;
- ManyChat automatizacija komentara i DM poruka;
- autonomno odgovaranje korisnicima;
- spremanje stvarnih API ključeva;
- potpuno autonomno donošenje marketinških ili poslovnih odluka.

## 3. Arhitekturna načela

1. **Human-in-the-loop:** objava je moguća samo nakon eksplicitnog ljudskog odobrenja.
2. **Dokazivost tvrdnji:** svaka brojka i provjerljiva poslovna tvrdnja mora imati izvor ili biti uklonjena.
3. **Kontrolirana automatizacija:** n8n koordinira korake, ali ne smije zaobići poslovna pravila.
4. **Sljedivost:** strategija, prompt, generirani sadržaj, revizije, odobrenja i metrike čuvaju se kao povijest.
5. **Odvojene odgovornosti:** generiranje, validacija, odobrenje, objavljivanje i analitika zasebni su koraci.
6. **Sigurnost po zadanim postavkama:** tajne se drže izvan repozitorija, uz minimalne ovlasti integracija.
7. **Mjerljiv poslovni ishod:** optimizacija se temelji na kvalificiranim interakcijama i leadovima, ne na vanity metrikama.

## 4. Logičke komponente

### 4.1 n8n — orkestracijski sloj

n8n pokreće vremenske i ručne procese, prenosi podatke između servisa, provodi statusne uvjete, evidentira pogreške i šalje zadatke na odobrenje. Poslovna pravila koja štite objavu moraju biti izričito provjerena prije svakog koraka prema Meta API-ju.

### 4.2 Content Benchmark Super Task — istraživanje i quality gate

Prije svake nove ili materijalno izmijenjene feed, carousel, Reel ili Story
objave sustav pregledava najmanje tri aktualna i provjerljiva izvora iz iste
niše, buyer konteksta i formata. Benchmark vrijedi najviše sedam dana.
Prenosivi obrasci koriste se kao principi, ne kao predložak za kopiranje.

Svaka varijanta dobiva interni creative score prema rubrici iz
`docs/content_research_gate.md`. Rezultat ispod 80/100, istekli benchmark,
neprovjerena tvrdnja ili nedostatak izvora blokiraju odobrenje i objavu.

### 4.3 OpenAI API — strategija i generiranje

OpenAI API koristi se za:

- prijedlog mjesečne strategije iz odobrenog poslovnog konteksta i prethodnih rezultata;
- izradu nacrta objava, carousela i reel scenarija;
- strukturiranje tvrdnji koje zahtijevaju provjeru;
- generiranje varijanti naslova, CTA-a i vizualnog briefa;
- analizu rezultata i prijedlog hipoteza za idući ciklus.

Model nema ovlast samostalno potvrditi istinitost tvrdnje ni odobriti objavu.

### 4.4 Canva — priprema vizuala

Canva prima odobreni tekstualni i vizualni brief. U prvoj fazi integracija može biti ručna ili poluautomatska: sustav priprema strukturiran paket, a korisnik izrađuje ili potvrđuje finalni vizual. Canva datoteka i izvezena verzija evidentiraju se uz objavu.

### 4.5 Meta Instagram API — objava i analitika

Lokalni approval-gated adapter nalazi se u `instagram_agent/`. OAuth konektor
`instagram_agent/oauth.py` provodi službeni Instagram Login preko loopback
callbacka, CSRF state provjere i lokalne Git-ignorirane token sesije s dozvolom
`0600`. Može objaviti pojedinačnu feed sliku preko službenog Meta Graph API-ja
tek kada su konfigurirani Instagram App ID/Secret, Graph verzija, javni HTTPS
URL asseta i ručno odobren hash točne verzije. Produkcijski hosting, scheduler,
carousel, Reel i analitika još nisu implementirani.
OAuth i neposredna pre-publish provjera fail-closed dopuštaju samo kanonski
profesionalni račun `@autoinsightdata`.

Za kontrolirani jednokratni image publish postoji loopback one-file media
server koji može poslužiti samo zaključani JPEG. Javni HTTPS tunel nije trajni
hosting i ne pokreće se automatski: prije svakog korištenja vlasnik mora
izričito prihvatiti da će finalni javni sadržaj kratko biti dostupan odabranom
tunnel provideru. Nasumični URL, JPEG hash i termin moraju biti poznati prije
sadržajnog odobrenja te ostati nepromijenjeni do dovršetka Meta containera.

Adapter mora:

- prihvatiti samo sadržaj u statusu `approved` ili `scheduled`;
- objaviti točno odobrenu verziju teksta i vizuala;
- spremiti vanjski Instagram identifikator i vrijeme objave;
- čekati `FINISHED` stanje media containera prije publish poziva te blokirati
  automatski retry kada je ishod vanjskog poziva nejasan;
- dohvatiti dostupne metrike u definiranim intervalima;
- biti idempotentan kako ponovni pokušaj ne bi stvorio duplikat.

Read-only adapter `instagram_agent/scout.py` može, nakon službene autorizacije,
dohvatiti profil i zadnje medije vlastitog profesionalnog računa bez promjene
profila. Osnovni like/comment countovi iz tog snapshot-a nisu privatni Insights
i ne koriste se kao zamjena za reach, saves, shares, retention ili leadove.

Native Story poll/link/location stickeri nisu podržani službenim publishing
API-jem. Takve stavke ostaju `manual_only` i ne mogu zaobići ručni Share čak ni
nakon uspješne OAuth autorizacije.

### 4.6 Instagram Control Agent — operativni nadzor

Read-only dashboard u `instagram_agent/dashboard.py` prikazuje raspored,
preview finalnog PNG-a, caption, research score, status media URL-a, valjanost
ručnog approvala, manual-only Story stavke i audit podatke objavljene stavke. Dashboard ne sadrži
akciju za odobrenje ili objavu i ne prikazuje tokene. Stanje čita iz manifesta
te lokalnih `approvals/` i `published/` audit zapisa.

### 4.7 ManyChat — naknadni modul

ManyChat se uvodi tek nakon stabilizacije content enginea. Koristit će se za kontrolirane tokove pokrenute komentarom ili DM porukom. Svaki tok mora imati jasnu svrhu, dopuštene odgovore, pravila eskalacije čovjeku i evidenciju pristanka gdje je potrebna.

### 4.8 PostgreSQL — izvor operativne istine

PostgreSQL čuva strategije, objave, verzije sadržaja, tvrdnje i izvore, odobrenja, rasporede, vanjske identifikatore, metrike, leade i audit događaje. Baza je izvor statusa; n8n izvršava procese, ali nije jedino mjesto na kojem postoji poslovno stanje.

## 5. Obavezni end-to-end tijek

1. Sustav učita odobreni AID poslovni kontekst, ciljne segmente i rezultate prethodnog razdoblja.
2. OpenAI pripremi nacrt mjesečne strategije.
3. Odgovorna osoba pregleda i odobri ili vrati strategiju na doradu.
4. Za odobrenu strategiju pokreće se aktualni benchmark iste niše, buyera i formata.
5. Generiraju se najmanje dvije varijante, a odabrana mora proći research gate i creative score 80/100.
6. Sustav izdvaja sve brojke, usporedbe, superlative i poslovne tvrdnje.
7. Svaka tvrdnja dobiva izvor i status provjere. Neprovjerene tvrdnje blokiraju odobrenje.
8. Agent prikazuje finalni approval paket i staje bez objave.
9. Urednik pregledava finalni tekst, vizual, termin, upozorenja i hash te eksplicitno odobrava konkretnu verziju.
10. Tek odobrena verzija može biti označena za objavu. Feed objava može se
   izvršiti lokalnim adapterom; Story s native stickerom ostaje ručan.
11. Neposredno prije Meta poziva ponovno se provjeravaju research gate, approval hash, termin i duplikat.
12. Nakon objave spremaju se Instagram ID, URL i vrijeme objave.
13. Metrike se dohvaćaju u definiranim vremenskim prozorima i povezuju s objavom.
14. Rezultati se pretvaraju u dokumentirane uvide i hipoteze za sljedeću strategiju.

## 6. Životni ciklus sadržaja

Preporučeni statusi objave:

`idea` → `draft` → `verification_required` → `verified` → `review_required` → `approved` → `scheduled` → `published` → `measured` → `archived`

Povratni statusi:

- `changes_requested` — potreban je novi sadržaj ili revizija;
- `rejected` — objava se neće koristiti;
- `failed` — tehnička obrada ili objava nije uspjela;
- `cancelled` — prethodno odobrena ili planirana objava povučena je prije objave.

Svaka sadržajna izmjena nakon odobrenja stvara novu verziju i poništava prethodno odobrenje.

## 7. Sigurnost i upravljanje tajnama

- Stvarni ključevi ne ulaze u Git ni u dokumentaciju.
- Lokalni razvoj koristi `.env`, a repozitorij smije sadržavati samo `.env.example` s praznim vrijednostima.
- Produkcijske tajne čuvaju se u n8n credentials spremištu ili namjenskom secret manageru.
- Svaka integracija dobiva samo potrebne ovlasti.
- Webhookovi moraju provjeravati potpis ili drugi pouzdani autentikacijski mehanizam.
- Osjetljivi podaci ne smiju se slati modelu ako nisu potrebni za konkretan zadatak.
- Audit zapis ne smije sadržavati API ključeve ni pune autentikacijske tokene.

## 8. Pouzdanost i nadzor

Svaki workflow mora imati jedinstveni `run_id`, zapis početka i završetka, broj pokušaja, rezultat i čitljivu poruku pogreške. Ponovni pokušaji dopušteni su samo za tehničke pogreške i moraju biti idempotentni. Poslovne blokade, poput neprovjerene tvrdnje ili nedostatka odobrenja, ne rješavaju se automatskim retryjem.

Minimalni operativni pokazatelji su:

- broj sadržaja po statusu;
- prosječno vrijeme od nacrta do odobrenja;
- broj vraćenih i odbijenih objava;
- broj blokiranih tvrdnji;
- neuspjeli workflowi i ponovni pokušaji;
- objave bez uvezenih metrika;
- kvalificirane interakcije i leadovi povezani s objavom.

## 9. Faze isporuke

### Faza 1 — content engine s ručnim odobrenjem

PostgreSQL model, n8n nacrti workflowa, OpenAI generiranje, provjera tvrdnji,
verzioniranje i ručno odobrenje. Lokalni adapter može izvršiti odobrenu feed
objavu, ali nije produkcijski konfiguriran.

### Faza 2 — kontrolirano objavljivanje i analitika

Produkcijska OAuth konfiguracija, javni media hosting, scheduler, idempotentno
zakazivanje, periodični dohvat metrika i operativni alerti.

### Faza 3 — lead automatizacija

ManyChat tokovi, evidencija kvalifikacije leadova, eskalacija prodaji i atribucija leadova sadržaju.

### Faza 4 — optimizacija

Eksperimenti s formatima i CTA-ovima, kvalitetniji modeli atribucije i kontrolirano uključivanje rezultata u sljedeći ciklus strategije.
