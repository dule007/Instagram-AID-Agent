# WF-14 — operations monitoring

- Faza: `MVP`
- Status: `specified`
- Okidač: Schedule or workflow failure event
- Ulazi: Workflow runs and entity states
- Obavezna kontrola: Alert rules and age thresholds are configured
- Izlaz: Actionable alert with run_id and owner
- Sigurno ponašanje: Monitoring never changes business approval state

## Vizual

```mermaid
flowchart LR
    N1[System state]
    N2[Detect anomaly]
    N3[Classify]
    N4[Notify owner]
    N5[Audit]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

