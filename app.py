import os
import cv2
import numpy as np
import mediapipe as mp
import random
from flask import Flask, render_template, Response, jsonify, request

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Game state
scores = {"player": 0, "computer": 0}
results = {"result": "", "player_move": "", "computer_move": ""}
game_active = True
winner = None
manual_lock_requested = False
current_detected_move = "unknown"

# Gesture recognition thresholds and variables
gesture_history = []
history_length = 10  # Store last 10 frames' gestures for stability

def reset_game():
    global scores, results, game_active, winner, gesture_history, manual_lock_requested, current_detected_move
    scores = {"player": 0, "computer": 0}
    results = {"result": "", "player_move": "", "computer_move": ""}
    game_active = True
    winner = None
    gesture_history = []
    manual_lock_requested = False
    current_detected_move = "unknown"

def detect_gesture(hand_landmarks):
    """
    Detect if the hand gesture is rock, paper, or scissors
    - Rock: All fingers are curled in
    - Paper: All fingers are extended
    - Scissors: Index and middle fingers extended, others curled
    """
    # Get fingertip and finger base landmarks
    fingertips = [
        hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    ]
    
    finger_bases = [
        hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP],  # Use IP (interphalangeal) for thumb
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    ]
    
    # Check if fingers are extended or curled
    extended_fingers = []
    for i in range(5):
        # For the thumb, compare the x-coordinate due to its different orientation
        if i == 0:
            # Adjust based on which hand (left or right)
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            is_extended = (fingertips[i].x > finger_bases[i].x) if (finger_bases[i].x > wrist.x) else (fingertips[i].x < finger_bases[i].x)
        else:
            # For other fingers, compare y-coordinates
            is_extended = fingertips[i].y < finger_bases[i].y
        
        extended_fingers.append(is_extended)
    
    # Determine gesture
    if not extended_fingers[1] and not extended_fingers[2] and not extended_fingers[3] and not extended_fingers[4]:
        return "rock"
    elif extended_fingers[1] and extended_fingers[2] and not extended_fingers[3] and not extended_fingers[4]:
        return "scissors"
    elif extended_fingers[1] and extended_fingers[2] and extended_fingers[3] and extended_fingers[4]:
        return "paper"
    else:
        return "unknown"

def get_stable_gesture():
    """Return the most common non-unknown gesture from recent history with consensus"""
    if not gesture_history:
        return "unknown"

    # Consider only non-unknown frames
    filtered = [g for g in gesture_history if g in ("rock", "paper", "scissors")]
    if not filtered:
        return "unknown"

    # Count occurrences
    counts = {}
    for g in filtered:
        counts[g] = counts.get(g, 0) + 1

    # Most common gesture and its count
    gesture, cnt = max(counts.items(), key=lambda x: x[1])

    # Require at least 60% of known frames and a minimal count
    if cnt >= max(4, int(0.6 * len(filtered))):
        return gesture
    return "unknown"

def get_computer_move():
    """Generate a random move for the computer"""
    moves = ["rock", "paper", "scissors"]
    return random.choice(moves)

def determine_winner(player_move, computer_move):
    """Determine the winner based on player and computer moves"""
    if player_move == computer_move:
        return "tie"
    elif (player_move == "rock" and computer_move == "scissors") or \
         (player_move == "paper" and computer_move == "rock") or \
         (player_move == "scissors" and computer_move == "paper"):
        return "player"
    else:
        return "computer"

