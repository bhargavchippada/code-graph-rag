import os
from pathlib import Path

from .. import constants as cs


def should_skip_path(
    path: Path,
    repo_path: Path,
    exclude_paths: frozenset[str] | None = None,
    unignore_paths: frozenset[str] | None = None,
) -> bool:
    # (H) Skip GNU sed temporary files (e.g. sedYUwglZ) from accidental indexing.
    if (
        path.is_file()
        and not path.suffix
        and path.name.startswith("sed")
        and len(path.name) == 8
        and path.name[3:].isalnum()
    ):
        return True

    # (H) Skip files with ignored suffixes (temp files, compiled)
    if path.is_file() and path.suffix in cs.IGNORE_SUFFIXES:
        return True

    # (H) Skip files with ignored extensions (non-code files)
    if path.is_file() and path.suffix.lower() in cs.IGNORE_EXTENSIONS:
        return True

    # (H) Skip files larger than MAX_FILE_SIZE_BYTES
    if path.is_file():
        try:
            if path.stat().st_size > cs.MAX_FILE_SIZE_BYTES:
                return True
        except OSError:
            pass  # File might not exist or be inaccessible

    # (H) Skip files with numeric/timestamp extensions (temp files like .1772368411198)
    if path.is_file() and path.suffix:
        # Remove leading dot and check if remainder is all digits
        suffix_without_dot = path.suffix[1:]
        if suffix_without_dot.isdigit():
            return True

    rel_path = path.relative_to(repo_path)
    rel_path_str = rel_path.as_posix()
    dir_parts = rel_path.parent.parts if path.is_file() else rel_path.parts

    # (H) Skip files whose filename itself is in IGNORE_PATTERNS (e.g. ".coverage")
    if path.is_file() and path.name in cs.IGNORE_PATTERNS:
        return True

    # (H) Skip paths matching explicit exclude_paths
    if exclude_paths and (
        not exclude_paths.isdisjoint(dir_parts)
        or rel_path_str in exclude_paths
        or any(rel_path_str.startswith(f"{p}/") for p in exclude_paths)
    ):
        return True

    # (H) Allow paths matching unignore_paths (override ignore patterns)
    if unignore_paths and any(
        rel_path_str == p or rel_path_str.startswith(f"{p}/") for p in unignore_paths
    ):
        return False

    # (H) Skip paths containing any IGNORE_PATTERNS directory
    return not cs.IGNORE_PATTERNS.isdisjoint(dir_parts)
