import os
import tarfile
import zipfile
from pathlib import Path
from typing import List, Tuple
from app.errors.exceptions import ArchiveExtractionError, SecurityViolationError
from app.security.path_sanitizer import PathSanitizer


class ArchiveValidator:
    """Validates project archive structure, protects against Zip Slip attacks, and safely extracts files."""

    MAX_RATIO = 100  # Max uncompressed to compressed ratio
    DANGEROUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".vbs", ".scr", ".msi", ".dll", ".so", ".dylib", ".pif"}

    @classmethod
    def is_safe_zip_entry(cls, zip_entry: zipfile.ZipInfo, destination_dir: Path) -> Tuple[bool, str]:
        """Verify zip entry does not perform path traversal or target restricted paths."""
        filename = zip_entry.filename
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            return False, f"Zip Slip detected in archive entry: {filename}"

        # Test resolved destination
        dest_path = (destination_dir / filename).resolve()
        try:
            dest_path.relative_to(destination_dir.resolve())
        except ValueError:
            return False, f"Archive entry escapes destination: {filename}"

        return True, "Safe"

    @classmethod
    def extract_zip(cls, zip_path: Path, destination_dir: Path, max_files: int = 15000, max_bytes: int = 250 * 1024 * 1024) -> List[str]:
        """Safely extract zip archive with strict bounds checking."""
        extracted_files: List[str] = []
        total_extracted_size = 0

        destination_dir.mkdir(parents=True, exist_ok=True)
        dest_resolved = destination_dir.resolve()

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                infolist = zf.infolist()
                if len(infolist) > max_files:
                    raise SecurityViolationError(f"Archive exceeds maximum file count ({len(infolist)} > {max_files})")

                for member in infolist:
                    safe, reason = cls.is_safe_zip_entry(member, dest_resolved)
                    if not safe:
                        raise SecurityViolationError(reason)

                    total_extracted_size += member.file_size
                    if total_extracted_size > max_bytes:
                        raise SecurityViolationError(f"Archive extracted size exceeds allowed quota of {max_bytes // (1024*1024)} MB")

                    if member.is_dir():
                        target_dir = dest_resolved / member.filename
                        target_dir.mkdir(parents=True, exist_ok=True)
                        continue

                    # Extract file
                    target_file = dest_resolved / member.filename
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as source, open(target_file, "wb") as target:
                        while chunk := source.read(65536):
                            target.write(chunk)

                    extracted_files.append(str(member.filename))

            return extracted_files
        except SecurityViolationError:
            raise
        except Exception as err:
            raise ArchiveExtractionError(f"Failed to extract zip archive: {str(err)}")

    @classmethod
    def extract_tar(cls, tar_path: Path, destination_dir: Path, max_files: int = 15000, max_bytes: int = 250 * 1024 * 1024) -> List[str]:
        """Safely extract tar / tar.gz archive with strict path checking."""
        extracted_files: List[str] = []
        total_size = 0
        destination_dir.mkdir(parents=True, exist_ok=True)
        dest_resolved = destination_dir.resolve()

        try:
            with tarfile.open(tar_path, "r:*") as tf:
                members = tf.getmembers()
                if len(members) > max_files:
                    raise SecurityViolationError(f"Tar archive exceeds max file limit ({len(members)} > {max_files})")

                for member in members:
                    if ".." in member.name or member.name.startswith("/") or member.name.startswith("\\"):
                        raise SecurityViolationError(f"Tar Slip detected: {member.name}")

                    target_path = (dest_resolved / member.name).resolve()
                    try:
                        target_path.relative_to(dest_resolved)
                    except ValueError:
                        raise SecurityViolationError(f"Tar member escapes destination: {member.name}")

                    if member.issym() or member.islnk():
                        # Disallow symlinks to prevent symlink traversal attacks
                        continue

                    total_size += member.size
                    if total_size > max_bytes:
                        raise SecurityViolationError("Extracted size exceeds allowed storage quota.")

                    tf.extract(member, path=str(dest_resolved), filter="data" if hasattr(tarfile, "data_filter") else None)
                    if member.isfile():
                        extracted_files.append(member.name)

            return extracted_files
        except SecurityViolationError:
            raise
        except Exception as err:
            raise ArchiveExtractionError(f"Failed to extract tar archive: {str(err)}")
