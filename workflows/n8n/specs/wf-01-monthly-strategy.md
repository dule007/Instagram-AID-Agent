# WF-01 — monthly strategy

- Faza: `MVP`
- Status: `specified`
- Okidač: Schedule or manual request
- Ulazi: Approved business context, target period, prior approved insights
- Obavezna kontrola: Required context exists and target period is valid
- Izlaz: Draft strategy version in review_required
- Sigurno ponašanje: Missing business goal blocks the run

## Vizual

```mermaid
flowchart LR
    N1[Context]
    N2[Validate]
    N3[OpenAI]
    N4[Save draft]
    N5[Human review]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

