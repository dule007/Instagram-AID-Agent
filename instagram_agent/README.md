# AID Instagram agent

Ovo je lokalni approval-gated publisher za pojedinačne Instagram slike i
Stories preko službenog Meta Graph API-ja. Ništa se ne objavljuje pri pokretanju
repozitorija i agent ne čita Instagram lozinku.

Sustav ima sedam komponenti:

- `oauth.py` — službeni Instagram Login OAuth preko lokalnog loopback callbacka;
- `agent.py` — approval-gated publisher i izvršavanje rasporeda;
- `run_agent.sh` — sigurno učitava Git-ignorirani `.env` prije CLI naredbe;
- `single_asset_server.py` — loopback allowlist server koji poslužuje samo
  jedan zaključani JPEG tijekom kontrolirane objave;
- `media_host.py` — objava finalnog JPEG-a na javni GitHub repozitorij i
  stabilan `raw.githubusercontent.com` URL koji Meta može povući;
- `dashboard.py` — operativni kontrolni centar: pregled, odobrenje, objava,
  raspored i autopilot;
- `scout.py` — read-only dohvat vlastitog profesionalnog profila i zadnjih
  objava preko službenog Meta API-ja, nakon autorizacije vlasnika računa.

## Control dashboard

Najjednostavnije pokretanje:

```bash
./instagram_agent/run_dashboard.sh
```

Ili izravno:

```bash
python3 instagram_agent/dashboard.py \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json
```

Zatim otvorite `http://127.0.0.1:7010`. Dashboard se osvježava svakih 30
sekundi, a JSON stanje dostupno je na `http://127.0.0.1:7010/api/status`.

Dashboard izvršava stvarne radnje i zato sluša isključivo na loopbacku. Svaki
POST zahtijeva CSRF token izdan pri učitavanju stranice, a zahtjev izvan
loopbacka odbija se prije bilo kakve promjene stanja.

### Operacije po stavci

| Gumb | Što radi |
|---|---|
| `Objavi asset na host` | šalje zaključani JPEG na javni GitHub repozitorij i upisuje `media_url` |
| `Odobri` | prikazuje puni paket za pregled i tek nakon upisanog imena i točnog ID-a zapisuje approval |
| `Povuci odobrenje` | briše approval; autopilot stavku više ne dira |
| `Termin` | mijenja `scheduled_at`; offset se računa iz vremenske zone kampanje |
| `Objavi sad` | stvarna Meta objava nakon potvrde točnog ID-a |
| `Razriješi pokušaj` | zatvara nerazriješen publish pokušaj tek nakon ljudske provjere stvarnog stanja |

Izmjena media URL-a ili termina mijenja fingerprint i time poništava postojeće
odobrenje. To je namjerno; nova verzija traži novo odobrenje.

### Autopilot

Prekidač u zaglavlju uključuje pozadinski scheduler koji svakih *N* minuta
pregleda raspored i objavljuje **isključivo stavke koje već imaju važeće ručno
odobrenje**. Bez approvala, bez javnog media URL-a ili uz nerazriješen prethodni
pokušaj stavka se preskače i razlog se zapisuje u log akcija.

Autopilot se ne može uključiti bez valjanog Meta credentiala. Za pokretanje bez
schedulera koristi se `--no-autopilot`.

## Javni media host

Meta publish container traži javni HTTPS URL; lokalna datoteka nije dovoljna.
`media_host.py` objavljuje **samo finalni publish asset** u zaseban javni
GitHub repozitorij. Naziv datoteke sadrži SHA-256 sažetak sadržaja, pa
izmijenjeni vizual uvijek dobiva novi URL i Meta nikada ne povuče
predmemoriranu staru verziju.

Konfiguracija je u istom `.env` fileu: `GITHUB_TOKEN`, `GITHUB_MEDIA_REPO`,
`GITHUB_MEDIA_BRANCH`, `GITHUB_MEDIA_DIR`. Token treba ovlast
`Contents: Read and write` na tom repozitoriju, a repozitorij mora biti Public
jer inače Meta ne može dohvatiti sliku. Prije upisa `media_url` agent provjerava
da URL stvarno vraća `image/*`.

U taj repozitorij ne ide izvorni kod ovog projekta, nego samo finalni vizuali.

## Povezivanje Instagram računa

Preduvjeti u Meta App Dashboardu:

