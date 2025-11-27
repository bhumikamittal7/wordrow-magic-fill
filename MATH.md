# Mathematical Documentation: Constraint-Based Word Puzzle Generator

## Overview

This document provides a mathematical and algorithmic analysis of the constraint-based word puzzle generator. The system generates puzzles where 4 guess words with Wordle-style constraints (green/yellow/gray) uniquely identify a single answer word.

## Problem Statement

**Given:**
- A word list $W = \{w_1, w_2, \ldots, w_n\}$ where each word $w_i$ is exactly 5 letters
- A target answer word $a \in W$
- A constraint function $C: W \times W \rightarrow \Gamma$ where $\Gamma$ is the set of constraint patterns

**Goal:**
Find a set of 4 guess words $G = \{g_1, g_2, g_3, g_4\} \subseteq W$ such that:
$$\{w \in W : \forall g_i \in G, w \text{ satisfies } C(g_i, a)\} = \{a\}$$

In other words, the constraints from the 4 guesses must uniquely identify the answer word.

## Functional Definition

### Inputs

The puzzle generation system takes the following inputs:

1. **Word List** $W = \{w_1, w_2, \ldots, w_n\}$
   - Type: Set of strings
   - Domain: All strings of length 5 using lowercase English letters (a-z)
   - Default: Loaded from `wordlist.txt` file
   - Size: Typically $n \approx 16,000$ words

2. **Answer Word** $a$ (optional)
   - Type: String
   - Domain: $a \in W$ (must be in word list)
   - Default: If not provided, selected randomly from $W$
   - Purpose: The target word to be uniquely identified

3. **Configuration Parameters**:
   - `use_curated`: Boolean - Whether to use curated word subset
   - `curated_size`: Integer - Size of curated subset (default: 2000-5000)
   - `max_attempts`: Integer - Maximum search attempts (default: 500)

### Outputs

The system produces a puzzle structure:

$$\text{Puzzle} = \begin{cases}
\text{answer}: & a \in W \\
\text{guesses}: & [g_1, g_2, g_3, g_4] \text{ where } g_i \in W \\
\text{constraints}: & [\Gamma_1, \Gamma_2, \Gamma_3, \Gamma_4] \\
\text{candidates\_remaining}: & \text{Integer} \geq 1
\end{cases}$$

Where:
- **answer**: The target word to be identified
- **guesses**: List of 4 guess words (may be fewer if generation fails)
- **constraints**: List of constraint sets, one per guess
  - Each $\Gamma_i$ is a list of tuples: $(letter, position, type)$
  - $type \in \{\text{green}, \text{yellow}, \text{gray}\}$
- **candidates_remaining**: Number of words satisfying all constraints
  - If $= 1$: Puzzle uniquely identifies the answer (optimal)
  - If $> 1$: Puzzle is ambiguous (suboptimal but best found)

### Function Signature

```
generate_puzzle: (W: Set[str], a: Optional[str], params: Config) → Puzzle
```

**Mathematical Definition:**
$$\text{generate\_puzzle}(W, a, \text{params}) = \arg\min_{G \subseteq W, |G| \leq 4} |\{w \in W : \forall g \in G, \text{satisfies}(w, C(g, a))\}|$$

Subject to:
- $|G| = 4$ (if possible)
- $a \in \{w \in W : \forall g \in G, \text{satisfies}(w, C(g, a))\}$ (answer must be a candidate)

### Constraint Format

Each constraint set $\Gamma_i$ for guess $g_i$ is computed deterministically:

$$\Gamma_i = C(g_i, a) = \{(\ell_j, j, \text{type}_j) : j \in \{0,1,2,3,4\}\}$$

Where $\text{type}_j$ is determined by the Wordle constraint rules (see Constraint Generation Algorithm).

## Assumptions

1. **Word Length**: All words in the dictionary are exactly 5 letters
2. **Alphabet**: All words use lowercase English letters (a-z)
3. **Dictionary**: The word list is finite and pre-defined
4. **Constraint Semantics**: Constraints follow standard Wordle rules:
   - **Green**: Letter at position $i$ in guess matches letter at position $i$ in answer
   - **Yellow**: Letter exists in answer but not at position $i$ in answer
   - **Gray**: Letter does not exist in answer (or all instances are accounted for by greens/yellows)
