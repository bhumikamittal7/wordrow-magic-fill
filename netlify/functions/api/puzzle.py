import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import puzzle_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from puzzle_generator import PuzzleGenerator
import uuid

# Initialize generator (this will be reused across invocations)
# Note: In serverless, this may be recreated, but Netlify tries to reuse
_generator = None
_active_puzzles = {}

def get_generator():
    """Get or create the puzzle generator."""
    global _generator
    if _generator is None:
        # Get wordlist path - in Netlify, files are in the repo root
        wordlist_path = os.path.join(os.path.dirname(__file__), '../../../wordlist.txt')
        _generator = PuzzleGenerator(wordlist_path=wordlist_path, use_curated=True, curated_size=2000)
    return _generator

def cleanup_old_puzzles():
    """Remove puzzles older than 1 hour."""
    now = datetime.now()
    expired_ids = [
        pid for pid, data in _active_puzzles.items()
        if now - data['created_at'] > timedelta(hours=1)
    ]
    for pid in expired_ids:
        del _active_puzzles[pid]

def handler(event, context):
    """Netlify function handler for /api/puzzle"""
    try:
        generator = get_generator()
        
        # Generate puzzle
        puzzle = generator.generate_puzzle(answer=None, max_attempts=500)
        
        # Generate unique puzzle ID
        puzzle_id = str(uuid.uuid4())
        
        # Store puzzle answer server-side
        _active_puzzles[puzzle_id] = {
            'answer': puzzle['answer'],
            'created_at': datetime.now(),
            'guesses': []
        }
        
        # Clean up old puzzles
        cleanup_old_puzzles()
        
        # Format for frontend
        response_data = {
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
            
            response_data['guesses'].append({
                'word': word,
                'constraints': constraint_array
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps(response_data)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to generate puzzle. Please try again.'})
        }

