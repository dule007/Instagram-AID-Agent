# Poslovna pravila

## 1. Poslovni cilj

Sadržaj mora povećavati broj relevantnih poslovnih razgovora za AutoInsight Data. Broj pratitelja, lajkova i pregleda prati se kao pomoćni signal, ali ne predstavlja krajnji kriterij uspjeha.

Prioritetni ishodi su:

- interes relevantne tvrtke ili donositelja odluka;
- kvalificirani komentar, DM ili posjet poslovnoj odredišnoj stranici;
- zahtjev za demonstraciju, razgovor ili dodatne informacije;
- prepoznat problem koji AID može riješiti;
- dokaz da sadržaj gradi povjerenje u podatke i stručnost AID-a.

## 2. Uloge i ovlasti

### Strateg / vlasnik sadržaja

Definira poslovni fokus, ciljnu publiku i mjesečne prioritete te odobrava strategiju.

### Urednik

Pregledava tekst, ton, strukturu, vizual i CTA. Može zatražiti izmjene, odbiti ili odobriti konkretnu verziju objave.

### Provjeravatelj tvrdnji

Potvrđuje brojke i poslovne tvrdnje na temelju dopuštenih izvora. Ne smije potvrditi tvrdnju samo zato što je zvučno ili uvjerljivo formulirana.

### Administrator sustava

Upravlja integracijama, tajnama i operativnim incidentima. Administratorska ovlast ne zamjenjuje sadržajno odobrenje.

Jedna osoba može imati više uloga u MVP-u, ali svaki čin provjere i odobrenja mora biti zasebno evidentiran.

## 3. Pravila strategije

- Strategija se izrađuje za određeni kalendarski mjesec i mora imati vlasnika.
- Mora navesti poslovni cilj, ciljne segmente, probleme publike, tematske stupove, formate, CTA pristup i hipoteze koje se testiraju.
- Strategija je nacrt dok je čovjek eksplicitno ne odobri.
- Objave se ne planiraju iz strategije koja nije odobrena.
- Promjena poslovnog cilja ili ciljne publike zahtijeva novu verziju strategije i novo odobrenje.
- Rezultati prethodnog razdoblja mogu utjecati na novu strategiju samo kao dokumentirani uvidi, ne kao automatska naredba.

## 4. Pravila generiranja sadržaja

- Svaka objava mora biti povezana s jednom odobrenom strategijom i jednim primarnim poslovnim ciljem.
- Svaka objava mora imati jasno definiranu ciljnu personu, problem, ključnu poruku, format i CTA.
- Model mora odvojeno vratiti tekst objave, vizualni brief, popis tvrdnji i popis korištenih izvora.
- Ako nema dovoljno podataka, model mora označiti nedostatak umjesto izmišljanja sadržaja.
- Zabranjeni su izmišljeni korisnici, izjave, studije slučaja, brojke, partnerstva, nagrade i rezultati.
- AID interne informacije koriste se samo ako su odobrene za vanjsku komunikaciju.
- Sadržaj ne smije obećavati rezultat koji AID ne može dokazati ili isporučiti.
- Svaka generacija i ručna izmjena stvaraju novu verziju sadržaja.

## 5. Provjera brojki i tvrdnji

Provjera je obavezna za:

- sve brojke, postotke, iznose i vremenske periode;
- usporedbe s tržištem ili konkurentima;
- tvrdnje o rastu, uštedi, preciznosti, pokrivenosti ili performansama;
- superlative poput „najbolji”, „najveći”, „jedini” ili „prvi”;
- pravne, regulatorne, sigurnosne i tehničke tvrdnje;
- rezultate klijenata i studije slučaja;
- podatke koji mogu zastarjeti.

Svaka tvrdnja mora imati:

- doslovni tekst ili jasno označen raspon teksta;
- vrstu tvrdnje;
- izvor ili internog vlasnika informacije;
- datum pristupa ili potvrde;
- status `pending`, `verified`, `rejected` ili `not_applicable`;
- identitet provjeravatelja i bilješku.

Objava ne može prijeći u `verified` ako postoji barem jedna tvrdnja u statusu `pending` ili `rejected`. Ako pouzdan izvor ne postoji, tvrdnja se uklanja ili preformulira tako da ne zahtijeva nedokazivu činjenicu.

