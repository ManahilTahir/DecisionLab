"""Data upload service — handles CSV/Excel ingestion and validation."""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@dataclass
class UploadResult:
    success: bool
    df: pd.DataFrame | None = None
    file_name: str = ""
    error: str = ""
    warnings: list[str] = field(default_factory=list)


def validate_file(name: str, size_bytes: int, max_size_mb: int = 50) -> str | None:
    ext = Path(name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return f"Unsupported file type '{ext}'. Please upload a CSV or Excel file."
    if size_bytes > max_size_mb * 1024 * 1024:
        return f"File exceeds the {max_size_mb} MB size limit."
    return None


def load_file(uploaded_file, max_size_mb: int = 50) -> UploadResult:
    name = getattr(uploaded_file, "name", "uploaded")
    size = getattr(uploaded_file, "size", 0)
    err = validate_file(name, size, max_size_mb)
    if err:
        return UploadResult(False, error=err)

    ext = Path(name).suffix.lower()
    warnings: list[str] = []

    try:
        if ext == ".csv":
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except pd.errors.EmptyDataError:
        return UploadResult(False, file_name=name, error="The file is empty.")
    except Exception as exc:
        return UploadResult(False, file_name=name, error=f"Could not read file: {exc}")

    if df.empty:
        return UploadResult(False, file_name=name, error="The file contains no rows.")

    if df.shape[1] == 1 and df.columns[0].startswith("Unnamed"):
        warnings.append("Only one unnamed column was detected — the file may be misformatted.")

    df.columns = [str(c).strip() for c in df.columns]
    duplicate_cols = df.columns[df.columns.duplicated()].tolist()
    if duplicate_cols:
        warnings.append(f"Duplicate column names found: {', '.join(duplicate_cols)}.")

    return UploadResult(True, df=df, file_name=name, warnings=warnings)


def load_sample(sample_name: str, data_dir: Path) -> UploadResult:
    path = data_dir / sample_name
    if not path.exists():
        return UploadResult(False, error=f"Sample file not found: {sample_name}")
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
    except Exception as exc:
        return UploadResult(False, error=f"Could not read sample file: {exc}")
    return UploadResult(True, df=df, file_name=sample_name)