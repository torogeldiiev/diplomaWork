from sqlalchemy import Column, Integer, String, Float, ForeignKey

from sqlalchemy.orm import relationship
from .base import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer,ForeignKey("executions.id", ondelete="CASCADE"),nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    error_details = Column(String, nullable=True)

    execution = relationship("Execution", back_populates="test_results")

    def as_dict(self):
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "name": self.name,
            "status": self.status,
            "duration": self.duration,
            "error_details": self.error_details
        }