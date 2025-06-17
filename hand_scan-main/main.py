import cv2
import mediapipe as mp
import numpy as np
import os
import time

# Get correct file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(script_dir, "hand_template.png")
video_path = os.path.join(script_dir, "vid.mp4")

# Check if files exist
if not os.path.exists(template_path):
    print(f"Error: Template image not found at {template_path}")
    exit(1)
if not os.path.exists(video_path):
    print(f"Error: Video not found at {video_path}")
    exit(1)

# Load hand template image
template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
if template is None:
    print(f"Error: Failed to load template from {template_path}")
    exit(1)
template_h, template_w = template.shape[:2]

# Initialize camera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    # Try default camera if camera 1 is not available
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        exit(1)

# MediaPipe for hand detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7)

# Function to overlay transparent image
def overlay_image_alpha(img, img_overlay, pos):
    x, y = pos
    if img_overlay.shape[2] < 4:  # No alpha channel
        img[y:y+img_overlay.shape[0], x:x+img_overlay.shape[1]] = img_overlay
        return
        
    alpha_overlay = img_overlay[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(0, 3):
        img[y:y+img_overlay.shape[0], x:x+img_overlay.shape[1], c] = (
            alpha_overlay * img_overlay[:, :, c] +
            alpha_background * img[y:y+img_overlay.shape[0], x:x+img_overlay.shape[1], c]
        )

# Variables for state management
is_playing_video = False
video_player = None
alignment_score = 0
alignment_threshold = 0.80  # High threshold for less sensitivity
cooldown_seconds = 5  # Cooldown in seconds
cooldown_end_time = 0  # Time when cooldown will end

# Time-based alignment variables
alignment_start_time = 0  # When alignment began
required_alignment_seconds = 5  # Hold position for this many seconds

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()  # Get current time for cooldown check
    
    # Flip horizontal for mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Calculate center position for template
    center_x, center_y = w // 2 - template_w // 2, h // 2 - template_h // 2

    # If we're playing video, continue playing it
    if is_playing_video and video_player is not None:
        ret_vid, frame_vid = video_player.read()
        if ret_vid:
            cv2.imshow('Hand Scanner', frame_vid)
            if cv2.waitKey(30) & 0xFF == 27:  # ESC to exit
                break
        else:
            # Video ended, close and reset
            video_player.release()
            video_player = None
            is_playing_video = False
            cooldown_end_time = current_time + cooldown_seconds  # Set cooldown after video ends
        continue

    # Overlay template
    frame_with_overlay = frame.copy()
    overlay_image_alpha(frame_with_overlay, template, (center_x, center_y))

    # Process hand detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    alignment_detected = False
    frame_aligned = False
    
    # Check if we're in cooldown period
    in_cooldown = current_time < cooldown_end_time
    
    # Display cooldown timer if active
    if in_cooldown:
        remaining = int(cooldown_end_time - current_time) + 1
        cv2.putText(frame_with_overlay, f"Cooldown: {remaining}s", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(frame_with_overlay, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmark positions
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append((int(lm.x * w), int(lm.y * h)))
            
            # Check specific key points
            index_tip = landmarks[8]
            thumb_tip = landmarks[4]
            middle_tip = landmarks[12]
            
            # Calculate template center
            template_center_x = center_x + template_w // 2
            template_center_y = center_y + template_h // 2
            
            # Calculate distances for key points
            index_distance = np.sqrt((index_tip[0] - template_center_x)**2 + 
                                     (index_tip[1] - template_center_y)**2)
            thumb_distance = np.sqrt((thumb_tip[0] - template_center_x)**2 + 
                                     (thumb_tip[1] - template_center_y)**2)
            middle_distance = np.sqrt((middle_tip[0] - template_center_x)**2 + 
                                      (middle_tip[1] - template_center_y)**2)
            
            # Normalize distances
            max_distance = np.sqrt(w**2 + h**2)
            index_score = 1.0 - (index_distance / (max_distance * 0.3))
            thumb_score = 1.0 - (thumb_distance / (max_distance * 0.3))
            middle_score = 1.0 - (middle_distance / (max_distance * 0.3))
            
            # Combined score - weighted average
            current_score = (index_score * 0.4 + thumb_score * 0.3 + middle_score * 0.3)
            
            # Smooth alignment score with more emphasis on history
            alignment_score = 0.8 * alignment_score + 0.2 * current_score
            
            # Draw alignment score
            color = (0, 0, 255)  # Red by default
            if alignment_score > alignment_threshold * 0.7:
                color = (0, 255, 255)  # Yellow when getting closer
            if alignment_score > alignment_threshold:
                color = (0, 255, 0)  # Green when aligned
                
            cv2.putText(frame_with_overlay, f"Alignment: {alignment_score:.2f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Check if hand is aligned with template
            if alignment_score > alignment_threshold:
                frame_aligned = True
                # If this is the first aligned frame, start the timer
                if alignment_start_time == 0:
                    alignment_start_time = current_time
                
                # Calculate how long we've been aligned
                alignment_duration = current_time - alignment_start_time
                
                # Display alignment duration
                cv2.putText(frame_with_overlay, 
                           f"Hold position: {alignment_duration:.1f}/{required_alignment_seconds}s", 
                           (w//2-180, h-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Check if we've held position long enough
                if alignment_duration >= required_alignment_seconds:
                    alignment_detected = True
            else:
                # Reset alignment timer if we lost alignment
                alignment_start_time = 0

    # Show the frame with overlay
    cv2.imshow('Hand Scanner', frame_with_overlay)
    
    # If alignment detected, start playing video (only if not in cooldown)
    if alignment_detected and not is_playing_video and not in_cooldown:
        print("Alignment detected! Starting video...")
        is_playing_video = True
        video_player = cv2.VideoCapture(video_path)
        # Set cooldown when starting video
        cooldown_end_time = current_time + cooldown_seconds
        # Reset alignment timer
        alignment_start_time = 0

    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
        break

# Clean up
if video_player is not None:
    video_player.release()
cap.release()
cv2.destroyAllWindows()
