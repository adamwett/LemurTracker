import os
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from .models import Base

class DatabaseHandler:
    def __init__(self):
        try:
            # Get the paths
            self.src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src directory
            self.db_dir = os.path.dirname(os.path.abspath(__file__))  # database directory
            
            # Set up file paths
            self.db_path = os.path.join(self.db_dir, 'lemur_tracking.db')
            self.processed_videos_dir = os.path.join(self.src_dir, 'processed_videos')
            
            # Create camera-specific directories
            self.camera_dirs = {
                'Camera1': os.path.join(self.processed_videos_dir, 'camera1'),
                'Camera2': os.path.join(self.processed_videos_dir, 'camera2'),
                'Camera3': os.path.join(self.processed_videos_dir, 'camera3')
            }
            
            print("\n=== Initializing DatabaseHandler ===")
            print(f"Database path: {self.db_path}")
            print(f"Database exists: {os.path.exists(self.db_path)}")
            print(f"Videos directory: {self.processed_videos_dir}")
            
            # Create all necessary directories
            os.makedirs(self.processed_videos_dir, exist_ok=True)
            for camera_dir in self.camera_dirs.values():
                os.makedirs(camera_dir, exist_ok=True)
            
            # Database setup
            db_url = f'sqlite:///{self.db_path}'
            print(f"Database URL: {db_url}")
            
            self.engine = create_engine(db_url, connect_args={'check_same_thread': False})
            Base.metadata.create_all(self.engine)
            
            # Create thread-safe session factory
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            
            # Verify connection by trying to query the database
            try:
                session = self.Session()
                video_count = session.execute(text("SELECT COUNT(*) FROM processed_videos")).scalar()
                print(f"Successfully connected to database. Found {video_count} videos.")
                
                # Print table schema
                result = session.execute(text("SELECT * FROM sqlite_master WHERE type='table' AND name='processed_videos'"))
                table_info = result.fetchone()
                if table_info:
                    print("Table schema:", table_info[4])
                session.close()
                
            except Exception as e:
                print(f"Error verifying database connection: {e}")
                raise
            
        except Exception as e:
            print(f"Error initializing DatabaseHandler: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

        
    def get_database_url(self):
        """Return the database URL."""
        return f'sqlite:///{self.db_path}'