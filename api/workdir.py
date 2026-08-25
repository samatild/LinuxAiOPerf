"""Safe, process-wide working-directory changes for upload processors."""

from __future__ import annotations

from contextlib import contextmanager
import os
import threading
from collections.abc import Iterator


_CWD_LOCK = threading.RLock()


@contextmanager
def working_directory(path: str, *, restore_to: str) -> Iterator[None]:
    """Run a block in ``path`` and always restore a known, existing directory.

    ``os.chdir`` is process-global, so the lock prevents parallel HTTP requests
    from observing each other's temporary upload directory.  ``restore_to`` is
    explicit rather than derived with ``os.getcwd()`` because a failed upload
    may have already deleted the current directory.
    """
    with _CWD_LOCK:
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(restore_to)
