"""
PDF / HTML Document Exporter for Recommendation Report.
Renders clean HTML/PDF executive summary reports.
"""

from typing import Any, Dict, Optional
from backend.recommendation_engine.report.markdown_export import MarkdownReportExporter
from backend.recommendation_engine.utils.logger import report_logger


class PDFReportExporter:
    """
    Exports recommendation reports into PDF or HTML formatted document artifacts.
    """

    @staticmethod
    def export(report_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """
        Generate HTML formatted document string (convertible to PDF).
        """
        md_content = MarkdownReportExporter.export(report_data)

        # Convert markdown formatted sections to styled HTML document
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>CurricuAlign AI - Recommendation Report</title>",
            "<style>",
            "body { font-family: 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; padding: 40px; max-width: 900px; margin: 0 auto; }",
            "h1 { color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }",
            "h2 { color: #1e3a8a; margin-top: 30px; }",
            "h3 { color: #2563eb; }",
            "table { width: 100%; border-collapse: collapse; margin: 20px 0; }",
            "th, td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }",
            "th { background-color: #f1f5f9; }",
            "code { background-color: #f8fafc; padding: 2px 6px; border-radius: 4px; color: #2563eb; }",
            ".card { background: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 4px; }",
            "</style>",
            "</head>",
            "<body>",
        ]

        for line in md_content.splitlines():
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")

        html_lines.extend(["</body>", "</html>"])
        html_doc = "\n".join(html_lines)

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_doc)
            report_logger.info(f"Report Exported [PDF/HTML] to {file_path}")

        return html_doc
