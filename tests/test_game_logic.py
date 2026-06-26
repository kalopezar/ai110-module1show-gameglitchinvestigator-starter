from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

# FIX: Regression test co-written with AI to lock in the comparison-bug fix.
def test_numeric_comparison_not_lexicographic():
    # Regression test for the int-vs-string comparison bug.
    # 9 is numerically LESS than 100, so the hint must be "Too Low".
    # The old buggy code compared values as strings, where "9" > "100"
    # (alphabetical order), which wrongly returned "Too High".
    result = check_guess(9, 100)
    assert result == "Too Low"
