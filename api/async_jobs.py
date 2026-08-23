"""Ephemeral in-process state for analysis jobs on persistent containers."""

from __future__ import annotations

import secrets
import threading
import time


class AnalysisJobs:
    """Thread-safe job state.  Deliberately local to one container instance."""

    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def start(self) -> str:
        job_id = secrets.token_hex(16)
        with self._lock:
            self._jobs[job_id] = {
                'status': 'processing',
                'percent': 0,
                'stage': 'Archive extracted, starting analysis',
                'log': [],
                'created': time.time(),
            }
        return job_id

    def progress(self, job_id: str, percent: float | None, stage: str | None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job['status'] != 'processing':
                return
            if percent is not None:
                job['percent'] = round(percent, 1)
            if stage:
                job['stage'] = stage
                job['log'].append({'ts': int(time.time() * 1000), 'message': stage})

    def complete(self, job_id: str, result: dict) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.update({'status': 'done', 'percent': 100, 'stage': 'Done', 'result': result})

    def fail(self, job_id: str, message: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.update({'status': 'error', 'stage': 'Failed', 'error': message})

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return {key: value for key, value in job.items() if key != 'created'}