1. Business Meta aplikacija s proizvodom `Instagram API with Instagram Login`;
2. AID Business/Professional Instagram račun dodan kao app user/tester dok je
   aplikacija u Development modu;
3. OAuth redirect URI točno `http://127.0.0.1:7012/callback`;
4. dostupni scopeovi `instagram_business_basic`,
   `instagram_business_content_publish` i
   `instagram_business_manage_insights`;
5. aktualna Graph API verzija potvrđena u Dashboardu.

Kopirati `instagram_agent/.env.example` u lokalni, Git-ignorirani
`instagram_agent/.env` i unijeti Instagram App ID, App Secret, redirect URI i
Graph verziju. `EXPECTED_INSTAGRAM_USERNAME=autoinsightdata` zaključava OAuth
na AID račun. Datoteka mora biti čitljiva samo vlasniku, a launcher je
automatski učitava:

```bash
chmod 600 instagram_agent/.env
./instagram_agent/run_oauth.sh
```

Otvara se `http://127.0.0.1:7012`, a prijava se nastavlja u službenom
Instagram prozoru. Agent ne prima lozinku. Authorization code se jednokratno
zamjenjuje tokenom. Konektor zahtijeva sve tražene ovlasti, potvrđuje da je
odabran upravo `@autoinsightdata` i zahtijeva 60-dnevni token. Lokalna sesija
sprema se u Git-ignorirani `instagram_agent/state/oauth/session.json` s
dozvolom `0600` i nikada se ne prikazuje u dashboardu ili auditu.

Za privremeni direktni credential iz `.env` podržan je par
`INSTAGRAM_IG_USER_ID` / `INSTAGRAM_ACCESS_TOKEN`. Ako su postavljeni i
kanonski aliasi s različitim vrijednostima, agent blokira rad bez ispisa tajni.

Provjera i osvježavanje:

```bash
python3 instagram_agent/oauth.py status
python3 instagram_agent/oauth.py refresh
```

Odspajanje zahtijeva eksplicitnu potvrdu:

```bash
python3 instagram_agent/oauth.py disconnect --confirm DISCONNECT
```

Ova naredba uklanja samo lokalnu sesiju. Za potpuno opozivanje dodijeljenih
ovlasti treba ukloniti aplikaciju i u Meta/Instagram postavkama računa.

## Read-only scouting vlastitog računa

Nakon službene autorizacije OAuth sesija automatski se koristi za dohvat profila
i zadnjih objava bez promjene računa:

```bash
python3 instagram_agent/scout.py --limit 25 \
  --output instagram_agent/state/scouting/latest.json
```

Snapshot ne sadrži token. Sadrži javne countove dostupne vlasniku računa i
jasno je označen kao podatak bez privatnih Insights metrika. Za reach, saves,
shares, Story retention, profilne radnje i leadove potreban je zaseban Insights
modul i odgovarajuće read-only ovlasti.

## Sigurnosni model

- svaki sadržaj mora imati `claims_status: verified`;
- svaki sadržaj mora imati aktualan benchmark i research score najmanje 80/100;
- `request-approval` ispisuje puni paket za pregled i zatim staje bez upisa ili
  mrežnog poziva;
- `approve` zaključava hash preview PNG-a i zasebnog API JPEG-a, cijelog
  briefa, research zapisa, captiona, native stickera, termina, kanala i javnog
  media URL-a;
- svaka naknadna izmjena automatski poništava approval;
- `publish` ponovno provjerava research gate i approval neposredno prije Meta poziva;
- published zapis blokira duplikat;
- pending zapis blokira automatski retry nakon nejasnog Meta ishoda;
- token se čita iz environmenta ili Git-ignorirane OAuth sesije i ne ulazi u
  dashboard, manifest ni audit zapis;
- token se prema Meti šalje samo u `Authorization: Bearer` headeru;
- agent čeka `FINISHED` status media containera prije `media_publish` poziva;
- neposredno prije Meta publish poziva ponovno se potvrđuju IG User ID,
  profesionalni tip i kanonski username `@autoinsightdata`;
- Story s native poll/question/link stickerom označen je za ručnu objavu jer
  statički PNG ne može sadržavati funkcionalan Instagram sticker.

## 1. Aktualni research gate

