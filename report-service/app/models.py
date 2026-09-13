"""Pydantic models for returns report."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SkuRanking(BaseModel):
    sku: str = Field(..., description="Product SKU")
    product_name: str = Field(..., description="Product name from catalog")
    return_count: int = Field(..., ge=0, description="Number of returns")
    percent_of_total: float = Field(..., ge=0, le=100, description="Percentage of total returns")
    category_breakdown: dict[str, int] = Field(..., description="Return counts per category")


class ReturnsReportRequest(BaseModel):
    run_date: datetime = Field(default_factory=datetime.utcnow, description="Date of the analysis run")
    reporting_period: str = Field(..., description="e.g. '2026-09-08 to 2026-09-15'")
    total_returns: int = Field(..., ge=0, description="Total number of returns analyzed")
    top_skus: list[SkuRanking] = Field(..., description="Top SKUs by return count (min 5, max 20)")
    total_flagged_for_review: int = Field(..., ge=0, description="Cases with low confidence")
    categories: tuple[
        Literal[
            "Niezgodność z opisem lub zdjęciem",
            "Wada jakościowa, uszkodzenie fabryczne",
            "Uszkodzenie w transporcie",
            "Błędna wysyłka, nie ten produkt",
            "Niedopasowanie, rozmiar, kolor, dopasowanie",
            "Zmiana decyzji klienta",
            "Opóźniona dostawa, zamówienie nieaktualne",
            "Inne, nieokreślone",
        ],
        ...,
    ] = (
        "Niezgodność z opisem lub zdjęciem",
        "Wada jakościowa, uszkodzenie fabryczne",
        "Uszkodzenie w transporcie",
        "Błędna wysyłka, nie ten produkt",
        "Niedopasowanie, rozmiar, kolor, dopasowanie",
        "Zmiana decyzji klienta",
        "Opóźniona dostawa, zamówienie nieaktualne",
        "Inne, nieokreślone",
    )

    def summary_by_category(self) -> dict[str, int]:
        summary = {cat: 0 for cat in self.categories}
        for sku in self.top_skus:
            for cat, count in sku.category_breakdown.items():
                if cat in summary:
                    summary[cat] += count
        return summary
