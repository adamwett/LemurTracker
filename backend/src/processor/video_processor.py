from datetime import datetime, timedelta
import threading
import cv2
import numpy as np
from collections import deque
from .frame_processor import process_frame
from .save_queue import SaveQueueHandler
import logging
import json

log = logging.getLogger(__name__) # Added logging

MINUTE_BUFFER_SIZE = 1000000
FPS = 15

class VideoProcessor:
    def __init__(self, db_url: str, cam_dir: str, source: str, camera_name: str, real_start_time: datetime): # Removed webrtc_client
        self.db_url = db_url
        self.cam_dir = cam_dir
        self.source = source 
        self.camera_name = camera_name
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            log.error(f"Failed to open video source: {source} for {camera_name}")
            # Handle error appropriately, maybe raise exception or set a failed state
            self.running = False
            return
        else:
            log.info(f"Successfully opened video source: {source} for {camera_name}")
            self.running = False # Will be set true by start()

        self.thread = None
        self.frame_buffer = deque(maxlen=MINUTE_BUFFER_SIZE)
        self.metadata_buffer = deque(maxlen=MINUTE_BUFFER_SIZE)
        self.buffer_lock = threading.Lock() # Lock for buffer/metadata/segment time

        self.real_start_time = real_start_time
        self.video_start_time = self.real_start_time
        self.segment_start_time = self.real_start_time
        self.frame_count = 0

        self.save_handler = SaveQueueHandler(
            db_url=db_url,
            cam_dir=cam_dir,
            camera_name=camera_name,
            fps=FPS
        )


    def start(self):
        if not self.running and self.cap.isOpened(): # Check cap is opened before starting thread
            self.running = True
            self.thread = threading.Thread(target=self._process_video, daemon=True, name=f"Processor-{self.camera_name}")
            self.thread.start()
        elif not self.cap.isOpened():
             log.error(f"Cannot start processor for {self.camera_name}: VideoCapture not opened.")


    def _process_video(self):
        log.info(f"Starting video processing loop for {self.camera_name}")
        back_sub = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
        lk_params = dict(winSize=(15, 15), maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        frame_read_success_count = 0

        while self.running and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self._save_segment()
                    # frame_read_fail_count += 1
                    # # Log less frequently on failure to avoid spam
                    # if frame_read_fail_count % 10 == 1 or frame_read_fail_count < 5:
                    #     log.warning(f"[{self.camera_name}] cap.read() returned False. End of stream or error? (Fail count: {frame_read_fail_count})")
                    break 


                frame_read_success_count += 1
                frame_read_fail_count = 0

                frame_resized = cv2.resize(frame, (640, 480))
                processed_frame, coordinateX, coordinateY, activity = process_frame(frame_resized, back_sub, lk_params)

                current_time = self._get_current_video_time()
                metadata = {
                    "coordinateX": coordinateX,
                    "coordinateY": coordinateY,
                    "activity": activity,
                    "timestamp": current_time.isoformat() # Use ISO format string
                }


                with self.buffer_lock:
                    self.frame_buffer.append(processed_frame)
                    self.metadata_buffer.append(metadata)
                    self.frame_count += 1
                    #should_save = len(self.frame_buffer) >= MINUTE_BUFFER_SIZE

                # if should_save:
                #     self._save_segment()

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                     log.info(f"[{self.camera_name}] 'q' pressed, stopping processor.")
                     self.running = False
                     break

            except Exception as e:
                log.error(f"[{self.camera_name}] Error in processing loop: {e}", exc_info=True)
                self.running = False 
                break

        log.info(f"[{self.camera_name}] Processing loop finished. Read {frame_read_success_count} frames successfully.")

        if self.frame_buffer:
            log.info(f"[{self.camera_name}] Saving final segment...")
            self._save_segment()

        if self.cap.isOpened():
            self.cap.release()
            log.info(f"[{self.camera_name}] Video capture released.")
        self.save_handler.stop() # Ensure save queue is stopped and flushed
        log.info(f"[{self.camera_name}] Processor stopped.")


    def _get_current_video_time(self):
        return self.video_start_time + timedelta(seconds=self.frame_count / FPS)


    def _save_segment(self):
         frames_to_save = None
         metadata_to_save = None
         segment_time_to_save = None

         with self.buffer_lock:
             if not self.frame_buffer: # Check if buffer is empty
                 return # Nothing to save

             frames_to_save = list(self.frame_buffer)
             metadata_to_save = list(self.metadata_buffer)
             segment_time_to_save = self.segment_start_time

             # Clear buffers *after* copying
             self.frame_buffer.clear()
             self.metadata_buffer.clear()
             # Update segment start time for the *next* segment
             self.segment_start_time = self._get_current_video_time()
             log.debug(f"[{self.camera_name}] Prepared segment from {segment_time_to_save} with {len(frames_to_save)} frames for saving.")


         # Enqueue outside the lock
         if frames_to_save: # Ensure we actually have something to save
            self.save_handler.enqueue_save(frames_to_save, metadata_to_save, segment_time_to_save)


    def stop(self):
        log.info(f"Stopping processor for {self.camera_name}...")
        self.running = False
        if self.thread and self.thread.is_alive():
             log.debug(f"Waiting for {self.camera_name} processor thread to join...")
             self.thread.join(timeout=5.0) # Add a timeout
             if self.thread.is_alive():
                 log.warning(f"[{self.camera_name}] Processor thread did not join cleanly after 5 seconds.")
             else:
                 log.debug(f"[{self.camera_name}] Processor thread joined.")

    def wait(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()