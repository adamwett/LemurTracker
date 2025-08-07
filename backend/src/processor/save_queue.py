import threading
import queue
import time
from src.database.save_processed_data import save_video_and_metadata

class SaveQueueHandler:
    def __init__(self, db_url: str, cam_dir: str, camera_name: str, fps: int, max_queue_size: int = 3):
        self.db_url = db_url
        self.cam_dir = cam_dir
        self.camera_name = camera_name
        self.fps = fps
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.running = True
        self.condition = threading.Condition()

        self.save_thread = threading.Thread(target=self._process_save_queue, daemon=True)
        self.save_thread.start()

    def enqueue_save(self, frames, metadata, segment_time):
        with self.condition:
            if self.queue.full():
                print(f"Warning: Save queue full for {self.camera_name}, dropping segment")
                return False
            
            self.queue.put((frames, metadata, segment_time))
            self.condition.notify()
            return True

    def _process_save_queue(self):
        while self.running or not self.queue.empty():
            with self.condition:
                while self.queue.empty() and self.running:
                    self.condition.wait()

                if not self.queue.empty():
                    item = self.queue.get()
                    if item is not None:
                        frames, metadata, segment_time = item
                        self._save_segment(frames, metadata, segment_time)

    def _save_segment(self, frames, metadata, segment_time):
        try:
            save_video_and_metadata(
                self.db_url,
                self.cam_dir,
                frames,
                metadata,
                self.camera_name,
                self.fps,
                segment_time
            )
        except Exception as e:
            print(f"Error saving video for {self.camera_name}: {str(e)}")

    def stop(self):
        self.running = False
        with self.condition:
            self.condition.notify() 
        if self.save_thread.is_alive():
            self.save_thread.join()