## 6. Dopušteni izvori

Prednost imaju:

1. odobreni AID podaci i dokumenti s poznatim vlasnikom;
2. službeni javni izvori i regulatorne publikacije;
3. primarna istraživanja i službena dokumentacija;
4. pouzdani sekundarni izvori kada primarni nisu dostupni.

Objava na društvenoj mreži, generički blog ili odgovor jezičnog modela sami po sebi nisu dokaz tvrdnje.

## 7. Ručno odobrenje

- Ručno odobrenje obavezno je za svaku objavu i svaku finalnu vizualnu verziju.
- Odobrenje mora sadržavati korisnika, vrijeme i točan `content_version_id`.
- Odobrenje nije valjano ako je dano samo u slobodnoj poruci koja nije povezana sa zapisom objave.
- Nakon izmjene teksta, CTA-a, ključne brojke, vizuala ili datoteke odobrenje se automatski poništava.
- Osoba koja odobrava mora vidjeti finalni caption, vizual, izvore tvrdnji i planirano vrijeme objave.
- `rejected` sadržaj ne smije se ponovno koristiti bez stvaranja nove verzije i novog pregleda.

## 8. Pravila objavljivanja

- U prvoj fazi objava je ručna.
- Buduća automatizacija smije objaviti samo finalnu odobrenu verziju.
- Status u bazi provjerava se neposredno prije objave, ne samo pri zakazivanju.
- Otkazivanje ili povlačenje odobrenja blokira objavu.
- Jedan odobreni zapis smije rezultirati najviše jednom Instagram objavom, osim ako je ponovna objava eksplicitno kreirana kao novi zapis.
- Nakon objave spremaju se vanjski ID, URL, vrijeme objave i identitet izvršitelja.
- Tehnička pogreška ne smije promijeniti sadržaj ni automatski generirati zamjensku objavu.

## 9. Pravila mjerenja i učenja

- Metrike se vežu uz konkretnu objavu i točan trenutak mjerenja.
- Sirove metrike čuvaju se odvojeno od izvedenih pokazatelja i AI zaključaka.
- Uvid mora navesti koje objave i koje metrike ga podupiru.
- Korelacija se ne smije predstavljati kao uzročnost.
- Jedna uspješna ili neuspješna objava nije dovoljan dokaz trajnog obrasca.
- AI može predložiti hipotezu, ali čovjek odobrava promjenu strategije.
- Optimizacija ne smije nagraditi clickbait, nedokazive tvrdnje ili nerelevantan engagement.

## 10. Definicija kvalificiranog leada

Lead je kvalificiran kada postoji dovoljno podataka da se procijeni poslovna relevantnost, primjerice:

- osoba ili tvrtka pripada ciljnom segmentu;
- prepoznat je konkretan poslovni problem ili interes;
- postoji namjera za razgovor, demonstraciju ili razmjenu dodatnih informacija;
- kontakt i obrada podataka dopušteni su prema primjenjivim pravilima.

Kvalifikacija mora biti transparentna i omogućiti ručnu korekciju. Automatizirani score nije konačna poslovna odluka.

## 11. Privatnost, sigurnost i audit

- Prikuplja se samo potreban minimum osobnih podataka.
- Tajne i tokeni nikada se ne spremaju u tablice sadržaja, promptove ili audit poruke.
- Svaka promjena statusa mora ostaviti audit trag.
- Brisanje ili anonimizacija osobnih podataka mora biti moguća bez brisanja agregiranih rezultata kampanje.
- Pristup podacima i odobrenjima ograničava se po ulozi.
- Incidenti objave, neovlaštene promjene i pogrešni podaci moraju se evidentirati i ručno obraditi.

## 12. Minimalni kriterij spremnosti objave

Objava je spremna za planiranje samo ako:

- povezana strategija ima status `approved`;
- finalna verzija teksta postoji;
- finalni vizual ili potvrđen vizualni paket postoji;
- sve obavezne tvrdnje imaju status `verified` ili opravdani `not_applicable`;
- CTA i ciljna publika su definirani;
- nema aktivnog zahtjeva za izmjenom;
- konkretna verzija ima važeće ručno odobrenje;
- planirano vrijeme i kanal su valjani.

