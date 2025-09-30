from collections import defaultdict
from typing import List, Dict, Optional, Tuple
import rich
from rich.prompt import Prompt


class WordleSolver:
    def __init__(self, wordlist: List[str]):
        self.wordlist = [w.upper() for w in wordlist if len(w) == 5]
        self.position_freq = self._build_position_frequencies()

    def _build_position_frequencies(self) -> List[Dict[str, int]]:
        freqs: List[Dict[str, int]] = [defaultdict(int) for _ in range(5)]

        for word in self.wordlist:
            for pos, char in enumerate(word):
                freqs[pos][char] += 1

        return freqs

    def score_word(
        self, word: str, possible_words: Optional[List[str]] = None
    ) -> float:
        if possible_words:
            # Recalculate frequencies for remaining possibilities
            temp_freqs = [defaultdict(int) for _ in range(5)]
            for w in possible_words:
                for pos, char in enumerate(w):
                    temp_freqs[pos][char] += 1
            freqs = temp_freqs
        else:
            freqs = self.position_freq

        word = word.upper()
        score = 0.0
        seen = set()

        for pos, char in enumerate(word):
            # Penalize duplicate letters (less information)
            if char in seen:
                score += freqs[pos][char] * 0.5
            else:
                score += freqs[pos][char]
                seen.add(char)

        return score

    def filter_words(
        self, possible_words: List[str], guess: Optional[str], result: str
    ) -> List[str]:
        """
        Filter word list based on guess result.

        result: 5-char string where:
            'G' = Green (correct position)
            'Y' = Yellow (wrong position, but in word)
            'B' = Black/Gray (not in word)

        Example: guess='CRANE', result='BYGBB'
        """
        if guess is None:
            return possible_words
        result = result.upper()

        filtered = []

        # Track yellow letters and their forbidden positions
        yellow_letters = {}  # {char: [forbidden_positions]}
        green_positions = {}  # {position: char}
        black_letters = set()

        # Parse result
        for pos, (char, res) in enumerate(zip(guess, result)):
            if res == "G":
                green_positions[pos] = char
            elif res == "Y":
                if char not in yellow_letters:
                    yellow_letters[char] = []
                yellow_letters[char].append(pos)
            elif res == "B":
                # Only mark as black if it's not yellow/green elsewhere
                if char not in yellow_letters and char not in green_positions.values():
                    black_letters.add(char)

        # Filter words
        for word in possible_words:
            word = word.upper()
            valid = True

            # Check green positions
            for pos, char in green_positions.items():
                if word[pos] != char:
                    valid = False
                    break

            if not valid:
                continue

            # Check yellow letters (must exist but not in guessed position)
            for char, forbidden_pos in yellow_letters.items():
                if char not in word:
                    valid = False
                    break
                for pos in forbidden_pos:
                    if word[pos] == char:
                        valid = False
                        break
                if not valid:
                    break

            if not valid:
                continue

            # Check black letters
            for char in black_letters:
                if char in word:
                    valid = False
                    break

            if valid:
                filtered.append(word)

        return filtered

    def suggest_best_guess(
        self, possible_words: Optional[List[str]] = None
    ) -> Tuple[Optional[str], float]:
        """Return the best guess and its score."""
        candidates = possible_words if possible_words else self.wordlist

        if not candidates:
            return None, 0.0

        best_word = max(candidates, key=lambda w: self.score_word(w, candidates))
        best_score = self.score_word(best_word, candidates)

        return best_word, best_score

    def solve_interactive(self):
        """Interactive solving session."""
        possible = self.wordlist

        rich.print(f"Starting with {len(possible)} possible words")

        for attempt in range(1, 7):
            guess, score = self.suggest_best_guess(possible)
            rich.print()
            rich.print(
                f"[bold]Attempt {attempt}[/]: Try '{guess}' (score: {score:.0f})"
            )
            rich.print(f"[bold]Remaining possibilities[/]: {len(possible)}")

            result = (
                Prompt.ask(
                    "Enter result (G/Y/B for each position, or 'q' to quit): ",
                )
                .strip()
                .upper()
            )

            if result == "Q":
                break

            if result == "GGGGG":
                rich.print(f"[green bold]Solved in {attempt} attempts![/]")
                break

            if len(result) != 5:
                rich.print("[red bold]Invalid result. Must be 5 characters.[/]")
                continue

            possible = self.filter_words(possible, guess, result)

            if len(possible) == 0:
                rich.print(
                    "[red bold]No possible words remaining. Check your inputs.[/]"
                )
                break

            if len(possible) <= 10:
                rich.print(f"Remaining words: {', '.join(possible)}")


