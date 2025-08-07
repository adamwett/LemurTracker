import cv2
import numpy as np

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


    return frame, coordinateX, coordinateY, activity
