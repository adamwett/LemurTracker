import math
import multiprocessing
import os
import signal
from threading import Thread, Lock
from queue import Empty, Queue
from datetime import datetime
import time
import sys
from src.database.endpoints import create_app as create_flask_app
from src.processor.queue_processor import QueueProcessor


_frontend_status_lock = Lock()
_is_frontend_open = False

ProcessingItem = tuple[str, datetime]
processing_queue: Queue[ProcessingItem] = Queue()

_process_percentage_lock = Lock()
_process_percentage = 0


def set_process_percentage(percentage: int):
    global _process_percentage
    with _process_percentage_lock:
        if 0 <= percentage <= 100:
            _process_percentage = percentage
        else:
            raise ValueError("Percentage must be between 0 and 100.")

def get_process_percentage() -> int:
    with _process_percentage_lock:
        percentage = _process_percentage
    return percentage

def set_frontend_status(is_open: bool):
    global _is_frontend_open
    with _frontend_status_lock:
        _is_frontend_open = is_open

def get_frontend_status() -> bool:
    with _frontend_status_lock:
        status = _is_frontend_open
    return status

def trigger_shutdown():
    current_pid = os.getpid()
    try:
        #Trying three times just to make sure
        os.kill(current_pid, signal.SIGINT)
    except Exception as e:
        print(f"[Main - trigger_shutdown in PID {current_pid}] Error sending SIGINT: {e}")
        print("[Main - trigger_shutdown] Attempting fallback sys.exit().")
        sys.exit(1)


def run_flask_app(flask_app):
    print("Starting Flask server on http://0.0.0.0:5055...")
    try:
        flask_app.run(host="0.0.0.0", port=5055, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask server encountered an error: {e}")



def start_backend():

    

    flask_app = create_flask_app(
        processing_queue=processing_queue,
        set_frontend_status=set_frontend_status,
        get_frontend_status=get_frontend_status,
        request_shutdown=trigger_shutdown,
        get_process_percentage=get_process_percentage,
    )

    flask_thread = Thread(target=run_flask_app, args=(flask_app,), name="FlaskThread", daemon=True)
    print("Starting Flask thread...")
    flask_thread.start()
    print("Flask thread started.")

    return flask_thread

if __name__ == '__main__':
    print("Main application starting...")
    set_frontend_status(True)
    flask_server_thread = start_backend()
    max_workers = math.floor(multiprocessing.cpu_count() * 0.75) 
    queue_processor = QueueProcessor(max_workers=max_workers)


    while True:
            if not processing_queue.empty():
                queue_size = processing_queue.qsize()

                print(f"[{datetime.now()}] Detected item in queue, starting processing sam")
                queue_item = processing_queue.queue[0] # gets the first item in the queue
                processor_status = queue_processor.process_items(queue_item, set_process_percentage)
                print(f"[{datetime.now()}] Finished item in queue sam")
                print(f"[Main] Processor finished with status: {processor_status}")
                processing_queue.get() # Remove the first item to simulate processing
                set_process_percentage(0)
                if not get_frontend_status() and processing_queue.empty():
                    print("[Main] Frontend is closed and processing queue is empty. Triggering shutdown.")
                    trigger_shutdown()
                    break

            time.sleep(1)