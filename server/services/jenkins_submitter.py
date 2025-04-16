from __future__ import annotations

import logging
import json

import requests
from jenkinsapi.jenkins import Jenkins, JenkinsAPIException
from config import JENKINS_PROJECT_NAMES
from db_utils import execution_utils
from models.execution import Execution
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class JenkinsSubmitter:
    def __init__(self, jenkins_url: str, user: str, password: str, db_session_maker) -> None:
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
        self.db_session_maker = db_session_maker

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

            logger.info("Waiting for job to start building...")
            build = queue_item.block_until_building()
            logger.info("Blocking the build")
            build_number = build.get_number()
            logger.info("Build has started: #%s", build_number)
            logger.info(f"JOB name: {JENKINS_PROJECT_NAMES.get(job_type)}")
            response_data = {
                "success": True,
                "message": "Job triggered successfully",
                "data": {
                    "job_name": JENKINS_PROJECT_NAMES.get(job_type),
                    "job_url": str(job.url),
                    "queue_number": build_number,
                    "status": "QUEUED"
                }
            }
            logger.debug("Returning response: %s", response_data)
            return response_data
        except Exception as ex:
            logger.error("Unexpected error: %s", ex)
            return {
                "success": False,
                "message": "An unexpected error occurred"
            }

    def create_execution_entry(self, job_type, build_number, parameters):
        with self.db_session_maker() as session:
            return execution_utils.create_execution_entry(session, job_type, build_number, parameters)

    def get_recent_executions(self):
        # returns 10 latest executions
        with self.db_session_maker() as session:
            return execution_utils.get_recent_executions(session)

    def get_job_status(self, job_type, build_number):
        url = f"{self.jenkins_url}/job/{job_type}/{build_number}/api/json"
        logger.info(f"Job name: {job_type}")
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self.user, self.password))
            data = response.json()

            result = data.get("result")

            if result is None:
                status = "IN_PROGRESS"
            else:
                status = result

            return status

        except requests.RequestException as e:
            print(f"Error fetching job status from Jenkins: {e}")
            return "IN_PROGRESS"

    def update_running_execution(self, execution: Execution, new_status: str):
        with self.db_session_maker() as session:
            return execution_utils.update_running_execution(session, execution, new_status)

    def get_job_results(self, job_id: str):
        try:
            job = self.jenkins_server[JENKINS_PROJECT_NAMES["Configdiff"]]
            last_build = job.get_last_build()

            if not last_build:
                return {
                    'success': False,
                    'message': 'No builds found'
                }

            logger.debug(f"Checking build {last_build.buildno} for job {job_id}")

            if last_build.is_running():
                return {
                    'success': True,
                    'data': {
                        'status': 'RUNNING',
                        'test_cases': []
                    }
                }

            try:
                artifacts = last_build.get_artifact_dict()
                if 'report.json' not in artifacts:
                    raise Exception("report.json not found in artifacts")

                report_artifact = artifacts['report.json']
                report_content = report_artifact.get_data().decode("utf-8")
                parsed_report = json.loads(report_content)

                test_cases = []
                for test in parsed_report.get('tests', []):
                    name = test.get('nodeid')
                    status = test.get('call', {}).get('outcome', 'unknown').upper()
                    duration = test.get('call', {}).get('duration', 0.0)
                    error_details = test.get('call', {}).get('crash', {}).get('message')

                    test_cases.append({
                        'name': name,
                        'status': 'PASSED' if status == 'PASSED' else 'FAILED',
                        'duration': duration,
                        'errorDetails': error_details
                    })

                return {
                    'success': True,
                    'data': {
                        'status': last_build.get_status(),
                        'test_cases': test_cases
                    }
                }

            except Exception as e:
                logger.debug(f"Failed to fetch or parse report.json: {e}")
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
