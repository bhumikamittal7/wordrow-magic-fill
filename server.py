#!/usr/bin/env python3
"""
Web server for the constraint-based word puzzle game.
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import random
import uuid
import csv
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production
CORS(app)

# Load puzzles from CSV file
PUZZLES_CSV = 'puzzles.csv'
puzzles_db = []

def load_puzzles_from_csv():
    """Load puzzles from CSV file."""
    global puzzles_db
    puzzles_db = []
    
    if not os.path.exists(PUZZLES_CSV):
        app.logger.warning(f"Puzzles CSV file '{PUZZLES_CSV}' not found. Run generate_puzzle_csv.py first.")
        return
    
    try:
        with open(PUZZLES_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                puzzle_id = int(row['puzzle_id'])
                answer = row['answer']
                guesses_data = json.loads(row['guesses_json'])
                
                puzzles_db.append({
                    'puzzle_id': puzzle_id,
                    'answer': answer,
                    'guesses': guesses_data
                })
        
        app.logger.info(f"Loaded {len(puzzles_db)} puzzles from {PUZZLES_CSV}")
    except Exception as e:
        app.logger.error(f"Error loading puzzles from CSV: {e}")
        puzzles_db = []

# Load puzzles on startup
load_puzzles_from_csv()

# Load word list for validation
word_set = set()
def load_word_list():
    """Load word list for validation."""
    global word_set
    wordlist_path = 'wordlist.txt'
    if os.path.exists(wordlist_path):
        try:
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                word_set = {line.strip().lower() for line in f if line.strip()}
            app.logger.info(f"Loaded {len(word_set)} words for validation")
        except Exception as e:
            app.logger.error(f"Error loading word list: {e}")
            word_set = set()
    else:
        app.logger.warning(f"Word list file '{wordlist_path}' not found. Word validation disabled.")

load_word_list()

# Store active puzzles (in production, use Redis or database)
# Format: {puzzle_id: {'answer': str, 'created_at': datetime, 'guesses': list}}
active_puzzles = {}

# Track which puzzles from the database have been served
# This ensures we don't repeat puzzles until all are exhausted
served_puzzle_ids = set()

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
    """Load and return a random puzzle from CSV, prioritizing unserved puzzles."""
    try:
        if not puzzles_db:
            return jsonify({'error': 'No puzzles available. Please generate puzzles first.'}), 500
        
        # Get all puzzle database IDs
        all_puzzle_ids = {p['puzzle_id'] for p in puzzles_db}
        
        # Find unserved puzzles
        unserved_ids = all_puzzle_ids - served_puzzle_ids
        
        # If all puzzles have been served, return a message
        if not unserved_ids:
            return jsonify({
                'error': 'No new puzzle available at the moment. All puzzles have been served. Please try again later.'
            }), 503  # 503 Service Unavailable
        
        # Select a random puzzle from unserved puzzles
        selected_db_id = random.choice(list(unserved_ids))
        puzzle = next(p for p in puzzles_db if p['puzzle_id'] == selected_db_id)
        
        # Mark this puzzle as served
        served_puzzle_ids.add(selected_db_id)
        
        # Generate unique puzzle ID for this session
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
        
        # Convert guesses data to frontend format
        for guess_data in puzzle['guesses']:
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
        app.logger.error(f"Error loading puzzle: {e}")
        return jsonify({'error': 'Failed to load puzzle. Please try again.'}), 500

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
        if word_set and guess not in word_set:
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

