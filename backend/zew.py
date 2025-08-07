import cv2
from src.processor.frame_processor import process_frame


def alex_sucks(videos_array):
    print("Starting")
    cap = cv2.VideoCapture("stitched_video.mp4")
    back_sub = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
    lk_params = dict(winSize=(15, 15), maxLevel=2,
                        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    frame_count = 0
    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                print("Video is done")
            
            process_frame(frame, back_sub, lk_params)

            if frame_count % 900 == 0:
                 print(f"Processed {frame_count / 900} minutes of video")

            frame_count += 1
        except Exception as e:
                print(f'Error is {e}')
                break

if __name__ == "__main__":
    videos_array = [
         "stitched_video.mp4",
         "stitched_video.mp4",
         "stitched_video.mp4",
    ]
    print("starting stream")
    alex_sucks()