def generate_frames():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    global gesture_history, results, scores, game_active, winner, manual_lock_requested
    current_move = "unknown"
    prev_stable_gesture = "unknown"
    move_confirmed = False
    confirm_frames = 0           # frames needed to confirm a move
    display_frames = 0           # frames to display the round result overlay
    cooldown_frames = 0          # frames to wait before allowing next round
    countdown_frames = 0         # frames for countdown display
    CONFIRM_THRESHOLD = 90       # ~3s at ~30fps for countdown
    DISPLAY_DURATION = 60        # ~2s overlay
    COOLDOWN_DURATION = 30       # ~1s cooldown to avoid double triggers
    COUNTDOWN_DURATION = 90      # ~3s countdown
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame and detect hands
        results_mp = hands.process(rgb_frame)
        
        # Draw hand annotations on the frame
        if results_mp.multi_hand_landmarks:
            for hand_landmarks in results_mp.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
                
                # Detect gesture
                detected_gesture = detect_gesture(hand_landmarks)
                
                # Add to history and maintain its length
                gesture_history.append(detected_gesture)
                if len(gesture_history) > history_length:
                    gesture_history.pop(0)
                
                # Get stable gesture
                stable_gesture = get_stable_gesture()
                # Track and confirm stable gesture over consecutive frames
                if stable_gesture in ["rock", "paper", "scissors"]:
                    current_move = stable_gesture
                    current_detected_move = stable_gesture  # Update global for frontend
                    if stable_gesture == prev_stable_gesture:
                        if (not move_confirmed) and game_active and cooldown_frames == 0:
                            confirm_frames += 1
                            countdown_frames = COUNTDOWN_DURATION - confirm_frames
                            if confirm_frames >= CONFIRM_THRESHOLD or manual_lock_requested:
                                # Confirm move and play round
                                move_confirmed = True
                                confirm_frames = 0
                                countdown_frames = 0
                                manual_lock_requested = False
                                computer_move = get_computer_move()
                                round_winner = determine_winner(current_move, computer_move)

                                # Update results
                                results["player_move"] = current_move
                                results["computer_move"] = computer_move

                                if round_winner == "tie":
                                    results["result"] = "It's a tie!"
                                elif round_winner == "player":
                                    results["result"] = "You win this round!"
                                    scores["player"] += 1
                                else:
                                    results["result"] = "Computer wins this round!"
                                    scores["computer"] += 1

                                # Check if game is over
                                if scores["player"] >= 5:
                                    game_active = False
                                    winner = "player"
                                    results["result"] = "You win the game!"
                                elif scores["computer"] >= 5:
                                    game_active = False
                                    winner = "computer"
                                    results["result"] = "Computer wins the game!"

                                # Set overlay display and cooldown
                                display_frames = DISPLAY_DURATION
                                cooldown_frames = COOLDOWN_DURATION
                    else:
                        # Gesture changed; reset confirmation counter
                        confirm_frames = 0
                        countdown_frames = 0
                        prev_stable_gesture = stable_gesture
                else:
                    # Unknown gesture; reset confirmation
                    current_move = "unknown"
                    current_detected_move = "unknown"  # Update global
                    confirm_frames = 0
                    countdown_frames = 0
                    prev_stable_gesture = "unknown"
        else:
            # Reset when no hand is detected
            current_move = "unknown"
            current_detected_move = "unknown"  # Update global
            confirm_frames = 0
            countdown_frames = 0
            prev_stable_gesture = "unknown"
        
        # Display current gesture and game info on the frame
        cv2.putText(frame, f"Detected: {current_move}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Player: {scores['player']} Computer: {scores['computer']}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show countdown when confirming
        if countdown_frames > 0 and current_move != "unknown" and game_active:
            countdown_sec = int(countdown_frames / 30) + 1
            cv2.putText(frame, f"Confirming {current_move}... {countdown_sec}", 
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        if move_confirmed:
            cv2.putText(frame, f"Player: {results['player_move']} vs Computer: {results['computer_move']}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, results["result"], 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Handle overlay display duration and cooldown countdowns
        if display_frames > 0:
            display_frames -= 1
            if display_frames == 0:
                move_confirmed = False

        if cooldown_frames > 0:
            cooldown_frames -= 1
        
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/game_status')
def game_status():
    global scores, results, game_active, winner, current_detected_move
    return jsonify({
        "scores": scores,
        "results": results,
        "game_active": game_active,
        "winner": winner,
        "current_move": current_detected_move,
        "can_lock": game_active and not winner and current_detected_move in ["rock", "paper", "scissors"]
    })

@app.route('/lock_move', methods=['POST'])
def lock_move():
    global manual_lock_requested, current_detected_move
    if current_detected_move in ["rock", "paper", "scissors"] and game_active:
        manual_lock_requested = True
        return jsonify({"status": "success", "message": "Move lock requested"})
    else:
        return jsonify({"status": "error", "message": "No valid move to lock"})

@app.route('/reset_game', methods=['POST'])
def reset_game_route():
    reset_game()
    return jsonify({"status": "success", "message": "Game reset successfully"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
