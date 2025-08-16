document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const playerScoreElement = document.getElementById('player-score');
    const computerScoreElement = document.getElementById('computer-score');
    const resultTextElement = document.getElementById('result-text');
    const countdownTextElement = document.getElementById('countdown-text');
    const playerMoveElement = document.getElementById('player-move');
    const computerMoveElement = document.getElementById('computer-move');
    const resetGameButton = document.getElementById('reset-game');
    const lockMoveButton = document.getElementById('lock-move');
    
    // Game state
    let gameActive = true;
    let winner = null;
    let currentDetectedMove = "";
    
    // Function to update the game status from the server
    function updateGameStatus() {
        fetch('/game_status')
            .then(response => response.json())
            .then(data => {
                // Update scores
                playerScoreElement.textContent = data.scores.player;
                computerScoreElement.textContent = data.scores.computer;
                
                // Update results
                if (data.results.result) {
                    resultTextElement.textContent = data.results.result;
                }
                
                // Update moves
                if (data.results.player_move) {
                    playerMoveElement.textContent = data.results.player_move;
                }
                
                if (data.results.computer_move) {
                    computerMoveElement.textContent = data.results.computer_move;
                }
                
                // Update current detected move for lock button
                currentDetectedMove = data.current_move || "";
                
                // Update game state
                gameActive = data.game_active;
                winner = data.winner;
                
                // Update lock button state
                if (data.can_lock && currentDetectedMove && 
                    ['rock', 'paper', 'scissors'].includes(currentDetectedMove)) {
                    lockMoveButton.disabled = false;
                    lockMoveButton.textContent = `Lock ${currentDetectedMove}`;
                } else {
                    lockMoveButton.disabled = true;
                    lockMoveButton.textContent = 'Lock Move';
                }
                
                // Visual feedback based on game state
                if (!gameActive && winner) {
                    resultTextElement.style.color = winner === 'player' ? '#27ae60' : '#e74c3c';
                    resultTextElement.style.fontSize = '1.5rem';
                } else {
                    resultTextElement.style.color = '#3498db';
                    resultTextElement.style.fontSize = '1.2rem';
                }
            })
            .catch(error => {
                console.error('Error fetching game status:', error);
            });
    }
    
    // Lock move function
    function lockMove() {
        fetch('/lock_move', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                lockMoveButton.disabled = true;
                countdownTextElement.textContent = 'Move locked! Playing round...';
            }
        })
        .catch(error => {
            console.error('Error locking move:', error);
        });
    }
    
    // Reset game function
    function resetGame() {
        fetch('/reset_game', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Reset UI elements
                playerScoreElement.textContent = '0';
                computerScoreElement.textContent = '0';
                resultTextElement.textContent = 'Show your hand gesture to play!';
                countdownTextElement.textContent = '';
                playerMoveElement.textContent = '-';
                computerMoveElement.textContent = '-';
                
                // Reset styling
                resultTextElement.style.color = '#3498db';
                resultTextElement.style.fontSize = '1.2rem';
                
                // Reset game state
                gameActive = true;
                winner = null;
                currentDetectedMove = "";
                
                // Reset lock button
                lockMoveButton.disabled = true;
                lockMoveButton.textContent = 'Lock Move';
            }
        })
        .catch(error => {
            console.error('Error resetting game:', error);
        });
    }
    
    // Add event listeners
    resetGameButton.addEventListener('click', resetGame);
    lockMoveButton.addEventListener('click', lockMove);
    
    // Update game status every 500ms
    setInterval(updateGameStatus, 500);
    
    // Handle video feed errors
    const videoFeed = document.getElementById('video-feed');
    videoFeed.onerror = function() {
        resultTextElement.textContent = 'Error loading video feed. Please refresh the page.';
        resultTextElement.style.color = '#e74c3c';
    };
    
    // Improve mobile experience
    const videoContainer = document.querySelector('.video-container');
    
    // Function to check if device is in portrait mode
    function isPortrait() {
        return window.innerHeight > window.innerWidth;
    }
    
    // Function to adjust video container height on mobile
    function adjustVideoHeight() {
        if (window.innerWidth <= 768) {
            const screenHeight = window.innerHeight;
            const headerHeight = document.querySelector('h1').offsetHeight;
            const gameInfoHeight = document.querySelector('.game-info').offsetHeight;
            const instructionsHeight = document.querySelector('.instructions').offsetHeight;
            const controlsHeight = document.querySelector('.controls').offsetHeight;
            
            // Calculate available height
            const availableHeight = screenHeight - headerHeight - gameInfoHeight - instructionsHeight - controlsHeight - 100; // 100px for margins/padding
            
            // Set max-height for video feed
            if (isPortrait() && availableHeight > 200) {
                videoFeed.style.maxHeight = availableHeight + 'px';
            } else {
                videoFeed.style.maxHeight = 'none';
            }
        } else {
            videoFeed.style.maxHeight = 'none';
        }
    }
    
    // Call on load and on resize
    window.addEventListener('load', adjustVideoHeight);
    window.addEventListener('resize', adjustVideoHeight);
});
