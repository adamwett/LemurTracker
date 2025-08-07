# queue_processor.py
import math
import os
import cv2
from datetime import datetime, timedelta
from multiprocessing import Pool
from functools import partial
from .video_processor import VideoProcessor
from src.database.database_handler import DatabaseHandler

class QueueProcessor:
    def __init__(self, max_workers: int = 6):
        self.max_workers = max_workers
        self.finished_videos = 0

    def get_video_duration(self, filepath: str) -> float:
        """Returns duration of video in seconds."""
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {filepath}")
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        return frame_count / fps if fps > 0 else 0

    def run_video_processor(self, db_url, camera_dirs, item):
        video_path, start_time, camera_name = item
        vp = VideoProcessor(
            db_url=db_url,
            cam_dir=camera_dirs[camera_name],
            source=video_path,
            camera_name=camera_name,
            real_start_time=start_time
        )
        try:
            vp.start()  # Start the background thread
            vp.wait()   # Wait for the thread to complete its work
            return f"Success: {video_path}" # Return status
        except Exception as e:
            return f"Failed: {video_path}, {e}"

    def process_items(self, queue_item, set_process_percentage) -> str:
        db = DatabaseHandler()
        db_url = db.get_database_url()
        root_path, initial_time = queue_item
        print(queue_item)

        cameras = ['Camera1', 'Camera2', 'Camera3']
        video_map = {camera: [] for camera in cameras}

        for camera in cameras:
            camera_dir = os.path.join(root_path, camera)
            if not os.path.isdir(camera_dir):
                print(f"Warning: {camera_dir} does not exist or is not a directory.")
                continue

            video_files = sorted([
                f for f in os.listdir(camera_dir)
                if f.lower().endswith('.mp4')
            ])

            for video in video_files:
                full_path = os.path.join(camera_dir, video)
                video_map[camera].append(full_path)

        result_tuples = []
        current_time = initial_time

        duration = self.get_video_duration(video_map['Camera1'][0]) if video_map['Camera1'] else 0
        for i in range(len(video_map['Camera1'])):  # assuming same number of videos in all
            video_lengths = {}
            for camera in cameras:
                video_path = video_map[camera][i]
                video_lengths[camera] = duration
                result_tuples.append((video_path, current_time, camera))

            current_time += timedelta(seconds=video_lengths['Camera1'])  # adjust based on Camera1

        # Parallel processing
        print(f"[QueueProcessor] Starting parallel processing of {len(result_tuples)} videos...")

        with Pool(processes=self.max_workers) as pool:
            worker_fn = partial(self.run_video_processor, db_url, db.camera_dirs)
            results = pool.imap_unordered(worker_fn, result_tuples)

            total = len(result_tuples)
            for index, result_value in enumerate(results, start=1):
                # Use the 'index' for the calculation
                set_process_percentage(math.floor((index / total) * 100))
                # You can optionally use 'result_value' here if needed, e.g., for logging
                # print(f"Processed item {index}/{total}: {result_value}")

        

        result_message = f"[{datetime.now()}] QueueProcessor: All video processing finished using {self.max_workers} workers."
        print(result_message)
        return result_message
