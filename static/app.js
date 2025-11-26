// Game state
let currentPuzzle = null;
let puzzleId = null;
let currentGuess = '';
let letterStates = {}; // Track letter states for keyboard coloring

// DOM elements
const guessesContainer = document.getElementById('guesses-container');
const answerRow = document.getElementById('answer-row');
const answerBoxes = answerRow.querySelectorAll('.letter-box');
const submitBtn = document.getElementById('submit-btn');
const deleteBtn = document.getElementById('delete-btn');
const newPuzzleBtn = document.getElementById('new-puzzle-btn');
const messageDiv = document.getElementById('message');
const keyboardKeys = document.querySelectorAll('.key');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPuzzle();
    
    submitBtn.addEventListener('click', handleSubmit);
    deleteBtn.addEventListener('click', handleDelete);
    newPuzzleBtn.addEventListener('click', () => {
        if (confirm('Start a new puzzle? Your current progress will be lost.')) {
            loadPuzzle();
        }
    });
    
    // Keyboard input
    document.addEventListener('keydown', handleKeyPress);
    
    // Virtual keyboard
    keyboardKeys.forEach(key => {
        key.addEventListener('click', () => {
            const letter = key.dataset.key;
            if (currentGuess.length < 5) {
                addLetter(letter);
            }
        });
    });
});

function handleKeyPress(e) {
    // Ignore if typing in an input field
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
    }
    
    if (e.key === 'Enter') {
        handleSubmit();
    } else if (e.key === 'Backspace' || e.key === 'Delete') {
        handleDelete();
    } else if (e.key.length === 1 && /[a-zA-Z]/.test(e.key)) {
        if (currentGuess.length < 5) {
            addLetter(e.key.toUpperCase());
        }
    }
}

function addLetter(letter) {
    if (currentGuess.length < 5) {
        currentGuess += letter;
        updateAnswerRow();
    }
}

function handleDelete() {
    if (currentGuess.length > 0) {
        currentGuess = currentGuess.slice(0, -1);
        updateAnswerRow();
        clearMessage();
    }
}

function updateAnswerRow() {
    answerBoxes.forEach((box, index) => {
        if (index < currentGuess.length) {
            box.textContent = currentGuess[index];
            box.classList.remove('empty');
            box.classList.add('filled');
        } else {
            box.textContent = '';
            box.classList.remove('filled');
            box.classList.add('empty');
        }
    });
    
    submitBtn.disabled = currentGuess.length !== 5;
}

async function loadPuzzle() {
    try {
        showLoading();
        clearMessage();
        currentGuess = '';
        letterStates = {};
        puzzleId = null;
        
        // Reset answer boxes to empty state
        answerBoxes.forEach(box => {
            box.textContent = '';
            box.classList.remove('empty', 'filled', 'green', 'yellow', 'gray');
            box.classList.add('empty');
        });
        
        submitBtn.disabled = true;
        deleteBtn.disabled = true;
        resetKeyboard();
        
        const response = await fetch('/api/puzzle');
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Server error' }));
            const errorMessage = errorData.error || `Server error: ${response.status}`;
            
            // Show error message and disable buttons
            showMessage(errorMessage, 'error');
            submitBtn.disabled = true;
            deleteBtn.disabled = true;
            return;
        }
        
        const data = await response.json();
        
        if (data.error) {
            showMessage(data.error, 'error');
            submitBtn.disabled = true;
            deleteBtn.disabled = true;
            return;
        }
        
        currentPuzzle = data;
        puzzleId = data.puzzle_id;
        
        if (!puzzleId) {
            throw new Error('No puzzle ID received from server');
        }
        
        if (!data.guesses || data.guesses.length === 0) {
            throw new Error('No guesses received from server');
        }
        
        renderGuesses(data.guesses);
        updateKeyboardFromGuesses(data.guesses);
        
        submitBtn.disabled = false;
        deleteBtn.disabled = false;
        // Focus will be handled by keyboard input
        
    } catch (error) {
        console.error('Error loading puzzle:', error);
        showMessage(error.message || 'Failed to load puzzle. Please try again.', 'error');
        submitBtn.disabled = true;
        deleteBtn.disabled = true;
    }
}

