# Privremeni ownership datoteka

Prije rada dodaj red. Nakon predaje postavi status na `released` ili ukloni zastarjeli red. Ne preuzimaj datoteku koju drugi agent aktivno uređuje.

| Agent | Datoteka ili područje | Svrha | Preuzeto UTC | Status |
|---|---|---|---|---|
| Codex | `AGENTS.md`, `CLAUDE.md`, `coordination/` | Uvođenje protokola suradnje | 2026-07-15 | released |
| Codex | `content/autodijelovi/`, `coordination/CURRENT_HANDOFF.md`, `coordination/DECISIONS.md` | Vertikalni pilot sadržaja za autodijelove | 2026-07-15 | released |
| Codex | `content/autodijelovi/`, `coordination/CURRENT_HANDOFF.md`, `coordination/DECISIONS.md` | Prerada autodijelovi vizuala s realnim niche imageryjem | 2026-07-15 | released |
| Codex | `content/README.md`, `content/nise/`, `docs/vertical_content_system.md` | Razdvajanje sadržaja po automotive i financijskim nišama | 2026-07-15 | released |
| Codex | `content/`, `instagram_agent/`, `docs/`, `coordination/` | Potpuni restart Instagram sadržaja, raspored i approval-gated Meta publisher | 2026-07-20 | released |
| Codex | `instagram_agent/`, `coordination/` | Read-only Instagram Control dashboard za praćenje rasporeda, approvala i objava | 2026-07-20 | released |
| Codex | `content/campaigns/2026-08-relaunch/`, `content/design_system.md`, `coordination/` | Vizualno diferenciranje kampanje i jači buyer-interest mehanizmi | 2026-07-20 | released |
| Codex | `AGENTS.md`, `docs/content_research_gate.md`, `content/`, `instagram_agent/`, `coordination/` | Obavezni aktualni benchmark i quality gate za svaki feed/Story sadržaj | 2026-07-20 | released |
| Codex | `content/campaigns/2026-08-relaunch/schedule.csv`, `content/campaigns/2026-08-relaunch/publishing-manifest.json`, `instagram_agent/build_manifest.py`, `instagram_agent/state/`, `coordination/` | Današnje korisničko odobrenje za AID-2608-S01 i priprema ručne Story objave | 2026-07-20T17:43:00Z | released |
| Codex | `instagram_agent/`, `docs/instagram_account_access.md`, `docs/architecture.md`, `coordination/` | Službeni Meta/Instagram OAuth konektor i sigurna lokalna credential sesija | 2026-07-20T17:55:00Z | released |
| Codex | `.gitignore`, `token i isntagram app secret.txt`, `coordination/` | Zaštita slučajno spremljenih Instagram tajni bez čitanja ili uporabe kompromitiranog tokena | 2026-07-21T14:10:31Z | released |
| Codex | `coordination/` | Evidencija jednokratne read-only Meta provjere kompromitiranog tokena nakon ponovljene izričite korisničke naredbe | 2026-07-21T14:20:16Z | released |
| Codex | `instagram_agent/credentials.py`, `instagram_agent/test_credentials.py`, `coordination/` | Ispravak izbora OAuth session credential izvora kada je Graph verzija postavljena u `.env` | 2026-07-21T14:24:18Z | released |
| Codex | `instagram_agent/oauth.py`, `instagram_agent/test_oauth.py`, `coordination/` | Usklađivanje Instagram Business Login URL-a sa službenim boolean parametrima i novi OAuth pokušaj | 2026-07-21T14:41:00Z | released |
| Codex | `instagram_agent/`, `content/campaigns/2026-08-relaunch/`, `docs/`, `coordination/` | Prvi potpuno agent-izvršen Instagram feed publish uz točan approval i privremeni izolirani HTTPS media URL | 2026-07-21T17:37:35Z | released |
| Claude Code | `instagram_agent/dashboard.py`, `instagram_agent/media_host.py`, `instagram_agent/agent.py`, `instagram_agent/credentials.py`, `instagram_agent/test_dashboard.py`, `coordination/` | Operativni Instagram Control Agent: publish i approve iz sučelja, autopilot za odobrene stavke, GitHub media hosting | 2026-07-22T08:20:00Z | released |

Status može biti `active`, `blocked` ili `released`.
