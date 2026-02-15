# COPILOT_CONTEXT.md — Tennis Pre-Match Betting System (Data Availability Audit First)

## 0) Objetivo (no confundir con “predicción académica”)
Queremos construir un sistema de apuestas **pre-match** de tenis rentable.
El enfoque rentable NO es “tener el modelo más preciso”, sino **encontrar apuestas mal preciadas** (mispriced) y optimizar *price improvement* (mejor precio de entrada). En grandes volúmenes, el price improvement puede dominar la rentabilidad. (Referencia interna)  [oai_citation:0‡text.txt](sediment://file_00000000b80471fca26bfd7e78d08068)

El sistema será operado por **una sola persona** y debe ser **ejecutable dentro de GCP Free Tier**, entrenando modelos pesados localmente (Mac M1 Pro / M3) y usando GCP solo para ingestión, storage, scoring batch y alertas.

## 1) Restricciones de diseño (hard constraints)
### 1.1 Pre-match solamente
Nada de live/in-play en el MVP. Pre-match tolera latencias de 10–120s y se lleva bien con polling + batch scoring.  [oai_citation:1‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)  
In-play serio en free tier es mala idea por streams persistentes/costos.  [oai_citation:2‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)

### 1.2 Free tier GCP (arquitectura sugerida)
- BigQuery (warehouse): particionar/clusterizar para no “quemar” el free tier.  [oai_citation:3‡text.txt](sediment://file_00000000b80471fca26bfd7e78d08068)
- Cloud Run / Cloud Run Jobs: ingestión/processing efímero, escala a cero.  [oai_citation:4‡text.txt](sediment://file_00000000b80471fca26bfd7e78d08068)
- Cloud Scheduler: triggers limitados → agrupar lógica.  [oai_citation:5‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)
- e2-micro: orquestador/centinela (si hace falta).  [oai_citation:6‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)

## 2) Lo primero es la “Auditoría de Datos” (Data Availability Audit)
Antes de modelar, debemos responder con evidencia:
1) ¿Podemos conseguir **odds pre-match históricos** (con timestamps “as-of”) para el universo objetivo?
2) ¿Qué cobertura real hay de resultados, calendario, superficie/sede y stats por nivel?
3) ¿Qué fuentes tienen licencia comercial/permiten uso para fines económicos?
4) ¿Cuál es el costo operativo (rate limits, latencia, reliability)?
5) ¿Qué tanto missingness hay por temporada / torneo / nivel?
6) ¿Qué tanto “data leakage” evitamos con timestamps?

### 2.1 Universo inicial recomendado
**Challengers** es un sweet spot porque suele tener mejor cobertura de stats desde ~2008.  [oai_citation:7‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)  
En **Futures/ITF** los MatchStats suelen estar vacíos o incompletos → depender de marcadores y features derivados.  [oai_citation:8‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)

### 2.2 Aviso legal/licencias (crítico)
Muchos datasets “gratis” de tenis están bajo CC BY-NC-SA (No Comercial), lo cual es riesgoso si el modelo se usa para generar beneficios económicos directos.  [oai_citation:9‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)  
=> El audit debe incluir “licencia/ToS” como campo obligatorio.

## 3) Fuentes candidatas (para auditar, no para asumir)
### 3.1 Resultados + stats históricas
- Datasets tipo “atp_matches_challengers_YYYY.csv / atp_matches_futures_YYYY.csv”:
  - Challenger: robusto desde ~2008 con stats.  [oai_citation:10‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)
  - ITF: stats vacías/incompletas.  [oai_citation:11‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)
  - Licencia frecuente en repos académicos: CC BY-NC-SA (riesgo comercial).  [oai_citation:12‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)

### 3.2 Odds históricas (bookmakers)
- tennis-data.co.uk (ATP/WTA): útil para entrenar “model vs mercado” y CLV/overround, pero hay que revisar licencia y consistencia.  [oai_citation:13‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)

### 3.3 Odds en tiempo real (agregadores, free tier)
- odds-api.io free tier (100 req/h): útil para MVP pre-match/monitoreo, cobertura variable.  [oai_citation:14‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)
- The Odds API (otro proveedor): en el plan gratuito no cubre sistemáticamente Challenger/ITF (inviable como fuente primaria para ese nicho).  [oai_citation:15‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)