Prije nove objave ili materijalne izmjene provodi se Content Benchmark Super
Task iz `docs/content_research_gate.md`. Benchmark ne smije biti stariji od
sedam dana, a sadržaj mora ostvariti najmanje 80/100:

```bash
python3 instagram_agent/research_gate.py \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json
```

Ista se provjera ponavlja pri odobrenju i neposredno prije stvarne objave.
Istekli benchmark tehnički blokira agent.

## 2. Validacija kampanje

```bash
python3 instagram_agent/agent.py validate \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json
```

Prazan `media_url` daje upozorenje. Meta API ne može povući sliku s lokalnog
diska, pa prije odobrenja feed stavke treba upisati javni HTTPS URL točno tog
PNG-a. URL mora ostati nepromijenjen nakon odobrenja.

## 3. Paket koji agent šalje na odobrenje

```bash
python3 instagram_agent/agent.py request-approval \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json \
  --id AID-2608-F01
```

Naredba prikazuje finalni vizual, caption ili Story uputu, termin, research
score, odabrane obrasce, tvrdnje, upozorenja, media URL i zaključani hash.
Ništa ne odobrava i ništa ne objavljuje. Agent na toj točki mora stati i čekati
izričitu odluku odgovorne osobe.

## 4. Ručno evidentiranje odobrene zaključane verzije

Tek nakon stvarne ljudske potvrde pokreće se:

```bash
python3 instagram_agent/agent.py approve \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json \
  --id AID-2608-F01 \
  --approved-by "IME ODGOVORNE OSOBE" \
  --confirm AID-2608-F01
```

Approval se lokalno zapisuje u `instagram_agent/state/approvals/`. Taj direktorij
je runtime evidencija i nije mjesto za tokene.

## 5. Dry run

```bash
./instagram_agent/run_agent.sh publish \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json \
  --id AID-2608-F01 \
  --dry-run
```

## 6. Stvarna objava

Tek nakon službene, interaktivne autorizacije i provjere povezanog računa u
planiranom terminu pokrenuti:

```bash
./instagram_agent/run_agent.sh publish \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json \
  --id AID-2608-F01
```

`META_GRAPH_VERSION` namjerno nema hardkodiranu verziju: administrator je mora
potvrditi u trenutačnom Meta App Dashboardu. Meta za image publish zahtijeva
javni HTTPS URL. Repo sadrži izolirani one-file server, ali javni tunel nije
automatski dopušten: za svaki pokušaj traži se izričita potvrda izlaganja jedne
finalne slike trećoj strani, nakon čega URL ulazi u approval fingerprint.

Agent ne prihvaća Instagram lozinku. Autorizacija se provodi kroz službeni Meta
login za profesionalni račun i odvojena je od sadržajnog approvala. Čak i kada
je račun autoriziran, publish poziv ostaje blokiran bez točnog ručnog approval
hasha.

## 7. Pokretanje rasporeda

Ova naredba pregledava manifest i objavljuje samo dospjele feed stavke koje
imaju javni HTTPS URL i važeće ručno odobrenje:

```bash
python3 instagram_agent/agent.py run-due \
  --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json
```

Za periodičan rad administrator može tu naredbu dodati u vlastiti cron,
systemd timer ili n8n, ili jednostavno uključiti autopilot u dashboardu koji
izvršava istu logiku. Storyji s native stickerom ostaju označeni kao ručni.

## Nije implementirano

- media hosting na vlastitoj AID domeni; trenutačno se koristi javni GitHub
  repozitorij;
- read-only dohvat privatnih Instagram Insightsa; `scout.py` trenutačno dohvaća
  samo profil, vlastite medije i osnovne countove;
- carousel i Reel objava;
- automatsko dodavanje native Story stickera;
- autonomno odgovaranje na komentare ili DM-ove;
- generiranje novog sadržaja iz sučelja i uvoz rasporeda iz `schedule.csv`;
- samostalno agentsko odobravanje sadržaja; autopilot izvršava raspored, ali
  odobrenje verzije i dalje daje čovjek.

## Važno ograničenje Storyja

Meta API ne podržava objavu funkcionalnih `poll`, `link` ili `location`
stickera. API Story slika mora biti JPEG na javnom URL-u. Zato se odobreni
`AID-2608-S01` s pollom `Izvještaj / Odluka` i nakon OAuth povezivanja mora
objaviti ručno u Instagram aplikaciji; statički nacrtani poll nije interaktivan.
