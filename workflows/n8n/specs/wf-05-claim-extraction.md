# WF-05 — claim extraction

- Faza: `MVP`
- Status: `specified`
- Okidač: New content version
- Ulazi: Caption or script and linked sources
- Obavezna kontrola: Content version is current
- Izlaz: Deduplicated claims in pending state
- Sigurno ponašanje: No claim may be silently marked verified

## Vizual

```mermaid
flowchart LR
    N1[Content]
    N2[Extract claims]
    N3[Deduplicate]
    N4[Link sources]
    N5[Human queue]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

