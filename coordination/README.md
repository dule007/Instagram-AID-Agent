# Codex ↔ Claude Code koordinacija

Ovaj direktorij je zajednički komunikacijski sloj za agente koji rade nad istim Git repozitorijem.

## Datoteke

- `CURRENT_HANDOFF.md` — aktualno projektno stanje i sljedeći siguran korak;
- `OWNERSHIP.md` — privremeno vlasništvo nad datotekama tijekom aktivnog rada;
- `DECISIONS.md` — trajne odluke i otvorene kontradikcije;
- `HANDOFF_TEMPLATE.md` — format predaje rada drugom agentu.

## Pravilo

Git je izvor istine za kod i dokumentaciju. `coordination/` je izvor istine za to tko trenutačno što radi i zašto.

Ownership nije trajno vlasništvo datoteke. Red se dodaje prije rada i uklanja ili označava `released` nakon predaje.

