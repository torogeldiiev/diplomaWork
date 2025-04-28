from __future__ import annotations

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

    def _fetch_jenkins_report_json(self, job_name: str, build_number: int) -> str | None:
        job = self.client.get_job(job_name)
        build = job.get_build(build_number)

        if build.is_running():
            return None

        artifacts = build.get_artifact_dict()
        if "report.json" not in artifacts:
            logger.error("report.json not found for %s#%s", job_name, build_number)
            return None

        return artifacts["report.json"].get_data().decode("utf-8")

    def _parse_report(self, report_content: str) -> list[dict]:
        parsed = json.loads(report_content)
        cases = []
        for test in parsed.get("tests", []):
            call = test.get("call", {})
            cases.append({
                "name": test.get("nodeid"),
                "status": call.get("outcome", "unknown").upper(),
                "duration": float(call.get("duration", 0.0)),
                "errorDetails": call.get("crash", {}).get("message")
            })
        return cases

    def store_tests_results(self, job_name: str, build_number: int):
        raw = self._fetch_jenkins_report_json(job_name, build_number)
        if raw is None:
            return {
                "success": False,
                "message": "No report.json found (or build still running)"
            }
        cases = self._parse_report(raw)
        with self.db_session_maker() as session:
            execution = execution_utils.get_execution_by_build_number(session, build_number)
            return execution_utils.store_test_results(session,execution.id, cases)

    def get_stored_test_results(self, build_number: int):
        with self.db_session_maker() as session:
            return execution_utils.get_test_results_for_execution(session, build_number)

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

            tr = self.get_stored_test_results(e.build_number)
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
            params: dict[str, str] = {}

            for pd in root.findall(
                    ".//hudson.model.ParametersDefinitionProperty/parameterDefinitions/*"
            ):
                pname = pd.findtext("name", "")
                if pd.tag.endswith("StringParameterDefinition"):
                    pval = pd.findtext("defaultValue", "")
                elif pd.tag.endswith("ChoiceParameterDefinition"):
                    choices = pd.find("choices")
                    if choices is not None:
                        opts = choices.findall("string")
                        pval = opts[0].text or "" if opts else ""
                    else:
                        pval = ""
                else:
                    pval = pd.findtext("defaultValue", "")

                params[pname] = pval

            out.append({"name": name, "parameters": params})

        return out

