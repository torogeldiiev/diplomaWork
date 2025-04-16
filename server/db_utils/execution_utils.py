from __future__ import annotations

import logging
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
