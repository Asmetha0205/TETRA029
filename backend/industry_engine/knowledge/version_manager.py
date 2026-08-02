"""
Version Manager for the CurricuAlign AI Industry Knowledge Layer.

Manages semantic versioning for technology knowledge records.
Tracks version history, supports increment operations, and
validates version format consistency across the knowledge layer.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from backend.industry_engine.knowledge.exceptions import InvalidVersionFormat, VersionError
from backend.industry_engine.knowledge.knowledge_models import VersionInfo

logger = logging.getLogger("industry_engine.knowledge.version_manager")


class VersionManager:
    """
    Manages semantic versioning for technology knowledge records.

    Each technology has a VersionInfo that tracks its major.minor.patch version,
    creation/update timestamps, and optional snapshot association.
    """

    def __init__(self) -> None:
        """Initialize the version manager with empty state."""
        self._versions: Dict[str, VersionInfo] = {}
        self._content_hashes: Dict[str, str] = {}
        logger.info("[Version] Version Manager initialized.")

    def get_version(self, technology_id: str) -> VersionInfo:
        """
        Get the current version for a technology.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            The current VersionInfo, or a default v1.0.0 if not tracked.

        Raises:
            VersionError: If the stored version data is corrupted.
        """
        if technology_id not in self._versions:
            logger.debug("[Version] No version found for '%s', returning default v1.0.0.", technology_id)
            return VersionInfo()
        version = self._versions[technology_id]
        logger.debug("[Version] Version for '%s': %s.", technology_id, version.to_string())
        return version

    def increment(self, technology_id: str, bump: str = "patch") -> VersionInfo:
        """
        Increment the version for a technology and return the new version.

        Args:
            technology_id: The unique technology identifier.
            bump: One of 'major', 'minor', or 'patch'.

        Returns:
            The new VersionInfo after increment.

        Raises:
            VersionError: If bump is not a valid increment type.
        """
        current = self.get_version(technology_id)
        if bump == "major":
            new_version = current.increment_major()
        elif bump == "minor":
            new_version = current.increment_minor()
        elif bump == "patch":
            new_version = current.increment_patch()
        else:
            raise VersionError(f"Invalid bump type '{bump}'. Must be 'major', 'minor', or 'patch'.")

        self._versions[technology_id] = new_version
        logger.info(
            "[Version] Updated %s: %s -> %s.",
            technology_id,
            current.to_string(),
            new_version.to_string(),
        )
        return new_version

    def set_version(self, technology_id: str, version: VersionInfo) -> None:
        """
        Explicitly set the version for a technology.

        Args:
            technology_id: The unique technology identifier.
            version: The VersionInfo to assign.
        """
        self._versions[technology_id] = version
        logger.debug("[Version] Set %s to %s.", technology_id, version.to_string())

    def set_version_from_string(self, technology_id: str, version_str: str) -> None:
        """
        Set the version from a semver string.

        Args:
            technology_id: The unique technology identifier.
            version_str: Version string in 'X.Y.Z' format.

        Raises:
            InvalidVersionFormat: If the version string is not valid semver.
        """
        try:
            version = VersionInfo.from_string(version_str)
        except ValueError as exc:
            raise InvalidVersionFormat(str(exc)) from exc
        self.set_version(technology_id, version)

    def has_changed(self, technology_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Check whether the data for a technology has changed since last check.

        Computes a SHA-256 hash of the serialized data and compares it with
        the stored hash. Returns True if data is different or unknown.

        Args:
            technology_id: The unique technology identifier.
            new_data: The data dictionary to compare.

        Returns:
            True if the data has changed or is unknown, False otherwise.
        """
        data_hash = self._compute_hash(new_data)
        stored_hash = self._content_hashes.get(technology_id)
        if stored_hash is None:
            logger.debug("[Version] No previous hash for '%s', treating as changed.", technology_id)
            return True
        changed = data_hash != stored_hash
        if changed:
            logger.debug("[Version] Data changed for '%s'.", technology_id)
        return changed

    def record_hash(self, technology_id: str, data: Dict[str, Any]) -> None:
        """
        Store the content hash for a technology's current data.

        Args:
            technology_id: The unique technology identifier.
            data: The data dictionary to hash.
        """
        self._content_hashes[technology_id] = self._compute_hash(data)

    def get_all_versions(self) -> Dict[str, str]:
        """
        Get all tracked versions as a dictionary of technology_id -> version string.

        Returns:
            Dictionary mapping technology IDs to their version strings.
        """
        return {tid: v.to_string() for tid, v in self._versions.items()}

    def remove(self, technology_id: str) -> bool:
        """
        Remove version tracking for a technology.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            True if the version was tracked and removed, False if not found.
        """
        removed_version = self._versions.pop(technology_id, None)
        self._content_hashes.pop(technology_id, None)
        if removed_version:
            logger.debug("[Version] Removed version tracking for '%s'.", technology_id)
            return True
        return False

    def count(self) -> int:
        """Return the number of technologies with tracked versions."""
        return len(self._versions)

    def set_snapshot_version(self, technology_id: str, snapshot_number: int) -> None:
        """
        Record which snapshot number a technology version belongs to.

        Args:
            technology_id: The unique technology identifier.
            snapshot_number: The snapshot number.
        """
        version = self.get_version(technology_id)
        version.snapshot_version = snapshot_number
        self._versions[technology_id] = version

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the version manager state to a dictionary.

        Returns:
            Dictionary with 'versions' and 'content_hashes' keys.
        """
        return {
            "versions": {
                tid: v.to_string() for tid, v in self._versions.items()
            },
            "content_hashes": dict(self._content_hashes),
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load version manager state from a dictionary.

        Args:
            data: Dictionary with 'versions' and 'content_hashes' keys.
        """
        self._versions.clear()
        self._content_hashes.clear()

        versions_data = data.get("versions", {})
        for tid, version_str in versions_data.items():
            try:
                self._versions[tid] = VersionInfo.from_string(version_str)
            except ValueError:
                logger.warning("[Version] Skipping invalid version '%s' for '%s'.", version_str, tid)

        self._content_hashes.update(data.get("content_hashes", {}))
        logger.info("[Version] Loaded %d version records.", len(self._versions))

    @staticmethod
    def _compute_hash(data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of serialized data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
