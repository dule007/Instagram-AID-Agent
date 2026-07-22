# AID n8n workflow registry

Ovaj direktorij čuva implementacijske specifikacije workflowa. Datoteke nisu n8n import JSON i ne predstavljaju aktivnu automatizaciju. Svaki workflow mora prvo biti implementiran, konfiguriran u n8n-u, testiran i odobren.

## Statusi

- `specified` — dokumentiran, ali nije implementiran;
- `planned-later` — izvan MVP-a i ovisi o vanjskoj integraciji;
- `blocked-integration` — ne aktivirati bez službenih API vjerodajnica i testnog okruženja.

## Pregled sustava

```mermaid
flowchart LR
    A[Poslovni kontekst i metrike] --> B[WF-01 Strategija]
    B --> C{WF-02 Ljudsko odobrenje}
    C -->|odobreno| D[WF-03 Plan objava]
    C -->|izmjene| B
    D --> E[WF-04 Generiranje objave]
    E --> F[WF-05 Ekstrakcija tvrdnji]
    F --> G{WF-06 Ljudska verifikacija}
    G -->|provjereno| H[WF-07 Canva paket]
    G -->|izmjene| E
    H --> I{WF-08 Finalno odobrenje}
    I -->|odobreno| J[WF-09 Paket za ručnu objavu]
    I -->|izmjene| E
    J --> K[WF-10 Evidencija objave]
    K --> L[WF-11 Unos metrika]
    L --> M[WF-12 Prijedlog uvida]
    M --> N{WF-13 Odobrenje uvida}
    N -->|odobreno| A
    O[WF-14 Monitoring] -. nadzire .-> B
    O -. nadzire .-> E
    O -. nadzire .-> J
    O -. nadzire .-> L
```

## Kasnije integracije

```mermaid
flowchart LR
    A[Odobren sadržaj] --> B[WF-15 Meta objava]
    B --> C[Instagram]
    C --> D[WF-16 Meta metrike]
    C --> E[WF-17 ManyChat ulaz]
    E --> F[WF-18 Kvalifikacija leada]
    G[Canva] --> H[WF-19 Sinkronizacija asseta]
    H --> A
```

## Struktura

- `specs/` — jedna specifikacija i Mermaid vizual za svaki glavni i zajednički workflow;
- glavni workflowi: `WF-01` do `WF-19`;
- zajednički podworkflowi: `SUB-01` do `SUB-09`.

Službena sadržajna pravila nalaze se u `docs/business_rules.md`, model podataka u `docs/database_schema.md`, a širi opis workflowa u `docs/n8n_workflows.md`.

