"""Backward-compatible wrapper for the feature extractor.

Some parts of the project import `extract_features` from the repository root
(`from extract_features import extract_features`). The real implementation lives
in `ml/extract_features.py`. This file re-exports the function so legacy
imports continue to work without changing caller code.
"""
from ml.extract_features import extract_features

__all__ = ["extract_features"]
