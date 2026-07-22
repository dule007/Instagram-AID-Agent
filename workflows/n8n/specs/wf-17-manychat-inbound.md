# WF-17 — manychat inbound

- Faza: `Later`
- Status: `blocked-integration`
- Okidač: Verified comment or DM webhook
- Ulazi: Approved automation rule and inbound event
- Obavezna kontrola: Signature, consent rules and allowed intent pass
- Izlaz: Recorded interaction or human escalation
- Sigurno ponašanje: Unknown intent cannot receive unrestricted AI response

## Vizual

```mermaid
flowchart LR
    N1[Inbound event]
    N2[Verify]
    N3[Match rule]
    N4[Respond or escalate]
    N5[Audit]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