### 3.4 “Mercado gris” (scraping)
Si no hay APIs oficiales asequibles para ITF, el scraping suele ser lo predominante; agregadores como Sofascore/Flashscore son relevantes como fuente de livescores/feeds.  [oai_citation:16‡Data availability ITF and Challengers.txt](sediment://file_00000000e38871fca4a1cb1a29ba702a)  
(Nota: scraping implica riesgos ToS; registrar en el audit.)

## 4) Definición del “Mínimo Dataset Viable” (MDV) para apostar pre-match
Para cada match, necesitamos como mínimo:
- match_id estable
- player_a_id, player_b_id (y nombres normalizados)
- torneo_id, nivel (ATP/Challenger/ITF), fecha y hora local (si existe)
- superficie, indoor/outdoor, ciudad/país (si existe)
- resultado (ganador)
- **odds pre-match** con timestamp “as-of” (ideal: múltiples snapshots, mínimo 1)
- fuente + licencia/ToS + timestamp de captura

Sin odds “as-of”, NO hay forma honesta de evaluar un sistema rentable “vs mercado”.

## 5) Entregables del Audit (lo que Copilot debe implementar)
### 5.1 Repo layout (crear esto)
.
├── COPILOT_CONTEXT.md
├── pyproject.toml  (o requirements.txt)
├── scripts/
│   └── audit/
│       ├── run_audit.py
│       ├── sources/
│       │   ├── tennis_data_uk.py
│       │   ├── odds_api_io.py
│       │   ├── local_csv_repo.py
│       │   └── manual_sources.yaml
│       ├── metrics.py
│       ├── report.py
│       └── schemas.py
├── data/
│   ├── raw/              (NO commitear si es grande; usar .gitignore)
│   ├── samples/          (pequeñas muestras para tests)
│   └── audit_outputs/
│       ├── audit_summary.json
│       ├── audit_summary.csv
│       └── audit_report.md
└── README.md

### 5.2 `scripts/audit/run_audit.py` debe:
1) Cargar configuración (`config.yaml` o env vars) con:
   - fuentes habilitadas (on/off)
   - API keys (si aplica)
   - rango de fechas (ej. últimos 6–24 meses o 2008–hoy para challenger)
   - universo: niveles (ATP/Challenger/ITF), tours (ATP/WTA), regiones

2) Ejecutar “conectores” por fuente (cada fuente devuelve un DataFrame/tabla estandarizada):
   - `matches` (resultados/calendario)
   - `match_stats` (si hay)
   - `odds_snapshots` (timestamp, book, mercado, cuota)
   - `players` (metadatos)
   - `venues` (sede/altitud si hay)

3) Calcular métricas de disponibilidad y calidad:
   - cobertura: % matches con odds, % con stats, % con superficie/sede
   - missingness por campo y por nivel/año/torneo
   - duplicados/colisiones de IDs
   - “timeliness”: distribución de timestamps de odds (¿hay as-of real?)
   - drift: cambios en formato/columns por año
   - rate limit / errores / retries (contadores)

4) Generar outputs:
   - `data/audit_outputs/audit_summary.json` (machine-readable)
   - `data/audit_outputs/audit_summary.csv` (tabla resumen)
   - `data/audit_outputs/audit_report.md` (human-readable con hallazgos y recomendaciones)

### 5.3 Especificación del output `audit_summary.json`
Debe incluir:
- fuentes auditadas (nombre, endpoint/url, licencia status: {ok, unknown, noncommercial, forbidden})
- cobertura por dataset:
  - by_level: ATP / Challenger / ITF
  - by_year
  - by_tournament (top N por volumen)
- odds availability:
  - #matches con >=1 snapshot
  - #matches con >=k snapshots (k=2/3/4)
  - histograma de “time_to_match_start”
- calidad:
  - % filas con nombres no parseables / IDs faltantes
  - % de odds con books desconocidos
  - flags de riesgo (scraping, ToS unclear, no timestamps)

## 6) Configuración y ejecución local (para empezar hoy)
### 6.1 Python
Recomendado: Python 3.11+

`requirements.txt` mínimo:
- pandas
- numpy
- requests
- pydantic
- python-dateutil
- rich (opcional)
- tenacity (retries)

### 6.2 Variables de entorno (ejemplo)
- ODDS_API_IO_KEY=...
- DATA_DIR=./data
- AUDIT_START_DATE=2008-01-01
- AUDIT_END_DATE=2026-12-31
- LEVELS=challenger,itf,atp

### 6.3 Ejecutar
python -m scripts.audit.run_audit

## 7) Criterios de decisión (cuando el audit termina)
### 7.1 “Go” para Challenger pre-match
- >=70% de matches target con odds pre-match (>=1 snapshot) en la fuente elegida
- timestamps razonables (ej. snapshots a horas/minutos antes del partido)
- licencia comercial OK o ToS permite uso

### 7.2 “Pivot”
Si no hay odds confiables para Challenger/ITF:
- Opción A: cambiar universo a ATP/WTA (más datos, pero mercado más eficiente)
- Opción B: empezar “captura propia” de odds desde hoy (build historial)
- Opción C: pagar proveedor (si lo permites) o reducir universo a pocos torneos

## 8) Nota estratégica (para Copilot: NO implementar aún)
Modelado vendrá después del audit y será “residual vs mercado” cuando haya odds. tennis-data.co.uk es particularmente bueno para ese enfoque (ATP/WTA) pero hay que validar licencia y consistencia.  [oai_citation:17‡Estado del arte de apuestas deportivas en tenis y diseño de un sistema “one‑person” en GCP Free Tier.pdf](sediment://file_00000000a81871fc896d92a04a509564)

## 9) Principio anti-leakage (obligatorio)
Toda feature debe tener un `available_at` timestamp.
Nunca usar información posterior al “bet decision time”.
Para odds, el snapshot debe ser “as-of” del instante en que apostarías.