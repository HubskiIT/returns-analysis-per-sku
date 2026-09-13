"""Pure SVG bar chart generator for category distribution."""

from __future__ import annotations


def generate_category_chart_svg(category_counts: dict[str, int], width: int = 600, height: int = 300) -> str:
    """
    Generate a horizontal bar chart as pure SVG for return category distribution.

    Args:
        category_counts: dict of category name -> count
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    if not category_counts:
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><text x="10" y="20">No data</text></svg>'

    bar_height = 25
    margin_left = 300
    margin_bottom = 40
    margin_top = 20
    margin_right = 40

    max_count = max(category_counts.values()) if category_counts.values() else 1
    max_bar_width = width - margin_left - margin_right
    chart_height = len(category_counts) * bar_height + margin_top + margin_bottom

    colors = [
        "#EF4444",  # red
        "#F97316",  # orange
        "#EAB308",  # yellow
        "#22C55E",  # green
        "#0EA5E9",  # sky
        "#6366F1",  # indigo
        "#D946EF",  # magenta
        "#6B7280",  # gray
    ]

    lines = [f'<svg width="{width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">']

    lines.append(
        '<defs><style>'
        ".chart-label { font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px; fill: #374151; }"
        ".chart-value { font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 11px; fill: #1F2937; font-weight: 500; }"
        '.chart-axis { stroke: #E5E7EB; stroke-width: 1; }'
        '</style></defs>'
    )

    y = margin_top
    for idx, (category, count) in enumerate(sorted(category_counts.items(), key=lambda x: -x[1])):
        color = colors[idx % len(colors)]
        bar_width = (count / max_count * max_bar_width) if max_count > 0 else 0
        x_start = margin_left

        lines.append(
            f'<rect x="{x_start}" y="{y}" width="{bar_width}" height="{bar_height - 5}" fill="{color}" rx="2" />'
        )

        label_width = margin_left - 10
        lines.append(
            f'<text x="10" y="{y + 16}" class="chart-label" text-anchor="start" dominant-baseline="middle">{category[:45]}</text>'
        )

        value_x = x_start + bar_width + 5 if bar_width > 30 else x_start + bar_width + 5
        lines.append(f'<text x="{value_x}" y="{y + 16}" class="chart-value" dominant-baseline="middle">{count}</text>')

        y += bar_height

    lines.append("</svg>")
    return "".join(lines)
