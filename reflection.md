# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
The game loaded and allowed me to enter guesses, but several parts of the gameplay did not work correctly. The feedback messages, attempt tracking, difficulty settings, and new game functionality were inconsistent and often gave incorrect results.

- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
The hint system gave backward results. For example, it would say "Go higher" when my guess was already higher than the secret number, and "Go lower" when the secret number was actually higher.
The game reported that I still had attempts remaining, but when I submitted another guess it displayed "Game Over" and would not allow me to continue.
Clicking "New Game" did not properly restart the game. The attempt counter was not reset, and sometimes the game would not start a new round at all.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess: 70, Secret :40 | :Go lower" (70 > 40) | "Go higher" - hint is reversed| Comparison operator flipped: guess > secret triggers "Go higher instead of "Go lower" |

| Guess submitted when counter shows "2 attempts left"| Accept guess, show hint, decrement cuonter| Immediately shows "Game Over" and blocks further input| Attempt counter off-by-one error; game ends at 1 remaining instead of 0 |

| Click "New Game" button | Reset attempts to max, generate new secret number, clear input and feedback| Attempt counter stays at previous value; secret number may not regenerate | newGame() function not reinitializing attemptsLeft or secretNumber variables |

| Select "Hard" difficulty (e.g. 1-200), then guess 150| Secret number is somewhere in 1-200 range| Secret number is still in Easy range (e.g. 1-50); hints resolve too quickly| Difficulty setting upgdates the UI label but does not change the range passed to Match.randow()|

| Guess: 30, Secret: 80 -> told "Go higher" -> guess 60| If 60<80, show :Go higher" again| Shows "Go higher" repeatedly even after guessing above 80| Hint logic re-checks against a stale or wrong value of secretNumber|

| Score display after winning| Score updates clearly (e.g. "You won in 4 guesses!")| Score either doesn't update, shows wrong number, or is ambiguous | Score variable not tied to actual attempt count, or display element not refreshed on win|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I used Claude (Claude Code) in agent mode as my main AI teammate. I treated it like a pair-programming partner: I described the glitches I saw while playing, and asked it to trace the root cause before changing any code so I could understand the bug myself instead of just accepting a patch.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

**What the AI suggested:** When I asked why the Higher/Lower hints lied on every other guess, Claude pointed to the `if st.session_state.attempts % 2 == 0:` block in `app.py`, which converted the secret to a string (`str(st.session_state.secret)`) on even-numbered attempts. It explained that this forced Python to compare an `int` guess against a `str` secret, and suggested removing the block so the integer secret is always passed straight to `check_guess`. **Was it correct?** Yes — this was the real root cause of the alternating bug. **How I verified it:** I wrote a pytest regression test, `check_guess(9, 100)`, which must return `"Too Low"` (9 < 100). It passed after the fix, and when I replayed the game with the Developer Debug Info open, the hints pointed the correct direction on every guess instead of only odd ones.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

**What the AI suggested:** The original AI that *generated* the game had written `check_guess` with a `try/except TypeError` block: when the int-vs-string comparison crashed, it "handled" the error by converting both values to strings and comparing those instead. In the code comments it claimed this made the game "production-ready." **Was it correct?** No — it was misleading. The `except` block looked like responsible error handling, but it silently hid the type bug and produced wrong hints, because strings compare alphabetically. **How I verified it:** I traced the comparison by hand — `"9" > "100"` evaluates to `True` (since `'9' > '1'`) even though numerically `9 < 100`. That is exactly why guessing 9 against a secret of 100 told me to "Go LOWER." Once I saw that the fallback was masking the bug rather than fixing it, I deleted the whole `try/except` and replaced it with a plain numeric comparison.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

I decided a bug was fixed only when I could confirm it two ways: the automated tests passed, and the behavior was correct when I actually played the game. For the hint bug specifically, I wasn't satisfied that the green checkmark from `pytest` was enough, so I also replayed several rounds with the Developer Debug Info expander open so I could see the secret number and check that every "Higher/Lower" message pointed the right way. A bug only counted as fixed when both the test and the live gameplay agreed.

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.

I ran `python -m pytest tests/ -v`, which executes the `check_guess` tests in `tests/test_game_logic.py`. The key one was the regression test I added, `test_numeric_comparison_not_lexicographic`, which asserts `check_guess(9, 100) == "Too Low"`. This test was important because 9 and 100 are a pair where numeric order and alphabetical order disagree — under the old buggy string comparison, `"9" > "100"` is `True`, so it would have returned "Too High." When all 4 tests passed, it showed me that the function was now comparing numbers as numbers, not as text, which was the heart of the original glitch.

- Did AI help you design or understand any tests? How?

Yes. AI helped me design a test that actually targets the bug instead of one that passes by coincidence. At first I would have just tested something like `check_guess(40, 50)`, but the AI pointed out that `"40" < "50"` happens to match numeric order, so that test would pass even with the bug present. It suggested using `9` vs `100` precisely because lexicographic and numeric ordering give opposite answers there, which is what makes it a real regression test. That taught me to choose test inputs that would actually fail if the bug came back, rather than inputs that look reasonable but prove nothing.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

I'd tell my friend that Streamlit re-runs the entire script from top to bottom every single time you interact with the page — every button click, text entry, or checkbox toggle restarts the whole file as if you just opened it. That means any normal Python variable gets recreated from scratch on each interaction, so something like `secret = random.randint(1, 100)` would pick a brand-new number on every guess and the game would be impossible. To remember things between reruns, Streamlit gives you `st.session_state`, which is like a small backpack that survives the rerun and holds your data. That's exactly why this project stores `secret`, `attempts`, `score`, and `history` in `st.session_state` and only initializes them with an `if "secret" not in st.session_state` guard, so they're set once and then persist instead of resetting. The big lesson for me was that in Streamlit you have to be deliberate about what lives in session state versus what gets rebuilt every run, because forgetting that distinction is what makes a value seem to "glitch" or reset on its own.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

The habit I really want to keep is writing a test that would actually fail if the bug came back, instead of just clicking around and assuming it's fixed. The `check_guess(9, 100)` test was an eye-opener for me, because an "obvious" test like `40` vs `50` would have passed even with the broken code. Now I think about picking inputs that prove something, not just inputs that happen to work.

- What is one thing you would do differently next time you work with AI on a coding task?

Next time I'd slow down and make the AI explain the root cause before it changes anything, rather than letting it jump straight to a patch. A couple of times I almost accepted a fix without really understanding why the bug happened, and I think that's how you end up with code you can't maintain. I'd rather ask "why is this broken?" first and only apply the fix once I actually get it.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

I used to assume that if AI-generated code ran without errors, it was basically correct. Now I treat it like a first draft from a confident coworker who might be wrong — the `try/except` that "handled" the error while quietly producing wrong answers showed me that code can look polished and still be broken, so I need to read it and test it myself.
