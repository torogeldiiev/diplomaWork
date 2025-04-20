import logging
import requests
from jenkinsapi.jenkins import Jenkins, JenkinsAPIException
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class JenkinsClient:
    def __init__(self, url: str, user: str, token: str):
        self.url = url
        self.user = user
        self.token = token
        try:
            self._jenkins = Jenkins(url, username=user, password=token, lazy=True)
            logger.debug("Connected to Jenkins at %s", url)
        except JenkinsAPIException as e:
            logger.error("Jenkins connection failed: %s", e)
            raise

    def list_jobs(self) -> list[str]:
        return [name for name, _ in self._jenkins.get_jobs()]

    def invoke(self, job_name: str, params: dict[str, str]):
        job = self._jenkins[job_name]
        return job.invoke(build_params=params)

    def get_build(self, job_name: str, build_no: int):
        return self._jenkins[job_name].get_build(build_no)

    def get_job_config_xml(self, job_name: str) -> str:
        return self._jenkins[job_name].get_config()

    def get_json(self, path: str) -> dict:
        resp = requests.get(self.url + path, auth=HTTPBasicAuth(self.user, self.token))
        resp.raise_for_status()
        return resp.json()

    def get_build_info(self, job_name: str, build_no: int) -> dict:
        return self.get_json(f"/job/{job_name}/{build_no}/api/json")

    def get_job_url(self, job_name: str) -> str:
        return str(self._jenkins[job_name].url)

    def get_job_status(self, job_name: str, build_no: int) -> str:
        info = self.get_build_info(job_name, build_no)
        logger.debug("Status %s", info)
        return info.get("result") or "IN_PROGRESS"

    def get_job(self, name: str):
        return self._jenkins[name]
