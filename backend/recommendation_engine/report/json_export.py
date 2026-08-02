"""
JSON Exporter for Recommendation Report.
Serializes recommendation reports into formatted JSON files or string payloads.
"""

import json
from typing import Any, Dict, Optional
from backend.recommendation_engine.utils.logger import report_logger



class JSONReportExporter:
    """
    Exports recommendation reports into JSON payloads.
    """

    @staticmethod
    def export(report_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """
        Serialize report data to JSON string and optionally save to file.
        """
        json_str = json.dumps(report_data, indent=2)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            report_logger.info(f"Report Exported [JSON] to {file_path}")

        return json_str
