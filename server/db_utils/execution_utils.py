from __future__ import annotations

import logging
from typing import List, Optional

import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session
from datetime import datetime

from models.execution import Execution

logger = logging.getLogger(__name__)

def create_execution_entry(db_session: Session, job_name: str, build_number: str, parameters: dict) -> Execution:
    execution = Execution(
        job_name=job_name,
        status="IN_PROGRESS",
        build_number=build_number,
        start_time=datetime.utcnow(),
        parameters=parameters
    )
    db_session.add(execution)
    db_session.commit()
    logger.info(f"Created execution entry for job {job_name} with build number {build_number}")
    return execution


def get_recent_executions(db_session: Session) -> list[Execution]:
    executions = db_session.query(Execution).order_by(Execution.start_time.desc()).limit(10).all()
    return [e.as_dict() for e in executions]


def update_running_execution(db_session: Session, execution: Execution, new_status: str) -> Execution:
    """Updates the status of a running execution."""
    execution = db_session.merge(execution)
    logger.info("Updating execution status from %s to %s", execution.status, new_status)

    if new_status != 'IN_PROGRESS':
        execution.status = new_status
        db_session.commit()
        logger.info("Execution %s updated to status: %s", execution.id, new_status)
    else:
        logger.info("No update needed for execution %s; status is already %s", execution.id, execution.status)
    return execution


def get_execution_by_build_number(db_session: Session, build_number: int):
    return db_session.query(Execution).filter(Execution.build_number == build_number).first()


def get_executions_by_job_in_time_range(session: Session, job_name: str, cutoff_date: datetime) -> List[Execution]:
    """
    Retrieves executions for a specific job name that started on or after the given cutoff datetime.
    """
    return (
        session.query(Execution)
        .filter(
            Execution.job_name == job_name,
            Execution.start_time >= cutoff_date
        )
        .order_by(Execution.start_time.desc())
        .all()
    )
