from sqlalchemy import Column, Integer, String
from .base import Base


class Cluster(Base):
    __tablename__ = 'clusters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    source_version = Column(String, nullable=False)
    target_version = Column(String, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source_version": self.source_version,
            "target_version": self.target_version
        }

    def as_list(self):
        return [
            self.id,
            self.name,
            self.source_version,
            self.target_version
        ]