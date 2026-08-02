"""
File Manager for PDF Upload Module.

Handles saving PDF files to local disk storage, generating document IDs,
computing SHA-256 checksums, and cataloging upload metadata.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.upload.exceptions import DuplicateDocumentError
from backend.academic_engine.upload.metadata import DocumentUploadMetadata
from backend.academic_engine.utils.hash_utils import compute_bytes_checksum

logger = logging.getLogger("academic_engine.upload.file_manager")


class FileManager:
    """
    Manages physical PDF disk storage and metadata catalog tracking.
    """

    def __init__(self, config: Optional[AcademicEngineConfig] = None) -> None:
        self.config = config or AcademicEngineConfig()
        self.upload_dir = Path(self.config.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_path = Path(self.config.document_catalog_path)
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

        self._catalog: Dict[str, DocumentUploadMetadata] = {}
        self._lock = threading.RLock()

        self._load_catalog()

    def save_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> DocumentUploadMetadata:
        """
        Save PDF bytes to disk storage and register metadata in catalog.

        Returns:
            DocumentUploadMetadata model.

        Raises:
            DuplicateDocumentError: If document checksum already exists.
        """
        checksum = compute_bytes_checksum(file_bytes)

        with self._lock:
            # Check for duplicate checksum
            for existing in self._catalog.values():
                if existing.checksum == checksum:
                    logger.warning("[Academic] Duplicate PDF upload detected (checksum='%s').", checksum)
                    raise DuplicateDocumentError(
                        f"Document with checksum '{checksum}' already exists (ID: {existing.document_id})."
                    )

            doc_id = f"doc-{checksum[:12]}"
            sanitized_name = Path(filename).name.replace(" ", "_")
            out_file = self.upload_dir / f"{doc_id}_{sanitized_name}"

            out_file.write_bytes(file_bytes)

            meta = DocumentUploadMetadata(
                document_id=doc_id,
                filename=filename,
                file_size_bytes=len(file_bytes),
                checksum=checksum,
                storage_path=str(out_file.resolve()),
                university_name=university_name,
                curriculum_year=curriculum_year,
                department=department,
            )

            self._catalog[doc_id] = meta
            self._save_catalog()

            logger.info("[Academic] PDF Uploaded: '%s' saved as %s (%d bytes).", filename, doc_id, len(file_bytes))
            return meta

    def get_metadata(self, document_id: str) -> Optional[DocumentUploadMetadata]:
        with self._lock:
            return self._catalog.get(document_id)

    def list_documents(self) -> List[DocumentUploadMetadata]:
        with self._lock:
            return list(self._catalog.values())

    def update_status(self, document_id: str, new_status: str) -> None:
        with self._lock:
            if document_id in self._catalog:
                self._catalog[document_id].status = new_status
                self._save_catalog()

    def _load_catalog(self) -> None:
        with self._lock:
            if self.catalog_path.exists():
                try:
                    data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
                    for doc_id, d in data.items():
                        self._catalog[doc_id] = DocumentUploadMetadata.model_validate(d)
                except Exception as exc:
                    logger.warning("[Academic] Failed to load document catalog: %s", exc)

    def _save_catalog(self) -> None:
        with self._lock:
            try:
                data = {doc_id: meta.model_dump() for doc_id, meta in self._catalog.items()}
                self.catalog_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception as exc:
                logger.error("[Academic] Failed to save document catalog: %s", exc)
