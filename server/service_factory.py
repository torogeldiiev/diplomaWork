from services.clusters_handler import ClustersHandler
from database_handler import db_session_maker
from services.jenkins_submitter import JenkinsSubmitter
from config import JENKINS_URL, JENKINS_USER, JENKINS_PSWRD


class ServiceFactory:
    def __init__(self):
        self.db_session_maker = db_session_maker
        self.clusters_handler = ClustersHandler(self.db_session_maker)
        self.jenkins_submitter = JenkinsSubmitter(JENKINS_URL, JENKINS_USER, JENKINS_PSWRD, db_session_maker)

    def get_clusters_handler_service(self) -> ClustersHandler:
        return self.clusters_handler

    def get_jenkins_submitter_service(self) -> JenkinsSubmitter:
        return self.jenkins_submitter
