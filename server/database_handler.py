"""
Handles Creation of a connection with the database.
Making sure connection is created only once and can be imported to needed modules
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import logging

from config import DATABASE_URL
from models.base import Base

logger = logging.getLogger(__name__)


db_engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
logger.info("Database engine created")
db_session_maker = sessionmaker(bind=db_engine)
logger.info("database session maker created")

meta = MetaData()
meta.reflect(bind=db_engine)
Base.metadata.create_all(db_engine)
