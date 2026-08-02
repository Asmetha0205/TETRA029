"""
Academic Knowledge Builder for CurricuAlign AI Academic Engine.

Converts normalized technology extractions and parsed document structure into
canonical AcademicTechnologyRecord objects ready for repository persistence.
"""

import re
import datetime
import logging
from typing import Any, Dict, List, Optional

from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.academic_engine.models.academic_document import ParsedAcademicDocument
from backend.industry_engine.processing.normalization.models import NormalizationResult

logger = logging.getLogger("academic_engine.knowledge.academic_builder")


class AcademicKnowledgeBuilder:
    """
    Transforms NormalizedTechnology items into AcademicTechnologyRecord objects.
    """

    def build_records(
        self,
        normalization_result: NormalizationResult,
        document: ParsedAcademicDocument,
    ) -> List[AcademicTechnologyRecord]:
        """
        Build AcademicTechnologyRecord objects from normalization result and document context.

        Args:
            normalization_result: NormalizationResult from AcademicTechnologyNormalizer.
            document: ParsedAcademicDocument context.

        Returns:
            List of AcademicTechnologyRecord objects sorted by technology_id.
        """
        records: List[AcademicTechnologyRecord] = []
        seen_ids = set()

        first_course = document.courses[0] if document.courses else {}
        course_code = first_course.get("course_code", "CS101")
        course_name = first_course.get("title", "Computer Science Core")
        semester = first_course.get("semester", "Semester 1")
        credits_val = first_course.get("credits", 3.0)

        now_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for norm_tech in normalization_result.normalized:
            cname = norm_tech.canonical_name.strip()
            if not cname:
                continue

            tech_id = self._slugify(cname)
            if tech_id in seen_ids:
                continue
            seen_ids.add(tech_id)

            rec = AcademicTechnologyRecord(
                technology_id=tech_id,
                canonical_name=cname,
                category=norm_tech.category or "Unknown",
                aliases=sorted(list(set(norm_tech.aliases))),
                university=document.university_name,
                department=document.department,
                degree_program=document.degree_program,
                course_code=course_code,
                course_name=course_name,
                semester=semester,
                credits=credits_val,
                module_name="Core Curriculum Unit",
                learning_outcomes=[f"Demonstrate proficiency in {cname}"],
                frequency=1,
                first_seen=now_ts,
                last_updated=now_ts,
                metadata={"document_id": document.document_id},
            )
            records.append(rec)

        records.sort(key=lambda r: r.technology_id)
        logger.info("[Academic] Built %d AcademicTechnologyRecords.", len(records))
        return records

    @staticmethod
    def _slugify(text: str) -> str:
        slug = text.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        return slug or "unknown"
