import logging
from db_utils import execution_utils
from jenkins_client import JenkinsClient

logger = logging.getLogger(__name__)


class JenkinsSubmitter:
    def __init__(self, client: JenkinsClient, db_session_maker):
        self.client = client
        self.db_session_maker = db_session_maker

    def trigger_job(self, job_name: str, parameters: dict[str, str]) -> dict:
        try:
            queue_item = self.client.invoke(job_name, parameters)
            logger.info("Job %s queued: %s", job_name, queue_item)

            build = queue_item.block_until_building()
            build_no = build.get_number()
            logger.info("Job %s started build #%s", job_name, build_no)

            return {
                "success": True,
                "message": "Job triggered successfully",
                "data": {
                    "job_name": job_name,
                    "job_url": self.client.get_job_url(job_name),
                    "queue_number": build_no,
                    "status": "QUEUED"
                }
            }
        except Exception as e:
            logger.error("Trigger failed for %s: %s", job_name, e, exc_info=True)
            return {"success": False, "message": "An unexpected error occurred"}

    def create_execution_entry(self, job_type, build_number, parameters):
        with self.db_session_maker() as session:
            return execution_utils.create_execution_entry(session, job_type, build_number, parameters)
