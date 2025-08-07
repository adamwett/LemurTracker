from flask import Flask, jsonify, request, send_file
from queue import Queue
from datetime import datetime
from flask_cors import CORS 
import os
from .database_handler import DatabaseHandler
from .endpoint_helpers import get_activity_helper, get_coordinate_helper, find_relevant_videos, stitch_videos

from typing import Callable, Tuple
ProcessingItem = Tuple[str, datetime]
SetStatusFunc = Callable[[bool], None]
GetStatusFunc = Callable[[], bool]
ShutdownFunc = Callable[[], None]
GetPecentFunc = Callable[[], int]


def create_app(processing_queue: Queue[ProcessingItem], set_frontend_status: SetStatusFunc, get_frontend_status: GetStatusFunc, request_shutdown: ShutdownFunc, get_process_percentage: GetPecentFunc):
    app = Flask(__name__)
    CORS(app)
    db = DatabaseHandler()

    @app.route('/on-open', methods=['GET'])
    def handle_on_open():
        """Handles the frontend opening."""
        try:
            print(f"Frontend status is: {get_frontend_status()}")
            set_frontend_status(True)
            print("Received /on-open request.")
            print(f"Frontend status set to open: {get_frontend_status()}")
            return jsonify({"status": "open", "already_running": True}), 200
        except Exception as e:
            print(f"Error in /on-open: {e}")
            return jsonify({"error": "Failed to process on-open request"}), 500

    @app.route('/on-close', methods=['GET'])
    def handle_on_close():
        """Handles the frontend closing."""
        print("Received /on-close request.")
        try:
            # Use the passed-in queue and functions
            is_queue_empty = processing_queue.empty()
            print(f"Processing queue empty: {is_queue_empty}")

            set_frontend_status(False) # Always mark as closed

            if is_queue_empty:
                print("Queue is empty. Attempting to shut down server...")
                request_shutdown()
            else:
                print("Queue is not empty. Server will continue running.")
                return jsonify({"message": "frontend_closed_server_remains_active", "status": "closed"}), 200

        except Exception as e:
            print(f"Error in /on-close: {e}")
            return jsonify({"error": "Failed to process on-close request"}), 500

    @app.route('/add-job', methods=['POST'])
    def add_job():
        print("Adding job")
        data = request.get_json()
        if not data:
            print("[FlaskRoute /add-job] No JSON data received in request body.")
            return jsonify({"error": "Request body must contain JSON data"}), 400
        
        if 'file_path' not in data or 'start_dt' not in data:
            print(f"[FlaskRoute /add-job] Missing required fields in JSON data: {data}")
            return jsonify({"error": "Missing 'file_path' or 'start_dt' in JSON body"}), 400
        
        file_path = data.get('file_path')
        start_dt_str = data.get('start_dt')



        if not isinstance(file_path, str) or not file_path:
             print(f"[FlaskRoute /add-job] Invalid file_path type or empty: {file_path}")
             return jsonify({"error": "Invalid 'file_path' provided"}), 400
        if not isinstance(start_dt_str, str) or not start_dt_str:
             print(f"[FlaskRoute /add-job] Invalid start_dt type or empty: {start_dt_str}")
             return jsonify({"error": "Invalid 'start_dt' provided"}), 400
        
        required_folders = ['Camera1', 'Camera2', 'Camera3']
        
        # Keep track of missing folders
        missing_folders = []
        for folder in required_folders:
            folder_path = os.path.join(file_path, folder)
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                missing_folders.append(folder)
                
        if missing_folders:
            print(f"[FlaskRoute /add-job] Missing required folders: {missing_folders}")
            return jsonify({"error": f"Missing required folders: {', '.join(missing_folders)}"}), 400
        
        try:
            try:
                start_dt = datetime.fromisoformat(start_dt_str)
                print(f"[FlaskRoute /add-job] Parsed start_dt: {start_dt}")
            except ValueError:
                print(f"[FlaskRoute /add-job] Invalid ISO format for start_dt: {start_dt_str}")
                # Re-raise specific error for the outer try/except
                raise ValueError("Invalid start_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
            
            # Use the passed-in queue
            item: ProcessingItem = (file_path, start_dt)
            print("I do not think error is right here")
            processing_queue.put(item)
            print(f"Added job to queue: {item}")
            return jsonify({"message": "Job added successfully", "queue_size": processing_queue.qsize()}), 201
        except ValueError:
            return jsonify({"error": "Invalid start_time format. Use ISO format."}), 400
        except Exception as e:
            print(f"Error adding job: {e}")
            return jsonify({"error": "Failed to add job"}), 500
        
    @app.route('/get-queue-status', methods=['GET'])
    def get_queue_status():
        """Returns the current status of the processing queue."""
        try:
            queue_list = list(processing_queue.queue)  # Converts the queue to a list for easy indexing
            queue_size = len(queue_list)

            if queue_size == 0:
                return jsonify({"status": "not processing"}), 200
            else:
                current_item: ProcessingItem = queue_list[0]
                on_deck_items = queue_list[1:]
                print("Percent: ", get_process_percentage())

                response = {
                    "status": "processing",
                    "current_process": {
                        "file_path": current_item[0],
                        "percent": get_process_percentage()  # Hardcoded percent
                    },
                    "processes_on_deck": [item[0] for item in on_deck_items]
                }

                return jsonify(response), 200
        except Exception as e:
            print(f"Error getting queue status: {e}")
            return jsonify({"error": "Failed to get queue status"}), 500
        

    @app.route('/activity-data', methods=['GET'])
    def get_activity_data():
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if not all([start_time, end_time]):
            return jsonify({"error": "Missing required parameters."}), 400
        
        try:
            session = db.Session()
            activity = get_activity_helper(session, start_time, end_time)

            if (activity is None) or (not activity) or len(activity) == 0:
                return jsonify({"error": "No activity data found for the given time range."}), 404
            
            return jsonify({"activity": activity}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
        finally:
            session.close()

    @app.route('/coordinate-data', methods=['GET'])
    def get_coordinate_data():
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if not all([start_time, end_time]):
            return jsonify({"error": "Missing required parameters."}), 400
        
        try:
            session = db.Session()
            coordinates = get_coordinate_helper(session, start_time, end_time)

            if not coordinates:
                return jsonify({"error": "No activity data found for the given time range."}), 404
            
            return jsonify({"coordinates": coordinates}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
        finally:
            session.close()

    @app.route('/stitched-video', methods=['GET'])
    def get_stitched_video():
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        camera_name = request.args.get('camera_name')


        if not all([start_time, end_time, camera_name]):
            return jsonify({"error": "Missing required parameters."}), 400

        try:
            session = db.Session()
            print (f"Start time: {start_time}")
            print (f"End time: {end_time}")
            camera_videos = find_relevant_videos(session, start_time, end_time, camera_name)

            if not camera_videos:
                return jsonify({"error": "No videos found for the given time range."}), 404

            stitched_video_path = stitch_videos(camera_videos["selected"], camera_name, start_time, end_time)

            print("Sam here lol")
            print(f"Stitched video path: {stitched_video_path}")
            if not stitched_video_path:
                return jsonify({"error": "No videso were stitched"}), 404
            print("Sam here second lol")

            print(f"Here is the stiched video path{stitched_video_path}")
            return send_file(stitched_video_path, as_attachment=True, mimetype='video/mp4')
        except Exception as e:
            return jsonify({"error 500": str(e)}), 500

        finally:
            session.close()

    # --- Return the configured app instance ---
    return app