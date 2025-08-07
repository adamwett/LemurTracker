from datetime import datetime, timedelta
import os
import subprocess

from .models import LemurTracking, ProcessedVideo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STITCHED_VIDEOS_DIR = os.path.join(BASE_DIR, "stitched_videos")

def get_activity_helper(session, start_time, end_time):

    dt_start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    dt_end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
    formatted_start = f"{dt_start.strftime('%Y-%m-%d')} {dt_start.strftime('%Y-%m-%dT%H:%M:%S')}"
    formatted_end = f"{dt_end.strftime('%Y-%m-%d')} {dt_end.strftime('%Y-%m-%dT%H:%M:%S')}"

    results = session.query(LemurTracking).filter(
        LemurTracking.time_stamp >= formatted_start,
        LemurTracking.time_stamp <= formatted_end
    ).all()

    camera1 = []
    camera2 = []
    camera3 = []

    for result in results:
        if result.camera_name == "Camera1":
            camera1.append(result)
        elif result.camera_name == "Camera2":
            camera2.append(result)
        elif result.camera_name == "Camera3":
            camera3.append(result)

    activity = []

    for i in range(0, len(camera1), 15):
        chunk1 = camera1[i:i+15]
        chunk2 = camera2[i:i+15]
        chunk3 = camera3[i:i+15]
        if any(r.is_active for r in chunk1) or any(r.is_active for r in chunk2) or any(r.is_active for r in chunk3):
           activity.append(True)
        else:
            activity.append(False)

    return activity


def get_coordinate_helper(session, start_time, end_time):
    dt_start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    dt_end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
    formatted_start = f"{dt_start.strftime('%Y-%m-%d')} {dt_start.strftime('%Y-%m-%dT%H:%M:%S')}"
    formatted_end = f"{dt_end.strftime('%Y-%m-%d')} {dt_end.strftime('%Y-%m-%dT%H:%M:%S')}"

    dt_start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    dt_end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
    formatted_start = f"{dt_start.strftime('%Y-%m-%d')} {dt_start.strftime('%Y-%m-%dT%H:%M:%S')}"
    formatted_end = f"{dt_end.strftime('%Y-%m-%d')} {dt_end.strftime('%Y-%m-%dT%H:%M:%S')}"

    results = session.query(LemurTracking).filter(
        LemurTracking.time_stamp >= formatted_start,
        LemurTracking.time_stamp <= formatted_end
    ).all()

    camera1 = []
    camera2 = []
    camera3 = []

    for result in results:
        if result.camera_name == "Camera1":
            camera1.append({"x": result.coordinate_x, "y": result.coordinate_y})
        elif result.camera_name == "Camera2":
            camera2.append({"x": result.coordinate_x, "y": result.coordinate_y})
        elif result.camera_name == "Camera3":
            camera3.append({"x": result.coordinate_x, "y": result.coordinate_y})

    coordinates = [
        {"Camera1": camera1},
        {"Camera2": camera2},
        {"Camera3": camera3}
    ]

    print(len(camera1))
    print(len(camera2))
    print(len(camera3))

    return coordinates


def find_relevant_videos(session, start_time, end_time, camera_name):
    """Finds and organizes videos for a specific camera within the specified date and time range."""
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)

    videos = session.query(ProcessedVideo).filter(
        ProcessedVideo.camera_name == camera_name
    ).order_by(ProcessedVideo.time_stamp).all()

    camera_data = {"first": None, "last": None, "selected": []}

    for video in videos:
        video_start = datetime.fromisoformat(video.time_stamp)
        video_end = video_start + timedelta(seconds=video.duration)

        # Check for any overlap between video and the desired time range
        if video_end >= start_time_dt and video_start <= end_time_dt:
            camera_data["selected"].append(video)
            if not camera_data["first"]:
                camera_data["first"] = video
            camera_data["last"] = video

    return camera_data
    

