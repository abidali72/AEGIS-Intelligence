import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import os
import collections
from detector import SmokingDetector
from database import Database
from notifier import AegisNotifier

class AegisIntelligenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aegis Intelligence v5.0 - Biometric & Security Platform")
        self.root.geometry("1300x900")
        ctk.set_appearance_mode("dark")
        
        self.detector = SmokingDetector()
        self.db = Database()
        self.notifier = AegisNotifier()
        
        # Camera Initialization
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        self.running = True
        self.event_buffer = collections.deque(maxlen=15) 
        self.last_log_time = 0
        
        self.setup_ui()
        
        # Start Engine
        self.thread = threading.Thread(target=self.engine_loop, daemon=True)
        self.thread.start()

    def setup_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.title_label = ctk.CTkLabel(self.sidebar, text="AEGIS v5.0", font=("Arial", 32, "bold"), text_color="#3498db")
        self.title_label.pack(pady=30, padx=20)
        
        # Status Panel
        self.status_panel = ctk.CTkFrame(self.sidebar, corner_radius=10, fg_color="#2c3e50")
        self.status_panel.pack(pady=10, padx=15, fill="x")
        
        ctk.CTkLabel(self.status_panel, text="ANALYTICS ENGINE", font=("Arial", 10, "bold")).pack(pady=(5, 0))
        self.diag_label = ctk.CTkLabel(self.status_panel, text="Initializing...", text_color="#2ecc71", font=("Arial", 14, "bold"))
        self.diag_label.pack(pady=5)
        
        # Biometrics Section
        self.bio_frame = ctk.CTkFrame(self.sidebar, corner_radius=10, fg_color="#1a252f")
        self.bio_frame.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(self.bio_frame, text="BIOMETRIC DATA", font=("Arial", 10, "bold"), text_color="gray").pack(pady=5)
        self.motion_status = ctk.CTkLabel(self.bio_frame, text="Motion: Idle", font=("Arial", 11))
        self.motion_status.pack(pady=2)
        self.height_display = ctk.CTkLabel(self.bio_frame, text="Avg Height: --", font=("Arial", 11))
        self.height_display.pack(pady=(2, 10))

        # Live Feed
        ctk.CTkLabel(self.sidebar, text="OBJECT INTELLIGENCE FEED", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.product_feed = ctk.CTkTextbox(self.sidebar, height=180, font=("Arial", 11), fg_color="#1a252f")
        self.product_feed.pack(pady=5, padx=15, fill="x")
        
        self.history_btn = ctk.CTkButton(self.sidebar, text="Unified Archive", command=self.show_history, fg_color="#2980b9", hover_color="#3498db")
        self.history_btn.pack(pady=20, padx=20)
        
        self.version_label = ctk.CTkLabel(self.sidebar, text="University Project v5.0", font=("Arial", 10, "italic"), text_color="gray")
        self.version_label.pack(side="bottom", pady=20)
        
        # Main Viewer
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="#000000")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.video_label = ctk.CTkLabel(self.main_frame, text="Booting Analytics Pipeline...", font=("Arial", 16))
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.alert_box = ctk.CTkFrame(self.main_frame, height=100, corner_radius=15, fg_color="transparent")
        self.alert_box.pack(fill="x", side="bottom", pady=10)
        
        self.alert_label = ctk.CTkLabel(self.alert_box, text="", font=("Arial", 28, "bold"))
        self.alert_label.pack(pady=10)

    def engine_loop(self):
        # Camera fallback
        if not self.cap.isOpened():
             for idx in [0, 1, 2]:
                self.cap = cv2.VideoCapture(idx)
                if self.cap.isOpened(): break

        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.5)
                    continue
                
                # Brain v5.0 Analysis
                detections, people, motion_detected = self.detector.detect(frame)
                event, diagnostic, mouth_zone = self.detector.get_contextual_event(detections, people, motion_detected)
                
                # Update UI Analytics
                self.diag_label.configure(text=f"{diagnostic}")
                self.motion_status.configure(text=f"Motion: {'DETECTED' if motion_detected else 'Idle'}", 
                                             text_color="#e74c3c" if motion_detected else "#bdc3c7")
                
                if people:
                    avg_h = sum(p["estimated_height"] for p in people) / len(people)
                    self.height_display.configure(text=f"Last Height: {avg_h:.2f}m")
                
                # Event Handling
                if event:
                    self.process_event(event, frame)
                else:
                    self.event_buffer.append(False)
                
                # UI Visualization
                display_frame = self.detector.draw_detections(frame.copy(), detections, people, mouth_zone)
                img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                
                w, h = self.video_label.winfo_width(), self.video_label.winfo_height()
                if w > 1 and h > 1:
                    img = img.resize((w, h), Image.Resampling.LANCZOS)
                
                img_tk = ImageTk.PhotoImage(image=img)
                if self.running:
                    self.video_label.configure(image=img_tk, text="")
                    self.video_label.image = img_tk
                    
            except Exception as e:
                self.diag_label.configure(text=f"Err: {str(e)[:20]}", text_color="#e74c3c")
                time.sleep(1)
            
            time.sleep(0.01)

    def process_event(self, event, frame):
        category = event["category"]
        product = event["product"]
        
        # Update Live Feed
        timestamp = time.strftime("%H:%M:%S")
        self.product_feed.insert("0.0", f"[{timestamp}] {category}: {product}\n")
        
        if category == "SMOKING":
            self.event_buffer.append(True)
            if sum(self.event_buffer) >= 8:
                self.trigger_critical_alert(frame, product)
        else:
            self.event_buffer.append(False)
            if time.time() - self.last_log_time > 15:
                self.log_to_db(frame, "BIO_LOG", product, event["confidence"])
                self.last_log_time = time.time()

    def trigger_critical_alert(self, frame, product):
        if self.alert_label.cget("text") == "":
            self.alert_label.configure(text=f"🚨 SECURITY ALERT: SMOKING ({product})", text_color="#e74c3c")
            path = self.log_to_db(frame, "SMOKING_INCIDENT", product, 0.99)
            
            # Dispatch Neural Alert (Non-blocking)
            threading.Thread(target=self.notifier.send_alert, args=(path, "SMOKING_INCIDENT", product), daemon=True).start()
            
            self.root.after(8000, self.reset_alert)

    def reset_alert(self):
        self.alert_label.configure(text="")
        self.event_buffer.clear()

    def log_to_db(self, frame, event_type, product, conf):
        if not os.path.exists("archives"): os.makedirs("archives")
        path = f"archives/{event_type.lower()}_{int(time.time())}.jpg"
        cv2.imwrite(path, frame)
        self.db.log_event(path, event_type, product, conf)
        return path

    def show_history(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Aegis Intelligence Archive")
        win.geometry("950x650")
        win.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(win, width=930, height=600)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        for h in self.db.get_history(100):
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=5, padx=5)
            color = "#c0392b" if "SMOKING" in h[3] else "#27ae60" if "BIO" in h[3] else "#2980b9"
            ctk.CTkLabel(f, text=f"[{h[1]}]", font=("Arial", 11)).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=h[3], text_color=color, font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"Target: {h[4]}", font=("Arial", 12)).pack(side="left", padx=10)

    def on_closing(self):
        self.running = False
        time.sleep(0.2)
        if self.cap.isOpened(): self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AegisIntelligenceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
