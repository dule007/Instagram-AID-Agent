# WF-04 — single post generation

- Faza: `MVP`
- Status: `specified`
- Okidač: Manual selection of content idea
- Ulazi: Content item, approved strategy, prompt version, approved sources
- Obavezna kontrola: Strategy is approved and content item is editable
- Izlaz: New content version in verification_required
- Sigurno ponašanje: Invalid structure or missing context fails safely

## Vizual

```mermaid
flowchart LR
    N1[Idea]
    N2[Validate]
    N3[OpenAI]
    N4[Save version]
    N5[Claim review]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

