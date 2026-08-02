"""
Hash Utilities for CurricuAlign AI Academic Engine.
"""

import hashlib
from pathlib import Path
from typing import Union


def compute_bytes_checksum(data: bytes) -> str:
    """Compute SHA-256 checksum for byte content."""
    return hashlib.sha256(data).hexdigest()


def compute_file_checksum(file_path: Union[str, Path]) -> str:
    """Compute SHA-256 checksum for a file on disk."""
    hasher = hashlib.sha256()
    path = Path(file_path)
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()
