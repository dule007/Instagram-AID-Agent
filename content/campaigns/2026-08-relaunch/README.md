# Kolovoz 2026. — AID Instagram relaunch

Paket je spreman za sadržajni i vizualni pregled, ali nije odobren za objavu.

## Što paket sadrži

- 8 feed objava utorkom i petkom;
- 12 Storyja koji najavljuju, produbljuju ili distribuiraju feed objave;
- jednu dosljednu priču: `problem → signal → odluka → ograničeni pilot`;
- captions bez neprovjerenih tržišnih brojki i bez izmišljenih rezultata;
- aktualni benchmark, research gate i interni creative score za svih 20
  sadržaja;
- objavni manifest za `instagram_agent/agent.py`.

## Redoslijed pregleda

1. pročitaj `strategy.md`;
2. pregledaj PNG i pripadajući `.md` za svaki sadržaj;
3. provjeri `research-gate.json` i važeći benchmark u `../../research/`;
4. provjeri `claims-register.csv`;
5. potvrdi CTA odredište i termine u `schedule.csv`;
6. pokreni `python3 instagram_agent/agent.py validate --manifest content/campaigns/2026-08-relaunch/publishing-manifest.json`;
7. pokreni `request-approval` za odabrani content ID i pregledaj puni paket;
8. tek nakon izričite ljudske potvrde evidentiraj approval zaključane verzije.

Aktualni CTA vodi na `https://www.autoinsightdata.com/contact`. Ako se CTA ili
URL promijeni, postojeće odobrenje više ne vrijedi.
