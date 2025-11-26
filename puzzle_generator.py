#!/usr/bin/env python3
"""
Constraint-based word puzzle generator.
Generates 4 words with constraints (green/yellow/gray) that uniquely identify an answer word.
Uses efficient constraint satisfaction approach.
"""

import random
from typing import List, Tuple, Dict, Set, Optional
from collections import Counter, defaultdict

class WordleConstraints:
    """Represents Wordle-style constraints (green, yellow, gray)."""
    
    GREEN = 'green'
    YELLOW = 'yellow'
    GRAY = 'gray'
    
    @staticmethod
    def get_constraints(guess: str, answer: str) -> List[Tuple[str, int, str]]:
        """
        Get constraints for a guess word against an answer.
        Returns list of (letter, position, constraint_type) tuples.
        
        Args:
            guess: The guess word
            answer: The answer word
            
        Returns:
            List of (letter, position, constraint_type) where constraint_type is 'green', 'yellow', or 'gray'
        """
        constraints = []
        answer_counts = Counter(answer)
        used_positions = set()
        
        # First pass: mark greens (exact matches)
        for i in range(5):
            if guess[i] == answer[i]:
                constraints.append((guess[i], i, WordleConstraints.GREEN))
                used_positions.add(i)
                answer_counts[guess[i]] -= 1
        
        # Second pass: mark yellows (letter in word but wrong position)
        for i in range(5):
            if i not in used_positions:
                if guess[i] in answer_counts and answer_counts[guess[i]] > 0:
                    constraints.append((guess[i], i, WordleConstraints.YELLOW))
                    answer_counts[guess[i]] -= 1
                else:
                    constraints.append((guess[i], i, WordleConstraints.GRAY))
        
        return constraints
    
    @staticmethod
    def word_satisfies_constraints(word: str, constraints: List[Tuple[str, int, str]]) -> bool:
        """
        Check if a word satisfies all given constraints.
        
        Args:
            word: Word to check
            constraints: List of (letter, position, constraint_type) tuples
            
        Returns:
            True if word satisfies all constraints
        """
        word_counts = Counter(word)
        constraint_counts = Counter()
        
        # Check green constraints (exact position matches)
        for letter, pos, constraint_type in constraints:
            if constraint_type == WordleConstraints.GREEN:
                if word[pos] != letter:
                    return False
                constraint_counts[letter] += 1
        
        # Check yellow constraints (letter in word but not at this position)
        for letter, pos, constraint_type in constraints:
            if constraint_type == WordleConstraints.YELLOW:
                if word[pos] == letter:  # Can't be at this position
                    return False
                if letter not in word:
                    return False
                constraint_counts[letter] += 1
        
        # Check gray constraints (letter not in word)
        for letter, pos, constraint_type in constraints:
            if constraint_type == WordleConstraints.GRAY:
                if letter in word:
                    # But only if it's not required by green/yellow
                    if constraint_counts[letter] >= word_counts[letter]:
                        return False
        
        # Verify minimum letter counts (for yellows and greens)
        for letter, count in constraint_counts.items():
            if word_counts[letter] < count:
                return False
        
        return True


