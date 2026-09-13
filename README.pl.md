*[Read in English](./README.md)*

# Analiza przyczyn zwrotów per SKU

**Status:** ✅ Gotowy (v1.0)  
**Eval:** 90% trafności (próg 85% spełniony)  
**API:** FastAPI + n8n + Postgres

Cotygodniowa automatyzacja łącząca dane zwrotów z trzech źródeł (opis klienta, stan magazynu, katalog) i klasyfikująca przyczyny zwrotów do 8 kategorii, aby pokazać które produkty generują najwięcej zwrotów i dlaczego. PDF report + email.

## 🚀 Szybki start (30 sekund)

```bash
cd 01-analiza-zwrotow-per-sku
export ANTHROPIC_API_KEY="sk-..."  # Twój klucz
docker compose up -d               # Startuj serwisy
sleep 10
open http://localhost:5678         # n8n UI
# Import workflow: File → Import from File → n8n-workflows/weekly-returns-analysis.json
# Kliknij "Execute Workflow"
```

## 📊 Eval: Klasyfikacja przyczyn

| Metryka | Wynik |
|---------|-------|
| Model | Claude Haiku 4.5 |
| Dataset | 30 przykładów |
| Trafność | **90% (27/30)** |
| Próg | >85% ✅ |
| Błędy | 3 (na granicach kategorii) |

Szczegóły: [`eval/results.md`](./eval/results.md)

## 🏗️ Architektura

```
Schedule Trigger (poniedziałek 6:00)
    ↓
Fetch Mock Data (albo BaseLinker)
    ↓
Upsert SKU Cache (Postgres)
    ↓
Claude Haiku textClassifier (8 kategorii)
    ↓
Check Confidence (>0.6)
    ├─→ Save to returns (needs_review=true jeśli <0.6)
    │
Aggregate SQL (ranking per SKU)
    ↓
POST /render (report-service)
    ↓
Send Email
    ↓
Log classification_run
```

## 📂 Struktura plików

```
├── DESIGN.md                      Pełna specyfikacja
├── README.md                      Ten plik
├── docker-compose.yml             3 serwisy (n8n, postgres, report-service)
├── .env.example                   Template zmiennych
├── db/
│   └── init.sql                   Schemat Postgres
├── data/mock/
│   ├── returns_sample.json        36 zwrotów do testowania
│   └── catalog_sample.json        18 SKU
├── n8n-workflows/
│   ├── weekly-returns-analysis.json  Workflow (do importu w n8n)
│   └── classifier_prompt.md        Prompt dla textClassifier
├── eval/
│   ├── dataset.jsonl              30 labeled examples
│   ├── run_eval.py                Skrypt eval
│   └── results.md                 Wyniki eval (90%)
├── report-service/                FastAPI + Jinja2 + SVG
│   ├── app/main.py                Endpoint POST /render
│   ├── app/models.py              Pydantic models
│   ├── app/chart.py               SVG chart generator
│   ├── app/templates/             HTML + CSS
│   ├── tests/                     Pytest (7 testów)
│   └── Dockerfile
└── bruno-collection/              HTTP testy (opcjonalne)
```

## 🔌 Serwisy (docker-compose)

| Serwis | Port | Rola |
|--------|------|------|
| **n8n** | 5678 | Orkiestracja + UI |
| **postgres** | 5432 | Baza danych |
| **report-service** | 8000 | API do generowania raportów |

## 📝 Konfiguracja

### .env (nie commituj!)

```bash
# Wymagane
N8N_ENCRYPTION_KEY=JbrVnwAOd8sWheXLedboh1WJtITeAF4dS3twv5Pphgg=
ANTHROPIC_API_KEY=sk-...

# Opcjonalne (domyślnie w docker-compose)
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
```

### Schemat Postgres

```sql
-- Zwroty z klasyfikacją
CREATE TABLE returns (
    id BIGSERIAL PRIMARY KEY,
    external_return_id TEXT UNIQUE NOT NULL,  -- Idempotencja
    sku TEXT NOT NULL REFERENCES sku_catalog_cache(sku),
    reason_category TEXT NOT NULL,             -- 8 kategorii
    confidence NUMERIC(4,3) NOT NULL,          -- 0.0-1.0
    needs_review BOOLEAN NOT NULL DEFAULT false,  -- <0.6
    reason_text TEXT NOT NULL,                 -- Od klienta
    condition_note TEXT,                       -- Od magazynu
    returned_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cachowane dane produktów
CREATE TABLE sku_catalog_cache (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    unit_price NUMERIC(10,2),
    supplier TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Log przebiegów
CREATE TABLE classification_runs (
    id BIGSERIAL PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    returns_processed INT NOT NULL,
    flagged_for_review INT NOT NULL
);
```

## 🧪 Testowanie

### Unit (report-service)

```bash
cd report-service
python -m pytest tests/ -v
```

7 testów:
- POST /render z 2 SKU
- SVG chart generation
- Pydantic model validation
- Error handling (brakujące SKU, negatywne liczby)

### Eval (klasyfikator)

```bash
export ANTHROPIC_API_KEY="sk-..."
python eval/run_eval.py
# Output: eval/results.md (macierz pomyłek + szczegóły)
```

30 przykładów, rezultat 90% trafności.

### End-to-end

1. Uruchom workflow w n8n UI (localhost:5678)
2. Sprawdź Postgres: `docker compose exec postgres psql -U postgres -d returns_analysis -c "SELECT * FROM returns;"`
3. Sprawdź że powtórne uruchomienie nie duplikuje wpisów (`UNIQUE` na `external_return_id`)

## 🔧 Troubleshooting

| Problem | Rozwiązanie |
|---------|-------------|
| ANTHROPIC_API_KEY missing | `export ANTHROPIC_API_KEY="sk-..."` |
| Postgres connection refused | `docker compose ps` (sprawdź healthy), `docker compose logs postgres` |
| report-service nie responds | `curl http://localhost:8000/health` |
| n8n workflow nie uruchamia się | Sprawdź credentials, test każdego węzła osobno |

## 📈 Jak wdrożyć

1. **Ustawy BaseLinker adapter** zamiast mock HTTP Request
2. **Testuj na 50 zwrotach** zanim puszczasz do produkcji
3. **Zaplanuj schedule trigger** na każdy poniedziałek 6:00 (UTC+2)
4. **Skonfiguruj email** (SendGrid lub inne)
5. **Monitoring**: logi z n8n, alerty jeśli `flagged_for_review` > 20%

## 📚 Dokumentacja

- [DESIGN.md](./DESIGN.md) — Full spec (architektura, decyzje, model danych)
- [n8n-workflows/classifier_prompt.md](./n8n-workflows/classifier_prompt.md) — Prompt do klasyfikatora
- [eval/results.md](./eval/results.md) — Wyniki eval (macierz pomyłek)
- [docker-compose.yml](./docker-compose.yml) — Konfiguracja serwisów

## 📄 Licencja

MIT License — autor: Hubert Grzybowski (grzybowski.it@gmail.com)