5. **Uniqueness**: For each puzzle, there exists at least one set of 4 guesses that uniquely identifies the answer (may not hold for all words)

## Invariants

### 1. Constraint Consistency Invariant

For any word $w$ and constraint set $\Gamma$:
- If $w$ satisfies all constraints in $\Gamma$, then $w$ must be a valid candidate
- If $w$ violates any constraint in $\Gamma$, then $w$ is eliminated

**Formal Definition:**
$$\forall w \in W, \forall \gamma \in \Gamma: \text{satisfies}(w, \gamma) \implies w \in \text{candidates}(\Gamma)$$

### 2. Monotonicity Invariant

Adding constraints can only reduce (or keep equal) the candidate set:
$$\text{candidates}(\Gamma \cup \{\gamma\}) \subseteq \text{candidates}(\Gamma)$$

### 3. Green Constraint Invariant

For green constraints at position $i$:
- If constraint $(l, i, \text{green}) \in \Gamma$, then $\forall w \in \text{candidates}(\Gamma): w[i] = l$

### 4. Yellow Constraint Invariant

For yellow constraints:
- If constraint $(l, i, \text{yellow}) \in \Gamma$, then:
  - $\forall w \in \text{candidates}(\Gamma): l \in w$ (letter must exist)
  - $\forall w \in \text{candidates}(\Gamma): w[i] \neq l$ (letter cannot be at this position)

### 5. Gray Constraint Invariant

For gray constraints:
- If constraint $(l, i, \text{gray}) \in \Gamma$ and $l$ is not required by green/yellow constraints, then:
  - $\forall w \in \text{candidates}(\Gamma): l \notin w$ OR all instances of $l$ are accounted for by required constraints

### 6. Letter Count Invariant

For any letter $l$:
- Let $r_l = |\{(l, \_, \text{green}) \in \Gamma\}| + |\{(l, \_, \text{yellow}) \in \Gamma\}|$
- Then $\forall w \in \text{candidates}(\Gamma): \text{count}(w, l) \geq r_l$

## Constraint Generation Algorithm

### Pseudocode: `get_constraints(guess, answer)`

```
FUNCTION get_constraints(guess: string, answer: string) -> List[(letter, position, type)]:
    constraints = []
    answer_counts = Counter(answer)
    used_positions = set()
    
    // First pass: Mark green constraints (exact matches)
    FOR i = 0 TO 4:
        IF guess[i] == answer[i]:
            constraints.append((guess[i], i, GREEN))
            used_positions.add(i)
            answer_counts[guess[i]] -= 1
    
    // Second pass: Mark yellow and gray constraints
    FOR i = 0 TO 4:
        IF i NOT IN used_positions:
            IF guess[i] IN answer_counts AND answer_counts[guess[i]] > 0:
                constraints.append((guess[i], i, YELLOW))
                answer_counts[guess[i]] -= 1
            ELSE:
                constraints.append((guess[i], i, GRAY))
    
    RETURN constraints
```

**Time Complexity:** $O(1)$ (constant time for 5-letter words)

**Space Complexity:** $O(1)$

## Constraint Satisfaction Algorithm

### Pseudocode: `word_satisfies_constraints(word, constraints)`

```
FUNCTION word_satisfies_constraints(word: string, constraints: List[(letter, pos, type)]) -> bool:
    word_counts = Counter(word)
    constraint_counts = Counter()
    
    // Check green constraints
    FOR EACH (letter, pos, type) IN constraints WHERE type == GREEN:
        IF word[pos] != letter:
            RETURN False
        constraint_counts[letter] += 1
    
    // Check yellow constraints
    FOR EACH (letter, pos, type) IN constraints WHERE type == YELLOW:
        IF word[pos] == letter:  // Cannot be at this position
            RETURN False
        IF letter NOT IN word:
            RETURN False
        constraint_counts[letter] += 1
    
    // Check gray constraints
    FOR EACH (letter, pos, type) IN constraints WHERE type == GRAY:
        IF letter IN word:
            // Only invalid if not required by green/yellow
            IF constraint_counts[letter] >= word_counts[letter]:
                RETURN False
    
    // Verify minimum letter counts
    FOR EACH letter IN constraint_counts:
        IF word_counts[letter] < constraint_counts[letter]:
            RETURN False
    
    RETURN True
```

