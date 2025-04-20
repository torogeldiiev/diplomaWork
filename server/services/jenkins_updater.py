import logging
from scheduler import AbstractJob
from db_utils import execution_utils
from notification import send_notification

logger = logging.getLogger(__name__)


class JenkinsUpdater(AbstractJob):
    def __init__(self, client, db_session_maker, job_name, build_number):
        self.client = client
        self.db_session_maker = db_session_maker
        self.job_name = job_name
        self.build_number = build_number

    def notify_job_completion(self, job_name: str, build_number: int, status: str) -> None:
        """
        Send a Gmail notification that the given Jenkins job build has completed.
        """
        subject = f"Jenkins Job {job_name} #{build_number} is {status}"
        body = (
            f"Your Jenkins job **{job_name}** (build #{build_number}) "
            f"has completed with status **{status}**.\n\n"
            "Head over to the dashboard to view full details."
        )

        try:
            send_notification(subject, body)
            logger.info("Sent notification email for %s#%s", job_name, build_number)
        except Exception as e:
            logger.error("Failed to send notification for %s#%s: %s", job_name, build_number, e)

    def execute(self) -> None:
        status = self.client.get_job_status(self.job_name, self.build_number)
        logger.info(f"Jenkins updater status: {status}")

        if status != "IN_PROGRESS":
            logger.info("Build %s#%s finished → %s", self.job_name, self.build_number, status)
            with self.db_session_maker() as session:
                execution = execution_utils.get_execution_by_build_number(session, self.build_number)
                execution_utils.update_running_execution(session, execution, status)
                self.notify_job_completion(self.job_name, self.build_number, status)
        else:
            logger.debug("Build %s#%s still IN_PROGRESS", self.job_name, self.build_no)


