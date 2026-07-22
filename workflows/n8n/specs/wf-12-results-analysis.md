# WF-12 — results analysis

- Faza: `MVP`
- Status: `specified`
- Okidač: Metric snapshot or month close
- Ulazi: Strategy, content hypothesis, metrics, qualitative signals
- Obavezna kontrola: Evidence set is linked and complete enough
- Izlaz: Draft content insights for human review
- Sigurno ponašanje: AI output cannot directly change strategy

## Vizual

```mermaid
flowchart LR
    N1[Evidence]
    N2[Calculate KPIs]
    N3[OpenAI analysis]
    N4[Save hypotheses]
    N5[Human review]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