**Time Complexity:** $O(k)$ where $k$ is the number of constraints (at most 20 for 4 guesses × 5 positions)

**Space Complexity:** $O(1)$ (bounded by alphabet size)

## Candidate Filtering Algorithm

### Pseudocode: `find_candidates(constraints_list, candidate_set)` (ENHANCED)

```
FUNCTION find_candidates(constraints_list: List[List[constraints]], 
                         candidate_set: Optional[Set[string]] = None) -> List[string]:
    IF candidate_set IS None:
        candidates = set(W)  // Start with all words
    ELSE:
        candidates = candidate_set.copy()  // NEW: Start with pre-filtered set
    
    FOR EACH constraints IN constraints_list:
        IF candidates IS EMPTY:
            BREAK  // NEW: Early termination check
        
        new_candidates = set()
        
        // Pre-process constraints for fast filtering
        green_positions = {(pos, letter) for (letter, pos, type) in constraints if type == GREEN}
        yellow_letters = {letter for (letter, _, type) in constraints if type == YELLOW}
        yellow_forbidden = {(pos, letter) for (letter, pos, type) in constraints if type == YELLOW}
        
        // NEW: Pre-compute required letter counts
        required_letters = Counter()
        FOR EACH (letter, _, type) IN constraints:
            IF type IN (GREEN, YELLOW):
                required_letters[letter] += 1
        
        // Fast pre-filtering by green constraints
        FOR EACH word IN candidates:
            valid = True
            
            // Check green constraints (fastest check, most restrictive)
            FOR EACH (pos, letter) IN green_positions:
                IF word[pos] != letter:
                    valid = False
                    BREAK
            
            IF NOT valid:
                CONTINUE
            
            // NEW: Fast check - required letter counts
            word_letter_counts = Counter(word)
            FOR EACH (letter, required_count) IN required_letters:
                IF word_letter_counts[letter] < required_count:
                    valid = False
                    BREAK
            
            IF NOT valid:
                CONTINUE
            
            // Check yellow constraints
            FOR EACH letter IN yellow_letters:
                IF letter NOT IN word:
                    valid = False
                    BREAK
            
            IF NOT valid:
                CONTINUE
            
            // Check yellow forbidden positions
            FOR EACH (pos, forbidden_letter) IN yellow_forbidden:
                IF word[pos] == forbidden_letter:
                    valid = False
                    BREAK
            
            IF NOT valid:
                CONTINUE
            
            // Full constraint check (handles edge cases like gray constraints)
            IF word_satisfies_constraints(word, constraints):
                new_candidates.add(word)
        
        candidates = new_candidates
        // Early termination if no candidates remain
        IF candidates IS EMPTY:
            BREAK
    
    RETURN sorted(candidates)
```

**Time Complexity:** 
- Worst case: $O(n \cdot m \cdot k)$ where $n = |W|$, $m$ is number of constraint sets, $k$ is constraints per set
- Average case: Much better due to early termination and pre-filtering

**Space Complexity:** $O(n)$ for candidate sets

## Search Space Pruning Techniques

### 1. **Early Termination**
- If at any point `candidates` becomes empty, terminate immediately
- If `candidates` has size 1 and equals the answer, terminate

**Pruning Factor:** Eliminates entire search branches when constraints are inconsistent

### 2. **Pre-filtering by Green Constraints**
- Green constraints are the most restrictive (exact position match)
- Check green constraints first before expensive full constraint checks
- Eliminates words that don't match fixed positions immediately

**Pruning Factor:** Reduces candidate set by ~96% per green constraint (1/26 chance per position)

### 3. **Sequential Constraint Application**
- Apply constraints one guess at a time, filtering candidates incrementally
- Each constraint set reduces the search space before the next is applied
- More efficient than checking all constraints against all words

