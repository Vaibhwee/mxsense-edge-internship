"""Compatibility shim for the legacy top-level app path.

The active Django app lives in ``apps.data_ingestion``. These re-exports keep old
imports and open editor tabs from drifting away from the actual implementation.
"""

from apps.data_ingestion.models import *  # noqa: F401,F403
