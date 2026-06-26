# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.**

  Glitchy Guesser is a Streamlit number-guessing game. The app picks a secret
  number within a range that depends on the chosen difficulty (Easy 1–20,
  Normal 1–100, Hard 1–50), and the player tries to guess it within a limited
  number of attempts. After each guess the game gives a "Higher/Lower" hint,
  tracks the score, and ends with a win (correct guess) or a loss (out of
  attempts). It was deliberately shipped with bugs as a debugging exercise.

- [x] **Detail which bugs you found.**

  - **Lying Higher/Lower hints (every other guess):** on even-numbered
    attempts the secret was converted to a string, so `check_guess` compared an
    `int` guess against a `str` secret. The comparison fell back to alphabetical
    ordering (e.g. `"9" > "100"` is `True`), producing wrong hints and making
    wins impossible on those turns.
  - **Swapped hint text:** "Too High" displayed "📈 Go HIGHER!" and "Too Low"
    displayed "📉 Go LOWER!" — both pointed the player the wrong direction.
  - **Misleading error handling:** the original `check_guess` wrapped its
    comparison in a `try/except TypeError` that silently compared values as
    strings, hiding the type bug instead of fixing it.

- [x] **Explain what fixes you applied.**

  - Refactored `check_guess` into `logic_utils.py` using a clean numeric
    comparison and returning a single outcome string; removed the misleading
    `try/except` fallback.
  - Removed the `attempts % 2` block in `app.py` so the integer secret is always
    passed straight to `check_guess`.
  - Corrected the hint directions via a `HINT_MESSAGES` map (Too High → 📉 Go
    LOWER!, Too Low → 📈 Go HIGHER!).
  - Added a regression test, `check_guess(9, 100) == "Too Low"`, that fails
    under the old string-comparison bug. All 4 tests pass.

## 📝 Demo Walkthrough

A textual walkthrough of a sample game on **Normal** difficulty (range 1–100,
8 attempts). For this example the secret number is **63**.

1. The app loads and shows "Guess a number between 1 and 100. Attempts left: 8".
2. User enters a guess of **40** and clicks "Submit Guess 🚀".
3. Since 40 < 63, the game returns **"Too Low"** with the hint **"📈 Go HIGHER!"**.
4. User enters a guess of **80** → 80 > 63, so the game returns **"Too High"** with the hint **"📉 Go LOWER!"**.
5. The score and attempt counter update after each guess (attempts left ticks down, score adjusts based on the outcome).
6. User narrows in and enters **63** → the game returns **"Win"** with **"🎉 Correct!"**.
7. The game celebrates with balloons, shows "You won! The secret was 63." plus the final score, and locks input until "New Game 🔁" is clicked.
8. Clicking **"New Game 🔁"** resets the attempts and picks a fresh secret number, so the next round starts cleanly.

> The hints now always point the correct direction (HIGHER when the guess is
> too low, LOWER when it's too high) on every attempt — including even-numbered
> ones, which was the original glitch.

## 🧪 Test Results

```
$ python -m pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: ...\ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.13.0, html-4.2.0, metadata-3.1.1
collecting ... collected 4 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 25%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 50%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 75%]
tests/test_game_logic.py::test_numeric_comparison_not_lexicographic PASSED [100%]

============================== 4 passed in 0.01s =============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
