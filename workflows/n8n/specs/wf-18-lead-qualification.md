# WF-18 — lead qualification

- Faza: `Later`
- Status: `planned-later`
- Okidač: Eligible interaction
- Ulazi: Minimum contact and business relevance signals
- Obavezna kontrola: Consent and data minimization rules pass
- Izlaz: Reviewable lead score and handoff
- Sigurno ponašanje: Automated score is not a final business decision

## Vizual

```mermaid
flowchart LR
    N1[Interaction]
    N2[Validate consent]
    N3[Propose score]
    N4[Human review]
    N5[Sales handoff]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

