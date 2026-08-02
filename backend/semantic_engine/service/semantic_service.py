"""
Semantic Service for CurricuAlign AI Semantic Intelligence Engine.

The single authoritative public interface for the entire Semantic Engine.
Compares Academic Knowledge against Industry Knowledge.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.service.industry_service import IndustryService
from backend.academic_engine.knowledge.academic_service import AcademicKnowledgeService
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.matching.semantic_matcher import SemanticMatcher
from backend.semantic_engine.similarity.similarity_service import SimilarityService
from backend.semantic_engine.classification.coverage_classifier import CoverageClassifier
from backend.semantic_engine.priority.priority_engine import PriorityEngine
from backend.semantic_engine.evidence.evidence_builder import EvidenceBuilder
from backend.semantic_engine.report.report_builder import SemanticReportBuilder
from backend.semantic_engine.models.semantic_models import (
    CoverageClassificationEnum,
    GapPriorityEnum,
    SemanticComparisonReport,
    SkillMatchResult,
)
from backend.semantic_engine.service.service_models import SemanticEngineHealthStatus
from backend.semantic_engine.service.service_validator import SemanticServiceValidator

logger = logging.getLogger("semantic_engine.service.semantic_service")


class SemanticService:
    """
    Principal Business Facade for the Semantic Intelligence Engine.
    """

    def __init__(
        self,
        industry_service: Optional[IndustryService] = None,
        academic_knowledge_service: Optional[AcademicKnowledgeService] = None,
        config: Optional[SemanticEngineConfig] = None,
    ) -> None:
        self.config = config or SemanticEngineConfig()
        self.industry_service = industry_service or IndustryService(force_fallback_embeddings=True)
        self.academic_knowledge_service = academic_knowledge_service or AcademicKnowledgeService()

        self.matcher = SemanticMatcher(industry_service=self.industry_service, config=self.config)
        self.similarity_service = SimilarityService(threshold_config=self.config.thresholds)
        self.classifier = CoverageClassifier(config=self.config)
        self.priority_engine = PriorityEngine()
        self.report_builder = SemanticReportBuilder(config=self.config)

        logger.info("[Semantic] SemanticService facade initialized successfully.")

    def compare_curriculum(
        self, academic_records: Optional[List[AcademicTechnologyRecord]] = None
    ) -> SemanticComparisonReport:
        """
        Execute complete curriculum comparison against Industry Knowledge.

        Args:
            academic_records: Optional list of AcademicTechnologyRecords. If None, reads from AcademicKnowledgeService.

        Returns:
            SemanticComparisonReport model containing score, statistics, covered, partial, and gap items.
        """
        records = academic_records or self.academic_knowledge_service.get_all()
        if not records:
            # Baseline mock records if academic store is empty
            records = self._create_baseline_academic_records()

        logger.info("[Semantic] Starting comparison for %d academic skills.", len(records))

        match_results: List[SkillMatchResult] = []
        covered_industry_ids: set = set()

        # Step 1: Evaluate academic records against industry candidate matches
        for rec in records:
            candidate = self.matcher.find_best_candidate(rec.canonical_name)
            if candidate:
                sim = candidate.similarity_score
                ind_skill = candidate.industry_skill
                ind_id = candidate.industry_technology_id
                cat = candidate.category
                covered_industry_ids.add(ind_id)
            else:
                sim = 0.0
                ind_skill = rec.canonical_name
                ind_id = rec.technology_id
                cat = rec.category

            classification = self.classifier.classify_match(rec.canonical_name, ind_skill, sim)

            # Retrieve industry scores
            ind_tech = self.industry_service.knowledge_service.get_optional(ind_id) if hasattr(self.industry_service.knowledge_service, "get_optional") else None
            ind_score = ind_tech.industry_score if ind_tech else 70.0
            dem_score = ind_tech.demand_score if ind_tech else 65.0
            dem_pct = ind_tech.metadata.get("percentage", 35.0) if ind_tech else 35.0

            evidence = EvidenceBuilder.build_evidence(
                academic_skill=rec.canonical_name,
                industry_skill=ind_skill,
                similarity=sim,
                classification=classification,
                demand_percentage=dem_pct,
            )

            match_results.append(
                SkillMatchResult(
                    academic_skill=rec.canonical_name,
                    industry_skill=ind_skill,
                    industry_technology_id=ind_id,
                    category=cat,
                    similarity=sim,
                    classification=classification,
                    industry_score=ind_score,
                    demand_score=dem_score,
                    evidence=evidence,
                )
            )

        # Step 2: Identify unmapped Industry skills as Gaps
        all_industry_techs = self.industry_service.get_all_technologies()
        for ind_tech in all_industry_techs:
            if ind_tech.technology_id not in covered_industry_ids:
                dem_pct = ind_tech.metadata.get("percentage", 40.0)
                evidence = EvidenceBuilder.build_evidence(
                    academic_skill=None,
                    industry_skill=ind_tech.canonical_name,
                    similarity=0.0,
                    classification=CoverageClassificationEnum.GAP,
                    demand_percentage=dem_pct,
                )
                match_results.append(
                    SkillMatchResult(
                        academic_skill=None,
                        industry_skill=ind_tech.canonical_name,
                        industry_technology_id=ind_tech.technology_id,
                        category=ind_tech.category,
                        similarity=0.0,
                        classification=CoverageClassificationEnum.GAP,
                        industry_score=ind_tech.industry_score,
                        demand_score=ind_tech.demand_score,
                        evidence=evidence,
                    )
                )

        # Step 3: Priority Calculation
        self.priority_engine.assign_priorities(match_results)

        # Step 4: Build Report
        report = self.report_builder.build_report(match_results)
        return report

    def find_gaps(self, academic_records: Optional[List[AcademicTechnologyRecord]] = None) -> List[Dict[str, Any]]:
        report = self.compare_curriculum(academic_records)
        return report.gap

    def get_covered(self, academic_records: Optional[List[AcademicTechnologyRecord]] = None) -> List[Dict[str, Any]]:
        report = self.compare_curriculum(academic_records)
        return report.covered

    def get_partial(self, academic_records: Optional[List[AcademicTechnologyRecord]] = None) -> List[Dict[str, Any]]:
        report = self.compare_curriculum(academic_records)
        return report.partial

    def get_statistics(self, academic_records: Optional[List[AcademicTechnologyRecord]] = None) -> Dict[str, Any]:
        report = self.compare_curriculum(academic_records)
        return report.statistics

    def generate_alignment_report(self, academic_records: Optional[List[AcademicTechnologyRecord]] = None) -> SemanticComparisonReport:
        return self.compare_curriculum(academic_records)

    def search_similar(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        results = self.industry_service.search_similar(query=query, limit=limit)
        return [r.model_dump() for r in results]

    def health(self) -> SemanticEngineHealthStatus:
        return SemanticEngineHealthStatus(
            status="healthy",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            components={
                "industry_engine": self.industry_service.health().model_dump(),
                "academic_engine": self.academic_knowledge_service.get_statistics().model_dump(),
            },
        )

    @staticmethod
    def _create_baseline_academic_records() -> List[AcademicTechnologyRecord]:
        return [
            AcademicTechnologyRecord(
                technology_id="python", canonical_name="Python", category="Programming Languages", frequency=5
            ),
            AcademicTechnologyRecord(
                technology_id="machine-learning", canonical_name="Machine Learning", category="AI / ML", frequency=3
            ),
            AcademicTechnologyRecord(
                technology_id="postgresql", canonical_name="PostgreSQL", category="Databases", frequency=2
            ),
        ]
