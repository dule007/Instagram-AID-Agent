# Aktualni handoff

## Stanje

- Datum zadnjeg ažuriranja: 2026-07-22
- Zadnji agent: Claude Code
- Aktivni zadatak: operativni Instagram Control Agent je implementiran i
  testiran; čeka se ispravak GitHub token ovlasti da bi media hosting proradio
- Git grana: `main`
- Repozitorij još nema početni commit; projektne datoteke su untracked

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

## Blokirano

- **Upload na media host ne radi.** GitHub vraća
  `403 Resource not accessible by personal access token` na
  `PUT /repos/.../contents/...`. Token čita repozitorij, ali nema pravo pisanja.
  Vlasnik mora tom fine-grained tokenu dodijeliti ovlast
  `Contents: Read and write` za taj repozitorij, ili izdati novi token s tom
  ovlasti i zamijeniti `GITHUB_TOKEN` u `instagram_agent/.env`.
- Dok media hosting ne proradi, nijedna feed objava nema javni `media_url`, pa
  su `Objavi sad` i autopilot tehnički blokirani za feed sadržaj.

## Nije implementirano

- generiranje novog sadržaja iz sučelja i uvoz `schedule.csv` kroz dashboard;
- media hosting na vlastitoj AID domeni;
- carousel, Reels i privatni Insights;
- automatsko dodavanje native Story stickera;
- samostalno agentsko odobravanje sadržaja; korisnik je izričito odabrao da
  autopilot objavljuje isključivo prethodno odobrene stavke;
- ništa još nije objavljeno na stvarnom Instagram profilu.

## Sljedeći korak

1. Vlasnik dodaje `Contents: Read and write` GitHub tokenu i restarta dashboard.
2. Za `AID-2608-F01`: `Objavi asset na host`, zatim `Odobri` uz pregled punog
   paketa, pa `Objavi sad`.
3. Nakon prve uspješne objave uključiti autopilot za ostatak rasporeda, uz
   prethodno odobrene stavke.
4. Kompromitirani Instagram token iz `.env` zamijeniti službenim OAuth tokenom;
   `oauth.py` konektor i dalje čeka dovršen consent/callback.
5. `AID-2608-S01` ostaje ručan: native poll `Izvještaj / Odluka` mora se dodati
   u Instagram aplikaciji, a published status evidentira se tek nakon stvarne
   potvrde s Instagrama.

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