def stitch_videos(video_list, camera_name, start_time, end_time):
    if not video_list:
        return None 
    
    output_path = os.path.join(STITCHED_VIDEOS_DIR, f"{camera_name}_stitched_{start_time}_{end_time}.mp4")
    
    if os.path.exists(output_path):
        return output_path
        
    if not os.path.exists("stitched_videos"):
        os.makedirs("stitched_videos")
    
    # Handle single video case - prevents duplication bug
    if len(video_list) == 1:
        single_video = video_list[0]
        
        # Calculate time offsets for the single video
        video_start = datetime.fromisoformat(single_video.time_stamp)
        requested_start = datetime.fromisoformat(start_time)
        requested_end = datetime.fromisoformat(end_time)
        
        # Calculate start offset (how many seconds into the video to start)
        start_offset = max(0, (requested_start - video_start).total_seconds())
        
        # Calculate duration (how many seconds of video to include)
        video_end = video_start + timedelta(seconds=single_video.duration)
        actual_end = min(requested_end, video_end)
        duration = (actual_end - max(requested_start, video_start)).total_seconds()
        
        # Only trim if we need to, otherwise just copy
        if start_offset > 0 or duration < single_video.duration:
            subprocess.run([
                "ffmpeg", "-i", single_video.filepath, 
                "-ss", str(start_offset),
                "-t", str(duration),
                "-c", "copy", output_path, "-y"
            ], check=True)
        else:
            # Just copy the whole video
            subprocess.run([
                "ffmpeg", "-i", single_video.filepath, 
                "-c", "copy", output_path, "-y"
            ], check=True)
            
        return output_path
    
    # Multiple videos case - your existing logic
    temp_videos = []
    first_video = video_list[0]
    
    first_video_start = first_video.processed_filename.split('_')[1].replace('.mp4', '').split('.')[0].split(' ')[-1]
    h, m, s = map(int, first_video_start.split(':'))
    timestamp_seconds = h * 3600 + m * 60 + s 
    dt = datetime.fromisoformat(start_time)
    hours, minutes, seconds = dt.hour, dt.minute, dt.second
    start_time_seconds = hours * 3600 + minutes * 60 + seconds
    offset_seconds = start_time_seconds - timestamp_seconds
    first_video_start = max(0, offset_seconds)
    
    temp_first = f"temp_{camera_name}_first.mp4"
    subprocess.run([
        "ffmpeg", "-i", first_video.filepath, "-ss", str(first_video_start), 
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", temp_first, "-y"
    ], check=True)
    temp_videos.append(temp_first)
    
    # Add middle videos as they are
    for video in video_list[1:-1]:
        temp_videos.append(video.filepath)
    
    # Process last video
    last_video = video_list[-1]
    
    last_video_end = last_video.processed_filename.split('_')[1].replace('.mp4', '').split('.')[0].split(' ')[-1]
    h, m, s = map(int, last_video_end.split(':'))
    timestamp_seconds = h * 3600 + m * 60 + s 
    dt = datetime.fromisoformat(end_time)
    hours, minutes, seconds = dt.hour, dt.minute, dt.second
    end_time_seconds = hours * 3600 + minutes * 60 + seconds
    offset_seconds = end_time_seconds - timestamp_seconds
    last_video_end = max(0, offset_seconds)
    
    temp_last = f"temp_{camera_name}_last.mp4"
    subprocess.run([
        "ffmpeg", "-i", last_video.filepath, "-to", str(last_video_end), "-c", "copy", temp_last, "-y"
    ], check=True)
    temp_videos.append(temp_last)
    
    # Create file list for FFmpeg
    temp_list_path = f"video_list_{camera_name}.txt"
    with open(temp_list_path, "w") as f:
        for temp_video in temp_videos:
            f.write(f"file '{temp_video}'\n")
    
    # Concatenate videos
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", temp_list_path,
        "-c", "copy", output_path
    ], check=True)
    
    # Cleanup temporary files
    os.remove(temp_list_path)
    os.remove(temp_first)
    os.remove(temp_last)
    
    return output_path