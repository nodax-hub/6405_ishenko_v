import datetime

from sqlalchemy import (
    create_engine, Column, Integer, Float, DateTime, String, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker

from data_analysis.models import DataPoint

engine = create_engine('sqlite:///data.db', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class DataPointModel(Base):
    __tablename__ = 'data_points'
    id = Column(Integer, primary_key=True)
    domain = Column(String)
    keyword = Column(String)
    timestamp = Column(DateTime)
    value = Column(Float)


class MonitoringServiceModel(Base):
    __tablename__ = 'monitoring_services'
    id = Column(Integer, primary_key=True)
    domain = Column(String)
    keyword = Column(String)
    interval = Column(Integer)
    is_running = Column(Boolean)
    last_run = Column(DateTime)


Base.metadata.create_all(engine)


def get_data_points(domain: str, keyword: str, start_time: datetime.datetime, end_time: datetime.datetime):
    session = Session()
    query = session.query(DataPointModel).filter(
        DataPointModel.domain == domain,
        DataPointModel.keyword == keyword,
        DataPointModel.timestamp >= start_time,
        DataPointModel.timestamp <= end_time
    )
    data_models = query.all()
    session.close()
    data_points = [
        DataPoint(timestamp=dm.timestamp, value=dm.value)
        for dm in data_models
    ]
    return data_points