class LetterFrequencyAnalyzer:
    """Analyzes letter frequencies for better word selection."""
    
    # Wordle answer letter frequencies
    # e:53% a:42% r:39% o:33% t:31% l:31% i:29% s:29% n:25% c:21% u:20% y:18% d:17% h:17% p:16% m:14% g:13% b:12% f:10% k:9% w:8% v:7% z:2% x:2% q:1% j:1%
    WORDLE_FREQUENCIES = {
        'e': 0.53, 'a': 0.42, 'r': 0.39, 'o': 0.33, 't': 0.31, 'l': 0.31,
        'i': 0.29, 's': 0.29, 'n': 0.25, 'c': 0.21, 'u': 0.20, 'y': 0.18,
        'd': 0.17, 'h': 0.17, 'p': 0.16, 'm': 0.14, 'g': 0.13, 'b': 0.12,
        'f': 0.10, 'k': 0.09, 'w': 0.08, 'v': 0.07, 'z': 0.02, 'x': 0.02,
        'q': 0.01, 'j': 0.01
    }
    
    @staticmethod
    def compute_frequencies(words: List[str]) -> Dict[str, float]:
        """Compute letter frequencies from word list."""
        total_letters = 0
        letter_counts = Counter()
        
        for word in words:
            for letter in word:
                letter_counts[letter] += 1
                total_letters += 1
        
        return {letter: count / total_letters for letter, count in letter_counts.items()}
    
    @staticmethod
    def compute_position_frequencies(words: List[str]) -> List[Dict[str, float]]:
        """Compute letter frequencies for each position (0-4)."""
        position_counts = [Counter() for _ in range(5)]
        position_totals = [0] * 5
        
        for word in words:
            for pos, letter in enumerate(word):
                position_counts[pos][letter] += 1
                position_totals[pos] += 1
        
        return [
            {letter: count / position_totals[pos] 
             for letter, count in position_counts[pos].items()}
            for pos in range(5)
        ]
    
    @staticmethod
    def word_score(word: str, position_freqs: List[Dict[str, float]], 
                   letter_freqs: Dict[str, float]) -> float:
        """Score a word based on letter frequencies (higher = more informative)."""
        score = 0.0
        seen_letters = set()
        
        for pos, letter in enumerate(word):
            # Position-specific frequency
            if pos < len(position_freqs) and letter in position_freqs[pos]:
                score += position_freqs[pos][letter] * 2
            
            # Overall letter frequency (only count once per letter)
            if letter not in seen_letters:
                score += letter_freqs.get(letter, 0.01)
                seen_letters.add(letter)
        
        return score


