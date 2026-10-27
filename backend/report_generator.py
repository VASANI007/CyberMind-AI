"""
CyberMind AI - Report Generator Service (PDF & JSON)
"""

from __future__ import annotations

import io
import html
import json
from datetime import datetime
from typing import Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from core.logger import logger


def generate_pdf_report(scan_result: dict[str, Any]) -> bytes:
    """Generates a professional CyberMind AI Cybersecurity PDF report."""
    target = scan_result.get("target") or scan_result.get("value") or "Unknown Target"
    scanner = scan_result.get("scanner") or scan_result.get("scanner_key") or "CyberMind Scanner"
    risk_score = scan_result.get("risk_score", 0)
    risk_level = scan_result.get("risk_level", "Safe")
    duration = scan_result.get("duration", "0.45 sec")
    scan_time = scan_result.get("time", datetime.now().strftime("%H:%M:%S"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0284C7'),
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=8,
    )
    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#334155'),
    )
    cell_val = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#0F172A'),
    )
    summary_box = ParagraphStyle(
        'SummaryBox',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("CyberMind AI — Threat Intelligence Report", title_style))
    story.append(Paragraph(
        f"<b>Target:</b> {html.escape(str(target))} &nbsp;|&nbsp; <b>Scanner:</b> {html.escape(scanner)} &nbsp;|&nbsp; <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    # Executive Overview Table
    level_color = colors.HexColor('#10B981')
    if risk_level in ("Critical", "High", "Malicious"):
        level_color = colors.HexColor('#EF4444')
    elif risk_level in ("Medium", "Suspicious"):
        level_color = colors.HexColor('#F59E0B')

    overview_data = [
        [
            Paragraph("<b>Risk Score</b>", cell_label),
            Paragraph(f"<b>{risk_score:.1f} / 100</b>", cell_val),
            Paragraph("<b>Risk Level</b>", cell_label),
            Paragraph(f"<b>{risk_level}</b>", cell_val),
        ],
        [
            Paragraph("<b>Scan Duration</b>", cell_label),
            Paragraph(str(duration), cell_val),
            Paragraph("<b>Scan Time</b>", cell_label),
            Paragraph(str(scan_time), cell_val),
        ]
    ]
    t_overview = Table(overview_data, colWidths=[120, 150, 120, 150])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 12))

    # AI Executive Summary
    explain = scan_result.get("explain_ai", {})
    summary_text = explain.get("summary") or "Comprehensive automated cybersecurity scan performed across active threat feeds, heuristics engines, and machine learning models."
    story.append(Paragraph("AI Executive Summary", section_style))

    summary_table = Table([[Paragraph(html.escape(summary_text), summary_box)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#38BDF8')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Detailed Analysis Parameters
    analysis = scan_result.get("analysis", {})
    if analysis:
        story.append(Paragraph("Detailed Findings & Parameters", section_style))
        param_rows = [["Security Check / Parameter", "Observed Value / Status"]]

        def _flatten_analysis(d: dict, prefix=""):
            for k, v in d.items():
                label = f"{prefix}{k}".replace("_", " ").title()
                if isinstance(v, dict):
                    _flatten_analysis(v, f"{label} → ")
                elif isinstance(v, list):
                    param_rows.append([Paragraph(html.escape(label), cell_label), Paragraph(html.escape(f"{len(v)} item(s)"), cell_val)])
                else:
                    val_str = str(v)
                    if len(val_str) > 100:
                        val_str = val_str[:97] + "..."
                    param_rows.append([Paragraph(html.escape(label), cell_label), Paragraph(html.escape(val_str), cell_val)])

        _flatten_analysis(analysis)

        # Cap rows if too long
        display_rows = param_rows[:25]
        t_params = Table(display_rows, colWidths=[240, 300])
        t_params.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_params)
        story.append(Spacer(1, 10))

    # Recommendations
    recs = scan_result.get("recommendation", {}).get("recommendations", [])
    if recs:
        story.append(Paragraph("Actionable Recommendations", section_style))
        rec_rows = []
        for i, r in enumerate(recs, 1):
            rec_rows.append([
                Paragraph(f"<b>{i}.</b>", cell_label),
                Paragraph(html.escape(str(r)), cell_val)
            ])
        t_recs = Table(rec_rows, colWidths=[30, 510])
        t_recs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_recs)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_json_report(scan_result: dict[str, Any]) -> str:
    """Generates a structured JSON report string."""
    report_dict = {
        "report_metadata": {
            "application": "CyberMind AI",
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "target": scan_result.get("target"),
            "scanner": scan_result.get("scanner"),
        },
        "executive_summary": {
            "risk_score": scan_result.get("risk_score"),
            "risk_level": scan_result.get("risk_level"),
            "duration": scan_result.get("duration"),
            "summary": scan_result.get("explain_ai", {}).get("summary"),
        },
        "ml_inference": scan_result.get("ml_prediction", {}),
        "risk_breakdown": scan_result.get("risk", {}),
        "detailed_analysis": scan_result.get("analysis", {}),
        "recommendations": scan_result.get("recommendation", {}).get("recommendations", []),
        "mitre_attack": scan_result.get("mitre_attack", []),
        "geolocation": scan_result.get("geo", {}),
    }
    return json.dumps(report_dict, indent=2, default=str)
