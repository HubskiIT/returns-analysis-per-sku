"""Tests for report rendering."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from report_service.app.main import app
from report_service.app.models import ReturnsReportRequest, SkuRanking

client = TestClient(app)


@pytest.fixture
def valid_request() -> dict:
    return {
        "run_date": "2026-09-12T10:00:00",
        "reporting_period": "2026-09-08 to 2026-09-15",
        "total_returns": 45,
        "total_flagged_for_review": 3,
        "top_skus": [
            {
                "sku": "ABC-123",
                "product_name": "Kurtka zimowa XL",
                "return_count": 5,
                "percent_of_total": 11.1,
                "category_breakdown": {
                    "Niedopasowanie, rozmiar, kolor, dopasowanie": 3,
                    "Zmiana decyzji klienta": 2,
                },
            },
            {
                "sku": "DEF-456",
                "product_name": "Buty sportowe 42",
                "return_count": 4,
                "percent_of_total": 8.9,
                "category_breakdown": {
                    "Niezgodność z opisem lub zdjęciem": 2,
                    "Wada jakościowa, uszkodzenie fabryczne": 2,
                },
            },
            {
                "sku": "GHI-789",
                "product_name": "Sweter wełniany M",
                "return_count": 3,
                "percent_of_total": 6.7,
                "category_breakdown": {
                    "Uszkodzenie w transporcie": 3,
                },
            },
        ],
    }


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_render_valid_request(valid_request: dict) -> None:
    response = client.post("/render", json=valid_request)
    assert response.status_code == 200
    data = response.json()
    assert "html" in data
    assert "status" in data
    assert data["status"] == "rendered"
    assert "<!DOCTYPE html>" in data["html"]
    assert "Kurtka zimowa XL" in data["html"]
    assert "45" in data["html"]


def test_render_missing_skus() -> None:
    payload = {
        "reporting_period": "2026-09-08 to 2026-09-15",
        "total_returns": 0,
        "total_flagged_for_review": 0,
        "top_skus": [],
    }
    response = client.post("/render", json=payload)
    assert response.status_code == 400
    assert "At least one SKU ranking is required" in response.json()["detail"]


def test_render_invalid_total_returns() -> None:
    payload = {
        "reporting_period": "2026-09-08 to 2026-09-15",
        "total_returns": -1,
        "total_flagged_for_review": 0,
        "top_skus": [
            {
                "sku": "ABC-123",
                "product_name": "Test",
                "return_count": 1,
                "percent_of_total": 100,
                "category_breakdown": {"Inne, nieokreślone": 1},
            }
        ],
    }
    response = client.post("/render", json=payload)
    assert response.status_code == 400


def test_model_validation_missing_sku_code() -> None:
    with pytest.raises(ValueError, match="sku"):
        SkuRanking(product_name="Test", return_count=1, percent_of_total=50, category_breakdown={})


def test_model_validation_invalid_percentage() -> None:
    with pytest.raises(ValueError, match="less than or equal to 100"):
        SkuRanking(sku="ABC-123", product_name="Test", return_count=1, percent_of_total=150, category_breakdown={})


def test_model_summary_by_category(valid_request: dict) -> None:
    request = ReturnsReportRequest(**valid_request)
    summary = request.summary_by_category()

    assert "Niedopasowanie, rozmiar, kolor, dopasowanie" in summary
    assert summary["Niedopasowanie, rozmiar, kolor, dopasowanie"] == 3
    assert summary["Niezgodność z opisem lub zdjęciem"] == 2
    assert summary["Uszkodzenie w transporcie"] == 3
    assert summary["Zmiana decyzji klienta"] == 2


def test_html_contains_expected_sections(valid_request: dict) -> None:
    response = client.post("/render", json=valid_request)
    html = response.json()["html"]

    assert "Analiza przyczyn zwrotów" in html
    assert "Rozkład przyczyn zwrotów" in html
    assert "Ranking produktów" in html
    assert "Podsumowanie przyczyn" in html
    assert "2026-09-08 to 2026-09-15" in html


def test_html_contains_all_skus(valid_request: dict) -> None:
    response = client.post("/render", json=valid_request)
    html = response.json()["html"]

    for sku_data in valid_request["top_skus"]:
        assert sku_data["sku"] in html
        assert sku_data["product_name"] in html
        assert str(sku_data["return_count"]) in html