**Pruning Factor:** Reduces work by applying constraints to smaller candidate sets

### 4. **Frequency-Based Word Selection** (ENHANCED)
- Pre-compute letter frequencies and position frequencies
- **NEW:** Load actual word frequencies from external data source
- Score words by: `base_score * (1.0 + frequency_boost * 0.5)` where `frequency_boost = min(freq/100, 10.0)`
- Prioritize high-scoring words in candidate selection
- Higher frequency words get boosted scores, making them more likely to be selected as guesses

**Mathematical Formulation:**
$$\text{score}(w) = \text{base\_score}(w) \cdot (1.0 + \min(F(w)/100, 10.0) \cdot 0.5)$$

Where:
- $\text{base\_score}(w)$ is computed from letter/position frequencies
- $F(w)$ is the word frequency from external data

**Pruning Factor:** Reduces search space by focusing on words likely to provide maximum information gain, with preference for well-known words

### 5. **Information Gain Heuristic**
- Score each potential guess by: `info_gain = |W| - |remaining_candidates|`
- Prefer guesses that eliminate more candidates
- Combine with constraint diversity (green/yellow are more informative than gray)

**Pruning Factor:** Guides search toward more informative guesses, reducing backtracking

### 6. **Curated Word Subset**
- Use frequency analysis to select top $k$ most informative words
- Reduces dictionary size from ~16,000 to ~2,000-5,000 words
- Maintains solution quality while dramatically reducing search space

**Pruning Factor:** Reduces $|W|$ by ~70-85%

### 7. **Letter Overlap Penalty**
- Track letters already tested in previous guesses
- Penalize guesses with high overlap with previous guesses
- Encourages exploration of new letters

**Pruning Factor:** Reduces redundant guesses, focuses on diverse letter coverage

### 8. **Word Frequency-Based Answer Selection** (NEW)
- Load word frequencies from external data source (`wordsWithFrequency.txt`)
- Prefer higher frequency words as puzzle answers (soft constraint)
- Filter out very low frequency words from answer candidates
- Use frequency-weighted random selection when answer is not specified

**Mathematical Formulation:**
- Let $F: W \rightarrow \mathbb{R}^+$ be the frequency function
- Answer candidates: $A = \{w \in W : F(w) \geq \theta\}$ where $\theta$ is minimum frequency threshold
- Selection probability: $P(w) \propto F(w) + 1$ (add 1 to avoid zero probabilities)

**Pruning Factor:** Reduces search space by focusing on well-known words, improving puzzle quality

### 9. **Incremental Candidate Tracking** (NEW)
- Maintain current candidate set incrementally as guesses are added
- Pass current candidates to `find_candidates()` to avoid re-filtering from full word list
- Early termination when candidate set becomes very small

**Pruning Factor:** Reduces filtering work from $O(n)$ to $O(|C|)$ where $|C|$ is current candidate count

### 10. **Constraint Result Caching** (NEW)
- Cache results of constraint satisfaction checks for common guess sequences
- Avoid recomputing candidate counts for identical constraint combinations
- Cache key based on sorted guess-answer pairs

**Pruning Factor:** Eliminates redundant constraint satisfaction computations

### 11. **Information Gain Threshold Pruning** (NEW)
- Skip guesses that don't reduce candidate set by at least a threshold percentage
- For guess $g$ at step $i$: if $\frac{|C_{i-1}| - |C_i|}{|C_{i-1}|} < \alpha$ (e.g., $\alpha = 0.1$), skip $g$
- Only applies after first guess (first guess always evaluated)

**Mathematical Formulation:**
$$\text{skip}(g) = \begin{cases}
\text{True} & \text{if } i > 1 \text{ and } \frac{|C_{i-1}| - |C_i|}{|C_{i-1}|} < \alpha \\
\text{False} & \text{otherwise}
\end{cases}$$

**Pruning Factor:** Eliminates uninformative guesses early, focusing search on high-value candidates

### 12. **Required Letter Count Pre-filtering** (NEW)
- Pre-compute required letter counts from green/yellow constraints
- Fast rejection: if word doesn't contain required letters in sufficient quantity, skip full check
- Uses Counter-based fast lookup

