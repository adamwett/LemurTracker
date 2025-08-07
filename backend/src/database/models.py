from sqlalchemy import Column, Integer, Boolean, DateTime, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LemurTracking(Base):
    __tablename__ = 'lemur_tracking'

    id = Column(Integer, primary_key=True)
    time_stamp = Column(String)
    is_active = Column(Boolean, nullable=False)
    coordinate_x = Column(Float)
    coordinate_y = Column(Float)
    camera_name = Column(String)

class ProcessedVideo(Base):
    __tablename__ = 'processed_videos'
    
    id = Column(Integer, primary_key=True)
    processed_filename = Column(String)
    camera_name = Column(String)
    filepath = Column(String)
    duration = Column(Float)
    frame_count = Column(Integer)
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    time_stamp=Column(String)