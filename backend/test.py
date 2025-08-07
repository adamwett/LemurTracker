from collections import defaultdict
from datetime import datetime
from flask import Flask
from src.database.models import LemurTracking, ProcessedVideo
from src.database.database_handler import DatabaseHandler


def find_relevant_data(session, date: str, start_time: str, end_time: str, camera_names: list):
    # Convert start and end time strings into full datetime objects
    start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H%M%S")
    end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H%M%S")


    # Query the database with time filtering for multiple cameras
    data = session.query(
        LemurTracking.time_stamp, LemurTracking.is_active, LemurTracking.coordinate_x, LemurTracking.coordinate_y, LemurTracking.camera_name
    ).filter(
        LemurTracking.time_stamp >= start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        LemurTracking.time_stamp <= end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        LemurTracking.camera_name.in_(camera_names)  # Filter for multiple cameras
    ).all()

    print(len(data))

    # Storage for results per camera
    camera_data = {camera: {"activity_per_second": defaultdict(bool), "coordinates": []} for camera in camera_names}

    for timestamp, is_active, x, y, camera_name in data:
        second_key = timestamp[:19]  # Extract second-level timestamp (YYYY-MM-DD HH:MM:SS)

        # Store activity per second (if any record in that second is True, store True)
        camera_data[camera_name]["activity_per_second"][second_key] = camera_data[camera_name]["activity_per_second"][second_key] or is_active

        # Store coordinates (even if missing)
        camera_data[camera_name]["coordinates"].append((x, y) if x is not None and y is not None else (None, None))

    # Convert defaultdict values into sorted lists
    for camera in camera_names:
        camera_data[camera]["activity_per_second"] = [
            camera_data[camera]["activity_per_second"][key] for key in sorted(camera_data[camera]["activity_per_second"].keys())
        ]

    return camera_data

def create_app():
    db = DatabaseHandler()
    print("starting")
    date = "2025-04-02"
    start_time = "120000"
    end_time = "121000"

    camera_names = ["Camera1", "Camera2", "Camera3"] 

    try:
        
        session = db.Session()
        camera_data = find_relevant_data(session, date, start_time, end_time, camera_names)
        print(len(camera_data['Camera1']["activity_per_second"]))
    except Exception as e:
        print("failed")

    finally:
        session.close()


if __name__ == '__main__':
    create_app()