"""Tests for in-container analysis job state used by Azure mode."""

import unittest

from api.async_jobs import AnalysisJobs


class AnalysisJobsTests(unittest.TestCase):
    def test_progress_and_result_are_available_after_a_job_is_started(self):
        jobs = AnalysisJobs()
        job_id = jobs.start()

        jobs.progress(job_id, 42.5, 'Processing CPU')
        jobs.complete(job_id, {'report_id': job_id})

        state = jobs.get(job_id)
        self.assertEqual(state['status'], 'done')
        self.assertEqual(state['percent'], 100)
        self.assertEqual(state['stage'], 'Done')
        self.assertEqual(state['result'], {'report_id': job_id})
        self.assertEqual(state['log'][-1]['message'], 'Processing CPU')

    def test_unknown_job_is_not_reported_as_running(self):
        self.assertIsNone(AnalysisJobs().get('missing'))


if __name__ == '__main__':
    unittest.main()
