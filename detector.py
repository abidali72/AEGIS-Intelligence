import cv2
import numpy as np
from ultralytics import YOLO
import os

class SmokingDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # Load YOLOv8 for general object detection
        self.model = YOLO(model_path)
        
        # Motion Detection: MOG2
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
        
        # Calibration for Height Estimation
        # Example scale_factor: meters per pixel
        # This normally requires calibration (e.g., 1m = 300px at a certain distance)
        # We will use a baseline heuristic: 1.7m = 60% of vertical frame height at average distance
        self.scale_factor = 0.005 # Default placeholder (calibrated for roughly 1.7m at mid-distance)
        self.height_history = {} # Store moving averages for height stability

    def detect(self, frame):
        h, w, _ = frame.shape
        
        # 1. Motion Masking
        fgmask = self.fgbg.apply(frame)
        motion_detected = cv2.countNonZero(fgmask) > 5000 # Threshold for noise
        
        # 2. YOLOv8 Detections
        results = self.model(frame, verbose=False)
        detections = []
        people = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                label = self.model.names[cls]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                det = {
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                }
                
                if label == "person":
                    # Estimate Height
                    est_height = self.estimate_height(det, h)
                    det["estimated_height"] = est_height
                    people.append(det)
                else:
                    relevant_labels = ["cell phone", "remote", "cup", "bottle", "toothbrush", "scissors", "spoon", "book"]
                    if label in relevant_labels or conf < 0.25:
                        detections.append(det)
        
        return detections, people, motion_detected

    def estimate_height(self, person_det, frame_h):
        """
        Proportional Height Estimation:
        h_pixels / frame_h * world_constant
        """
        x1, y1, x2, y2 = person_det["bbox"]
        box_h = y2 - y1
        
        # Basic heuristic: If the person fills the whole vertical frame, they are roughly 1.8m
        # (Assuming the camera is at chest height or slightly angled)
        # We calibrate based on a 0.0035 multiplier for a standard webcam FOV
        raw_height = box_h * 0.0035 
        
        # Temporal Smoothing: Use moving average of 10 frames
        # For simplicity in this engine, we'll return the raw rounded to 2 decimal places
        return round(raw_height, 2)

    def classify_product(self, detection):
        label = detection["label"]
        conf = detection["confidence"]
        
        classmap = {
            "cell phone": "Smart Device",
            "remote": "Electronic Device",
            "cup": "Beverage Container",
            "bottle": "Bottle",
            "toothbrush": "Personal Item",
            "spoon": "Utensil",
            "scissors": "Tool",
            "book": "Document"
        }
        
        refined_label = classmap.get(label, "Unidentified Object")
        if conf < 0.20:
            refined_label = "Suspected Cigarette"
            
        return refined_label

    def get_contextual_event(self, detections, people, motion_detected):
        """
        Brain v5.0 Context Engine:
        Adds motion status and biometric analytics to the event stream.
        """
        if not people:
            status = "Motion Detected" if motion_detected else "Static/Empty"
            return None, status, None

        highest_conf_event = None
        main_diagnostic = "Monitoring System"
        
        for p in people:
            px1, py1, px2, py2 = p["bbox"]
            pw, ph = px2 - px1, py2 - py1
            est_h = p["estimated_height"]
            
            # Mouth Zone Calculation
            mx1, my1 = px1 + int(pw * 0.35), py1 + int(ph * 0.15)
            mx2, my2 = px1 + int(pw * 0.65), py1 + int(ph * 0.35)
            mouth_zone = [mx1, my1, mx2, my2]
            
            main_diagnostic = f"Tracking: {est_h}m"
            
            for d in detections:
                prod_name = self.classify_product(d)
                ox1, oy1, ox2, oy2 = d["bbox"]
                ocx, ocy = (ox1 + ox2) / 2, (oy1 + oy2) / 2
                
                # Check intersection with mouth zone
                if (mx1 <= ocx <= mx2) and (my1 <= ocy <= my2):
                    final_label = "Cigarette" if prod_name == "Suspected Cigarette" else prod_name
                    return {
                        "category": "SMOKING",
                        "product": final_label,
                        "confidence": d["confidence"],
                        "message": f"ALERT: {final_label} at Mouth"
                    }, f"Critical: Smoking ({est_h}m)", mouth_zone

                if highest_conf_event is None or d["confidence"] > highest_conf_event["confidence"]:
                    highest_conf_event = {
                        "category": "PRODUCT",
                        "product": prod_name,
                        "confidence": d["confidence"],
                        "message": f"Log: {prod_name} detected"
                    }

        if highest_conf_event:
            return highest_conf_event, highest_conf_event["message"], None
            
        return None, main_diagnostic, None

    def draw_detections(self, frame, detections, people, mouth_zone):
        # Draw Persons with Height
        for p in people:
            x1, y1, x2, y2 = p["bbox"]
            h_val = p["estimated_height"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
            # Banner for Height
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + 100, y1), (255, 255, 255), -1)
            cv2.putText(frame, f"HEIGHT: {h_val}m", (x1 + 5, y1 - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
            
        # Draw Mouth Zone
        if mouth_zone:
            mx1, my1, mx2, my2 = mouth_zone
            cv2.rectangle(frame, (mx1, my1), (mx2, my2), (255, 0, 0), 2)

        # Draw Objects
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            prod_name = self.classify_product(d)
            color = (0, 0, 255) if "Cigarette" in prod_name else (255, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.putText(frame, f"{prod_name}", (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
        return frame
