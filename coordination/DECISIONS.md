# Odluke i otvorena pitanja

Ova je datoteka append-only za važne projektne odluke. Postojeći zapis ne prepisuj; novu odluku dodaj na vrh odjeljka ili kronološki na kraj.

## 2026-07-15 — Kanonska poruka brenda

- Odluka: primarno pozicioniranje glasi „Tržišna analitika za operativne odluke u automotiveu.”
- Razlog: ulazni strateški dokumenti izričito traže odmak od generičke „digitalizacije procesa”.
- Posljedica: digitalizacija ostaje način isporuke, ne glavni opis proizvoda.

## 2026-07-15 — Ručno odobrenje

- Odluka: svaki sadržaj zahtijeva ljudsko odobrenje točne verzije teksta i vizuala.
- Posljedica: izmjena nakon odobrenja poništava approval; nijedan agent ne objavljuje autonomno.

## 2026-07-15 — Suradnja agenata

- Odluka: Codex i Claude Code koordiniraju se kroz `AGENTS.md` i `coordination/` datoteke.
- Razlog: agenti nemaju pouzdan izravni međusobni chat između zasebnih sesija.
- Posljedica: jedan aktivni urednik po datoteci, obavezni ownership i handoff.

## 2026-07-15 — Prvi vertikalni content pilot

- Odluka: autodijelovi su prvi zasebni vertikalni pilot.
- Izvor: `AID_Inteligentna_nabavka_autodijelova_BiH.pdf`.
- Posljedica: sadržaj koristi jezik nabave, category managementa, SKU-a, fitmenta, dead stocka, lost salesa, transfera i centralizacije.
- Sigurnosna odluka: ilustrativni podaci iz brošure ne predstavljaju se kao stvarni klijentski rezultat; tržišne brojke zahtijevaju zaseban fact-check.

## Otvoreno

- potvrditi službeni pravni naziv i javne kontaktne adrese;
- potvrditi službenu paletu i logo assete;
- potvrditi odredišnu stranicu za CTA `Dogovorite poslovni prikaz`;
- odlučiti kada napraviti početni Git commit.

## 2026-07-20 — Instagram relaunch i kontrolirani publisher

- Odluka: kanonski sljedeći ciklus je `content/campaigns/2026-08-relaunch/` s
  osam feed objava i dvanaest Storyja u četverotjednom rasporedu.
- Vizualni smjer: navy, amber i plavi signal preuzeti su iz aktualnog javnog
  web sučelja; postojeće autodijelovi fotografije ostaju dopušten vizualni
  izvor.
- Publika: primarni segment su distributeri autodijelova; sekundarni segmenti
  su leasing i flote.
- Objavljivanje: na izričit zahtjev korisnika uveden je lokalni
  `instagram_agent/` za pojedinačne slike, uz obavezni ručni approval točnog
  hasha i provjeru neposredno prije Meta API poziva.
- Granica: nisu implementirani Meta OAuth, javni media hosting, scheduler,
  carousel, Reel, analitika ni automatski native Story stickeri. Bez njih nema
  produkcijske automatske objave.

## 2026-07-20 — Read-only Instagram Control Agent

- Odluka: operativni pregled objava vodi se kroz lokalni read-only dashboard u
  `instagram_agent/dashboard.py`.
- Razlog: raspored, vizual, caption, approval, blokada i publish audit moraju
  biti vidljivi na jednom mjestu bez stvaranja drugog autonomnog publishera.
- Sigurnosna granica: dashboard ne odobrava i ne objavljuje sadržaj, ne prikazuje
  tokene i po zadanim postavkama sluša samo na `127.0.0.1`.

## 2026-07-20 — Vizualna diferencijacija relaunch kampanje

- Odluka: osam feed objava više ne koristi zajednički dominantni layout.
- Arhetipovi: tipografski manifest, procesni tok, fotografsko pitanje, akcijski
  stack, regionalni split, stock-aging sat, vrijednosni graf i pilot CTA poster.
- Storyji: uvedeni su različiti poll, procesni, lokacijski, vremenski,
  vrijednosni i KPI obrasci umjesto jednog ponovljenog predloška.
- Razlog: javni audit profila već je identificirao repetitivnost sadržaja i slab
  stručni razgovor; vizualna razlika mora služiti prepoznavanju buyer problema i
  voditi prema kvalificiranom interesu, ne biti samo dekoracija.

## 2026-07-20 — Obavezni Content Benchmark Super Task

- Odluka: prije svake nove ili materijalno izmijenjene feed, carousel, Reel ili
  Story objave obavezan je aktualni benchmark iste niše, buyera i formata.
