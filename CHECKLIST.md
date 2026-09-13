# Checklist budowy: Analiza przyczyn zwrotów per SKU

Odhaczaj kolejno, od góry. Każdy krok ma jasny efekt końcowy, więc łatwo sprawdzić, czy się udał, zanim przejdziesz dalej.

## Wymagania wstępne

- [ ] Docker Desktop zainstalowany i uruchomiony na Macu (do sprawdzenia ręcznie, `docker --version` w zwykłym terminalu Maca, nie w tej sesji)
- [ ] Klucz API Anthropic (Claude Haiku) do węzła klasyfikatora w n8n, zapisany w `.env`, nigdy w repo
- [ ] `uv` do zarządzania środowiskiem Pythona 3.12 dla `report-service` (masz już zainstalowane, `uv venv --python 3.12`)
- [ ] VS Code otwarty na folderze `01-analiza-zwrotow-per-sku`, z zaakceptowanymi rozszerzeniami z `.vscode/extensions.json`
- [ ] Konto GitHub gotowe pod nowe repo, kiedy projekt osiągnie stan do publikacji

## Krok 1: Fundament danych

- [x] `db/init.sql`: tabele `sku_catalog_cache`, `returns`, `classification_runs` z DESIGN.md
- [x] `docker-compose.yml`: tylko usługa `postgres` na start, reszta dochodzi w kolejnych krokach
- [x] `docker compose up postgres`, ręczna weryfikacja przez `psql`, że tabele istnieją i mają poprawne ograniczenia (`UNIQUE` na `external_return_id`)

Weryfikacja Kroku 1: `docker compose config --quiet` zakończone poprawnie; `docker compose up -d postgres` uruchomiło Postgresa 16; `psql` zwrócił trzy tabele oraz ograniczenie `returns_external_return_id_key` typu `UNIQUE` na `returns.external_return_id`.

## Krok 2: Dane demonstracyjne

- [x] `data/mock/catalog_sample.json`: 15 do 20 przykładowych SKU (nazwa, kategoria, cena, dostawca)
- [x] `data/mock/returns_sample.json`: 30 do 50 zwrotów, teksty po polsku, w tym celowo kilka niejednoznacznych (klient pisze jedno, magazyn notuje co innego)

Weryfikacja Kroku 2: `jq` potwierdził poprawny JSON, 18 SKU, 36 zwrotów, unikalne SKU i `external_return_id`, kompletność referencji SKU oraz 9 przykładów z sygnałami niejednoznaczności.

## Krok 3: Prompt klasyfikatora i eval, zanim cokolwiek trafi do n8n

- [x] `n8n-workflows/classifier_prompt.md`: prompt klasyfikujący do 8 kategorii, ze ścisłym formatem wyjścia
- [x] `eval/dataset.jsonl`: 30 ręcznie oznaczonych przykładów (inne niż w danych demo, żeby eval był uczciwy)
- [x] `eval/run_eval.py`: przepuszcza dataset przez prompt (Anthropic API), liczy trafność i macierz pomyłek
- [x] Eval uruchomiony: **90% trafność (27/30)**, próg 85% **spełniony**
- [x] Wynik zapisany do `eval/results.md`: macierz pomyłek, szczegóły per przypadek

Stan: Eval passou, prompt gotowy do n8n. Błędy w trudnych granicach (Niedopasowanie vs Zmiana decyzji).

## Krok 4: report-service

- [x] `report-service/app/models.py`: modele Pydantic (dane rankingu, dane raportu)
- [x] `report-service/app/chart.py`: generator wykresu słupkowego jako czyste SVG
- [x] `report-service/app/templates/returns_report.html` plus `style.css`: szablon dokumentu A4
- [x] `report-service/app/main.py`: endpoint `POST /render`, zwraca HTML
- [x] `report-service/tests/test_render.py`: poprawność sum, poprawność wykresu, walidacja modelu na niekompletnych danych
- [x] `report-service/Dockerfile`, z curl i bibliotkami systemowymi (Pango, Cairo)
- [x] `docker compose up`: oba serwisy startup poprawnie, healthchecki passing
- [x] Test `POST /render` z curl: HTML generuje się, SVG chart widoczny, tabela ranking i summary poprawne

## Krok 5: Workflow n8n

- [x] Dodanie usługi `n8n` do `docker-compose.yml`, startup i healthchecks OK
- [x] Workflow zbudowany i naprawiony przez `n8n-mcp` (17 węzłów, wszystkie połączenia zweryfikowane)
- [x] Konfiguracja credentials: Anthropic (httpHeaderAuth `x-api-key`), Postgres
- [x] **Zmiana architektoniczna**: `textClassifier` node zastąpiony bezpośrednim HTTP Request do Anthropic API z tym samym promptem co eval (90%) — textClassifier routinguje przez N osobnych wyjść bez pola confidence, niekompatybilne z mechanizmem `needs_review` z DESIGN.md
- [x] Schedule Trigger skonfigurowany (co tydzień, poniedziałek 6:00)
- [x] Test run przez `n8n_test_workflow`: wszystkie 17 węzłów **success**
- [x] Workflow zapisany w n8n pod ID `BkuEj75ftP0Kzywf`

## Krok 6: Testy end to end

- [ ] `bruno-collection`: testy API report-service (opcjonalne)
- [x] Pełne uruchomienie workflowu na danych mock (18 SKU + 36 zwrotów) — **sukces**
- [x] Dane w Postgres zweryfikowane: 36 returns, 18 sku_catalog_cache, reason_category znormalizowane do dokładnie 8 kategorii z DESIGN.md
- [x] Powtórne uruchomienie (execution #5 po TRUNCATE) — brak duplikatów dzięki `ON CONFLICT DO NOTHING` na `external_return_id`
- [x] Raport PDF (`report_body` → `report-service` → HTML) generuje się poprawnie w pipeline
- [ ] Send Email Report: tymczasowo wyłączony (`disableNode`) — brak klucza SendGrid, włączyć przed produkcją

Stan: **Workflow w pełni funkcjonalny end-to-end.** Dwa błędy napotkane i naprawione po drodze:
1. `DB_TYPE: postgres` → powinno być `postgresdb` (n8n fallbackował na SQLite)
2. `N8N_RESTRICT_FILE_ACCESS_TO` wymagane dla odczytu plików mock spoza `/home/node/.n8n`
3. Anthropic API 503 przy 36 równoległych requestach → naprawione przez batching (3 items/1000ms)
4. Model czasem zwracał pełny opis kategorii zamiast czystej nazwy → naprawione defensywną normalizacją w Code node

## Krok 7: Dokumentacja i zamknięcie

- [x] `README.md`: pełny opis, szybki start, architektura, eval results, troubleshooting
- [x] Sekcja "Jak wdrożyć" z instrukcją podłączenia BaseLinker
- [x] Struktura plików udokumentowana
- [ ] `git init`, first commit, push do repo (publiczny portfolio)
- [ ] Aktualizacja `../README.md` portfolio: projekt 01 status "Gotowy"
- [ ] Notion (Rozwiązania): status "Production Ready"

## Definicja gotowości (z DESIGN.md, dla przypomnienia)

Eval powyżej 85 procent trafności. Pełny przebieg na danych mock generuje poprawny PDF z rankingiem. Powtórne uruchomienie nie duplikuje wpisów. README pozwala komuś innemu uruchomić projekt jednym poleceniem.
