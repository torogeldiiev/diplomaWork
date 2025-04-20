from services.clusters_handler import ClustersHandler
from database_handler import db_session_maker
from services.jenkins_submitter import JenkinsSubmitter
from services.jenkins_checker import JenkinsChecker
from services.jenkins_updater import JenkinsUpdater
from config import JENKINS_URL, JENKINS_USER, JENKINS_PSWRD
from jenkins_client import JenkinsClient
from models.execution import Execution


class ServiceFactory:
    def __init__(self):
        self.db_session_maker = db_session_maker
        self.jenkins_client = JenkinsClient(JENKINS_URL, JENKINS_USER, JENKINS_PSWRD)
        self.clusters_handler = ClustersHandler(self.db_session_maker)
        self.jenkins_submitter = JenkinsSubmitter(self.jenkins_client, self.db_session_maker)
        self.jenkins_checker = JenkinsChecker(self.jenkins_client, self.db_session_maker)

    def get_clusters_handler_service(self) -> ClustersHandler:
        return self.clusters_handler

    def get_jenkins_submitter_service(self) -> JenkinsSubmitter:
        return self.jenkins_submitter

    def get_jenkins_checker_service(self) -> JenkinsChecker:
        return self.jenkins_checker

    def get_jenkins_updater(self, job_name, build_number) -> JenkinsUpdater:
        return JenkinsUpdater(self.jenkins_client, self.db_session_maker, job_name, build_number)

