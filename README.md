# Rock Paper Scissors with Hand Tracking

A real-time rock-paper-scissors game that uses computer vision to detect hand gestures, allowing you to play against a computer opponent using just your webcam.

## Features

- Real-time hand tracking using OpenCV and MediaPipe
- Gesture recognition to detect Rock, Paper, and Scissors hand shapes
- Computer opponent that plays random moves
- First to score 5 wins
- Fully responsive web interface with camera controls

## Tech Stack

- **Backend**: Python (Flask)
- **Computer Vision**: OpenCV + MediaPipe
- **Frontend**: HTML/CSS/JavaScript

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/rps-hand-tracking.git
cd rps-hand-tracking
```

2. Create a virtual environment and activate it:
```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

3. Install the required dependencies:
```
pip install flask opencv-python mediapipe numpy
```

## Usage

1. Start the Flask application:
```
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

3. Allow access to your webcam when prompted
4. Show your hand gestures to play against the computer!

## How to Play

1. Position your hand in front of the webcam
2. Make one of the following gestures:
   - **Rock**: Make a fist with all fingers curled in
   - **Paper**: Show an open hand with all fingers extended
   - **Scissors**: Extend only your index and middle fingers
3. Hold your gesture steady for a moment to make your move
4. The computer will randomly choose its move
5. First player to reach 5 points wins the game
6. Click "Reset Game" to start a new game

## Requirements

- Python 3.8+
- Webcam
- Modern web browser (Chrome, Firefox, Edge recommended)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
