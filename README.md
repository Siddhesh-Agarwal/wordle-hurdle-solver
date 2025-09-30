# Wordle/Hurdle Solver

## WTH is this?

### Wordle Solver

Solves the [New York Times Wordle](https://www.nytimes.com/games/wordle/index.html) puzzle in 6 guesses by creating a frequency table of the positions of each letter in the word. The frequency table was used to determine the most likely letters to guess next.


### Hurdle Solver

Solves the [Washington Post Hurdle](https://games.washingtonpost.com/games/todays-hurdle) puzzle. Uses the same frequency table logic as the Wordle solver to determine the most likely letters to guess next.

## How TH to use it?

```
git clone https://github.com/Siddhesh-Agarwal/wordle-hurdle-solver.git
cd wordle-hurdle-solver
uv sync
uv run ./main.py
```

## Key

* `Y` -> Yellow - Correct Letter, Wrong Position
* `G` -> Green - Correct Letter, Correct Position
* `B` -> Black - Incorrect Letter