class HurdleSolver(WordleSolver):
    """
    Hurdle solver - sequential Wordles where each answer becomes
    the first guess of the next puzzle.
    """

    def suggest_best_guess(
        self, possible_words: Optional[List[str]] = None, forced_first_guess: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Return the best guess and its score.
        If forced_first_guess is provided, that's the only option.
        """
        if forced_first_guess:
            return forced_first_guess.upper(), self.score_word(
                forced_first_guess, possible_words
            )

        return super().suggest_best_guess(possible_words)

    def solve_single_wordle(
        self, forced_first_guess: Optional[str] = None, puzzle_num: int = 1
    ) -> Optional[str]:
        """
        Solve a single Wordle puzzle.
        Returns the answer if solved, None if failed.
        """
        possible = self.wordlist[:]
        attempt = 1
        max_attempts = 6

        print(f"\n{'=' * 50}")
        print(f"PUZZLE #{puzzle_num}")
        print(f"{'=' * 50}")
        print(f"Starting with {len(possible)} possible words")

        if forced_first_guess:
            print(f"Forced first guess: {forced_first_guess.upper()}")

        while attempt <= max_attempts:
            if attempt == 1 and forced_first_guess:
                guess, score = self.suggest_best_guess(
                    possible, forced_first_guess=forced_first_guess
                )
            else:
                guess, score = self.suggest_best_guess(possible)

            print(f"\nAttempt {attempt}: Try '{guess}' (score: {score:.0f})")
            print(f"Remaining possibilities: {len(possible)}")

            result = input("Enter result (G/Y/B for each position): ").strip().upper()

            if result == "GGGGG":
                print(f"✓ Solved in {attempt} attempts! Answer: {guess}")
                return guess

            if len(result) != 5 or not all(c in "GYB" for c in result):
                print("Invalid result. Must be 5 characters (G/Y/B only).")
                continue

            possible = self.filter_words(possible, guess, result)

            if len(possible) == 0:
                print("⚠ No possible words remaining. Check your inputs.")
                return None

            if len(possible) <= 10:
                print(f"Remaining words: {', '.join(possible)}")

            attempt += 1

        print(f"✗ Failed to solve in {max_attempts} attempts")
        return None

    def solve_hurdle(self, num_puzzles: int = 4):
        """
        Solve a complete Hurdle game (sequential Wordles).
        Each puzzle's answer becomes the first guess of the next puzzle.
        """
        print("=" * 50)
        print(f"HURDLE SOLVER - {num_puzzles} SEQUENTIAL PUZZLES")
        print("=" * 50)

        previous_answer = None

        for puzzle_num in range(1, num_puzzles + 1):
            answer = self.solve_single_wordle(
                forced_first_guess=previous_answer, puzzle_num=puzzle_num
            )

            if answer is None:
                print(f"\n✗ HURDLE FAILED at puzzle #{puzzle_num}")
                return False

            previous_answer = answer

            if puzzle_num < num_puzzles:
                print(f"\n→ Next puzzle will start with: {previous_answer}")
                input("Press Enter to continue to next puzzle...")

        print("\n" + "=" * 50)
        print("🎉 HURDLE COMPLETED! All puzzles solved!")
        print("=" * 50)
        return True
