from sqlalchemy import Column, Integer, String
from .base import Base


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, nullable=False)
    config_name = Column(String, nullable=False)
    config_value = Column(String, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.cluster_id,
            "source_version": self.config_name,
            "target_version": self.config_value
        }

    def as_list(self):
        return [
            self.id,
            self.cluster_id,
            self.config_name,
            self.config_value
        ]