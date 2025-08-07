import json
import cv2
import numpy as np

def get_annotated_frames(json_path):
    """ Return a list indicating which frames have at least one bounding box. """
    with open(json_path, 'r') as f:
        coco_data = json.load(f)

    image_id_to_index = {img["id"]: idx for idx, img in enumerate(coco_data["images"])}
    
    annotated_indices = set()
    for ann in coco_data["annotations"]:
        image_id = ann["image_id"]
        if image_id in image_id_to_index:
            idx = image_id_to_index[image_id]
            annotated_indices.add(idx)

    # Create binary list where index i is 1 if frame i has annotation
    annotation_mask = [0] * 900
    for idx in annotated_indices:
        if idx < 900:
            annotation_mask[idx] = 1

    return annotation_mask


def process_frame(frame, back_sub, lk_params):

    # Process contours
    fg_mask = back_sub.apply(frame)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Group contours
    grouped_boxes = []
    distance_threshold = 400  # Maximum distance between contours to group them

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        # Use floating-point division for precise centroid calculation
        centroid = (x + w / 2, y + h / 2)

        grouped = False
        for group in grouped_boxes:
            group_centroid = group["centroid"]
            group_box = group["box"]
            group_area = group["area"]

            # Calculate distance between centroids using floating-point
            distance = np.sqrt(
                (centroid[0] - group_centroid[0]) ** 2 + 
                (centroid[1] - group_centroid[1]) ** 2
            )

            if distance < distance_threshold:
                # Merge bounding boxes
                x1 = min(x, group_box[0])
                y1 = min(y, group_box[1])
                x2 = max(x + w, group_box[0] + group_box[2])
                y2 = max(y + h, group_box[1] + group_box[3])
                            
                # Calculate weighted centroid using floating-point division
                total_area = area + group_area
                if total_area != 0:
                    weighted_centroid = (
                        (centroid[0] * area + group_centroid[0] * group_area) / total_area,
                        (centroid[1] * area + group_centroid[1] * group_area) / total_area
                    )
                else:
                    weighted_centroid = (
                        0,
                        0
                    )
                            
                # Store exact floating-point values
                group["box"] = (x1, y1, x2 - x1, y2 - y1)
                group["centroid"] = weighted_centroid
                group["area"] = total_area
                grouped = True
                break

        if not grouped:
            grouped_boxes.append({
                "id": len(grouped_boxes),
                "box": (x, y, w, h),
                "centroid": centroid,
                "area": area
            })

    old_gray = None # Variables for point tracking
    p0 = None  # Points to track
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Track points using optical flow
    tracked_points = []
    if old_gray is not None and p0 is not None:
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, gray, p0, None, **lk_params)

        if p1 is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            # Draw tracks and store valid points
            for new, old in zip(good_new, good_old):
                a, b = new.ravel()
                c, d = old.ravel()

                # Draw motion track
                cv2.line(frame, (int(c), int(d)), (int(a), int(b)), (0, 255, 0), 2)
                cv2.circle(frame, (int(a), int(b)), 5, (0, 0, 255), -1)

                tracked_points.append((a, b))

    # Determine activity based on both detection methods
    box_activity = len(grouped_boxes) > 0
    flow_activity = len(tracked_points) > 0
    activity = box_activity or flow_activity

    # Update coordinates based on both methods
    coordinateX = None
    coordinateY = None

    if box_activity:
        # Use first bounding box centroid
        centroid = grouped_boxes[0]["centroid"]
        coordinateX = centroid[0]
        coordinateY = centroid[1]
    elif flow_activity:
        # Use average of tracked points
        avg_x = sum(p[0] for p in tracked_points) / len(tracked_points)
        avg_y = sum(p[1] for p in tracked_points) / len(tracked_points)
        coordinateX = avg_x
        coordinateY = avg_y

    # Update points to track
    if box_activity:
        # Use box centroids as new points
        p0 = np.array([group["centroid"] for group in grouped_boxes], dtype=np.float32).reshape(-1, 1, 2)
    elif flow_activity:
        # Use tracked points as new points
        p0 = np.array(tracked_points, dtype=np.float32).reshape(-1, 1, 2)
    else:
        # No activity detected
        p0 = None

    old_gray = gray.copy()

    # Draw bounding boxes and store coordinates
    for group in grouped_boxes:
        x, y, w, h = group["box"]
        centroid = group["centroid"]
                    
        # Only round when drawing on the frame
        draw_centroid = (int(centroid[0]), int(centroid[1]))
        cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
        cv2.circle(frame, draw_centroid, 5, (0, 0, 255), -1)


    return activity

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return 0, []

    back_sub = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)

    lk_params = dict(winSize=(15, 15), maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    activity = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        active = process_frame(frame, back_sub, lk_params)
        activity.append(int(active))

    return activity


def evaluate_detection(annotation_mask, detected_activity):
    TP = FP = TN = FN = 0

    for ann, det in zip(annotation_mask, detected_activity):
        if ann == 1 and det == 1:
            TP += 1
        elif ann == 0 and det == 0:
            TN += 1
        elif ann == 0 and det == 1:
            FP += 1
        elif ann == 1 and det == 0:
            FN += 1

    return TP, TN, FP, FN


def evaluate_video_detection(video_path, json_path):
    detected_activity = process_video(video_path)
    annotation_mask = get_annotated_frames(json_path)
    TP, TN, FP, FN = evaluate_detection(annotation_mask, detected_activity)

    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) else 0
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "video": video_path,
        "annotation": json_path,
        "TP": TP,
        "TN": TN,
        "FP": FP,
        "FN": FN,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }



def run_batch_evaluation(video_annotation_pairs):
    results = []
    for video_path, json_path in video_annotation_pairs:
        print(f"\nEvaluating: {video_path} with {json_path}")
        result = evaluate_video_detection(video_path, json_path)
        results.append(result['accuracy'])

        print(f"  TP: {result['TP']}, TN: {result['TN']}, FP: {result['FP']}, FN: {result['FN']}")
        print(f"  Accuracy:  {result['accuracy']:.2f}")
        print(f"  Precision: {result['precision']:.2f}")
        print(f"  Recall:    {result['recall']:.2f}")
        print(f"  F1 Score:  {result['f1_score']:.2f}")

    return results

if __name__ == "__main__":
    test_cases = [
        ("../../assets/Camera1/00.mp4", "annotations/cam1_00.json"),
        ("../../assets/Camera1/01.mp4", "annotations/cam1_01.json"),
        ("../../assets/Camera2/00.mp4", "annotations/cam2_00.json"),
        ("../../assets/Camera2/01.mp4", "annotations/cam2_01.json"),
        ("../../assets/Camera3/00.mp4", "annotations/cam3_00.json"),
        ("../../assets/Camera3/01.mp4", "annotations/cam3_01.json")
    ]

    all_results = run_batch_evaluation(test_cases)
    r = 0.0
    for accuracy in all_results: 
        r += accuracy
    average_accuracy = r / len(all_results)
    print(f"\n  Average accuracy: {average_accuracy}")
