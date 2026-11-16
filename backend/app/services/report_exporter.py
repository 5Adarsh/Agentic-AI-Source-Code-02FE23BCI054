"""
Services layer: export generators for Excel, CSV, and PDF compliance reports.
"""
import io
from datetime import datetime, timezone
from typing import Any, Dict, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ReportExporter:
    @staticmethod
    def generate_excel_report(report_title: str, metrics: Dict[str, Any], publications: List[Dict[str, Any]]) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Summary Metrics"

        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        # Title
        ws.merge_cells("A1:D1")
        ws["A1"] = report_title
        ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        ws["A2"] = f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ws["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")

        # Metrics Table
        ws["A4"] = "Metric"
        ws["B4"] = "Value"
        ws["A4"].fill = header_fill
        ws["A4"].font = header_font
        ws["B4"].fill = header_fill
        ws["B4"].font = header_font

        row_idx = 5
        for k, v in metrics.items():
            ws[f"A{row_idx}"] = k.replace("_", " ").title()
            ws[f"B{row_idx}"] = str(v)
            row_idx += 1

        # Sheet 2: Publications
        ws_pubs = wb.create_sheet(title="Verified Publications")
        pub_headers = ["Title", "Authors", "Year", "DOI", "Citations", "Status"]
        for col_idx, h in enumerate(pub_headers, start=1):
            cell = ws_pubs.cell(row=1, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font

        for p_idx, pub in enumerate(publications, start=2):
            authors_str = "; ".join(pub.get("authors", [])) if isinstance(pub.get("authors"), list) else str(pub.get("authors") or "")
            ws_pubs.cell(row=p_idx, column=1, value=pub.get("title", ""))
            ws_pubs.cell(row=p_idx, column=2, value=authors_str)
            ws_pubs.cell(row=p_idx, column=3, value=pub.get("publication_year"))
            ws_pubs.cell(row=p_idx, column=4, value=pub.get("doi"))
            ws_pubs.cell(row=p_idx, column=5, value=pub.get("total_citations", 0))
            ws_pubs.cell(row=p_idx, column=6, value=pub.get("status", ""))

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @staticmethod
    def generate_pdf_report(report_title: str, metrics: Dict[str, Any], publications: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )
        elements.append(Paragraph(report_title, title_style))
        elements.append(Paragraph(f"Research Intelligence & Publication Analytics Portal • Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", styles["Normal"]))
        elements.append(Spacer(1, 16))

        # Metrics Table
        elements.append(Paragraph("<b>Certified Research Performance Metrics</b>", styles["Heading3"]))
        elements.append(Spacer(1, 8))
        
        table_data = [["Metric", "Value"]]
        for k, v in metrics.items():
            table_data.append([k.replace("_", " ").title(), str(v)])

        t = Table(table_data, colWidths=[280, 260])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Publications Sample
        if publications:
            elements.append(Paragraph("<b>Verified Publications Index</b>", styles["Heading3"]))
            elements.append(Spacer(1, 8))
            pub_table = [["Title", "Year", "Citations", "Status"]]
            for p in publications[:15]:
                title_short = (p.get("title") or "")[:45] + "..." if len(p.get("title") or "") > 45 else (p.get("title") or "")
                pub_table.append([
                    title_short,
                    str(p.get("publication_year") or "—"),
                    str(p.get("total_citations", 0)),
                    (p.get("status") or "verified").replace("_", " ").title(),
                ])
            pt = Table(pub_table, colWidths=[300, 60, 80, 100])
            pt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(pt)

        doc.build(elements)
        return buffer.getvalue()
