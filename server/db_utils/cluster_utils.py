from __future__ import annotations

from typing import Any, Dict
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.cluster import Cluster

logger = logging.getLogger(__name__)


def add_cluster(db_session: Session, cluster: Cluster) -> dict[str, Any] or None:
    try:
        db_session.add(cluster)
        db_session.commit()
        return cluster.as_dict()
    except SQLAlchemyError as ex:
        logger.error("Unexpected error occurred while adding product %s: %s", cluster, ex)
        return None


def get_cluster_by_id(db_session: Session, cluster_id: int) -> dict[str, Any] or None:
    try:
        cluster = db_session.query(Cluster).filter(Cluster.id == cluster_id).first()
        return cluster.as_dict()
    except SQLAlchemyError as ex:
        logger.error("Unexpected error occurred while getting product %s: %s", cluster_id, ex)


def delete_cluster(db_session: Session, cluster_id: int) -> dict[str, Any] or None:
    try:
        cluster = db_session.query(Cluster).filter(Cluster.id == cluster_id).first()
        db_session.delete(cluster)
        db_session.commit()
        return {"message": "Cluster deleted"}, 200
    except SQLAlchemyError as ex:
        logger.error("Unexpected error occurred while deleting the product %s: %s", cluster_id, ex)
        return {"message": "Cluster not found"}, 404


def update_cluster_by_id(db_session: Session, data: dict[str, Any], cluster_id: int) -> dict[str, Any] | None:
    try:
        cluster = db_session.query(Cluster).filter(Cluster.id == f"{cluster_id}").first()

        for key, value in data.items():
            if hasattr(cluster, key):
                setattr(cluster, key, value)

        db_session.commit()
        return cluster.as_dict()
    except SQLAlchemyError as ex:
        logger.error("Unexpected error occurred while updating product %s: %s", cluster_id, ex)
        return None
