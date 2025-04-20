from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey('clusters.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)

    cluster = relationship("Cluster", back_populates="platforms")

    def as_dict(self):
        return {
            "id": self.id,
            "clusterId": self.cluster_id,
            "name": self.name,
            "version": self.version,
        }
