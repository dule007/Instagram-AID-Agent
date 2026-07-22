# Pristup Instagram računu, scouting i objavljivanje

Ovaj dokument razdvaja tri različite ovlasti. Prijava na račun sama po sebi ne
daje agentu pravo objave.

## 1. Javni benchmark bez prijave

Agent smije pregledati javno dostupne profesionalne profile, objave i službene
izvore radi uočavanja formata, hooka, vizualnih obrazaca i CTA-a. Login zid se
ne zaobilazi. Vidljivi lajkovi, komentari ili pregledi tretiraju se samo kao
javni signali, ne kao reach, saves, shares, retention ili leadovi.

## 2. Read-only scouting vlastitog računa

Za stvarne performanse AID računa koristi se službeni Instagram API i
interaktivna Meta autorizacija profesionalnog Business ili Creator računa.
Traže se samo ovlasti potrebne za čitanje profila, vlastitih medija i Insightsa.
Token se drži izvan repozitorija, a Instagram lozinka se nikada ne daje agentu.

Lokalni `instagram_agent/scout.py` pripremljen je za read-only dohvat vlastitog
profila i zadnjih medija nakon autorizacije. Ovaj način može služiti za:

- pregled izvedbe vlastitih feed objava, Reelsa i Storyja;
- usporedbu hooka, formata, CTA-a i kvalificiranih reakcija;
- izradu hipoteza za sljedeći sadržajni ciklus;
- provjeru jesu li relevantni signali porasli nakon promjene sadržaja.

Ne daje pristup privatnim Insightsima konkurentskih računa niti osobnim
consumer računima. Osnovni javni podaci o drugim profesionalnim računima mogu
biti dostupni samo u granicama službenog API-ja i dodijeljenih ovlasti.

## Službeni OAuth tok

Lokalni konektor `instagram_agent/oauth.py` implementira Instagram Login za
Business/Creator račun:

1. generira authorization URL s CSRF `state` vrijednošću;
2. korisnika šalje na službeni `instagram.com` consent ekran;
3. prima jednokratni code na loopback callbacku;
4. code serverski zamjenjuje short-lived tokenom;
5. zahtijeva uspješnu zamjenu za 60-dnevni long-lived token;
6. potvrđuje dodijeljene scopeove, ID, tip i točno korisničko ime
   `@autoinsightdata`;
7. sprema token u lokalnu Git-ignoriranu datoteku s dozvolom `0600`.

App Secret ostaje samo u lokalnom environmentu. OAuth token, code i App Secret
ne ispisuju se u dashboard, manifest, approval ili publish audit.
CLI `disconnect` uklanja lokalnu kopiju sesije; potpuno opozivanje pristupa radi
se dodatno u Meta/Instagram postavkama računa.

Za pokretanje su potrebni `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`,
`INSTAGRAM_REDIRECT_URI`, `META_GRAPH_VERSION` i
`EXPECTED_INSTAGRAM_USERNAME=autoinsightdata`. App ID i secret dobivaju se u
Meta App Dashboardu; ne mogu se izvesti iz Instagram usernamea i lozinke.

## 3. Objavljivanje nakon odobrenja

Prije svake objave redoslijed je obavezan:

1. aktualni benchmark i `research-gate` prolaze provjeru;
2. finalni tekst, vizual, termin i CTA prolaze provjeru tvrdnji;
3. `request-approval` prikazuje puni zaključani paket i zaustavlja agenta;
4. odgovorna osoba izričito odobrava točnu verziju;
5. tek tada `approve` zapisuje lokalni approval hash;
6. `publish` ponovno provjerava research gate, hash, termin i duplikat prije
   službenog Meta API poziva.

Ako se promijeni bilo koji zaključani element, staro odobrenje više ne vrijedi.
Ako benchmark istekne, objava je blokirana dok se istraživanje ne osvježi.

## Trenutno stanje

- lokalni OAuth konektor, research, read-only account scout, approval, raspored,
  dashboard i publish adapter postoje;
- App ID, App Secret i Graph API verzija još nisu konfigurirani; loopback
  redirect je lokalno pripremljen, ali ga još treba registrirati i potvrditi u
  Meta App Dashboardu, pa račun još nije povezan;
- dohvat privatnih Insightsa još nije implementiran;
- račun nije autoriziran i nijedna stvarna objava nije poslana;
- za povezivanje su potrebni Meta App, profesionalni Instagram račun i
  interaktivna autorizacija vlasnika računa;
- produkcijski tokeni i tajne ne ulaze u Git, dokumentaciju ili audit zapise.

Aktualne tehničke mogućnosti i ograničenja treba potvrditi u službenoj Meta
Instagram API dokumentaciji prije svake produkcijske uporabe.

## Ograničenje native Story stickera

Službeni API može napraviti Story container iz javno dostupnog JPEG-a, ali ne
može dodati funkcionalni poll, link ili location sticker. Zato se
`AID-2608-S01` s pollom `Izvještaj / Odluka` mora završiti ručno u Instagram
aplikaciji i nakon uspješnog OAuth povezivanja.
