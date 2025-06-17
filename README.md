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