- Rok: benchmark vrijedi najviše sedam dana i mora sadržavati najmanje tri
  provjerljiva izvora ili javna primjera.
- Quality gate: svaka varijanta mora ostvariti najmanje 80/100 prema rubrici u
  `docs/content_research_gate.md`; neprovjerena tvrdnja, kopirana izvedba ili
  nedostatak izvora blokiraju sadržaj bez obzira na zbroj.
- Tumačenje: javni engagement drugih profila samo je kreativni signal. Izraz
  „najbolja objava” ne koristi se bez usporedivih podataka; AID koristi
  „interno najbolje ocijenjena varijanta”.

## 2026-07-20 — Approval paket i Instagram account scouting

- Odluka: prije evidentiranja svakog approvala agent prikazuje finalni vizual,
  caption ili Story uputu, termin, research score, upozorenja i zaključani hash,
  zatim staje i čeka izričitu ljudsku potvrdu.
- Zaključavanje: fingerprint obuhvaća PNG, puni brief, research zapis, caption,
  native sticker, kanal, termin i media URL. Promjena bilo kojeg elementa
  poništava postojeće odobrenje.
- Scouting: `instagram_agent/scout.py` smije samo read-only dohvatiti vlastiti
  profesionalni profil i medije preko službenog Meta API-ja. Ne koristi
  Instagram lozinku, ne zaobilazi login zid i ne mijenja račun.
- Granica: OAuth ekran, privatni Insights i stvarno povezivanje računa nisu
  implementirani; nijedna prijava ni objava nije izvršena.

## 2026-07-20 — Službeni Instagram Login OAuth konektor

- Odluka: lokalni `instagram_agent/oauth.py` koristi isključivo službeni
  Instagram Login authorization-code tok; Instagram username/password se ne
  čita, sprema niti prenosi agentu.
- Ciljni račun: autorizacija i svaki budući publish fail-closed su zaključani
  na kanonski profesionalni račun `@autoinsightdata`, uz provjeru usernamea,
  IG User ID-a i tipa računa prije spremanja sesije ili objave.
- Ovlasti: povezivanje uspijeva samo ako Meta stvarno dodijeli sve tražene
  scopeove i short-lived token uspješno zamijeni long-lived tokenom.
- Tajne: App Secret ostaje u lokalnom Git-ignoriranom `.env`; token sesija ima
  dozvolu `0600`, OAuth callback query se ne zapisuje u log, a token nije dio
  dashboarda, approvala ili publish audita.
- Stanje: konektor je implementiran i offline provjeren, ali račun nije
  povezan dok administrator ne konfigurira Instagram App ID, App Secret,
  redirect URI i aktualnu Graph API verziju u Meta App Dashboardu.
- Ograničenje: Meta publishing API ne dodaje funkcionalni poll/link/location
  Story sticker. `AID-2608-S01` zato ostaje ručna objava i nakon OAutha.

## 2026-07-21 — Kompromitirani Instagram access token

- Odluka: token zalijepljen u chat smatra se kompromitiranim i ne smije se
  testirati, razmjenjivati, spremati u OAuth sesiju niti koristiti za API poziv.
- Obavezni korak: vlasnik računa mora ukloniti aktivnu aplikacijsku autorizaciju
  u Instagram postavkama prije izdavanja novog tokena.
- Lokalna zaštita: korisnička tekstualna datoteka s tajnama nije čitana; dobila
  je dozvolu `0600` i izričito je ignorirana u Gitu.
- Nastavak: novi token dobiva se isključivo kroz lokalni službeni OAuth tok,
  nakon što se App ID, App Secret i Graph API verzija unesu u ignorirani
  `instagram_agent/.env`.

## 2026-07-21 — Jednokratna read-only provjera kompromitiranog tokena

- Kontekst: nakon sigurnosnog upozorenja korisnik je ponovio izričitu naredbu
  da se token testira.
- Ograničena radnja: izvršen je samo službeni Meta `/me` poziv s tokenom u
  Authorization headeru; token nije ispisan, razmijenjen, spremljen u OAuth
  sesiju niti korišten za objavu, a App Secret nije korišten.
- Rezultat: Meta je potvrdila kanonski račun `@autoinsightdata` tipa
  `BUSINESS`; ovaj rezultat ne mijenja kompromitirani status tokena.
- Posljedica: token i dalje treba opozvati te za trajno povezivanje izdati novi
  long-lived token kroz lokalni OAuth tok.

