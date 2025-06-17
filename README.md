# FYP Symposium Gimmick Hand Detection Keypoint

A computer vision application that detects when a hand matches a template image and triggers video playback when properly aligned.

## Description

This project uses computer vision and hand tracking to create an interactive experience. When the user's hand aligns with the provided template image, the application triggers video playback. This is good for gimmick or even officiating.

## Features

- Real-time hand tracking using MediaPipe
- Interactive template alignment guide
- Video playback when hand position matches template
- Adjustable sensitivity for alignment detection
- Time-based cooldown between interactions
- Visual feedback showing alignment progress

## Requirements

- Python 3.12.8
- OpenCV
- MediaPipe
- NumPy

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/RahulRKS01/hand-scan.git
   cd hand-scan
2. Create a virtual environment:
   ```bash
   python -m venv venv
3. Activate the virtual environment:
   Windows:
   ```bash
   venv\Scripts\activate
   ````
   macOS/Linux:
   ```bash
   source venv/bin/activate
   ````
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage

1. Ensure you have a webcam connected to your computer.
2. Run the application:
   ```bash
   python main.py
   ```
3. Position your hand to match the template overlay shown on screen.
4. Hold your hand in position for 2 seconds to trigger the video playback.
5. Watch as the video plays when your hand is properly aligned.
6. Press ESC at any time to exit the application.

## Configuration

You can modify these parameters in `main.py` to adjust the behavior:

- `alignment_threshold`: Controls how precisely your hand must match the template (0.0-1.0)
- `required_alignment_seconds`: How long to hold hand in position before triggering the video
- `cooldown_seconds`: Waiting period between activations

## Troubleshooting

- **Camera not working:** Try changing the camera index in the code from 1 to 0.
- **Template not visible:** Ensure `hand_template.png` is in the project directory.
- **Video not playing:** Verify that `vid.mp4` exists in the project directory.
- **Poor detection:** Use good lighting conditions and keep a clean background.

## License

This project is licensed under the MIT License - see the LICENSE file for
