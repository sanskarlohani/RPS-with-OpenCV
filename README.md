# Rock Paper Scissors with Hand Tracking

A real-time rock-paper-scissors game that uses computer vision to detect hand gestures, allowing you to play against a computer opponent using just your webcam.

🎮 **[Play Live Demo](https://your-app-name.onrender.com)** (Deploy to get this link)

## Features

- Real-time hand tracking using OpenCV and MediaPipe
- Gesture recognition to detect Rock, Paper, and Scissors hand shapes
- Computer opponent that plays random moves
- First to score 5 wins
- Fully responsive web interface with camera controls
- Visual countdown timer and manual lock button

## Tech Stack

- **Backend**: Python (Flask)
- **Computer Vision**: OpenCV + MediaPipe
- **Frontend**: HTML/CSS/JavaScript
- **Deployment**: Render/Heroku/Railway

## Quick Deploy

### Deploy to Render (Free)
1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Connect your GitHub and select this repo
4. Choose "Web Service"
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
6. Deploy!

### Deploy to Heroku
```bash
# Install Heroku CLI first
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Connect GitHub repo
3. Deploy automatically

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