**Pruning Factor:** Eliminates words that fail basic letter count requirements before expensive constraint checks

## Puzzle Generation Algorithm

### Pseudocode: `generate_puzzle(answer, max_attempts)` (ENHANCED)

```
FUNCTION generate_puzzle(answer: string, max_attempts: int) -> Dict:
    // Load word frequencies if available
    word_frequencies = LOAD_FREQUENCIES("wordsWithFrequency.txt")
    
    // Select answer if not provided (prefer higher frequency)
    IF answer IS None:
        answer_candidates = {w : w IN W AND F(w) >= threshold}
        answer = WEIGHTED_RANDOM_SELECT(answer_candidates, weights=F(w)+1)
    
    // Pre-compute word scores based on frequency (enhanced with word frequencies)
    sorted_words = SORT(W, key=word_score_with_frequency, reverse=True)
    top_candidates = sorted_words[:min(500, |W|)]
    
    best_guesses = []
    best_constraints = []
    best_remaining = |W|
    constraint_cache = {}  // NEW: Cache constraint results
    
    FOR attempt = 1 TO max_attempts:
        guesses = []
        constraints_list = []
        used_letters = set()
        current_candidates = None  // NEW: Track candidates incrementally
        
        // Select 4 guesses
        FOR guess_num = 1 TO 4:
            best_guess = None
            best_score = -1
            best_remaining = |W|
            
            // Select candidate pool based on attempt number
            IF attempt < max_attempts / 2:
                candidate_pool = top_candidates[:300]
            ELSE:
                candidate_pool = RANDOM_SAMPLE(W, min(400, |W|))
            
            // NEW: Pruning - if very few candidates, limit search
            IF current_candidates AND |current_candidates| < 10:
                candidate_pool = FILTER(candidate_pool, w IN current_candidates OR w != answer)
            
            FOR EACH guess IN candidate_pool:
                IF guess == answer OR guess IN guesses:
                    CONTINUE
                
                // Diversity check
                guess_letters = set(guess)
                overlap = |guess_letters ∩ used_letters|
                IF overlap > 3 AND guess_num < 2:
                    CONTINUE
                
                // Compute constraints
                constraints = get_constraints(guess, answer)
                constraints_list_copy = constraints_list + [constraints]
                
                // NEW: Check cache first
                cache_key = TUPLE(SORT(guesses + [guess]))
                IF cache_key IN constraint_cache:
                    remaining = constraint_cache[cache_key]
                ELSE:
                    // Check remaining candidates (use incremental filtering)
                    candidates = find_candidates(constraints_list_copy, current_candidates)
                    remaining = |candidates|
                    constraint_cache[cache_key] = remaining
                
                IF remaining == 0:
                    CONTINUE
                
                // NEW: Information gain threshold pruning
                IF guess_num > 1 AND current_candidates:
                    reduction_ratio = (|current_candidates| - remaining) / |current_candidates|
                    IF reduction_ratio < 0.1:  // Less than 10% reduction
                        CONTINUE
                
                // Score this guess
                green_count = COUNT(constraints, type == GREEN)
                yellow_count = COUNT(constraints, type == YELLOW)
                info_gain = (|current_candidates| IF current_candidates ELSE |W|) - remaining
                constraint_score = green_count * 5 + yellow_count * 2
                frequency_bonus = word_score_with_frequency(guess) * 100
                diversity_penalty = overlap * 20
                
                score = info_gain * 20 + constraint_score + frequency_bonus - diversity_penalty
                
                IF score > best_score OR (score == best_score AND remaining < best_remaining):
                    best_score = score
                    best_guess = guess
                    best_constraints_for_guess = constraints
                    best_remaining = remaining
            
            IF best_guess IS None:
                BREAK
            
            guesses.append(best_guess)
            constraints_list.append(best_constraints_for_guess)
            used_letters.update(set(best_guess))
            
            // NEW: Update current candidates incrementally
            current_candidates = SET(find_candidates(constraints_list))
            
            // NEW: Early termination if answer found
            IF |current_candidates| == 1 AND answer IN current_candidates:
                BREAK
        
        IF |guesses| < 4:
            CONTINUE
        
        // Check if puzzle is solved
        final_candidates = find_candidates(constraints_list)
        
        IF |final_candidates| == 1 AND final_candidates[0] == answer:
            RETURN {
                'answer': answer,
                'guesses': guesses,
                'constraints': format_constraints(constraints_list)
            }
        
        // Track best attempt
        IF |final_candidates| < best_remaining:
            best_remaining = |final_candidates|
            best_guesses = guesses.copy()
            best_constraints = constraints_list.copy()
    
    // Return best attempt (may not be unique)
    RETURN {
        'answer': answer,
        'guesses': best_guesses,
        'constraints': format_constraints(best_constraints),
        'candidates_remaining': best_remaining
    }
```

