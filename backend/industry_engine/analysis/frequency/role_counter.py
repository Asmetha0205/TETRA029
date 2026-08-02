"""
Role Counter for the CurricuAlign AI Technology Frequency Analysis Engine.

Computes per-role technology distributions: which technologies appear most
frequently across jobs sharing the same title.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger("industry_engine.analysis.frequency.role_counter")


class RoleCounter:
    """
    Accumulates per-role technology counts for distribution analysis.
    """

    def __init__(self) -> None:
        self._role_job_count: Dict[str, int] = defaultdict(int)
        self._role_tech_mentions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._jobs_per_role: Dict[str, set] = defaultdict(set)

    def record(
        self,
        role: str,
        tech_names: List[str],
        job_id: str,
    ) -> None:
        """
        Record an individual job's technologies under a role label.
        """
        if not role or not role.strip():
            return
        role = role.strip()
        self._jobs_per_role[role].add(job_id)
        self._role_job_count[role] = len(self._jobs_per_role[role])
        for tech in tech_names:
            if tech and tech.strip():
                self._role_tech_mentions[role][tech.strip()] = (
                    self._role_tech_mentions[role].get(tech.strip(), 0) + 1
                )

    def process_batch(
        self,
        records: List[Dict],
    ) -> None:
        """
        Process a batch of role records.
        Each record is: { "role": str, "technologies": List[str], "job_id": str }
        """
        for record in records:
            self.record(
                role=record.get("role", ""),
                tech_names=record.get("technologies", []),
                job_id=record.get("job_id", ""),
            )

    def get_top_for_role(
        self,
        role: str,
        top_n: int = 10,
    ) -> List[Dict[str, object]]:
        """
        Return top-N technologies for a single role sorted by percentage.
        """
        total_jobs = max(self._role_job_count.get(role, 1), 1)
        tech_counts = self._role_tech_mentions.get(role, {})
        sorted_techs = sorted(tech_counts.items(), key=lambda kv: kv[1], reverse=True)
        return [
            {
                "technology": tech,
                "percentage": round((count / total_jobs) * 100.0, 2),
            }
            for tech, count in sorted_techs[:top_n]
        ]

    def build_all_roles(self, top_n: int = 10) -> List[Dict[str, object]]:
        """
        Build a full per-role report for all known roles.
        """
        result = []
        for role in sorted(self._role_job_count.keys(), key=lambda r: self._role_job_count[r], reverse=True):
            top_techs = self.get_top_for_role(role, top_n=top_n)
            result.append({
                "role": role,
                "job_count": self._role_job_count[role],
                "top_technologies": top_techs,
            })
        return result

    def get_all_roles(self) -> List[str]:
        return list(self._role_job_count.keys())

    def get_job_count_for_role(self, role: str) -> int:
        return self._role_job_count.get(role, 0)

    def reset(self) -> None:
        self._role_job_count.clear()
        self._role_tech_mentions.clear()
        self._jobs_per_role.clear()

    @property
    def total_roles(self) -> int:
        return len(self._role_job_count)