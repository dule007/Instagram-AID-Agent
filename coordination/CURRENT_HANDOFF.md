# Aktualni handoff

## Stanje

- Datum zadnjeg ažuriranja: 2026-07-22
- Zadnji agent: Claude Code
- Aktivni zadatak: **prva stvarna objava je izvršena**; media hosting radi;
  ostatak rasporeda čeka odobrenje po stavci
- Git grana: `main`, praćena `origin/main`
- Repozitorij je objavljen na `dule007/Instagram-AID-Agent` (javan)

## Dovršeno u ovom ciklusu

- `instagram_agent/dashboard.py` pretvoren je iz read-only nadzora u operativnu
  kontrolu; dodan je `do_POST` s akcijama `host_media`, `approve`, `revoke`,
  `reschedule`, `publish`, `resolve_pending`, `autopilot`, `check_connection` i
  `media_host_status`;
- sučelje ima gumbe po stavci, modal s punim paketom za pregled prije
  odobrenja, modal s potvrdom točnog ID-a prije stvarne objave i panel s logom
  zadnjih akcija;
- dodan je autopilot: pozadinski scheduler s ON/OFF prekidačem i intervalom,
  koji objavljuje isključivo stavke s važećim ručnim odobrenjem; svaka
  preskočena stavka bilježi razlog;
- autopilot se ne može uključiti bez valjanog Meta credentiala;
- dodan je `instagram_agent/media_host.py`: finalni JPEG objavljuje se u javni
  GitHub repozitorij `dule007/Instagram-AID-Agent`, naziv datoteke sadrži
  SHA-256 sažetak sadržaja, a URL se prije upisa provjerava da vraća `image/*`;
- dodan je `instagram_agent/test_dashboard.py` sa 17 offline testova;
- `agent.py` je dobio `save_manifest` i `update_item` s whitelistom polja
  (`scheduled_at`, `media_url`, `status`) i atomskim upisom;
- `credentials.py` je dobio `load_env_file`, pa svaki ulazni put dijeli isti
  Git-ignorirani `.env`; postojeće environment vrijednosti i dalje imaju
  prednost, a vrijednosti se nikada ne ispisuju;
- `.env.example` dokumentira `GITHUB_TOKEN`, `GITHUB_MEDIA_REPO`,
  `GITHUB_MEDIA_BRANCH` i `GITHUB_MEDIA_DIR`;
- `instagram_agent/README.md` opisuje operativne akcije, autopilot i media host;
- `media_url` za `AID-2608-F01` očišćen je jer je pokazivao na ugašeni
  Cloudflare tunel i lažno prikazivao stavku spremnom za objavu.

## Provjereno

- svi Python moduli prolaze `py_compile`;
- 39/39 offline testova prolazi: `test_agent.py` 8, `test_credentials.py` 6,
  `test_oauth.py` 8, `test_dashboard.py` 17;
- test na živom serveru na portu 7011 potvrđuje:
  - POST bez CSRF tokena i s krivim CSRF tokenom vraća HTTP 403;
  - `approve` s krivom potvrdom i bez imena odgovorne osobe je blokiran;
  - `approve` s točnom potvrdom zapisuje approval, `revoke` ga uklanja;
  - `publish` bez točne potvrde ID-a blokiran je prije mrežnog poziva;
  - autopilot interval izvan raspona 1–720 minuta je odbijen;
  - nepoznata akcija je odbijena;
- `reschedule` računa offset iz vremenske zone kampanje: isti sat daje `+02:00`
  u srpnju i `+01:00` u prosincu, bez hardkodiranog pomaka;
- `autopilot_cycle` pokrenut nad stvarnim manifestom nije objavio ništa i točno
  je prijavio razlog preskakanja `AID-2608-F01`: nema važeće ručno odobrenje;
- `check_connection` je izvršio read-only Meta provjeru: token u `.env` valjan
  je za `@autoinsightdata`, tip računa `BUSINESS`, izvor `environment`;
- `media_host.repo_status()` potvrđuje da je `dule007/Instagram-AID-Agent`
  javan i dostupan tokenu;
- testni approval zapis stvoren tijekom provjere odmah je povučen, pa stanje
  approvala ostaje čisto; `PUBLISHED_RECORDS=0`.

## Ciklus 2026-07-22: objava repozitorija i prva Instagram objava

- repozitorij je inicijaliziran i pushan na `dule007/Instagram-AID-Agent`;
  `inputs_docuemtns/` je dodan u `.gitignore` jer sadrži interne poslovne
  dokumente, a repozitorij je javan;
