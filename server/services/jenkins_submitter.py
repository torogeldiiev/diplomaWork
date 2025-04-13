from __future__ import annotations

import logging
from jenkinsapi.jenkins import Jenkins, JenkinsAPIException
from config import JENKINS_PROJECT_NAMES
import time

logger = logging.getLogger(__name__)


class JenkinsSubmitter:
    def __init__(self, jenkins_url: str, user: str, password: str) -> None:
        self.jenkins_url = jenkins_url
        self.user = user
        self.password = password
        try:
            self.jenkins_server = Jenkins(
                self.jenkins_url, username=self.user, password=self.password, lazy=True
            )
            logger.debug("Jenkins server connected")
        except JenkinsAPIException as ex:
            logger.error("Failed to connect to Jenkins server %s", ex)
            raise

    def trigger_job(self, job_type: str, parameters: dict[str, str]):
        if job_type not in JENKINS_PROJECT_NAMES:
            logger.error("Invalid job_type: %s. Must be one of: %s", job_type, JENKINS_PROJECT_NAMES.keys())
            return {
                "success": False,
                "message": f"Invalid job type: {job_type}"
            }

        try:
            job = self.jenkins_server[JENKINS_PROJECT_NAMES[job_type]]
            queue_item = job.invoke(build_params=parameters)
            logger.info("Jenkins job submitted: %s", queue_item)
            
            # Add debug logs
            logger.debug("Queue item type: %s", type(queue_item))
            logger.debug("Queue item string representation: %s", str(queue_item))
            
            try:
                queue_number = str(queue_item).split('Queue #')[1]
                logger.debug("Extracted queue number: %s", queue_number)
            except Exception as e:
                logger.error("Failed to extract queue number: %s", e)
                queue_number = "unknown"

            response_data = {
                "success": True,
                "message": "Job triggered successfully",
                "data": {
                    "job_name": JENKINS_PROJECT_NAMES[job_type],
                    "job_url": str(job.url),
                    "queue_number": queue_number,
                    "status": "QUEUED"
                }
            }
            logger.debug("Returning response: %s", response_data)
            return response_data
        except JenkinsAPIException as ex:
            logger.error("Failed to submit Jenkins job %s", ex)
            return {
                "success": False,
                "message": str(ex)
            }
        except Exception as ex:
            logger.error("Unexpected error: %s", ex)
            return {
                "success": False,
                "message": "An unexpected error occurred"
            }

    def get_job_results(self, job_id: str):
        try:
            # Get the job
            job = self.jenkins_server[JENKINS_PROJECT_NAMES["Configdiff"]]
            
            # Get the last build number
            last_build = job.get_last_build()
            if not last_build:
                return {
                    'success': False,
                    'message': 'No builds found'
                }

            logger.debug(f"Checking build {last_build.buildno} for job {job_id}")
            
            # Check if build is running
            if last_build.is_running():
                return {
                    'success': True,
                    'data': {
                        'status': 'RUNNING',
                        'test_cases': []
                    }
                }

            try:
                test_report = last_build.get_resultset()
                test_cases = []
                for suite in test_report:
                    for case in suite.cases:
                        test_cases.append({
                            'name': case.name,
                            'status': 'PASSED' if case.status == 'PASSED' else 'FAILED',
                            'duration': case.duration,
                            'errorDetails': case.errorDetails if hasattr(case, 'errorDetails') else None
                        })

                return {
                    'success': True,
                    'data': {
                        'status': last_build.get_status(),
                        'test_cases': test_cases
                    }
                }
            except Exception as e:
                logger.debug(f"No test results available yet: {e}")
                return {
                    'success': True,
                    'data': {
                        'status': last_build.get_status(),
                        'test_cases': []
                    }
                }
                
        except Exception as ex:
            logger.error("Failed to fetch job results: %s", ex)
            return {
                'success': False,
                'message': str(ex)
            }
