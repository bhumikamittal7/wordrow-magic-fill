#!/usr/bin/env python3
"""
Generate a CSV file containing multiple word puzzles with answers.
"""

import csv
import json
from puzzle_generator import PuzzleGenerator
import argparse

def generate_puzzles_csv(output_file='puzzles.csv', num_puzzles=30, use_curated=False):
    """
    Generate multiple puzzles and save to CSV.
    
    Args:
        output_file: Output CSV file path
        num_puzzles: Number of puzzles to generate
        use_curated: Whether to use curated word subset (False = use full list)
    """
    print(f"Initializing puzzle generator with {'curated' if use_curated else 'full'} word list...")
    generator = PuzzleGenerator(use_curated=use_curated, curated_size=2000)
    
    print(f"Generating {num_puzzles} puzzles...")
    puzzles = []
    
    for i in range(num_puzzles):
        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{num_puzzles} puzzles...")
        
        try:
            puzzle = generator.generate_puzzle(max_attempts=500)
            
            # Format puzzle data - store constraints as JSON for easier parsing
            puzzle_data = {
                'puzzle_id': i + 1,
                'answer': puzzle['answer'],
                'guesses_json': json.dumps([
                    {
                        'word': puzzle['guesses'][j] if j < len(puzzle['guesses']) else '',
                        'constraints': puzzle['constraints'][j]['constraints'] if j < len(puzzle['constraints']) else []
                    }
                    for j in range(4)
                ]),
                'valid_answers_json': json.dumps(puzzle.get('valid_answers', [puzzle['answer']]))
            }
            
            puzzles.append(puzzle_data)
            
        except Exception as e:
            print(f"Error generating puzzle {i + 1}: {e}")
            continue
    
    # Write to CSV
    print(f"\nWriting {len(puzzles)} puzzles to {output_file}...")
    
    fieldnames = [
        'puzzle_id',
        'answer',
        'guesses_json',
        'valid_answers_json'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(puzzles)
    
    print(f"✓ Successfully generated {len(puzzles)} puzzles in {output_file}")
    
    # Print summary
    unique_answers = len(set(p['answer'] for p in puzzles))
    
    print(f"\nSummary:")
    print(f"  Total puzzles: {len(puzzles)}")
    print(f"  Unique answers: {unique_answers}")


def format_constraints(constraints):
    """
    Format constraints as a string representation.
    Example: "G-G-Y-G-X" where G=green, Y=yellow, X=gray
    """
    if not constraints:
        return ''
    
    # Create array of constraint types by position
    constraint_array = ['X'] * 5  # X = gray by default
    for constraint in constraints:
        pos = constraint['position']
        constraint_type = constraint['type']
        if constraint_type == 'green':
            constraint_array[pos] = 'G'
        elif constraint_type == 'yellow':
            constraint_array[pos] = 'Y'
        else:
            constraint_array[pos] = 'X'
    
    return '-'.join(constraint_array)


def main():
    parser = argparse.ArgumentParser(description='Generate word puzzle CSV file')
    parser.add_argument('-n', '--num', type=int, default=30,
                       help='Number of puzzles to generate (default: 30)')
    parser.add_argument('-o', '--output', type=str, default='puzzles.csv',
                       help='Output CSV file path (default: puzzles.csv)')
    parser.add_argument('--curated', action='store_true',
                       help='Use curated word subset instead of full list (faster but less comprehensive)')
    
    args = parser.parse_args()
    
    generate_puzzles_csv(
        output_file=args.output,
        num_puzzles=args.num,
        use_curated=args.curated
    )


if __name__ == '__main__':
    main()

