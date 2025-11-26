# Better Wordrow - Constraint-Based Word Puzzle Game

A constraint-based word puzzle game where players use 4 words with Wordle-style constraints (green/yellow/gray) to deduce the answer word.

## Features

- **Fast Puzzle Generation**: Optimized algorithm using letter frequency analysis and constraint satisfaction
- **Beautiful UI**: Minimal, modern frontend with smooth animations
- **Smart Word Selection**: Uses Wordle answer frequency patterns (ERAOTI LSCNUD) for better puzzles
- **Curated Word Lists**: Uses a curated subset for faster proof of concept, expandable to full list

## Algorithm Improvements

1. **Letter Frequency Analysis**: Uses Wordle answer letter frequencies (e:53%, a:42%, r:39%, etc.) instead of general English frequencies
2. **Position-Specific Frequencies**: Considers which letters are more common at each position
3. **Optimized Constraint Satisfaction**: Fast filtering with early termination
4. **Greedy Word Selection**: Maximizes information gain at each step
5. **Curated Subset**: Uses top 2000 most informative words for faster generation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start the server:
```bash
python server.py
```

Then open `http://localhost:5000` in your browser.

### Generate puzzles programmatically:
```python
from puzzle_generator import PuzzleGenerator

# Use curated subset (faster, ~2000 words)
generator = PuzzleGenerator(use_curated=True, curated_size=2000)

# Or use full word list (slower, ~16000 words)
generator = PuzzleGenerator(use_curated=False)

# Generate a puzzle
puzzle = generator.generate_puzzle()
print(f"Answer: {puzzle['answer']}")
for guess_data in puzzle['constraints']:
    print(f"Guess: {guess_data['word']}")
```

## Performance

- **Curated mode** (2000 words): ~0.3-0.5 seconds per puzzle
- **Full mode** (16000 words): ~2-5 seconds per puzzle

## How It Works

1. **Word Selection**: Uses frequency analysis to select informative guess words
2. **Constraint Generation**: Applies Wordle rules (green = correct position, yellow = wrong position, gray = not in word)
3. **Constraint Satisfaction**: Filters candidate words efficiently using pre-computed constraints
4. **Uniqueness Check**: Verifies that the 4 guesses uniquely identify the answer

## File Structure

- `puzzle_generator.py` - Core puzzle generation algorithm
- `server.py` - Flask web server
- `static/` - Frontend files (HTML, CSS, JS)
- `wordlist.txt` - Dictionary of 5-letter words
- `generate_wordlist.py` - Script to generate/update word list
