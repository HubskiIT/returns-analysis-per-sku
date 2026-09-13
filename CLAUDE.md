# CLAUDE.md

## Projekt

Analiza przyczyn zwrotów per SKU. Cotygodniowy batch, łączy dane od klienta (wolny tekst), z magazynu (stan towaru) i z katalogu, klasyfikuje przyczynę zwrotu do 8 kategorii, agreguje w Postgres, wysyła PDF z rankingiem.

Pełny projekt: DESIGN.md, przeczytaj przed pisaniem kodu. Uwaga: DESIGN.md nadal opisuje `textClassifier`, ale patrz sekcja "Odstępstwo od DESIGN.md" niżej.

## Stack

n8n (HTTP Request bezpośrednio do Anthropic API, model Claude Haiku — patrz odstępstwo niżej), FastAPI plus Jinja2 plus SVG (report-service, reużywa wzorca z ../cwiczenie-docker-n8n-pdf), Postgres 16.

## Odstępstwo od DESIGN.md: klasyfikator

DESIGN.md zakłada węzeł `@n8n/n8n-nodes-langchain.textClassifier`. W praktyce ten node routinguje przez N osobnych wyjść (po jednym na kategorię + fallback), **bez pola `confidence` w JSON** — niekompatybilne z mechanizmem `needs_review` (próg confidence <0.6) opisanym w DESIGN.md.

Zamiast tego: węzeł HTTP Request bezpośrednio do `https://api.anthropic.com/v1/messages`, z tym samym promptem co `eval/run_eval.py` (90% trafności), zwracający `{category, confidence}` jako JSON. Parsowanie i defensywna normalizacja kategorii (model czasem zwraca pełny opis zamiast czystej nazwy) w Code node "Parse Classification". Zachowuje cały mechanizm `needs_review` bez zmian.

Credential: `httpHeaderAuth` (nagłówek `x-api-key`), nie `anthropicApi` (ten typ credential działa tylko z natywnymi LangChain node'ami).

## Status

**Workflow n8n zbudowany, naprawiony i przetestowany end-to-end (17 węzłów, wszystkie success).** Workflow ID w n8n: `BkuEj75ftP0Kzywf`. Zbudowany przez `n8n-mcp` (community package `czlonkowski/n8n-mcp`, skonfigurowany w `.mcp.json` — wymaga `N8N_API_KEY` i `N8N_MCP_ACCESS_TOKEN` z n8n Settings).

Pozostaje: podłączyć prawdziwy klucz SendGrid (węzeł "Send Email Report" tymczasowo wyłączony), commit do gita, publikacja portfolio.

## Zasady

Patrz `../CLAUDE.md` dla konwencji całego portfolio.
