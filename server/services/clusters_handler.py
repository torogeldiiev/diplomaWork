from __future__ import annotations

import logging

from db_utils import cluster_utils
from models.cluster import Cluster
logger = logging.getLogger(__name__)


class ClustersHandler:
    def __init__(self, db_session_maker):
        self.db_session_maker = db_session_maker

    def add_cluster(self, cluster: Cluster):
        with self.db_session_maker() as session:
            return cluster_utils.add_cluster(session, cluster)

    def delete_cluster(self, cluster_id: int) :
        with self.db_session_maker() as session:
            return cluster_utils.delete_cluster(session, cluster_id)

    def get_cluster_by_id(self, cluster_id: int):
        with self.db_session_maker() as session:
            return cluster_utils.get_cluster_by_id(session, cluster_id)

    def update_cluster(self, cluster: Cluster, cluster_id: int):
        with self.db_session_maker() as session:
            return cluster_utils.update_cluster_by_id(session, cluster, cluster_id)

    def get_all_clusters(self):
        with self.db_session_maker() as session:
            return cluster_utils.get_all_clusters(session)
