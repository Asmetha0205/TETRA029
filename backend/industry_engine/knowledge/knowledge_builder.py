"""
Knowledge Builder for the CurricuAlign AI Industry Knowledge Layer.

Converts and merges outputs from previous pipeline phases (Normalization,
Frequency Analysis, and Demand & Trend Analysis) into canonical
TechnologyKnowledgeRecord objects ready for storage in the knowledge repository.

Deterministic: Given identical inputs, always generates identical records.
"""

import datetime
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.knowledge_models import (
    TechnologyClassification,
    TechnologyKnowledgeRecord,
    TechnologyStatus,
    TechnologyTrend,
    VersionInfo,
)

logger = logging.getLogger("industry_engine.knowledge.knowledge_builder")


class KnowledgeBuilder:
    """
    Transforms outputs from previous pipeline stages into TechnologyKnowledgeRecord objects.

    Fuses:
      1. NormalizationResult (or list of normalized tech dicts/models)
      2. FrequencyReport (or frequency data dict/model)
      3. IndustryReport (or demand/industry report dict/model)

    Populates every field in TechnologyKnowledgeRecord deterministically.
    """

    def __init__(self) -> None:
        """Initialize the knowledge builder."""
        logger.info("[Knowledge] Builder initialized.")

    def build(
        self,
        normalization_result: Any,
        frequency_report: Optional[Any] = None,
        industry_report: Optional[Any] = None,
        source: str = "pipeline",
        timestamp: Optional[str] = None,
    ) -> List[TechnologyKnowledgeRecord]:
        """
        Build technology knowledge records by merging NormalizationResult,
        FrequencyReport, and IndustryReport.

        Args:
            normalization_result: NormalizationResult instance, dict, or list of normalized techs.
            frequency_report: Optional FrequencyReport instance or dict.
            industry_report: Optional IndustryReport instance or dict.
            source: Identifier for data source provenance.
            timestamp: Optional fixed ISO timestamp string for deterministic record creation.

        Returns:
            List of merged TechnologyKnowledgeRecord objects, sorted by technology_id.
        """
        normalized_techs = self._extract_normalized_techs(normalization_result)
        freq_map, role_map = self._build_frequency_and_role_maps(frequency_report)
        demand_map = self._build_demand_map(industry_report)

        records: List[TechnologyKnowledgeRecord] = []
        seen_ids: set = set()

        for tech in normalized_techs:
            canonical_name = tech.get("canonical_name", "").strip()
            if not canonical_name:
                continue

            tech_id = self._generate_tech_id(canonical_name)
            if tech_id in seen_ids:
                logger.debug("[Knowledge] Skipping duplicate tech_id: %s", tech_id)
                continue
            seen_ids.add(tech_id)

            category = tech.get("category", "Unknown").strip() or "Unknown"
            aliases = self._clean_aliases(tech.get("aliases", []))

            freq_entry = freq_map.get(canonical_name) or freq_map.get(tech_id) or {}
            demand_entry = demand_map.get(canonical_name) or demand_map.get(tech_id) or {}
            role_coverage = role_map.get(canonical_name) or role_map.get(tech_id) or {}

            record = self._build_single_record(
                tech_id=tech_id,
                canonical_name=canonical_name,
                category=category,
                aliases=aliases,
                frequency_entry=freq_entry,
                demand_entry=demand_entry,
                role_coverage=role_coverage,
                source=source,
                matched_variants=tech.get("matched_variants", []),
                timestamp=timestamp,
            )
            records.append(record)

        # Sort records deterministically by technology_id
        records.sort(key=lambda r: r.technology_id)

        # Compute deterministic co-occurrence related technologies
        self.compute_related_technologies(records)

        logger.info(
            "[Knowledge] Built %d deterministic knowledge records from pipeline outputs.",
            len(records),
        )
        return records

    def build_from_pipeline_outputs(
        self,
        normalized_techs: List[Dict[str, Any]],
        frequency_data: Optional[Dict[str, Any]] = None,
        demand_data: Optional[Dict[str, Any]] = None,
        source: str = "pipeline",
        timestamp: Optional[str] = None,
    ) -> List[TechnologyKnowledgeRecord]:
        """
        Convenience facade for building from dictionary pipeline outputs.

        Args:
            normalized_techs: List of normalized technology dicts.
            frequency_data: Optional frequency report dict.
            demand_data: Optional industry report dict.
            source: Identifier for data source.
            timestamp: Optional ISO timestamp override.

        Returns:
            List of TechnologyKnowledgeRecord objects.
        """
        return self.build(
            normalization_result=normalized_techs,
            frequency_report=frequency_data,
            industry_report=demand_data,
            source=source,
            timestamp=timestamp,
        )

    def build_single(
        self,
        canonical_name: str,
        category: str,
        aliases: Optional[List[str]] = None,
        description: str = "",
        frequency: int = 0,
        percentage: float = 0.0,
        rank: int = 0,
        demand_score: float = 0.0,
        industry_score: float = 0.0,
        trend: Union[str, TechnologyTrend] = TechnologyTrend.STABLE,
        growth: float = 0.0,
        classification: Union[str, TechnologyClassification] = TechnologyClassification.SUPPORTING,
        role_coverage: Optional[Dict[str, float]] = None,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> TechnologyKnowledgeRecord:
        """
        Build a single TechnologyKnowledgeRecord with explicit parameters.

        Args:
            canonical_name: Canonical technology display name.
            category: Canonical category string.
            aliases: Optional list of known aliases.
            description: Optional description string.
            frequency: Job mention count.
            percentage: Mention percentage across jobs.
            rank: Frequency rank.
            demand_score: Demand score (0-100).
            industry_score: Industry intelligence score (0-100).
            trend: Trend enum or string.
            growth: Growth percentage.
            classification: Classification enum or string.
            role_coverage: Mapping of job role to percentage coverage.
            source: Data source identifier.
            metadata: Arbitrary additional metadata dict.
            timestamp: Optional timestamp string.

        Returns:
            A populated TechnologyKnowledgeRecord.
        """
        tech_id = self._generate_tech_id(canonical_name)
        clean_aliases = sorted(list(set(aliases or [])))
        parsed_trend = self._parse_trend(trend)
        parsed_classification = self._parse_classification(classification)

        now_ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()

        meta = dict(metadata or {})
        if percentage > 0:
            meta["percentage"] = round(float(percentage), 4)
        if rank > 0:
            meta["rank"] = int(rank)

        clean_description = description.strip() or self._generate_description(canonical_name, category)

        sorted_roles = {
            r: round(float(pct), 4)
            for r, pct in sorted((role_coverage or {}).items(), key=lambda x: x[0])
        }

        return TechnologyKnowledgeRecord(
            technology_id=tech_id,
            canonical_name=canonical_name.strip(),
            category=category.strip(),
            aliases=clean_aliases,
            description=clean_description,
            frequency=max(0, int(frequency)),
            demand_score=round(max(0.0, min(100.0, float(demand_score))), 4),
            industry_score=round(max(0.0, min(100.0, float(industry_score))), 4),
            trend=parsed_trend,
            growth=round(float(growth), 4),
            classification=parsed_classification,
            related_technologies=[],
            role_coverage=sorted_roles,
            sources=sorted(list(set([source]))),
            status=TechnologyStatus.ACTIVE,
            first_seen=now_ts,
            last_updated=now_ts,
            version=VersionInfo(created_at=now_ts, updated_at=now_ts),
            metadata=meta,
        )

    def update_record_with_frequency(
        self,
        record: TechnologyKnowledgeRecord,
        frequency_entry: Dict[str, Any],
    ) -> TechnologyKnowledgeRecord:
        """
        Update an existing record with new frequency data.

        Args:
            record: The record to update.
            frequency_entry: Dict containing 'mentions', 'percentage', 'rank', etc.

        Returns:
            The updated record.
        """
        if "mentions" in frequency_entry:
            record.frequency = max(0, int(frequency_entry["mentions"]))
        if "percentage" in frequency_entry:
            record.metadata["percentage"] = round(float(frequency_entry["percentage"]), 4)
        if "rank" in frequency_entry:
            record.metadata["rank"] = int(frequency_entry["rank"])
        record.touch()
        return record

    def update_record_with_demand(
        self,
        record: TechnologyKnowledgeRecord,
        demand_entry: Dict[str, Any],
    ) -> TechnologyKnowledgeRecord:
        """
        Update an existing record with new demand/trend intelligence.

        Args:
            record: The record to update.
            demand_entry: Dict containing demand_score, industry_score, trend, growth, classification.

        Returns:
            The updated record.
        """
        if "demand_score" in demand_entry:
            record.demand_score = round(max(0.0, min(100.0, float(demand_entry["demand_score"]))), 4)
        if "industry_score" in demand_entry:
            record.industry_score = round(max(0.0, min(100.0, float(demand_entry["industry_score"]))), 4)
        if "trend" in demand_entry:
            record.trend = self._parse_trend(demand_entry["trend"])
        if "growth" in demand_entry:
            record.growth = round(float(demand_entry["growth"]), 4)
        if "classification" in demand_entry:
            record.classification = self._parse_classification(demand_entry["classification"])
        record.touch()
        return record

    def compute_related_technologies(
        self,
        records: List[TechnologyKnowledgeRecord],
        max_related: int = 5,
    ) -> None:
        """
        Compute related technologies for each record deterministically.

        Peer records within the same category are scored by proximity of their industry_score.
        Ties are broken deterministically by technology_id ascending.

        Args:
            records: List of TechnologyKnowledgeRecord objects to process in place.
            max_related: Maximum number of related technology IDs per record.
        """
        by_category: Dict[str, List[TechnologyKnowledgeRecord]] = {}
        for record in records:
            by_category.setdefault(record.category, []).append(record)

        for record in records:
            category_peers = by_category.get(record.category, [])
            scored_peers = []
            for peer in category_peers:
                if peer.technology_id == record.technology_id:
                    continue
                score_diff = abs(peer.industry_score - record.industry_score)
                scored_peers.append((peer, score_diff))

            # Deterministic sort: primary = score_diff ascending, secondary = technology_id ascending
            scored_peers.sort(key=lambda item: (item[1], item[0].technology_id))

            record.related_technologies = [
                peer.technology_id for peer, _ in scored_peers[:max_related]
            ]

    def merge_role_coverage(
        self,
        existing: Dict[str, float],
        new_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Merge new role coverage data into existing coverage deterministically.

        Args:
            existing: Current role -> percentage mapping.
            new_data: Dict mapping role names to percentage values.

        Returns:
            Merged role coverage dictionary with sorted keys.
        """
        merged = dict(existing)
        for key, value in new_data.items():
            if isinstance(value, (int, float)) and 0 <= value <= 100:
                merged[str(key)] = round(float(value), 4)
            elif isinstance(value, dict):
                for role, pct in value.items():
                    if isinstance(pct, (int, float)) and 0 <= pct <= 100:
                        merged[str(role)] = round(float(pct), 4)
        return {r: merged[r] for r in sorted(merged.keys())}

    # ------------------------------------------------------------------
    # Internal Extraction Helpers
    # ------------------------------------------------------------------

    def _extract_normalized_techs(self, raw_input: Any) -> List[Dict[str, Any]]:
        """Extract a list of normalized tech dicts from various input representations."""
        if raw_input is None:
            return []

        # If it has a .normalized attribute (e.g. NormalizationResult Pydantic model)
        if hasattr(raw_input, "normalized"):
            items = getattr(raw_input, "normalized")
            return [self._model_or_dict_to_dict(i) for i in items]

        # If it's a dict containing 'normalized' key
        if isinstance(raw_input, dict) and "normalized" in raw_input:
            items = raw_input["normalized"]
            return [self._model_or_dict_to_dict(i) for i in items]

        # If it's a list directly
        if isinstance(raw_input, list):
            return [self._model_or_dict_to_dict(i) for i in raw_input]

        # Single item fallback
        if isinstance(raw_input, dict):
            return [raw_input]

        return []

    def _build_frequency_and_role_maps(
        self, frequency_report: Optional[Any]
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, float]]]:
        """
        Extract frequency_map (name -> dict) and role_map (name -> {role: pct}).
        """
        if not frequency_report:
            return {}, {}

        # Handle object or dict representation
        report_dict = self._model_or_dict_to_dict(frequency_report)
        tech_list = report_dict.get("technologies", [])
        role_list = report_dict.get("roles", [])

        freq_map: Dict[str, Dict[str, Any]] = {}
        for tech in tech_list:
            td = self._model_or_dict_to_dict(tech)
            name = td.get("name") or td.get("canonical_name") or ""
            if name:
                freq_map[name] = td

        role_map: Dict[str, Dict[str, float]] = {}
        for role_entry in role_list:
            re_dict = self._model_or_dict_to_dict(role_entry)
            role_title = re_dict.get("role", "General")
            top_techs = re_dict.get("top_technologies", [])
            for item in top_techs:
                item_dict = self._model_or_dict_to_dict(item)
                tech_name = item_dict.get("technology") or item_dict.get("name") or ""
                pct = item_dict.get("percentage", 0.0)
                if tech_name:
                    role_map.setdefault(tech_name, {})[role_title] = round(float(pct), 4)

        return freq_map, role_map

    def _build_demand_map(self, industry_report: Optional[Any]) -> Dict[str, Dict[str, Any]]:
        """Extract demand_map (name -> dict) from IndustryReport or dict."""
        if not industry_report:
            return {}

        report_dict = self._model_or_dict_to_dict(industry_report)
        tech_list = report_dict.get("technologies", [])

        demand_map: Dict[str, Dict[str, Any]] = {}
        for tech in tech_list:
            td = self._model_or_dict_to_dict(tech)
            name = td.get("name") or td.get("canonical_name") or ""
            if name:
                demand_map[name] = td
        return demand_map

    def _build_single_record(
        self,
        tech_id: str,
        canonical_name: str,
        category: str,
        aliases: List[str],
        frequency_entry: Dict[str, Any],
        demand_entry: Dict[str, Any],
        role_coverage: Dict[str, float],
        source: str,
        matched_variants: List[str],
        timestamp: Optional[str],
    ) -> TechnologyKnowledgeRecord:
        """Construct a complete, deterministic TechnologyKnowledgeRecord."""
        frequency = frequency_entry.get("mentions", demand_entry.get("mentions", 0))
        percentage = frequency_entry.get("percentage", demand_entry.get("percentage", 0.0))
        rank = frequency_entry.get("rank", demand_entry.get("rank", 0))

        demand_score = demand_entry.get("demand_score", 0.0)
        industry_score = demand_entry.get("industry_score", 0.0)
        trend_val = demand_entry.get("trend", TechnologyTrend.STABLE)
        growth = demand_entry.get("growth", 0.0)
        classification_val = demand_entry.get("classification", TechnologyClassification.SUPPORTING)

        meta: Dict[str, Any] = {}
        if percentage > 0:
            meta["percentage"] = round(float(percentage), 4)
        if rank > 0:
            meta["rank"] = int(rank)
        if matched_variants:
            meta["matched_variants"] = sorted(list(set(matched_variants)))

        now_ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
        sorted_roles = {r: round(float(pct), 4) for r, pct in sorted(role_coverage.items(), key=lambda x: x[0])}

        return TechnologyKnowledgeRecord(
            technology_id=tech_id,
            canonical_name=canonical_name,
            category=category,
            aliases=sorted(list(set(aliases))),
            description=self._generate_description(canonical_name, category),
            frequency=max(0, int(frequency)),
            demand_score=round(max(0.0, min(100.0, float(demand_score))), 4),
            industry_score=round(max(0.0, min(100.0, float(industry_score))), 4),
            trend=self._parse_trend(trend_val),
            growth=round(float(growth), 4),
            classification=self._parse_classification(classification_val),
            related_technologies=[],
            role_coverage=sorted_roles,
            sources=sorted(list(set([source]))),
            status=TechnologyStatus.ACTIVE,
            first_seen=now_ts,
            last_updated=now_ts,
            version=VersionInfo(created_at=now_ts, updated_at=now_ts),
            metadata=meta,
        )

    @staticmethod
    def _model_or_dict_to_dict(obj: Any) -> Dict[str, Any]:
        """Convert Pydantic model or object to dictionary safely."""
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return {}

    @staticmethod
    def _clean_aliases(aliases: Optional[List[str]]) -> List[str]:
        """Clean and deduplicate aliases case-insensitively."""
        if not aliases:
            return []
        seen = set()
        clean = []
        for a in aliases:
            a_str = str(a).strip()
            a_lower = a_str.lower()
            if a_str and a_lower not in seen:
                seen.add(a_lower)
                clean.append(a_str)
        clean.sort()
        return clean

    @staticmethod
    def _generate_tech_id(canonical_name: str) -> str:
        """Generate a clean slugified technology ID from canonical name."""
        slug = canonical_name.lower().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug or "unknown"

    @staticmethod
    def _generate_description(canonical_name: str, category: str) -> str:
        """Generate a concise description string."""
        return f"{canonical_name} is a {category.lower()} technology used in industry applications."

    @staticmethod
    def _parse_trend(trend: Any) -> TechnologyTrend:
        """Parse a trend value (enum, string, or dict) into TechnologyTrend."""
        if isinstance(trend, TechnologyTrend):
            return trend
        if isinstance(trend, str):
            for t in TechnologyTrend:
                if t.value.lower() == trend.strip().lower() or t.name.lower() == trend.strip().lower():
                    return t
        return TechnologyTrend.STABLE

    @staticmethod
    def _parse_classification(cls_val: Any) -> TechnologyClassification:
        """Parse a classification value into TechnologyClassification."""
        if isinstance(cls_val, TechnologyClassification):
            return cls_val
        if isinstance(cls_val, str):
            for c in TechnologyClassification:
                if c.value.lower() == cls_val.strip().lower() or c.name.lower() == cls_val.strip().lower():
                    return c
        return TechnologyClassification.SUPPORTING