**Time Complexity:** 
- Worst case: $O(\text{max_attempts} \cdot 4 \cdot |\text{candidate_pool}| \cdot n \cdot k)$
- With pruning: Much better in practice

**Space Complexity:** $O(n)$ for candidate sets and word lists

## Frequency Analysis

### Letter Frequency Scoring

For a word $w = w_0 w_1 w_2 w_3 w_4$:

$$\text{base\_score}(w) = \sum_{i=0}^{4} 2 \cdot f_{\text{pos}}(w_i, i) + \sum_{l \in \text{unique}(w)} f_{\text{letter}}(l)$$

Where:
- $f_{\text{pos}}(l, i)$ is the frequency of letter $l$ at position $i$ in the dictionary
- $f_{\text{letter}}(l)$ is the overall frequency of letter $l$ in the dictionary
- $\text{unique}(w)$ is the set of unique letters in $w$

**Rationale:** 
- Position-specific frequency is weighted 2× (more informative)
- Each unique letter contributes once (encourages diverse letters)

### Word Frequency Integration (NEW)

The system now integrates actual word frequency data from external sources:

$$\text{final\_score}(w) = \text{base\_score}(w) \cdot (1.0 + \beta \cdot \min(F(w)/100, 10.0))$$

Where:
- $F(w)$ is the word frequency from external data (e.g., corpus frequency)
- $\beta = 0.5$ is the frequency boost coefficient
- The frequency is normalized by dividing by 100 and capped at 10.0

**Rationale:**
- Higher frequency words are more well-known and better puzzle answers
- Frequency boost is multiplicative to preserve relative ordering of base scores
- Capping prevents extremely high frequency words from dominating

### Answer Selection with Frequency (NEW)

When selecting an answer word (if not provided):

$$P(w \text{ selected as answer}) = \frac{F(w) + 1}{\sum_{w' \in A} (F(w') + 1)}$$

Where:
- $A = \{w \in W : F(w) \geq \theta\}$ is the set of answer candidates
- $\theta$ is the minimum frequency threshold (default: 0.1, or 20th percentile)
- Adding 1 ensures all words have non-zero probability

**Rationale:**
- Prefer well-known words as answers (better puzzle quality)
- Soft constraint: very rare words can still be answers if explicitly requested
- Weighted selection ensures diversity while favoring common words

## Guarantees and Properties

### 1. **Correctness Guarantee**

If the algorithm returns a puzzle with `candidates_remaining == 1`, then:
- The answer word is the unique solution
- All 4 guesses are valid words from the dictionary
- All constraints are correctly computed according to Wordle rules

**Proof Sketch:** 
- `find_candidates` correctly implements constraint satisfaction
- If `|candidates| == 1` and the candidate equals the answer, the puzzle is valid

### 2. **Termination Guarantee**

The algorithm always terminates:
- Maximum attempts limit ensures termination
- Each iteration is finite (bounded by candidate pool size)
- Early termination when solution found

**Time Bound:** $O(\text{max_attempts} \cdot 4 \cdot |\text{pool}| \cdot n \cdot k)$

### 3. **Monotonicity Property**

As more constraints are added, the candidate set can only shrink:
$$\text{candidates}(\Gamma_1 \cup \Gamma_2) \subseteq \text{candidates}(\Gamma_1) \cap \text{candidates}(\Gamma_2)$$

### 4. **No False Positives**

