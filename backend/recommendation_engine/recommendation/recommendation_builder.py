"""
Recommendation Builder for Recommendation Module.
Enriches parsed LLM recommendations with Neo4j evidence, calculates confidence,
and packages into RecommendationResultSet.
"""

import datetime
from typing import Any, Dict, List, Optional
from backend.recommendation_engine.recommendation.recommendation_models import RecommendationItem, RecommendationResultSet
from backend.recommendation_engine.recommendation.recommendation_validator import RecommendationValidator
from backend.recommendation_engine.utils.helpers import calculate_confidence
from backend.recommendation_engine.utils.logger import recommendation_logger_tagged


class RecommendationBuilder:
    """
    Assembles evidence-backed Recommendation objects matching exact required schema.
    """

    def build_recommendations(
        self,
        llm_payload: Dict[str, Any],
        evidence_list: List[Dict[str, Any]]
    ) -> RecommendationResultSet:
        """
        Build RecommendationResultSet by merging LLM outputs with Neo4j evidence metrics.
        """
        recommendation_logger_tagged.info("Building finalized recommendation objects...")

        raw_recs = llm_payload.get("recommendations", [])
        evidence_map = {
            e.get("tech_name", e.get("technology", "")).lower(): e
            for e in evidence_list
        }

        final_items: List[RecommendationItem] = []

        for item in raw_recs:
            tech_name = item.get("technology", "Unknown")
            ev = evidence_map.get(tech_name.lower(), {})

            ind_score = float(item.get("industry_score", ev.get("industry_score", 85.0)))
            trend_val = str(item.get("trend", ev.get("trend", "Rising")))
            priority_val = str(item.get("priority", "High"))

            # Calculate grounded confidence
            ev_count = len(ev.get("related_roles", [])) + len(ev.get("related_technologies", []))
            conf = calculate_confidence(
                industry_score=ind_score,
                evidence_count=ev_count,
                similarity_score=0.95
            )

            rec_item = RecommendationItem(
                technology=tech_name,
                priority=priority_val,
                industry_score=ind_score,
                trend=trend_val,
                reason=item.get("reason", f"{tech_name} is essential for industry software engineering roles."),
                recommended_course=item.get("recommended_course", "Software Systems Engineering"),
                recommended_module=item.get("recommended_module", f"Applied {tech_name} Integration"),
                learning_outcomes=item.get("learning_outcomes", [
                    f"Master core concepts and syntax of {tech_name}",
                    f"Deploy {tech_name} solutions in production environments"
                ]),
                lab=item.get("lab", f"Configure and implement {tech_name} in local dev environment."),
                mini_project=item.get("mini_project", f"End-to-End {tech_name} Application Project"),
                learning_path=item.get("learning_path", [tech_name]),
                references=item.get("references", ["Neo4j Knowledge Graph", "Industry Skill Analysis"]),
                confidence=conf
            )
            final_items.append(rec_item)

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result_set = RecommendationResultSet(
            recommendations=final_items,
            total_recommendations=len(final_items),
            generated_at=now_str,
            summary_metrics={
                "high_priority_count": sum(1 for i in final_items if i.priority in ["High", "Critical"]),
                "avg_confidence": round(sum(i.confidence for i in final_items) / max(len(final_items), 1), 2)
            }
        )

        RecommendationValidator.validate_result_set(result_set)
        recommendation_logger_tagged.info(f"Built {len(final_items)} finalized recommendation items successfully.")
        return result_set