class PuzzleGenerator:
    """Generates constraint-based word puzzles with optimized algorithms."""
    
    def __init__(self, wordlist_path: str = "wordlist.txt", use_curated: bool = True, 
                 curated_size: int = 5000):
        """
        Initialize with word list.
        
        Args:
            wordlist_path: Path to word list file
            use_curated: If True, use a curated subset of common words for faster generation
            curated_size: Size of curated subset to use
        """
        with open(wordlist_path, 'r') as f:
            all_words = [line.strip().lower() for line in f if line.strip()]
        
        if use_curated and len(all_words) > curated_size:
            # Use frequency analysis to select most informative/common words
            print(f"Selecting curated subset of {curated_size} words from {len(all_words)}...")
            self.words = self._select_curated_words(all_words, curated_size)
            print(f"Using curated set of {len(self.words)} words")
        else:
            self.words = all_words
        
        self.word_set = set(self.words)
        
        # Pre-compute frequency data for optimization
        self.letter_freqs = LetterFrequencyAnalyzer.compute_frequencies(self.words)
        self.position_freqs = LetterFrequencyAnalyzer.compute_position_frequencies(self.words)
        
        # Pre-compute word scores for faster selection
        self.word_scores = {
            word: LetterFrequencyAnalyzer.word_score(word, self.position_freqs, self.letter_freqs)
            for word in self.words
        }
        
        print(f"Loaded {len(self.words)} words with frequency analysis")
    
    def _select_curated_words(self, words: List[str], size: int) -> List[str]:
        """Select a curated subset of words based on frequency and commonality."""
        # Compute frequencies from full list
        letter_freqs = LetterFrequencyAnalyzer.compute_frequencies(words)
        position_freqs = LetterFrequencyAnalyzer.compute_position_frequencies(words)
        
        # Score all words
        scored_words = [
            (word, LetterFrequencyAnalyzer.word_score(word, position_freqs, letter_freqs))
            for word in words
        ]
        
        # Sort by score (higher = more informative/common)
        scored_words.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N, but also add some random diversity
        selected = set()
        
        # Top 70% by score
        top_count = int(size * 0.7)
        for word, _ in scored_words[:top_count]:
            selected.add(word)
        
        # Add 30% random for diversity
        remaining = size - len(selected)
        random_words = random.sample([w for w in words if w not in selected], 
                                     min(remaining, len(words) - len(selected)))
        selected.update(random_words)
        
        return sorted(selected)
    
    def find_candidates(self, constraints_list: List[List[Tuple[str, int, str]]]) -> List[str]:
        """
        Find all words that satisfy all constraint sets.
        Optimized version that applies constraints more efficiently.
        
        Args:
            constraints_list: List of constraint sets (one per guess word)
            
        Returns:
            List of candidate words
        """
        candidates = set(self.words)
        
        # Apply constraints sequentially, filtering as we go
        for constraints in constraints_list:
            new_candidates = set()
            
            # Pre-process constraints for faster checking
            green_positions = {pos: letter for letter, pos, ct in constraints 
                             if ct == WordleConstraints.GREEN}
            yellow_letters = {letter for letter, _, ct in constraints 
                            if ct == WordleConstraints.YELLOW}
            yellow_forbidden_positions = {pos: letter for letter, pos, ct in constraints 
                                        if ct == WordleConstraints.YELLOW}
            gray_letters = {letter for letter, _, ct in constraints 
                          if ct == WordleConstraints.GRAY}
            
            # Quick filter: check green constraints first (fastest)
            for word in candidates:
                # Check green constraints
                valid = True
                for pos, letter in green_positions.items():
                    if word[pos] != letter:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Check yellow constraints
                for letter in yellow_letters:
                    if letter not in word:
                        valid = False
                        break
                    # Check forbidden positions
                    for pos, forbidden_letter in yellow_forbidden_positions.items():
                        if word[pos] == forbidden_letter:
                            valid = False
                            break
                
                if not valid:
                    continue
                
                # Full constraint check
                if WordleConstraints.word_satisfies_constraints(word, constraints):
                    new_candidates.add(word)
            
            candidates = new_candidates
            if not candidates:
                break
        
        return sorted(candidates)
    
    def generate_puzzle(self, answer: str = None, max_attempts: int = 500) -> Dict:
        """
        Generate a puzzle with 4 guess words that uniquely identify the answer.
        Uses optimized algorithm with frequency-based word selection.
        
        Args:
            answer: Optional answer word. If None, picks random word.
            max_attempts: Maximum attempts to find valid puzzle
            
        Returns:
            Dictionary with 'answer', 'guesses', and 'constraints' for each guess
        """
        if answer is None:
            answer = random.choice(self.words)
        
        if answer not in self.word_set:
            raise ValueError(f"Answer word '{answer}' not in word list")
        
        # Strategy: Smart greedy selection with frequency-based heuristics
        # 1. Start with high-frequency letters
        # 2. Prefer words that test different positions
        # 3. Maximize information gain at each step
        
        best_guesses = []
        best_constraints_list = []
        best_candidates_remaining = len(self.words)
        
        # Pre-select candidate guesses based on frequency scores
        # Use top-scoring words + some diversity
        sorted_words = sorted(self.words, key=lambda w: self.word_scores.get(w, 0), reverse=True)
        top_candidates = sorted_words[:min(500, len(sorted_words))]
        
        for attempt in range(max_attempts):
            guesses = []
            constraints_list = []
            used_letters = set()
            
            # Try to pick 4 diverse, informative words
            for guess_num in range(4):
                best_guess = None
                best_score = -1
                best_constraints_for_guess = None
                best_remaining = len(self.words)
                
                # Sample from top candidates, but add some randomness
                if attempt < max_attempts // 2:
                    # Early attempts: focus on high-frequency words
                    candidate_pool = top_candidates[:min(300, len(top_candidates))]
                else:
                    # Later attempts: more diversity
                    candidate_pool = random.sample(self.words, min(400, len(self.words)))
                
                for guess in candidate_pool:
                    if guess == answer or guess in guesses:
                        continue
                    
                    # Prefer words with letters we haven't tested much
                    guess_letters = set(guess)
                    overlap = len(guess_letters & used_letters)
                    if overlap > 3 and guess_num < 2:  # Early guesses should explore
                        continue
                    
                    constraints = WordleConstraints.get_constraints(guess, answer)
                    constraints_list_copy = constraints_list + [constraints]
                    
                    # Check how many candidates remain
                    candidates = self.find_candidates(constraints_list_copy)
                    remaining = len(candidates)
                    
                    if remaining == 0:
                        continue
                    
                    # Score based on:
                    # 1. Information gain (how many candidates eliminated)
                    # 2. Constraint diversity (green/yellow are more informative)
                    # 3. Word frequency score (common letters are more likely)
                    green_count = sum(1 for _, _, ct in constraints if ct == WordleConstraints.GREEN)
                    yellow_count = sum(1 for _, _, ct in constraints if ct == WordleConstraints.YELLOW)
                    
                    info_gain = len(self.words) - remaining
                    constraint_score = green_count * 5 + yellow_count * 2
                    frequency_bonus = self.word_scores.get(guess, 0) * 100
                    diversity_penalty = overlap * 20  # Penalize too much overlap
                    
                    score = info_gain * 20 + constraint_score + frequency_bonus - diversity_penalty
                    
                    if score > best_score or (score == best_score and remaining < best_remaining):
                        best_score = score
                        best_guess = guess
                        best_constraints_for_guess = constraints
                        best_remaining = remaining
                
                if best_guess is None:
                    break
                
                guesses.append(best_guess)
                constraints_list.append(best_constraints_for_guess)
                used_letters.update(set(best_guess))
            
            if len(guesses) < 4:
                continue
            
            # Check if we have exactly one candidate (the answer)
            final_candidates = self.find_candidates(constraints_list)
            
            if len(final_candidates) == 1 and final_candidates[0] == answer:
                # Success! Format the result
                result = {
                    'answer': answer,
                    'guesses': guesses,
                    'constraints': []
                }
                
                for i, guess in enumerate(guesses):
                    result['constraints'].append({
                        'word': guess,
                        'constraints': [
                            {
                                'letter': letter,
                                'position': pos,
                                'type': constraint_type
                            }
                            for letter, pos, constraint_type in constraints_list[i]
                        ]
                    })
                
                return result
            
            # Track best attempt
            if len(final_candidates) < best_candidates_remaining:
                best_candidates_remaining = len(final_candidates)
                best_guesses = guesses.copy()
                best_constraints_list = [c.copy() for c in constraints_list]
        
        # If we couldn't find a perfect puzzle, return the best attempt
        if best_guesses:
            result = {
                'answer': answer,
                'guesses': best_guesses,
                'constraints': []
            }
            
            for i, guess in enumerate(best_guesses):
                result['constraints'].append({
                    'word': guess,
                    'constraints': [
                        {
                            'letter': letter,
                            'position': pos,
                            'type': constraint_type
                        }
                        for letter, pos, constraint_type in best_constraints_list[i]
                    ]
                })
            
            result['candidates_remaining'] = best_candidates_remaining
            return result
        
        raise RuntimeError(f"Could not generate puzzle for '{answer}' after {max_attempts} attempts")


def main():
    """Test the puzzle generator."""
    generator = PuzzleGenerator()
    
    # Generate a puzzle
    print("Generating puzzle...")
    puzzle = generator.generate_puzzle()
    
    print(f"\nAnswer: {puzzle['answer']}")
    print(f"\nGuesses with constraints:")
    for i, guess_data in enumerate(puzzle['constraints'], 1):
        print(f"\nGuess {i}: {guess_data['word']}")
        for constraint in guess_data['constraints']:
            print(f"  {constraint['letter']} at position {constraint['position']}: {constraint['type']}")
    
    if 'candidates_remaining' in puzzle:
        print(f"\nNote: {puzzle['candidates_remaining']} candidates remain (not unique)")
    else:
        print("\n✓ Puzzle uniquely identifies the answer!")


if __name__ == "__main__":
    main()