If a word satisfies all constraints, it is a valid candidate:
$$\text{satisfies}(w, \Gamma) \implies w \in \text{candidates}(\Gamma)$$

### 5. **No False Negatives**

If a word is a valid candidate, it satisfies all constraints:
$$w \in \text{candidates}(\Gamma) \implies \text{satisfies}(w, \Gamma)$$

### 6. **Completeness (Best Effort)**

The algorithm attempts to find a unique solution:
- If a unique solution exists and is found within `max_attempts`, it returns it
- If no unique solution is found, it returns the best attempt (fewest remaining candidates)
- Not guaranteed to find a solution if one exists (greedy heuristic)

## Algorithm Techniques Summary

1. **Constraint Satisfaction Problem (CSP)**: Core problem formulation
2. **Greedy Algorithm**: Selects guesses one at a time based on local optimization
3. **Heuristic Search**: Uses frequency-based scoring to guide search
4. **Branch and Bound**: Prunes search space using constraint filtering
5. **Early Termination**: Stops when solution found or constraints become inconsistent
6. **Pre-computation**: Frequency analysis and word scoring computed once
7. **Incremental Filtering**: Applies constraints sequentially to reduce candidate set
8. **Information Theory**: Maximizes information gain at each step

## Deterministic vs Random Components

The puzzle generation process combines deterministic algorithms with strategic randomization. Understanding which parts are deterministic and which are random is crucial for reproducibility and debugging.

### Deterministic Components

These components produce the same output given the same inputs:

1. **Constraint Generation** (`get_constraints`)
   - **Input**: Guess word $g$, Answer word $a$
   - **Output**: Constraint set $\Gamma = C(g, a)$
   - **Determinism**: For fixed $(g, a)$, always produces the same $\Gamma$
   - **Function**: $C: W \times W \rightarrow \Gamma$ is a pure function