- push je u prva tri pokušaja padao na `HTTP 408`; uzrok je uzlazna brzina veze
  od ~100 KiB/s uz pack od 49 MiB. Riješeno dvojako: 11 PNG-ova u
  `content/autodijelovi/` optimizirano je `pngquantom` (8,3 MB → 0,37 MB, bez
  promjene dimenzija), a početni commit je podijeljen na četiri koja se
  pushaju zasebno, svaki ispod 6,7 MiB. `http.postBuffer` od 500 MB je uklonjen
  jer je prisiljavao jedan veliki POST umjesto chunked prijenosa;
- `GITHUB_TOKEN` je zamijenjen fine-grained tokenom s ovlašću
  `Contents: Read and write` ograničenom na taj repozitorij; time je odblokiran
  media hosting;
- **`AID-2608-F01` je objavljen na `@autoinsightdata`.**
  - permalink: https://www.instagram.com/p/DbGDQWjiG6b/
  - Meta media ID: `17863172289647108`, container `17877749382618176`
  - objavljeno: 2026-07-22T12:06:27Z
  - odobrio: Kristijan Pavičić, fingerprint `04e1f43709a8`
  - `media_url`: `media/AID-2608-F01-dd3f25336489.jpg` na raw.githubusercontent
- objava je potvrđena izravnim read-only upitom Meti
  (`fields=id,permalink,media_type,timestamp,caption,username`), ne samo
  lokalnim zapisom.

## Zapažanje za sljedeći ciklus

- `action_publish` je vratio `ActionError: već postoji published zapis` iako je
  objava uspjela. Duplikat-guard je uhvatio ponovni prolaz **nakon** što je
  `publish_item` već dovršio i upisao `state/published/`. Poziv je istovremeno
  ostavio i `pending` zapis s `phase: published`, koji je ručno uklonjen.
  Vrijedi provjeriti zašto se `publish_item` izvršio dvaput unutar jednog
  poziva i zašto `pending` nije očišćen po uspjehu — u trenutnom obliku
  uspješna objava korisniku izgleda kao greška.
- `resolve_pending` s ishodom `published` namjerno **nije** korišten jer bi
  prepisao točan zapis i zamijenio `credential_source: environment` s
  `manual_reconciliation`, čime bi audit trag bio lošiji od stvarnog.

## Nije implementirano

- generiranje novog sadržaja iz sučelja i uvoz `schedule.csv` kroz dashboard;
- media hosting na vlastitoj AID domeni;
- carousel, Reels i privatni Insights;
- automatsko dodavanje native Story stickera;
- samostalno agentsko odobravanje sadržaja; korisnik je izričito odabrao da
  autopilot objavljuje isključivo prethodno odobrene stavke.

## Sljedeći korak

1. **Sigurnosno, prioritetno:** classic PAT `ghp_67uSXtf…` je bio izložen u
   plain textu u agentskoj sesiji i mora se obrisati na GitHubu. Još stoji u
   `.env` pod `GITHUB_PERSONAL_ACCESS_TOKEN`, gdje ga nijedan modul ne čita.
2. Preostale stavke rasporeda odobravati pojedinačno kroz dashboard; nijedna
   nema `media_url` dok se ne pokrene `Objavi asset na host`.
3. Autopilot uključiti tek kad postoji više odobrenih stavki; objavljuje
   isključivo prethodno odobrene.
4. Kompromitirani Instagram token iz `.env` zamijeniti službenim OAuth tokenom;
   `oauth.py` konektor i dalje čeka dovršen consent/callback.
5. `AID-2608-S01` ostaje ručan: native poll `Izvještaj / Odluka` mora se dodati
   u Instagram aplikaciji, a published status evidentira se tek nakon stvarne
   potvrde s Instagrama.
6. Fine-grained `GITHUB_TOKEN` istječe za 30 dana (21.08.2026.); media hosting
   staje na taj datum ako se token ne obnovi.

## Kanonske početne datoteke

- `content/campaigns/2026-08-relaunch/README.md`
- `content/campaigns/2026-08-relaunch/strategy.md`
- `content/campaigns/2026-08-relaunch/schedule.csv`
- `content/campaigns/2026-08-relaunch/publishing-manifest.json`
- `instagram_agent/README.md`
- `instagram_agent/dashboard.py`
- `instagram_agent/media_host.py`
- `instagram_agent/scout.py`
- `docs/content_research_gate.md`
- `docs/instagram_account_access.md`
