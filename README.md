<div align="center">
  <h1>🛡️ AEGIS Intelligence v5.0</h1>
  <p><em>Advanced Biometric & Security Platform</em></p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
  [![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)](https://github.com/ultralytics/ultralytics)
  [![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green.svg)](https://opencv.org/)
  [![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
</div>

<hr />

## 📖 Overview

**AEGIS Intelligence** is a state-of-the-art computer vision and security analysis platform built for real-time monitoring and threat detection. Leveraging the power of the **YOLOv8** object detection architecture, AEGIS provides immediate insights into environments by detecting anomalous behaviors, such as indoor smoking, alongside performing basic biometric assessments. 

Designed with a sleek, futuristic interface using `customtkinter`, AEGIS acts as an intelligent surveillance dashboard suited for modern security command centers.

## ✨ Key Features

- **Real-Time Behavior Analysis**: Instantaneously detects prohibited activities (e.g., smoking) using a custom-trained YOLOv8 neural network.
- **Biometric Estimation**: Tracks motion states and estimates subject metrics such as average height in real-time.
- **Automated Event Logging**: Contextual events and critical alerts are logged to an embedded SQLite database, creating a permanent, auditable unified archive.
- **Critical Alert Pipeline**: Automatic snapshot capture and neural notification dispatch upon sustained threat detection.
- **Dark-Themed Command Center UI**: Built entirely in Python, the interface features a responsive layout, live intelligence feeds, status diagnostics, and a dedicated incident archive viewer.

## 🛠️ Technology Stack

- **Core Engine**: Python 3
- **Computer Vision**: OpenCV (`cv2`), Ultralytics YOLOv8
- **User Interface**: CustomTkinter (`customtkinter`), Pillow (`PIL`)
- **Database**: SQLite3
- **Concurrency**: Threading for non-blocking UI and background ML inference

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abidali72/AEGIS-Intelligence.git
   cd AEGIS-Intelligence
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install opencv-python customtkinter ultralytics Pillow
   ```

4. **Add YOLOv8 Weights:**
   Ensure your model file (e.g., `yolov8n.pt` or your custom `.pt` file) is present in the project root directory.

### Running the Application

Execute the main entry point to boot the analytics pipeline:

```bash
python app.py
```

## 🖥️ System Architecture

- **`app.py`**: The main GUI application and entry point.
- **`detector.py`**: The neural engine wrapping YOLOv8 for inference and bounding box rendering.
- **`database.py`**: SQLite database handler for robust event logging.
- **`notifier.py`**: Background service for dispatching alerts.
- **`web_app.py`**: Secondary web-based interface pipeline.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📄 License
This project is currently marked as an educational and research prototype (University Project v5.0).