function renderGuesses(guesses) {
    guessesContainer.innerHTML = '';
    
    guesses.forEach((guess, guessIndex) => {
        const guessRow = document.createElement('div');
        guessRow.className = 'guess-row';
        
        const word = guess.word;
        const constraints = guess.constraints;
        
        for (let i = 0; i < 5; i++) {
            const letterBox = document.createElement('div');
            letterBox.className = `letter-box ${constraints[i]}`;
            letterBox.textContent = word[i];
            
            // Add staggered animation
            letterBox.style.animationDelay = `${i * 0.1}s`;
            
            guessRow.appendChild(letterBox);
        }
        
        guessesContainer.appendChild(guessRow);
    });
}

function updateKeyboardFromGuesses(guesses) {
    // Reset keyboard
    resetKeyboard();
    
    // Track best state for each letter
    const letterBestState = {};
    
    guesses.forEach(guess => {
        const word = guess.word;
        const constraints = guess.constraints;
        
        for (let i = 0; i < 5; i++) {
            const letter = word[i].toUpperCase();
            const state = constraints[i];
            
            // Green > Yellow > Gray
            if (!letterBestState[letter] || 
                (state === 'green' && letterBestState[letter] !== 'green') ||
                (state === 'yellow' && letterBestState[letter] === 'gray')) {
                letterBestState[letter] = state;
            }
        }
    });
    
    // Apply states to keyboard
    Object.keys(letterBestState).forEach(letter => {
        const key = document.querySelector(`.key[data-key="${letter}"]`);
        if (key) {
            key.classList.remove('used-green', 'used-yellow', 'used-gray');
            key.classList.add(`used-${letterBestState[letter]}`);
        }
    });
}

function resetKeyboard() {
    keyboardKeys.forEach(key => {
        key.classList.remove('used-green', 'used-yellow', 'used-gray');
    });
}

async function handleSubmit() {
    const guess = currentGuess.toLowerCase();
    
    if (guess.length !== 5) {
        showMessage('Please enter a 5-letter word', 'error');
        shakeAnswerRow();
        return;
    }
    
    if (!currentPuzzle || !puzzleId) {
        showMessage('No puzzle loaded. Please start a new puzzle.', 'error');
        return;
    }
    
    try {
        submitBtn.disabled = true;
        deleteBtn.disabled = true;
        
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                puzzle_id: puzzleId,
                guess: guess
            })
        });
        
        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Server error' }));
            throw new Error(errorData.message || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.correct) {
            // Show success animation
            const answer = data.answer || guess.toUpperCase();
            showAnswerResult(true);
            showMessage(`🎉 Correct! The answer is "${answer}"`, 'success');
            submitBtn.disabled = true;
            deleteBtn.disabled = true;
        } else {
            showMessage(data.message || 'Not quite right. Try again!', 'error');
            shakeAnswerRow();
            currentGuess = '';
            updateAnswerRow();
        }
        
    } catch (error) {
        console.error('Error checking answer:', error);
        showMessage(error.message || 'Error checking answer. Please try again.', 'error');
        // Re-enable buttons on error so user can try again
        submitBtn.disabled = false;
        deleteBtn.disabled = false;
    }
}

function showAnswerResult(correct) {
    // Animate answer boxes with result
    answerBoxes.forEach((box, index) => {
        setTimeout(() => {
            box.classList.remove('empty', 'filled');
            if (correct) {
                box.classList.add('green');
            } else {
                box.classList.add('gray');
            }
        }, index * 100);
    });
}

function shakeAnswerRow() {
    answerRow.classList.add('shake');
    setTimeout(() => {
        answerRow.classList.remove('shake');
    }, 500);
}

function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'flex';
}

function clearMessage() {
    messageDiv.textContent = '';
    messageDiv.className = 'message';
    messageDiv.style.display = 'none';
}

function showLoading() {
    guessesContainer.innerHTML = '<div class="loading">Generating puzzle...</div>';
}
