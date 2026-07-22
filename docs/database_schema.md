# Prijedlog strukture PostgreSQL baze

## 1. Ciljevi modela

Baza mora čuvati operativno stanje, punu povijest verzija i audit trag. Generirani tekst ne prepisuje se u mjestu; nova generacija ili izmjena stvara novu verziju. Odobrenje se uvijek veže uz točnu verziju.

Preporuke:

- primarni ključevi tipa `uuid`;
- svi vremenski podaci kao `timestamptz` u UTC-u;
- strukturirani, često filtrirani podaci u kolonama;
- `jsonb` samo za promjenjive payloadove integracija i sirove odgovore;
- `created_at` i `updated_at` na operativnim tablicama;
- strani ključevi i ograničenja statusa u bazi, ne samo u n8n-u.

## 2. Predloženi enum tipovi

- `strategy_status`: `draft`, `review_required`, `approved`, `changes_requested`, `rejected`, `archived`
- `content_status`: `idea`, `draft`, `verification_required`, `verified`, `review_required`, `approved`, `scheduled`, `published`, `measured`, `changes_requested`, `rejected`, `failed`, `cancelled`, `archived`
- `claim_status`: `pending`, `verified`, `rejected`, `not_applicable`
- `approval_decision`: `approved`, `changes_requested`, `rejected`, `revoked`
- `publication_status`: `pending`, `scheduled`, `publishing`, `published`, `failed`, `cancelled`
- `workflow_status`: `running`, `succeeded`, `failed`, `blocked`, `cancelled`
- `lead_status`: `new`, `reviewing`, `qualified`, `unqualified`, `contacted`, `converted`, `closed`

## 3. Korisnici i poslovni kontekst

### `users`

- `id uuid primary key`
- `email citext unique not null`
- `display_name text not null`
- `role text not null`
- `is_active boolean not null default true`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `business_context_versions`

Odobrene informacije o AID-u koje modeli smiju koristiti.

- `id uuid primary key`
- `version integer unique not null`
- `title text not null`
- `content jsonb not null`
- `status text not null`
- `approved_by uuid references users(id)`
- `approved_at timestamptz`
- `valid_from timestamptz`
- `valid_until timestamptz`
- `created_at timestamptz not null`

## 4. Strategije i plan sadržaja

### `strategies`

- `id uuid primary key`
- `period_start date not null`
- `period_end date not null`
- `name text not null`
- `status strategy_status not null`
- `owner_id uuid references users(id)`
- `current_version_id uuid null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Ograničenje: `period_end >= period_start`.

### `strategy_versions`

- `id uuid primary key`
- `strategy_id uuid not null references strategies(id)`
- `version_no integer not null`
- `business_context_version_id uuid references business_context_versions(id)`
- `business_goal text not null`
- `primary_audience jsonb not null`
- `message text not null`
- `content_pillars jsonb not null`
- `hypotheses jsonb not null`
- `cta_approach text`
- `measurement_plan jsonb not null`
- `risks jsonb`
- `generation_run_id uuid null`
- `created_by uuid references users(id)`
- `created_at timestamptz not null`

Jedinstveno: `(strategy_id, version_no)`.

### `content_items`

Trajni identitet jedne planirane objave.

- `id uuid primary key`
- `strategy_id uuid not null references strategies(id)`
- `content_type text not null`
- `target_channel text not null default 'instagram'`
- `target_audience text not null`
- `business_goal text not null`
- `planned_publish_at timestamptz`
- `status content_status not null`
- `owner_id uuid references users(id)`
- `current_version_id uuid null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `content_versions`

- `id uuid primary key`
- `content_item_id uuid not null references content_items(id)`
- `version_no integer not null`
- `parent_version_id uuid references content_versions(id)`
- `hook text`
- `caption text`
- `script text`
- `cta text`
- `visual_brief jsonb not null`
- `hashtags text[]`
- `model_name text`
- `prompt_template text`
- `prompt_version text`
- `generation_run_id uuid null`
- `change_summary text`
- `created_by uuid references users(id)`
- `created_at timestamptz not null`

Jedinstveno: `(content_item_id, version_no)`.

