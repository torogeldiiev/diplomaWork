from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Cluster(Base):
    __tablename__ = 'clusters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    release_version = Column(String, nullable=False)

    configs = relationship("Config", back_populates="cluster", cascade="all, delete-orphan")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "release_version": self.release_version,
        }

    def as_list(self):
        return [
            self.id,
            self.name,
            self.release_version,
        ]
