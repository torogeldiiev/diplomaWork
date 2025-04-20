import logging
import json
from datetime import datetime, timedelta
from db_utils import execution_utils
import xml.etree.ElementTree as ET
from jenkins_client import JenkinsClient

logger = logging.getLogger(__name__)


class JenkinsChecker:
    def __init__(self, client: JenkinsClient, db_session_maker):
        self.client = client
        self.db_session_maker = db_session_maker

    def get_recent_executions(self):
        with self.db_session_maker() as session:
            return execution_utils.get_recent_executions(session)

    def get_test_results_for_build(self, job_name: str, build_number: int):
        try:
            job = self.client.get_job(job_name)
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

    def get_job_statistics(self, job_name: str, days: int) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self.db_session_maker() as session:
            executions = execution_utils.get_executions_by_job_in_time_range(session, job_name, cutoff)

        if not executions:
            return {"success": True,
                    "data": {"totalRuns": 0, "successRate": 0, "avgExecutionTime": None, "executions": []}}

        total = len(executions)
        success_count = sum(1 for e in executions if e.status == "SUCCESS")

        total_time = 0.0
        enriched = []

        for e in executions:
            if e.start_time and e.end_time:
                total_time += (e.end_time - e.start_time).total_seconds()

            tr = self.get_test_results_for_build(e.job_name, e.build_number)
            cases = tr.get("data", {}).get("test_cases", [])
            passed = sum(1 for c in cases if c["status"] == "PASSED")
            failed = len(cases) - passed

            enriched.append({
                "id": e.id,
                "startTime": e.start_time.isoformat(),
                "status": e.status,
                "totalTests": len(cases),
                "passed": passed,
                "failed": failed,
                "buildNumber": e.build_number,
                "parameters": e.parameters
            })

        avg_exec = (total_time / total) if total > 0 else None
        return {
            "success": True,
            "data": {
                "totalRuns": total,
                "successRate": round(success_count / total * 100, 2),
                "avgExecutionTime": round(avg_exec, 2) if avg_exec is not None else None,
                "executions": enriched
            }
        }

    def list_jobs_with_parameters(self) -> list[dict]:
        out = []
        for name in self.client.list_jobs():
            xml = self.client.get_job_config_xml(name)
            root = ET.fromstring(xml)
            params = {}
            for pd in root.findall(
                    ".//hudson.model.ParametersDefinitionProperty/parameterDefinitions/*"
            ):
                pname = pd.findtext("name", "")
                if pd.tag.endswith("StringParameterDefinition"):
                    pval = pd.findtext("defaultValue", "")
                elif pd.tag.endswith("ChoiceParameterDefinition"):
                    choices = pd.find("choices")
                    pval = choices.findall("string")[0].text if choices is not None else ""
                else:
                    pval = pd.findtext("defaultValue", "")
                params[pname] = pval
            out.append({"name": name, "parameters": params})
        return out