### `media_assets`

- `id uuid primary key`
- `content_version_id uuid not null references content_versions(id)`
- `asset_type text not null`
- `provider text not null`
- `external_id text`
- `source_url text`
- `storage_path text`
- `checksum text`
- `is_final boolean not null default false`
- `metadata jsonb`
- `created_at timestamptz not null`

Za produkciju treba odlučiti čuvaju li se Canva i Meta URL-ovi kao kratkotrajne reference ili se finalni asset kopira u kontrolirani object storage.

## 5. Tvrdnje, izvori i provjera

### `sources`

- `id uuid primary key`
- `source_type text not null`
- `title text not null`
- `publisher text`
- `url text`
- `internal_reference text`
- `published_at timestamptz`
- `accessed_at timestamptz`
- `owner_id uuid references users(id)`
- `metadata jsonb`
- `created_at timestamptz not null`

### `claims`

- `id uuid primary key`
- `content_version_id uuid not null references content_versions(id)`
- `claim_text text not null`
- `claim_type text not null`
- `location_hint text`
- `status claim_status not null default 'pending'`
- `verification_note text`
- `verified_by uuid references users(id)`
- `verified_at timestamptz`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `claim_sources`

- `claim_id uuid references claims(id)`
- `source_id uuid references sources(id)`
- `support_note text`
- `primary key (claim_id, source_id)`

Prijelaz objave u `verified` mora biti transakcijski blokiran ako postoji obavezna tvrdnja bez prihvatljivog statusa.

## 6. Odobrenja

### `approvals`

- `id uuid primary key`
- `entity_type text not null`
- `entity_id uuid not null`
- `version_id uuid not null`
- `decision approval_decision not null`
- `decided_by uuid not null references users(id)`
- `comment text`
- `decided_at timestamptz not null`
- `revokes_approval_id uuid references approvals(id)`

`entity_type` u prvoj fazi podržava `strategy` i `content`. Servisni sloj mora provjeriti da `version_id` pripada odgovarajućem entitetu. Alternativno se mogu koristiti dvije strože tablice ako aplikacija ne može sigurno provoditi polimorfnu vezu.

Važeće odobrenje je posljednja relevantna odluka za konkretnu verziju i nije opozvano. Nova verzija nikad ne nasljeđuje odobrenje stare verzije.

## 7. Objave i metrike

### `publications`

- `id uuid primary key`
- `content_item_id uuid not null references content_items(id)`
- `content_version_id uuid not null references content_versions(id)`
- `channel text not null`
- `status publication_status not null`
- `scheduled_at timestamptz`
- `published_at timestamptz`
- `external_post_id text`
- `external_permalink text`
- `idempotency_key text unique not null`
- `attempt_count integer not null default 0`
- `last_error text`
- `published_by uuid references users(id)`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

Jedinstveni parcijalni indeks treba spriječiti više aktivnih ili uspješnih publikacija istog `content_item_id` bez eksplicitnog novog zapisa sadržaja.

### `metric_snapshots`

- `id uuid primary key`
- `publication_id uuid not null references publications(id)`
- `captured_at timestamptz not null`
- `window_hours integer`
- `impressions bigint`
- `reach bigint`
- `likes bigint`
- `comments bigint`
- `saves bigint`
- `shares bigint`
- `profile_visits bigint`
- `link_clicks bigint`
- `video_views bigint`
- `raw_payload jsonb`
- `created_at timestamptz not null`

Jedinstveno: `(publication_id, captured_at)`. Raspoloživost pojedinih polja mora se potvrditi prema aktualnim Meta API ovlastima prije implementacije.

### `content_insights`

- `id uuid primary key`
- `publication_id uuid references publications(id)`
- `strategy_id uuid references strategies(id)`
- `insight_type text not null`
- `summary text not null`
- `evidence jsonb not null`
- `confidence text not null`
- `proposed_action text`
- `status text not null`
- `reviewed_by uuid references users(id)`
- `reviewed_at timestamptz`
- `created_at timestamptz not null`

## 8. Leadovi i atribucija

Ove tablice mogu postojati u modelu od početka, ali njihovo automatsko punjenje dolazi tek s kasnijim ManyChat ili CRM modulom.

