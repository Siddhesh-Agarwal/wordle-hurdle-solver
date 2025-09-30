import json
from rich.prompt import Prompt
from src.model import WordleSolver, HurdleSolver


def main():
    words: list[str] = json.load(open("./words.json", "r"))
    choices = ["wordle", "hurdle"]
    choice = Prompt.ask(
        "Choose game mode (wordle/hurdle): ", choices=choices, case_sensitive=False
    ).lower()
    if choice == choices[0]:
        solver = WordleSolver(words)
        solver.solve_interactive()
    elif choice == choices[1]:
        solver = HurdleSolver(words)
        solver.solve_hurdle(4)


if __name__ == "__main__":
    main()
