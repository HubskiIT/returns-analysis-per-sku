# Wynik ewaluacji klasyfikatora

- Model: `claude-haiku-4-5`
- Przypadki: 30
- Poprawne: 27/30
- Trafność: 90.00%
- Próg: >85% (spełniony)

## Macierz pomyłek

| Oczekiwana kategoria | Predykcja | Liczba |
|---|---|---:|
| Błędna wysyłka, nie ten produkt | Błędna wysyłka, nie ten produkt | 4 |
| Inne, nieokreślone | Inne, nieokreślone | 1 |
| Inne, nieokreślone | Zmiana decyzji klienta | 1 |
| Niedopasowanie, rozmiar, kolor, dopasowanie | Niedopasowanie, rozmiar, kolor, dopasowanie | 3 |
| Niedopasowanie, rozmiar, kolor, dopasowanie | Zmiana decyzji klienta | 2 |
| Niezgodność z opisem lub zdjęciem | Niezgodność z opisem lub zdjęciem | 4 |
| Opóźniona dostawa, zamówienie nieaktualne | Opóźniona dostawa, zamówienie nieaktualne | 3 |
| Uszkodzenie w transporcie | Uszkodzenie w transporcie | 4 |
| Wada jakościowa, uszkodzenie fabryczne | Wada jakościowa, uszkodzenie fabryczne | 4 |
| Zmiana decyzji klienta | Zmiana decyzji klienta | 4 |

## Przypadki

| ID | Oczekiwane | Predykcja | Confidence | Wynik |
|---|---|---|---:|---|
| eval-001 | Niezgodność z opisem lub zdjęciem | Niezgodność z opisem lub zdjęciem | 0.95 | OK |
| eval-002 | Wada jakościowa, uszkodzenie fabryczne | Wada jakościowa, uszkodzenie fabryczne | 0.95 | OK |
| eval-003 | Uszkodzenie w transporcie | Uszkodzenie w transporcie | 0.95 | OK |
| eval-004 | Błędna wysyłka, nie ten produkt | Błędna wysyłka, nie ten produkt | 0.95 | OK |
| eval-005 | Niedopasowanie, rozmiar, kolor, dopasowanie | Niedopasowanie, rozmiar, kolor, dopasowanie | 0.95 | OK |
| eval-006 | Zmiana decyzji klienta | Zmiana decyzji klienta | 0.95 | OK |
| eval-007 | Opóźniona dostawa, zamówienie nieaktualne | Opóźniona dostawa, zamówienie nieaktualne | 0.95 | OK |
| eval-008 | Inne, nieokreślone | Zmiana decyzji klienta | 0.60 | BŁĄD |
| eval-009 | Niezgodność z opisem lub zdjęciem | Niezgodność z opisem lub zdjęciem | 0.95 | OK |
| eval-010 | Wada jakościowa, uszkodzenie fabryczne | Wada jakościowa, uszkodzenie fabryczne | 0.95 | OK |
| eval-011 | Uszkodzenie w transporcie | Uszkodzenie w transporcie | 0.95 | OK |
| eval-012 | Błędna wysyłka, nie ten produkt | Błędna wysyłka, nie ten produkt | 0.95 | OK |
| eval-013 | Niedopasowanie, rozmiar, kolor, dopasowanie | Niedopasowanie, rozmiar, kolor, dopasowanie | 0.95 | OK |
| eval-014 | Zmiana decyzji klienta | Zmiana decyzji klienta | 0.95 | OK |
| eval-015 | Opóźniona dostawa, zamówienie nieaktualne | Opóźniona dostawa, zamówienie nieaktualne | 0.95 | OK |
| eval-016 | Niedopasowanie, rozmiar, kolor, dopasowanie | Zmiana decyzji klienta | 0.60 | BŁĄD |
| eval-017 | Niezgodność z opisem lub zdjęciem | Niezgodność z opisem lub zdjęciem | 0.85 | OK |
| eval-018 | Wada jakościowa, uszkodzenie fabryczne | Wada jakościowa, uszkodzenie fabryczne | 0.95 | OK |
| eval-019 | Uszkodzenie w transporcie | Uszkodzenie w transporcie | 0.95 | OK |
| eval-020 | Błędna wysyłka, nie ten produkt | Błędna wysyłka, nie ten produkt | 0.95 | OK |
| eval-021 | Niedopasowanie, rozmiar, kolor, dopasowanie | Zmiana decyzji klienta | 0.95 | BŁĄD |
| eval-022 | Zmiana decyzji klienta | Zmiana decyzji klienta | 0.95 | OK |
| eval-023 | Opóźniona dostawa, zamówienie nieaktualne | Opóźniona dostawa, zamówienie nieaktualne | 0.95 | OK |
| eval-024 | Inne, nieokreślone | Inne, nieokreślone | 0.65 | OK |
| eval-025 | Niezgodność z opisem lub zdjęciem | Niezgodność z opisem lub zdjęciem | 0.85 | OK |
| eval-026 | Wada jakościowa, uszkodzenie fabryczne | Wada jakościowa, uszkodzenie fabryczne | 0.85 | OK |
| eval-027 | Uszkodzenie w transporcie | Uszkodzenie w transporcie | 0.95 | OK |
| eval-028 | Błędna wysyłka, nie ten produkt | Błędna wysyłka, nie ten produkt | 0.95 | OK |
| eval-029 | Niedopasowanie, rozmiar, kolor, dopasowanie | Niedopasowanie, rozmiar, kolor, dopasowanie | 0.85 | OK |
| eval-030 | Zmiana decyzji klienta | Zmiana decyzji klienta | 0.95 | OK |
