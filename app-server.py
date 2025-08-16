import os
import cv2
import numpy as np
import random
from flask import Flask, render_template, Response, jsonify, request

app = Flask(__name__)

# Game state
scores = {"player": 0, "computer": 0}
results = {"result": "", "player_move": "", "computer_move": ""}
game_active = True
winner = None
manual_lock_requested = False
current_detected_move = "unknown"

def reset_game():
    global scores, results, game_active, winner, manual_lock_requested, current_detected_move
    scores = {"player": 0, "computer": 0}
    results = {"result": "", "player_move": "", "computer_move": ""}
    game_active = True
    winner = None
    manual_lock_requested = False
    current_detected_move = "unknown"

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
    """Generate demo frames for deployment (no camera/MediaPipe required)"""
    frame_count = 0
    demo_moves = ["rock", "paper", "scissors"]
    
    while True:
        # Create a demo frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (40, 40, 40)  # Dark gray background
        
        # Add demo content
        cv2.putText(frame, "RPS Hand Tracking Demo", (160, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(frame, "This is a server demo version", (180, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.putText(frame, "For full hand tracking, run locally", (160, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Show current game state
        cv2.putText(frame, f"Player: {scores['player']} Computer: {scores['computer']}", 
                   (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if results["result"]:
            cv2.putText(frame, results["result"], 
                       (180, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Simulate gesture detection for demo
        if frame_count % 120 == 0:  # Every 4 seconds
            demo_move = demo_moves[frame_count // 120 % 3]
            cv2.putText(frame, f"Demo Gesture: {demo_move}", 
                       (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Add instructions
        cv2.putText(frame, "Use the manual controls below", 
                   (180, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 255), 1)
        cv2.putText(frame, "to play the game!", 
                   (220, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 255), 1)
        
        frame_count += 1
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index-server.html')

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

@app.route('/manual_play', methods=['POST'])
def manual_play():
    """Allow manual game play for demo purposes"""
    global scores, results, game_active, winner
    
    data = request.get_json()
    player_move = data.get('move')
    
    if not game_active or player_move not in ["rock", "paper", "scissors"]:
        return jsonify({"status": "error", "message": "Invalid move or game not active"})
    
    computer_move = get_computer_move()
    round_winner = determine_winner(player_move, computer_move)
    
    # Update results
    results["player_move"] = player_move
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
    
    return jsonify({"status": "success", "message": "Round played"})

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
