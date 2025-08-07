from datetime import datetime, time
import os
import ffmpeg
import numpy as np
from sqlalchemy import create_engine
from src.database.models import Base, LemurTracking, ProcessedVideo
from sqlalchemy.orm import sessionmaker, scoped_session


def save_video_and_metadata(db_url, cam_dir, frames, metadata, camera_name, fps, time_stamp):
    """Save video and metadata to the database."""
    try:
        #print(f"Saving video and metadata for {camera_name}")
        engine = create_engine(db_url, connect_args={'check_same_thread': False})
        Base.metadata.create_all(engine)
        Session = scoped_session(sessionmaker(bind=engine))
        try:
            save_processed_video(Session, frames, cam_dir, fps, camera_name, time_stamp)
            for data in metadata:
                add_tracking_data(
                    Session,
                    is_active=data["activity"],
                    timestamp=data["timestamp"],
                    camera_name=camera_name,
                    coordinate_x=data["coordinateX"],
                    coordinate_y=data["coordinateY"],
                )
        finally:
            Session.close()
        #print(f"Saved video and metadata for {camera_name}")
    except Exception as e:
        print(f"Error saving video and metadata: {e}")


def save_processed_video(Session, video_frames, cam_dir, fps, camera_name, time_stamp):
    try:
        if not video_frames:
            raise ValueError("No frames to save")

        #print(f"Starting video save process...")
        #print(f"Number of frames to save: {len(video_frames)}")

        # Generate unique filename using timestamp
        processed_filename = f"{camera_name}_{time_stamp}.mp4"
        output_path = os.path.join(cam_dir, processed_filename)

        #print(f"Saving video to: {output_path}")

        # Get video properties
        height, width = video_frames[0].shape[:2]
        frame_count = len(video_frames)
        duration = frame_count / fps

        print(f"Video properties: {width}x{height}, {fps} fps, {duration:.2f} seconds")

        # Use ffmpeg piping instead of temporary file
        process = (
            ffmpeg
            .input(
                'pipe:0',
                format='rawvideo',
                pix_fmt='bgr24',
                s=f'{width}x{height}',
                r=fps
            )
            .output(
                output_path,
                pix_fmt='yuv420p',
                vcodec='libx264',
                preset='ultrafast',
                crf=30,
                movflags='faststart'
            )
            .overwrite_output()
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        # Write frames directly to FFmpeg
        for i, frame in enumerate(video_frames):
            process.stdin.write(frame.tobytes())
            #if i % 100 == 0:
                #print(f"Processed {i}/{len(video_frames)} frames")

        process.stdin.close()
        process.wait()

        # Verify file was created
        if not os.path.exists(output_path):
            raise RuntimeError(f"Video file was not created at {output_path}")

        file_size = os.path.getsize(output_path)
        #print(f"Video file created successfully. Size: {file_size/1024/1024:.2f} MB")

        # Save metadata to database
        video_metadata = ProcessedVideo(
            processed_filename=processed_filename,
            camera_name=camera_name,
            filepath=output_path,
            duration=duration,
            frame_count=frame_count,
            resolution_width=width,
            resolution_height=height,
            time_stamp=time_stamp
        )

        Session.add(video_metadata)
        Session.commit()
        
        print(f"Input: {len(video_frames)} frames at {fps} FPS")
        print(f"Expected duration: {len(video_frames) / fps} seconds")
        
        # After video creation:
        # Check actual video duration with ffprobe
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_path], capture_output=True, text=True)
        actual_duration = float(result.stdout.strip())
        print(f"Actual video duration: {actual_duration} seconds")

        #print("Video metadata saved to database")
        return output_path

    except Exception as e:
        Session.rollback()
        print(f"Error saving video: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e




def add_tracking_data(Session, is_active, timestamp, camera_name, coordinate_x=None, coordinate_y=None):
    try:
        # Get today's date
        today_date = datetime.today().strftime("%Y-%m-%d")

        # Ensure timestamp includes today's date
        if isinstance(timestamp, time):
            timestamp = f"{today_date} {timestamp.strftime('%H:%M:%S.%f')}"  # Combine date and time
        elif isinstance(timestamp, datetime):  
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")  # Keep full datetime format
        elif isinstance(timestamp, str):  
            timestamp = f"{today_date} {timestamp}"  # Assume timestamp is only time and prepend date
        else:
            raise TypeError(f"Unexpected type for timestamp: {type(timestamp)}")

        tracking_data = LemurTracking(
            time_stamp=timestamp,
            is_active=is_active,
            coordinate_x=coordinate_x,
            coordinate_y=coordinate_y,
            camera_name=camera_name,
        )
        Session.add(tracking_data)
        Session.commit()
        return tracking_data.id

    except Exception as e:
        Session.rollback()
        print(f"Error saving tracking data: {e}")
        raise e

