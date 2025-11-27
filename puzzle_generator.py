#!/usr/bin/env python3
"""
Constraint-based word puzzle generator.
Generates 4 words with constraints (green/yellow/gray) that uniquely identify an answer word.
Uses efficient constraint satisfaction approach.
"""

import random
from typing import List, Tuple, Dict, Set, Optional
from collections import Counter, defaultdict
import os

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
    
    def __init__(self, wordlist_path: str = "wordlist.txt", 
                 frequency_path: str = "wordsWithFrequency.txt",
                 use_curated: bool = True, 
                 curated_size: int = 5000,
                 min_answer_frequency: float = 0.1):
        """
        Initialize with word list.
        
        Args:
            wordlist_path: Path to word list file
            frequency_path: Path to word frequency file (word,frequency format)
            use_curated: If True, use a curated subset of common words for faster generation
            curated_size: Size of curated subset to use
            min_answer_frequency: Minimum frequency for answer words (soft constraint)
        """
        with open(wordlist_path, 'r') as f:
            all_words = [line.strip().lower() for line in f if line.strip()]
        
        # Load word frequencies from file
        self.word_frequencies = {}
        self.min_answer_frequency = min_answer_frequency
        if os.path.exists(frequency_path):
            print(f"Loading word frequencies from {frequency_path}...")
            with open(frequency_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ',' in line:
                        word, freq_str = line.rsplit(',', 1)
                        try:
                            freq = float(freq_str)
                            self.word_frequencies[word.lower()] = freq
                        except ValueError:
                            continue
            print(f"Loaded frequencies for {len(self.word_frequencies)} words")
        else:
            print(f"Warning: Frequency file {frequency_path} not found, using default scoring")
        
        # Filter answer candidates by frequency (soft constraint)
        if self.word_frequencies:
            # Get frequency threshold (e.g., bottom 20% if we want to avoid very rare words)
            all_freqs = [f for f in self.word_frequencies.values() if f > 0]
            if all_freqs:
                sorted_freqs = sorted(all_freqs)
                threshold = sorted_freqs[int(len(sorted_freqs) * 0.2)] if len(sorted_freqs) > 10 else 0.0
                self.min_answer_frequency = max(min_answer_frequency, threshold)
        
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
        
        # Pre-compute word scores using actual frequency data if available
        self.word_scores = {}
        for word in self.words:
            # Base score from letter frequencies
            base_score = LetterFrequencyAnalyzer.word_score(word, self.position_freqs, self.letter_freqs)
            # Boost score if word has high frequency
            if word in self.word_frequencies:
                freq_boost = min(self.word_frequencies[word] / 100.0, 10.0)  # Normalize frequency
                self.word_scores[word] = base_score * (1.0 + freq_boost * 0.5)
            else:
                self.word_scores[word] = base_score
        
        # Pre-compute answer candidates (words with sufficient frequency)
        self.answer_candidates = [
            w for w in self.words 
            if w not in self.word_frequencies or self.word_frequencies[w] >= self.min_answer_frequency
        ]
        if not self.answer_candidates:
            self.answer_candidates = self.words  # Fallback to all words
        
        print(f"Loaded {len(self.words)} words with frequency analysis")
        print(f"Answer candidates: {len(self.answer_candidates)} words (freq >= {self.min_answer_frequency:.2f})")
    
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
    
    def find_candidates(self, constraints_list: List[List[Tuple[str, int, str]]], 
                       candidate_set: Optional[Set[str]] = None) -> List[str]:
        """
        Find all words that satisfy all constraint sets.
        Optimized version with smart pruning and caching.
        
        Args:
            constraints_list: List of constraint sets (one per guess word)
            candidate_set: Optional pre-filtered candidate set to start with
            
        Returns:
            List of candidate words
        """
        if candidate_set is None:
            candidates = set(self.words)
        else:
            candidates = candidate_set.copy()
        
        # Apply constraints sequentially, filtering as we go
        for constraints in constraints_list:
            if not candidates:
                break  # Early termination
            
            new_candidates = set()
            
            # Pre-process constraints for faster checking
            green_positions = {pos: letter for letter, pos, ct in constraints 
                             if ct == WordleConstraints.GREEN}
            yellow_letters = {letter for letter, _, ct in constraints 
                            if ct == WordleConstraints.YELLOW}
            yellow_forbidden_positions = {pos: letter for letter, pos, ct in constraints 
                                        if ct == WordleConstraints.YELLOW}
            
            # Pre-compute required letter counts for fast filtering
            required_letters = Counter()
            for letter, _, ct in constraints:
                if ct in (WordleConstraints.GREEN, WordleConstraints.YELLOW):
                    required_letters[letter] += 1
            
            # Quick filter: check green constraints first (fastest, most restrictive)
            for word in candidates:
                # Fast path: green constraints (most restrictive)
                valid = True
                for pos, letter in green_positions.items():
                    if word[pos] != letter:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Fast path: check if word has all required letters
                word_letter_counts = Counter(word)
                for letter, required_count in required_letters.items():
                    if word_letter_counts[letter] < required_count:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Fast path: yellow constraints (letter exists but not at forbidden position)
                for letter in yellow_letters:
                    if letter not in word:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Check yellow forbidden positions
                for pos, forbidden_letter in yellow_forbidden_positions.items():
                    if word[pos] == forbidden_letter:
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Full constraint check (handles edge cases like gray constraints)
                if WordleConstraints.word_satisfies_constraints(word, constraints):
                    new_candidates.add(word)
            
            candidates = new_candidates
            # Early termination if no candidates remain
            if not candidates:
                break
        
        return sorted(candidates)
    
    def generate_puzzle(self, answer: str = None, max_attempts: int = 500) -> Dict:
        """
        Generate a puzzle with 4 guess words that uniquely identify the answer.
        Uses optimized algorithm with frequency-based word selection and smart pruning.
        
        Args:
            answer: Optional answer word. If None, picks from answer candidates (higher frequency words).
            max_attempts: Maximum attempts to find valid puzzle
            
        Returns:
            Dictionary with 'answer', 'guesses', and 'constraints' for each guess
        """
        if answer is None:
            # Prefer higher frequency words as answers
            if self.answer_candidates:
                # Weight selection by frequency (higher frequency = more likely)
                if self.word_frequencies:
                    weights = [
                        self.word_frequencies.get(w, 0.0) + 1.0  # Add 1 to avoid zero weights
                        for w in self.answer_candidates
                    ]
                    answer = random.choices(self.answer_candidates, weights=weights, k=1)[0]
                else:
                    answer = random.choice(self.answer_candidates)
            else:
                answer = random.choice(self.words)
        
        if answer not in self.word_set:
            raise ValueError(f"Answer word '{answer}' not in word list")
        
        # Strategy: Smart greedy selection with frequency-based heuristics and pruning
        # 1. Use frequency-weighted word selection
        # 2. Prefer words that test different positions
        # 3. Maximize information gain at each step
        # 4. Early termination and constraint caching
        
        best_guesses = []
        best_constraints_list = []
        best_candidates_remaining = len(self.words)
        best_final_candidates = []
        
        # Pre-select candidate guesses based on frequency scores
        # Use top-scoring words + some diversity
        sorted_words = sorted(self.words, key=lambda w: self.word_scores.get(w, 0), reverse=True)
        top_candidates = sorted_words[:min(500, len(sorted_words))]
        
        # Cache for constraint results to avoid recomputation
        constraint_cache = {}
        
        for attempt in range(max_attempts):
            guesses = []
            constraints_list = []
            used_letters = set()
            current_candidates = None  # Track candidates incrementally
            
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
                
                # Pruning: If we have very few candidates, we can still use any guess
                # (guesses don't need to be in current candidates to be useful)
                
                for guess in candidate_pool:
                    if guess == answer or guess in guesses:
                        continue
                    
                    # Prefer words with letters we haven't tested much
                    guess_letters = set(guess)
                    overlap = len(guess_letters & used_letters)
                    if overlap > 3 and guess_num < 2:  # Early guesses should explore
                        continue
                    
                    # Compute constraints
                    constraints = WordleConstraints.get_constraints(guess, answer)
                    constraints_list_copy = constraints_list + [constraints]
                    
                    # Check cache key (simplified - could be more sophisticated)
                    cache_key = tuple(sorted((g, answer) for g in guesses + [guess]))
                    if cache_key in constraint_cache:
                        remaining = constraint_cache[cache_key]
                    else:
                        # Check how many candidates remain (use incremental filtering)
                        candidates = self.find_candidates(constraints_list_copy, current_candidates)
                        remaining = len(candidates)
                        constraint_cache[cache_key] = remaining
                    
                    # Early termination: if no candidates, skip
                    if remaining == 0:
                        continue
                    
                    # Pruning: If remaining candidates is too high, this guess isn't informative enough
                    # Skip if it doesn't reduce candidates significantly (except for first guess)
                    # Only apply this if we have many candidates (otherwise any reduction is valuable)
                    if guess_num > 0 and current_candidates and len(current_candidates) > 20:
                        reduction = len(current_candidates) - remaining
                        if reduction < len(current_candidates) * 0.1:  # Less than 10% reduction
                            continue
                    
                    # Score based on:
                    # 1. Information gain (how many candidates eliminated)
                    # 2. Constraint diversity (green/yellow are more informative)
                    # 3. Word frequency score (common letters are more likely)
                    green_count = sum(1 for _, _, ct in constraints if ct == WordleConstraints.GREEN)
                    yellow_count = sum(1 for _, _, ct in constraints if ct == WordleConstraints.YELLOW)
                    
                    info_gain = (len(current_candidates) if current_candidates else len(self.words)) - remaining
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
                
                # Update current candidates incrementally (for next iteration)
                if best_constraints_for_guess:
                    current_candidates = set(self.find_candidates(constraints_list))
                    # Early termination if we've found the answer
                    if len(current_candidates) == 1 and answer in current_candidates:
                        break
            
            if len(guesses) < 4:
                continue
            
            # Check if we have exactly one candidate (the answer)
            final_candidates = self.find_candidates(constraints_list)
            
            if len(final_candidates) == 1 and final_candidates[0] == answer:
                # Success! Format the result
                result = {
                    'answer': answer,
                    'guesses': guesses,
                    'constraints': [],
                    'valid_answers': [answer]  # Unique puzzle, only one valid answer
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
                best_final_candidates = final_candidates.copy()  # Store the actual candidates
        
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
            # Store all valid answers (candidates that satisfy all constraints)
            if best_candidates_remaining > 1:
                result['valid_answers'] = best_final_candidates
            else:
                # For unique puzzles, valid_answers is just the answer
                result['valid_answers'] = [answer]
            
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

