import json
import sys
import os
from datetime import datetime

# Add parent directory to path to import puzzle_generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from puzzle_generator import PuzzleGenerator

# Initialize generator
_generator = None
_active_puzzles = {}

def get_generator():
    """Get or create the puzzle generator."""
    global _generator
    if _generator is None:
        wordlist_path = os.path.join(os.path.dirname(__file__), '../../../wordlist.txt')
        _generator = PuzzleGenerator(wordlist_path=wordlist_path, use_curated=True, curated_size=2000)
    return _generator

def handler(event, context):
    """Netlify function handler for /api/check"""
    try:
        # Handle OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        # Parse request body
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Request body required'})
            }
        
        try:
            data = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Invalid JSON format'})
            }
        
        puzzle_id = data.get('puzzle_id')
        guess = data.get('guess', '').lower().strip()
        
        # Validate input
        if not puzzle_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Puzzle ID required'})
            }
        
        if not guess:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Guess is required'})
            }
        
        if len(guess) != 5:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Guess must be exactly 5 letters'})
            }
        
        generator = get_generator()
        
        # Validate word is in dictionary
        if guess not in generator.word_set:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': f'"{guess.upper()}" is not a valid word'})
            }
        
        # Get answer from storage (in production, use external storage)
        # For now, we'll need to share state - this is a limitation of serverless
        # In a real deployment, use a database or cache
        if puzzle_id not in _active_puzzles:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'correct': False, 'message': 'Puzzle not found or expired. Please start a new puzzle.'})
            }
        
        puzzle_data = _active_puzzles[puzzle_id]
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
            response_data['answer'] = answer.upper()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
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
            'body': json.dumps({'correct': False, 'message': 'Server error. Please try again.'})
        }

