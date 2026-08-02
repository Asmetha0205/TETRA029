"""
Markdown Exporter for Recommendation Report.
Renders complete executive markdown document with all required report sections.
"""

from typing import Any, Dict, Optional
from backend.recommendation_engine.utils.logger import report_logger


class MarkdownReportExporter:
    """
    Renders structured Recommendation Reports into GitHub-flavored Markdown text.
    """

    @staticmethod
    def export(report_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """
        Render report into Markdown formatting.
        """
        exec_summary = report_data.get("executive_summary", "")
        alignment_score = report_data.get("alignment_score", 0.0)
        critical_gaps = report_data.get("critical_gaps", [])
        high_priority = report_data.get("high_priority_skills", [])
        categories = report_data.get("category_analysis", {})
        recommendations = report_data.get("recommendations", [])
        learning_paths = report_data.get("learning_paths", {})
        evidence = report_data.get("evidence", [])
        action_plan = report_data.get("action_plan", [])
        future_skills = report_data.get("future_skills", [])

        md = []
        md.append("# CurricuAlign AI - Executive Curriculum Recommendation Report\n")
        md.append(f"**Overall Alignment Score**: `{alignment_score}/100`\n")
        md.append("## 1. Executive Summary\n")
        md.append(f"{exec_summary}\n")

        md.append("## 2. Critical Gaps & High Priority Skills\n")
        md.append(f"- **Critical Gaps**: {', '.join(critical_gaps) if critical_gaps else 'None'}")
        md.append(f"- **High Priority Skills**: {', '.join(high_priority) if high_priority else 'None'}\n")

        md.append("## 3. Category Analysis\n")
        md.append("| Category | Alignment Score | Gaps Identified |")
        md.append("| :--- | :--- | :--- |")
        for cat, data in categories.items():
            if isinstance(data, dict):
                score = data.get("alignment_score", 0.0)
                gaps = data.get("gap_count", 0)
                md.append(f"| {cat} | {score}% | {gaps} |")
            else:
                md.append(f"| {cat} | {data}% | - |")
        md.append("")

        md.append("## 4. Evidence-Backed Curriculum Recommendations\n")
        for idx, rec in enumerate(recommendations, start=1):
            tech = rec.get("technology", "Unknown")
            pri = rec.get("priority", "High")
            ind_score = rec.get("industry_score", 0)
            trend = rec.get("trend", "Rising")
            reason = rec.get("reason", "")
            course = rec.get("recommended_course", "")
            module = rec.get("recommended_module", "")
            lab = rec.get("lab", "")
            proj = rec.get("mini_project", "")
            conf = rec.get("confidence", 0.0)

            md.append(f"### 4.{idx} {tech} ({pri} Priority - Demand Score: {ind_score})")
            md.append(f"- **Market Trend**: {trend}")
            md.append(f"- **Justification**: {reason}")
            md.append(f"- **Placement**: Course: *{course}* | Module: *{module}*")
            md.append(f"- **Lab Exercise**: {lab}")
            md.append(f"- **Mini Project**: {proj}")
            md.append(f"- **Confidence Score**: {conf}\n")

        md.append("## 5. Learning Path Sequence\n")
        seq = learning_paths.get("sequence", [])
        if seq:
            md.append(f"**Prerequisite Progression**: `{' -> '.join(seq)}`\n")

        md.append("## 6. Action Plan\n")
        for step in action_plan:
            md.append(f"- [ ] {step}")
        md.append("")

        md.append("## 7. Future Skills Radar\n")
        for fs in future_skills:
            md.append(f"- {fs}")
        md.append("")

        md_content = "\n".join(md)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            report_logger.info(f"Report Exported [Markdown] to {file_path}")

        return md_content
