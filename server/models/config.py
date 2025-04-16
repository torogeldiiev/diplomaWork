from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey('clusters.id', ondelete="CASCADE"), nullable=False)
    config_type = Column(String, nullable=False)
    config_value = Column(String, nullable=False)

    cluster = relationship("Cluster", back_populates="configs")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.cluster_id,
            "config_name": self.config_type,
            "config_value": self.config_value
        }
