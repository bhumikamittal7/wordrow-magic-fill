#!/usr/bin/env python3
"""
Web server for the constraint-based word puzzle game.
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from puzzle_generator import PuzzleGenerator
import random
import uuid
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production
CORS(app)

# Initialize puzzle generator with curated subset for faster generation
# Set use_curated=False to use full word list (slower but more comprehensive)
generator = PuzzleGenerator(use_curated=True, curated_size=2000)

# Store active puzzles (in production, use Redis or database)
# Format: {puzzle_id: {'answer': str, 'created_at': datetime, 'guesses': list}}
active_puzzles = {}

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')

@app.route('/style.css')
def serve_css():
    """Serve CSS file."""
    return send_from_directory('static', 'style.css')

@app.route('/app.js')
def serve_js():
    """Serve JavaScript file."""
    return send_from_directory('static', 'app.js')

@app.route('/api/puzzle', methods=['GET'])
def get_puzzle():
    """Generate and return a new puzzle."""
    try:
        # Optionally accept answer parameter
        answer = None
        # For now, generate random puzzle
        puzzle = generator.generate_puzzle(answer=answer, max_attempts=500)
        
        # Generate unique puzzle ID
        puzzle_id = str(uuid.uuid4())
        
        # Store puzzle answer server-side (don't trust client)
        active_puzzles[puzzle_id] = {
            'answer': puzzle['answer'],
            'created_at': datetime.now(),
            'guesses': []
        }
        
        # Clean up old puzzles (older than 1 hour)
        cleanup_old_puzzles()
        
        # Format for frontend
        response = {
            'puzzle_id': puzzle_id,
            'guesses': []
        }
        
        for guess_data in puzzle['constraints']:
            word = guess_data['word']
            constraints = guess_data['constraints']
            
            # Create a simple array representation: [type, type, type, type, type]
            constraint_array = ['gray'] * 5
            for constraint in constraints:
                pos = constraint['position']
                constraint_type = constraint['type']
                constraint_array[pos] = constraint_type
            
            response['guesses'].append({
                'word': word,
                'constraints': constraint_array
            })
        
        return jsonify(response)
    except Exception as e:
        app.logger.error(f"Error generating puzzle: {e}")
        return jsonify({'error': 'Failed to generate puzzle. Please try again.'}), 500

@app.route('/api/check', methods=['POST'])
def check_answer():
    """Check if a user's guess is correct."""
    try:
        if not request.is_json:
            return jsonify({'correct': False, 'message': 'Invalid request format'}), 400
        
        data = request.json
        puzzle_id = data.get('puzzle_id')
        guess = data.get('guess', '').lower().strip()
        
        # Validate input
        if not puzzle_id:
            return jsonify({'correct': False, 'message': 'Puzzle ID required'}), 400
        
        if not guess:
            return jsonify({'correct': False, 'message': 'Guess is required'}), 400
        
        if len(guess) != 5:
            return jsonify({'correct': False, 'message': 'Guess must be exactly 5 letters'}), 400
        
        # Validate word is in dictionary
        if guess not in generator.word_set:
            return jsonify({'correct': False, 'message': f'"{guess.upper()}" is not a valid word'}), 400
        
        # Get answer from server-side storage (don't trust client)
        if puzzle_id not in active_puzzles:
            return jsonify({'correct': False, 'message': 'Puzzle not found or expired. Please start a new puzzle.'}), 404
        
        puzzle_data = active_puzzles[puzzle_id]
        answer = puzzle_data['answer']
        
        # Track guess
        puzzle_data['guesses'].append({
            'guess': guess,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check if correct
        correct = (guess == answer)
        
        response_data = {
            'correct': correct,
            'message': 'Correct!' if correct else 'Try again!'
        }
        
        if correct:
            # Optionally clean up puzzle after correct answer
            # del active_puzzles[puzzle_id]
            response_data['answer'] = answer.upper()
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Error checking answer: {e}")
        return jsonify({'correct': False, 'message': 'Server error. Please try again.'}), 500


def cleanup_old_puzzles():
    """Remove puzzles older than 1 hour."""
    now = datetime.now()
    expired_ids = [
        pid for pid, data in active_puzzles.items()
        if now - data['created_at'] > timedelta(hours=1)
    ]
    for pid in expired_ids:
        del active_puzzles[pid]

if __name__ == '__main__':
    app.run(debug=True, port=8000)

