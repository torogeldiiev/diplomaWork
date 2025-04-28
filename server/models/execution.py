from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Execution(Base):
    __tablename__ = 'executions'

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default='IN_PROGRESS')
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    build_number = Column(Integer, nullable=True)
    parameters = Column(JSON, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "jobName": self.job_name,
            "status": self.status,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "buildNumber": self.build_number,
            "parameters": self.parameters
        }

    test_results = relationship("TestResult",back_populates="execution",cascade="all, delete-orphan")