### `leads`

- `id uuid primary key`
- `external_contact_id text`
- `display_name text`
- `company_name text`
- `job_title text`
- `source_channel text not null`
- `status lead_status not null`
- `qualification_score numeric(5,2)`
- `qualification_reason text`
- `consent_metadata jsonb`
- `owner_id uuid references users(id)`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`

### `lead_interactions`

- `id uuid primary key`
- `lead_id uuid not null references leads(id)`
- `publication_id uuid references publications(id)`
- `interaction_type text not null`
- `occurred_at timestamptz not null`
- `summary text`
- `external_reference text`
- `metadata jsonb`
- `created_at timestamptz not null`

### `lead_attributions`

- `id uuid primary key`
- `lead_id uuid not null references leads(id)`
- `publication_id uuid references publications(id)`
- `strategy_id uuid references strategies(id)`
- `attribution_type text not null`
- `weight numeric(5,4)`
- `evidence text`
- `created_at timestamptz not null`

## 9. Workflow i audit evidencija

### `workflow_runs`

- `id uuid primary key`
- `workflow_name text not null`
- `workflow_version text`
- `n8n_execution_id text`
- `trigger_type text not null`
- `entity_type text`
- `entity_id uuid`
- `status workflow_status not null`
- `attempt_no integer not null default 1`
- `input_summary jsonb`
- `output_summary jsonb`
- `error_code text`
- `error_message text`
- `started_at timestamptz not null`
- `finished_at timestamptz`

### `audit_events`

- `id uuid primary key`
- `actor_type text not null`
- `actor_id text not null`
- `action text not null`
- `entity_type text not null`
- `entity_id uuid not null`
- `previous_state jsonb`
- `new_state jsonb`
- `workflow_run_id uuid references workflow_runs(id)`
- `occurred_at timestamptz not null`
- `correlation_id uuid`

Audit zapisi su append-only. Payload se prije upisa mora očistiti od tajni i nepotrebnih osobnih podataka.

## 10. Ključni indeksi

- `strategies(period_start, period_end, status)`
- `content_items(strategy_id, status, planned_publish_at)`
- `content_versions(content_item_id, version_no desc)`
- `claims(content_version_id, status)`
- `approvals(entity_type, entity_id, version_id, decided_at desc)`
- `publications(status, scheduled_at)`
- `publications(external_post_id)` gdje vrijednost nije `null`
- `metric_snapshots(publication_id, captured_at desc)`
- `workflow_runs(status, started_at desc)`
- `audit_events(entity_type, entity_id, occurred_at desc)`
- `lead_interactions(lead_id, occurred_at desc)`

## 11. Integritet koji mora biti proveden u aplikaciji ili bazi

- `current_version_id` mora pripadati odgovarajućem roditeljskom zapisu.
- Odobrena verzija mora imati sve tvrdnje riješene.
- Sadržaj se ne smije planirati bez važećeg odobrenja iste verzije.
- Publikacija se ne smije izvršiti ako je odobrenje opozvano ili je status sadržaja promijenjen.
- Objavljena verzija postaje nepromjenjiva; ispravak se modelira kao novi sadržaj ili nova publikacija prema poslovnom slučaju.
- Uvoz iste vanjske objave ili istog metričkog snapshot-a mora biti idempotentan.
- Brisanje korisnika ne smije uništiti audit; umjesto toga korisnik se deaktivira ili anonimizira prema pravilima privatnosti.

## 12. Redoslijed implementacije migracija

1. enum tipovi, `users` i poslovni kontekst;
2. strategije i njihove verzije;
3. sadržaj, verzije i asseti;
4. izvori, tvrdnje i provjera;
5. odobrenja i audit;
6. publikacije i metrike;
7. uvidi;
8. leadovi i atribucija kada se otvori ManyChat/CRM faza.

Ovaj dokument je logički prijedlog, ne gotova SQL migracija. Prije implementacije treba potvrditi način autentikacije korisnika, mjesto pohrane asseta, Meta metrike dostupne AID računu i pravila zadržavanja osobnih podataka.

