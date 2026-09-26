"""
ForensiQ Core Universal File Uploader
High-performance resumable/chunked file upload utility for massive forensic evidence files (50+ GB).
Reusable across all Forensic-Q analytical modules (q_mail, q_bank, q_scan, q_voice, etc.).
"""

import hashlib
from pathlib import Path
from typing import Any

from loguru import logger


class FileUploader:
    """
    Manages streaming assembly of chunked file uploads on disk.
    Computes SHA-256 hash automatically upon completion for evidence chain of custody.
    """

    def __init__(self, storage_dir: Path | str, default_ext: str = ""):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.default_ext = default_ext

    def append_chunk(
        self,
        *,
        upload_id: str,
        chunk_index: int,
        total_chunks: int,
        chunk_data: bytes,
        extension: str | None = None,
    ) -> dict[str, Any]:
        """
        Appends chunk bytes to the target file.
        Returns upload status, progress, and SHA-256 hash when finished.
        """
        ext = extension or self.default_ext
        if ext and not ext.startswith("."):
            ext = f".{ext}"

        target_file = self.storage_dir / f"{upload_id}{ext}"

        # If first chunk and file exists, start clean
        if chunk_index == 0 and target_file.exists():
            target_file.unlink()

        # Append chunk data
        with open(target_file, "ab") as f:
            f.write(chunk_data)

        is_completed = (chunk_index + 1) >= total_chunks
        current_size = target_file.stat().st_size if target_file.exists() else 0
        sha256_hash = ""

        if is_completed:
            # Stream-compute SHA-256 hash
            hasher = hashlib.sha256()
            with open(target_file, "rb") as f:
                while chunk := f.read(1048576):  # 1MB read buffer
                    hasher.update(chunk)
            sha256_hash = hasher.hexdigest()
            logger.info(
                "Completed chunked upload {}: total_size={} bytes, sha256={}",
                upload_id,
                current_size,
                sha256_hash,
            )

        return {
            "upload_id": upload_id,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "current_size_bytes": current_size,
            "is_completed": is_completed,
            "file_path": str(target_file),
            "file_sha256": sha256_hash,
        }
