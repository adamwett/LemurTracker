import os
import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from sqlalchemy.orm import Session

from src.database.database_handler import DatabaseHandler
from src.database.models import Base, ProcessedVideo


class TestDatabaseHandler:
    @pytest.fixture
    def mock_os_path_exists(self):
        with patch('os.path.exists', return_value=False) as mock:
            yield mock
    
    @pytest.fixture
    def mock_makedirs(self):
        with patch('os.makedirs') as mock:
            yield mock
            
    @pytest.fixture
    def mock_engine(self):
        with patch('src.database.database_handler.create_engine') as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            yield mock_engine
            
    @pytest.fixture
    def mock_metadata_create(self):
        with patch('src.database.models.Base.metadata.create_all') as mock:
            yield mock
            
    @pytest.fixture
    def mock_session(self):
        mock = MagicMock()
        with patch('src.database.database_handler.scoped_session', return_value=mock):
            yield mock
    
    def test_init_creates_directories(self, mock_os_path_exists, mock_makedirs):
        """Test that DatabaseHandler creates required directories"""
        with patch('src.database.database_handler.create_engine'):
            with patch('src.database.models.Base.metadata.create_all'):
                with patch('src.database.database_handler.scoped_session'):
                    with patch('src.database.database_handler.sessionmaker'):
                        handler = DatabaseHandler()
                        
                        # Check processed_videos_dir is created
                        assert mock_makedirs.call_count >= 1
                        # Verify all camera dirs are created
                        for camera_dir in handler.camera_dirs.values():
                            mock_makedirs.assert_any_call(camera_dir, exist_ok=True)

    def test_database_initialization(self, mock_engine, mock_metadata_create, mock_session):
        """Test that database is properly initialized"""
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                with patch('src.database.database_handler.sessionmaker'):
                    # Mock the session execute and fetchone methods
                    mock_result = MagicMock()
                    mock_result.fetchone.return_value = ["CREATE TABLE processed_videos (...)"]
                    mock_session.return_value.execute.return_value = mock_result
                    mock_session.return_value.scalar.return_value = 0
                    
                    handler = DatabaseHandler()
                    
                    # Check that Base.metadata.create_all was called
                    mock_metadata_create.assert_called_once_with(mock_engine)
                    
                    # Check that database verification query was executed
                    mock_session.return_value.execute.assert_called()

    def test_get_database_url(self):
        """Test that get_database_url returns correct URL"""
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs'):
                with patch('src.database.database_handler.create_engine'):
                    with patch('src.database.models.Base.metadata.create_all'):
                        with patch('src.database.database_handler.scoped_session'):
                            with patch('src.database.database_handler.sessionmaker'):
                                handler = DatabaseHandler()
                                handler.db_path = "/test/path/lemur_tracking.db"
                                
                                assert handler.get_database_url() == "sqlite:////test/path/lemur_tracking.db"

    @pytest.mark.parametrize("exception_point", ["os_makedirs", "create_engine", "execute_query"])
    def test_init_error_handling(self, exception_point):
        """Test error handling during initialization"""
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs') as mock_makedirs:
                with patch('src.database.database_handler.create_engine') as mock_create_engine:
                    with patch('src.database.database_handler.scoped_session') as mock_scoped_session:
                        with patch('src.database.models.Base.metadata.create_all'):
                            
                            # Setup mocks to raise exceptions at different points
                            if exception_point == "os_makedirs":
                                mock_makedirs.side_effect = PermissionError("Permission denied")
                            elif exception_point == "create_engine":
                                mock_create_engine.side_effect = Exception("Engine creation failed")
                            elif exception_point == "execute_query":
                                mock_session = MagicMock()
                                mock_session.execute.side_effect = Exception("Query execution failed")
                                mock_scoped_session.return_value = mock_session
                            
                            # Test that exception is propagated
                            with pytest.raises(Exception):
                                DatabaseHandler()


class TestDatabaseHandlerIntegration:
    """Integration tests using an actual in-memory database"""
    
    @pytest.fixture
    def db_handler(self):
        """Create a database handler with in-memory SQLite database"""
        with patch.object(DatabaseHandler, '__init__', return_value=None):
            handler = DatabaseHandler()
            handler.db_path = ":memory:"
            handler.processed_videos_dir = "/tmp/test_processed_videos"
            handler.camera_dirs = {
                'Camera1': '/tmp/test_processed_videos/camera1',
                'Camera2': '/tmp/test_processed_videos/camera2',
                'Camera3': '/tmp/test_processed_videos/camera3'
            }
            
            # Create engine and session with in-memory database
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker, scoped_session
            
            handler.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(handler.engine)
            handler.Session = scoped_session(sessionmaker(bind=handler.engine))
            
            yield handler
            
            # Clean up
            Base.metadata.drop_all(handler.engine)
    
    def test_can_query_database(self, db_handler):
        """Test that we can query the database through the handler"""
        session = db_handler.Session()
        
        # Add a test record
        test_video = ProcessedVideo(
            processed_filename="test_video.mp4",
            camera_name="Camera1",
            filepath="/tmp/test.mp4",
            duration=30.0,
            frame_count=900,
            resolution_width=640,
            resolution_height=480,
            time_stamp="2025-03-31 12:00:00"
        )
        session.add(test_video)
        session.commit()
        
        # Query and verify
        result = session.query(ProcessedVideo).all()
        assert len(result) == 1
        assert result[0].processed_filename == "test_video.mp4"
        assert result[0].camera_name == "Camera1"