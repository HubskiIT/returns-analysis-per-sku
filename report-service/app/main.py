"""FastAPI service for rendering returns analysis reports as PDF."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .chart import generate_category_chart_svg
from .models import ReturnsReportRequest

app = FastAPI(title="Returns Report Service", version="1.0.0")

TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html", "xml"]))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/render")
def render_report(request: ReturnsReportRequest) -> dict[str, str]:
    """
    Render a returns report as HTML (PDF generation handled by caller).

    Takes ranking data and generates a formatted HTML report with charts.
    Caller (n8n) is responsible for converting HTML to PDF using WeasyPrint.
    """
    if not request.top_skus:
        raise HTTPException(status_code=400, detail="At least one SKU ranking is required")

    if request.total_returns < 0:
        raise HTTPException(status_code=400, detail="total_returns must be non-negative")

    summary = request.summary_by_category()
    chart_svg = generate_category_chart_svg(summary)

    template = jinja_env.get_template("returns_report.html")
    html = template.render(
        reporting_period=request.reporting_period,
        run_date=request.run_date,
        total_returns=request.total_returns,
        total_flagged_for_review=request.total_flagged_for_review,
        top_skus=request.top_skus,
        chart_svg=chart_svg,
        categories=request.categories,
        request=request,
    )

    return {"html": html, "status": "rendered"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
