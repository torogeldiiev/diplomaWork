from __future__ import annotations

import logging
from jenkinsapi.jenkins import Jenkins, JenkinsAPIException
from config import JENKINS_PROJECT_NAMES

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

        job = self.jenkins_server[JENKINS_PROJECT_NAMES[job_type]]
        try:
            queue_item = job.invoke(build_params=parameters)
            logger.info("Jenkins job submitted: %s", queue_item)
            # queue_item_data = {
            #     'id': queue_item.id,
            #     'url': queue_item.url,
            #     'status': queue_item.status,
            # }
            return "success"
        except JenkinsAPIException as ex:
            logger.error("Failed to submit Jenkins job %s", ex)
            return None