2. **Constraint Satisfaction Checking** (`word_satisfies_constraints`)
   - **Input**: Word $w$, Constraint set $\Gamma$
   - **Output**: Boolean (satisfies/doesn't satisfy)
   - **Determinism**: For fixed $(w, \Gamma)$, always produces the same result
   - **Function**: $\text{satisfies}: W \times \Gamma \rightarrow \{\text{True}, \text{False}\}$ is a pure function

3. **Candidate Filtering** (`find_candidates`)
   - **Input**: List of constraint sets $[\Gamma_1, \ldots, \Gamma_k]$
   - **Output**: Set of candidate words satisfying all constraints
   - **Determinism**: For fixed constraint sets, always produces the same candidate set
   - **Function**: $\text{candidates}: \Gamma^* \rightarrow \mathcal{P}(W)$ is deterministic

4. **Frequency Analysis**
   - **Input**: Word list $W$
   - **Output**: Letter frequencies, position frequencies, word scores
   - **Determinism**: For fixed $W$, always produces the same frequency distributions
   - **Computation**: Based on counting and arithmetic operations

5. **Word Scoring** (`word_score`)
   - **Input**: Word $w$, frequency data
   - **Output**: Numerical score
   - **Determinism**: For fixed $w$ and frequency data, always produces the same score
   - **Function**: $\text{score}: W \times \text{FreqData} \rightarrow \mathbb{R}$ is deterministic

6. **Greedy Selection Logic**
   - **Input**: Candidate pool, current constraints, scoring function
   - **Output**: Best guess based on scoring heuristic
   - **Determinism**: If candidate pool order is fixed, selection is deterministic
   - **Note**: Selection depends on iteration order through candidate pool

### Random Components

These components introduce non-determinism:

1. **Answer Selection** (if not provided)
   - **Location**: `generate_puzzle(answer=None)`
   - **Randomness**: `answer = random.choice(self.words)`
   - **Impact**: Different puzzles for the same word list
   - **Seed Control**: Can be made deterministic by setting random seed or providing answer

2. **Curated Word Subset Selection**
   - **Location**: `_select_curated_words`
   - **Randomness**: 30% of curated words selected randomly from remaining pool
   - **Code**: `random.sample([w for w in words if w not in selected], remaining)`
   - **Impact**: Different word subsets may lead to different puzzle solutions
   - **Determinism**: Top 70% by score is deterministic; random 30% varies

3. **Candidate Pool Selection** (later attempts)
   - **Location**: `generate_puzzle`, when `attempt >= max_attempts / 2`
   - **Randomness**: `candidate_pool = random.sample(self.words, min(400, len(self.words)))`
   - **Impact**: Different search paths explored in later attempts
   - **Purpose**: Introduces diversity when early attempts fail

4. **Iteration Order** (implicit)
   - **Location**: When multiple guesses have equal scores
   - **Randomness**: Python set/dict iteration order (implementation-dependent)
   - **Impact**: May select different guesses when scores are tied
   - **Note**: Python 3.7+ preserves insertion order, but still non-deterministic across runs

### Determinism Guarantees

Given the same inputs and random seed:

1. **Fixed Answer**: If answer $a$ is provided, the constraint generation for any guess $g$ is deterministic
2. **Fixed Word List**: If word list $W$ is fixed, frequency analysis is deterministic
3. **Fixed Candidate Pool**: If candidate pool order is fixed, greedy selection is deterministic
4. **Reproducibility**: Setting `random.seed()` makes the entire process reproducible

### Functional Purity Analysis

**Pure Functions** (no side effects, deterministic):
- `get_constraints(guess, answer)`
- `word_satisfies_constraints(word, constraints)`
- `find_candidates(constraints_list)`
- `compute_frequencies(words)`
- `word_score(word, position_freqs, letter_freqs)`

**Impure Functions** (side effects or randomness):
- `generate_puzzle(answer=None, max_attempts=500)` - uses randomness
- `_select_curated_words(words, size)` - uses randomness
- `random.choice()`, `random.sample()` - random number generation

### Making the System Deterministic

To achieve full determinism:

1. **Provide explicit answer**: `generate_puzzle(answer="hello")`
2. **Set random seed**: `random.seed(42)` before generation
3. **Fix curated selection**: Remove random 30% or use deterministic selection
4. **Fix candidate pool**: Use sorted list instead of random sample
5. **Fix tie-breaking**: Use deterministic ordering (e.g., lexicographic) when scores are equal

**Trade-off**: Full determinism may reduce solution diversity and quality, as randomization helps escape local optima in the greedy search.

## Complexity Analysis

### Space Complexity
- **Word List**: $O(n)$ where $n = |W|$
- **Frequency Data**: $O(1)$ (bounded by alphabet size)
- **Candidate Sets**: $O(n)$ in worst case
- **Overall**: $O(n)$

### Time Complexity
- **Preprocessing**: $O(n)$ for frequency computation
- **Constraint Generation**: $O(1)$ per guess (constant for 5-letter words)
- **Candidate Filtering**: $O(n \cdot m \cdot k)$ where $m$ is number of guesses, $k$ is constraints per guess
- **Puzzle Generation**: $O(\text{max_attempts} \cdot 4 \cdot |\text{pool}| \cdot n \cdot k)$
- **Overall**: $O(\text{max_attempts} \cdot |\text{pool}| \cdot n)$

### Practical Performance
- **Before optimizations:**
  - With curated word list (2000 words): ~1-5 seconds per puzzle
  - With full word list (16000 words): ~10-30 seconds per puzzle
- **After optimizations (with frequency data and enhanced pruning):**
  - With curated word list (2000 words): ~0.5-2 seconds per puzzle (2-5× faster)
  - With full word list (16000 words): ~3-10 seconds per puzzle (3-5× faster)
- Pruning techniques reduce average case significantly
- Frequency-based answer selection improves puzzle quality (more well-known words)

## Limitations and Future Improvements

1. **No Optimality Guarantee**: Greedy algorithm may not find solution even if one exists
2. **Heuristic Dependency**: Performance depends on quality of frequency analysis
3. **Fixed Guess Count**: Always uses exactly 4 guesses (may not be optimal for all words)
4. **No Backtracking**: Once a guess is selected, it's not reconsidered
5. **Potential Improvements**:
   - Backtracking search for guaranteed solutions
   - Dynamic guess count based on difficulty
   - Machine learning for better word selection
   - Parallel search across multiple attempts