## 2026-07-21 — Strogi Instagram Business Login authorize URL

- Odluka: authorization URL koristi službeni endpoint
  `https://www.instagram.com/oauth/authorize`, Instagram App ID, potpuno jednak
  redirect URI i boolean parametre `enable_fb_login=false` te
  `force_reauth=true`; zastarjeli `force_authentication` se ne koristi.
- Validacija: nenumerički Instagram App ID blokira lokalni `/start` prije
  vanjskog preusmjeravanja.
- Status: povratak na Instagram početni feed bez lokalnog `/callback` zahtjeva
  nije uspješno povezivanje i ne stvara OAuth sesiju.

## 2026-07-21 — Kontrolirani agent-izvršen feed publish

- Kontekst: korisnik je izričito zatražio da agent izvrši stvarnu objavu nakon
  ljudskog odobrenja, umjesto da korisnik ručno dovršava Instagram korake.
- Odluka: prvi API-publish kandidat je `AID-2608-F01`; native-poll Story
  `AID-2608-S01` ostaje ručan jer API ne može reproducirati odobrenu verziju.
- Sigurnost: preview PNG i API JPEG zaključavaju se odvojeno; token ide samo u
  Bearer headeru; Meta container mora biti `FINISHED`; nerazriješen pokušaj
  blokira automatski retry.
- Hosting: dopušten je samo izolirani one-file loopback server. Cloudflare Quick
  Tunnel nije pokrenut bez zasebne izričite potvrde vlasnika nakon upozorenja da
  treća strana privremeno prima finalni javni sadržaj.
- Approval: javni URL i današnji termin moraju biti dio finalnog fingerprinta;
  bez točnog sadržajnog approvala agent ne poziva Meta publish endpoint.

## 2026-07-22 — Odobren privremeni tunel za F01

- Korisnik je nakon upozorenja o trećoj strani točno potvrdio:
  `ODOBRAVAM PRIVREMENI CLOUDFLARE TUNEL ZA AID-2608-F01`.
- Tunel je pokrenut prema loopback portu 7013, ali one-file origin ostaje ugašen
  do zasebnog approvala točnog F01 vizuala, captiona, termina, URL-a i hasha.
- Nakon uspješne objave agent mora ugasiti origin i tunel; promjena URL-a ili
  asseta prije objave poništava sadržajni approval.

## 2026-07-22 — Operativni Instagram Control Agent

- Kontekst: korisnik je zatražio da dashboard prestane biti read-only nadzor i
  postane operativna kontrola: klik na objavu, zadavanje rasporeda i agent koji
  objavljuje bez ručne intervencije po svakoj stavci.
- Odluka o razini autonomije: autopilot objavljuje **isključivo stavke koje već
  imaju važeće ručno odobrenje**. Korisnik je odbio potpuno autonomno
  odobravanje. Pravilo iz `AGENTS.md` o obaveznom ljudskom odobrenju točne
  verzije ostaje nepromijenjeno; mijenja se samo mjesto odobravanja, s CLI-ja na
  sučelje, uz isti puni paket za pregled i isti zaključani fingerprint.
- Posljedica: `dashboard.py` dobiva `do_POST` s akcijama host_media, approve,
  revoke, reschedule, publish, resolve_pending, autopilot i check_connection.
  Sučelje sluša samo na loopbacku i svaki POST traži CSRF token izdan pri
  učitavanju stranice.
- Odluka o media hostingu: privremeni Cloudflare tunel zamijenjen je javnim
  GitHub repozitorijem `dule007/Instagram-AID-Agent`. Razlog: tunel daje
  nasumičan URL koji nestaje pri restartu, pa je neupotrebljiv za raspored koji
  se izvršava bez prisutnog čovjeka.
- Sigurnost hostinga: u javni repozitorij ide isključivo finalni publish asset,
  nikada izvorni kod, `.env` ni audit zapisi. Naziv datoteke sadrži SHA-256
  sažetak sadržaja, pa izmijenjeni vizual dobiva novi URL i Meta ne može povući
  predmemoriranu staru verziju. Prije upisa `media_url` provjerava se da URL
  stvarno vraća `image/*`.
- Odluka o ključevima: `instagram_agent/.env` ostaje jedini file s ključevima,
  sada i za `GITHUB_TOKEN`. Dashboard prikazuje status i izvor veze, ali nikada
  vrijednost tajne.
- Zatečeni `media_url` za `AID-2608-F01` pokazivao je na ugašeni Cloudflare
  tunel. Polje je očišćeno jer je mrtav URL lažno prikazivao stavku spremnom.
