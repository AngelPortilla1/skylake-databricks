# Evidencia: SKY-001 y SKY-005 (Repositorio, convenciones y estructura base)

- **Fecha:** 2026-11-05
- **Repositorio público:** https://github.com/AngelPortilla1/skylake-databricks
- **Tickets cubiertos:**
  - `SKY-001`: Repositorio público con licencia MIT, `README.md`, `.gitignore`, etiquetas (`etapa-0` a `etapa-8`) y los 28 issues creados (`#1` a `#28`).
  - `SKY-005`: Estructura completa de directorios, `CONTRIBUTING.md`, plantilla de PR (`.github/pull_request_template.md`), plantilla de hallazgos (`docs/free-edition-findings.md`) y decisión inicial `ADR-001` (`docs/decisions/ADR-001-ingesta-externa.md`).

## Verificación de estructura creada

```text
skylake-databricks/
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── databricks.yml
├── requirements-ingest.txt
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
├── data/
│   └── sample/
├── docs/
│   ├── decisions/
│   │   └── ADR-001-ingesta-externa.md
│   ├── evidence/
│   │   └── SKY-001-SKY-005-setup.md
│   └── free-edition-findings.md
├── resources/
├── scripts/
├── src/
│   ├── ingestion/
│   ├── pipelines/
│   └── utils/
└── tests/
    └── sql/
```

## Issues generados en GitHub

- `#1` a `#7`: Etapa 0 (`etapa-0`) — `SKY-001` a `SKY-007`
- `#8` a `#13`: Etapa 1 (`etapa-1`) — `SKY-010` a `SKY-015`
- `#14` a `#19`: Etapa 2 (`etapa-2`) — `SKY-020` a `SKY-025`
- `#20` a `#24`: Etapa 3 (`etapa-3`) — `SKY-030` a `SKY-034`
- `#25` a `#28`: Etapa 4 (`etapa-4`) — `SKY-040` a `SKY-043`
