#!/usr/bin/env python3
"""
Generate a CSV file containing multiple word puzzles with answers.
"""

import csv
import json
from puzzle_generator import PuzzleGenerator
import argparse

def generate_puzzles_csv(output_file='puzzles.csv', num_puzzles=100, use_curated=True):
    """
    Generate multiple puzzles and save to CSV.
    
    Args:
        output_file: Output CSV file path
        num_puzzles: Number of puzzles to generate
        use_curated: Whether to use curated word subset
    """
    print(f"Initializing puzzle generator...")
    generator = PuzzleGenerator(use_curated=use_curated, curated_size=2000)
    
    print(f"Generating {num_puzzles} puzzles...")
    puzzles = []
    
    for i in range(num_puzzles):
        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{num_puzzles} puzzles...")
        
        try:
            puzzle = generator.generate_puzzle(max_attempts=500)
            
            # Format puzzle data
            puzzle_data = {
                'puzzle_id': i + 1,
                'answer': puzzle['answer'],
                'guess_1': puzzle['guesses'][0] if len(puzzle['guesses']) > 0 else '',
                'guess_1_constraints': format_constraints(puzzle['constraints'][0]['constraints']) if len(puzzle['constraints']) > 0 else '',
                'guess_2': puzzle['guesses'][1] if len(puzzle['guesses']) > 1 else '',
                'guess_2_constraints': format_constraints(puzzle['constraints'][1]['constraints']) if len(puzzle['constraints']) > 1 else '',
                'guess_3': puzzle['guesses'][2] if len(puzzle['guesses']) > 2 else '',
                'guess_3_constraints': format_constraints(puzzle['constraints'][2]['constraints']) if len(puzzle['constraints']) > 2 else '',
                'guess_4': puzzle['guesses'][3] if len(puzzle['guesses']) > 3 else '',
                'guess_4_constraints': format_constraints(puzzle['constraints'][3]['constraints']) if len(puzzle['constraints']) > 3 else '',
                'candidates_remaining': puzzle.get('candidates_remaining', 1)
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
        'guess_1', 'guess_1_constraints',
        'guess_2', 'guess_2_constraints',
        'guess_3', 'guess_3_constraints',
        'guess_4', 'guess_4_constraints',
        'candidates_remaining'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(puzzles)
    
    print(f"✓ Successfully generated {len(puzzles)} puzzles in {output_file}")
    
    # Print summary
    unique_answers = len(set(p['answer'] for p in puzzles))
    perfect_puzzles = sum(1 for p in puzzles if p['candidates_remaining'] == 1)
    
    print(f"\nSummary:")
    print(f"  Total puzzles: {len(puzzles)}")
    print(f"  Unique answers: {unique_answers}")
    print(f"  Perfect puzzles (unique solution): {perfect_puzzles}")
    print(f"  Puzzles with multiple candidates: {len(puzzles) - perfect_puzzles}")


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
    parser.add_argument('-n', '--num', type=int, default=100,
                       help='Number of puzzles to generate (default: 100)')
    parser.add_argument('-o', '--output', type=str, default='puzzles.csv',
                       help='Output CSV file path (default: puzzles.csv)')
    parser.add_argument('--full-list', action='store_true',
                       help='Use full word list instead of curated subset (slower)')
    
    args = parser.parse_args()
    
    generate_puzzles_csv(
        output_file=args.output,
        num_puzzles=args.num,
        use_curated=not args.full_list
    )


if __name__ == '__main__':
    main()

