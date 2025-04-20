from __future__ import annotations

import logging
import json
from datetime import datetime, timedelta

import requests
from jenkinsapi.jenkins import Jenkins, JenkinsAPIException
from db_utils import execution_utils
from models.execution import Execution
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

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
        try:
            job = self.jenkins_server[job_type]
            queue_item = job.invoke(build_params=parameters)
            logger.info("Jenkins job submitted: %s", queue_item)

            logger.info("Waiting for job to start building...")
            build = queue_item.block_until_building()
            logger.info("Blocking the build")
            build_number = build.get_number()
            logger.info("Build has started: #%s", build_number)
            response_data = {
                "success": True,
                "message": "Job triggered successfully",
                "data": {
                    "job_name": job_type,
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

    def get_test_results_for_build(self, job_type: str, build_number: int):
        job_name = job_type
        try:
            job = self.jenkins_server[job_name]
            build = job.get_build(build_number)

            if build.is_running():
                return {
                    'success': True,
                    'data': {
                        'status': 'RUNNING',
                        'test_cases': []
                    }
                }

            artifacts = build.get_artifact_dict()
            if 'report.json' not in artifacts:
                raise Exception("report.json not found in artifacts")

            report_content = artifacts['report.json'].get_data().decode("utf-8")
            parsed = json.loads(report_content)

            test_cases = []
            for test in parsed.get('tests', []):
                test_cases.append({
                    'name': test.get('nodeid'),
                    'status': test.get('call', {}).get('outcome', 'unknown').upper(),
                    'duration': test.get('call', {}).get('duration', 0.0),
                    'errorDetails': test.get('call', {}).get('crash', {}).get('message')
                })

            return {
                'success': True,
                'data': {
                    'status': build.get_status(),
                    'test_cases': test_cases
                }
            }

        except Exception as e:
            logger.error(f"Failed to fetch test results for build #{build_number} of {job_name}: {e}")
            return {'success': False, 'message': str(e)}

    def get_job_statistics(self, job_type: str, days: int):

        logger.info(f"Calculating stats for job: {job_type} (last {days} days)")

        cutoff = datetime.utcnow() - timedelta(days=days)
        with self.db_session_maker() as session:
            executions = execution_utils.get_executions_by_job_in_time_range(session, job_type, cutoff)

            if not executions:
                return {
                    "success": True,
                    "data": {
                        "totalRuns": 0,
                        "successRate": 0,
                        "avgExecutionTime": None,
                        "executions": []
                    }
                }

            total_runs = len(executions)
            success_count = sum(1 for e in executions if e.status == 'SUCCESS')

            total_time = 0
            time_count = 0
            enriched_executions = []

            for e in executions:
                if e.start_time and e.end_time:
                    duration = (e.end_time - e.start_time).total_seconds()
                    total_time += duration
                    time_count += 1

                test_result = self.get_test_results_for_build(job_type, e.build_number)
                test_cases = test_result.get('data', {}).get('test_cases', []) if test_result.get('success') else []

                passed = sum(1 for t in test_cases if t['status'] == 'PASSED')
                failed = sum(1 for t in test_cases if t['status'] == 'FAILED')

                enriched_executions.append({
                    "id": e.id,
                    "startTime": e.start_time.isoformat(),
                    "status": e.status,
                    "totalTests": len(test_cases),
                    "passed": passed,
                    "failed": failed,
                    "buildNumber": e.build_number,
                    "parameters": e.parameters
                })

            success_rate = (success_count / total_runs) * 100
            avg_execution_time = (total_time / time_count) if time_count > 0 else None

            return {
                "success": True,
                "data": {
                    "totalRuns": total_runs,
                    "successRate": round(success_rate, 2),
                    "avgExecutionTime": round(avg_execution_time, 2) if avg_execution_time else None,
                    "executions": enriched_executions
                }
            }

    def list_jobs_with_parameters(self) -> list[dict]:
        jobs_list = []
        for name, _url in self.jenkins_server.get_jobs():
            job = self.jenkins_server[name]
            config_xml = job.get_config()
            root = ET.fromstring(config_xml)
            param_map: dict[str, str] = {}
            for pd in root.findall(
                    ".//hudson.model.ParametersDefinitionProperty/parameterDefinitions/*"
            ):
                p_name = pd.findtext("name", default="")
                if pd.tag.endswith("StringParameterDefinition"):
                    default = pd.findtext("defaultValue", default="")
                elif pd.tag.endswith("ChoiceParameterDefinition"):
                    choices_el = pd.find("choices")
                    if choices_el is not None and choices_el.findall("string"):
                        default = choices_el.findall("string")[0].text or ""
                    else:
                        default = ""
                else:
                    default = pd.findtext("defaultValue", default="")
                param_map[p_name] = default

            jobs_list.append({
                "name": name,
                "parameters": param_map
            })
        return jobs_list
