from datetime import date

from app.progression import (
    CautionResult,
    Level,
    SessionRecord,
    compute_caution,
    is_ready_to_advance,
    meets_standard,
    progress_percent,
)

LEVEL3 = Level(sets=3, reps=50, unit="reps", per_side=False)


def session(id_, sets, form_good=True, d=None):
    return SessionRecord(id=id_, date=d or date(2026, 1, id_), sets=sets, form_good=form_good)


# ---------- meets_standard ----------


def test_meets_standard_exact_n_sets_all_pass():
    s = session(1, [50, 50, 50])
    assert meets_standard(s, LEVEL3) is True


def test_meets_standard_fewer_than_n_sets():
    s = session(1, [50, 50])
    assert meets_standard(s, LEVEL3) is False


def test_meets_standard_one_of_n_below_threshold():
    s = session(1, [50, 50, 49])
    assert meets_standard(s, LEVEL3) is False


def test_meets_standard_broken_form_despite_high_reps():
    s = session(1, [100, 100, 100], form_good=False)
    assert meets_standard(s, LEVEL3) is False


def test_meets_standard_extra_low_sets_beyond_n_still_qualifies():
    s = session(1, [50, 50, 50, 1, 1])
    assert meets_standard(s, LEVEL3) is True


def test_meets_standard_boundary_reps_equals_threshold():
    s = session(1, [50, 50, 50])
    assert meets_standard(s, Level(sets=3, reps=50, unit="reps", per_side=False)) is True
    s2 = session(2, [49, 49, 49])
    assert meets_standard(s2, Level(sets=3, reps=50, unit="reps", per_side=False)) is False


# ---------- is_ready_to_advance ----------


def test_ready_zero_sessions():
    result = is_ready_to_advance([], LEVEL3)
    assert result.ready is False


def test_ready_one_session_meeting_standard():
    sessions = [session(1, [50, 50, 50])]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is False


def test_ready_exactly_two_both_meet():
    sessions = [session(1, [50, 50, 50]), session(2, [50, 50, 50])]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is True


def test_ready_exactly_two_only_most_recent_meets():
    sessions = [session(1, [10, 10, 10]), session(2, [50, 50, 50])]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is False


def test_ready_exactly_two_only_older_meets():
    sessions = [session(1, [50, 50, 50]), session(2, [10, 10, 10])]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is False


def test_ready_two_meet_reps_but_one_has_broken_form():
    sessions = [session(1, [50, 50, 50], form_good=False), session(2, [50, 50, 50])]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is False


def test_ready_uses_two_most_recent_not_any_two():
    # oldest two pass, most recent two don't -> not ready
    sessions = [
        session(1, [50, 50, 50], d=date(2026, 1, 1)),
        session(2, [50, 50, 50], d=date(2026, 1, 2)),
        session(3, [10, 10, 10], d=date(2026, 1, 3)),
        session(4, [10, 10, 10], d=date(2026, 1, 4)),
    ]
    result = is_ready_to_advance(sessions, LEVEL3)
    assert result.ready is False


def test_ready_flips_true_after_simulated_edit():
    sessions = [session(1, [10, 10, 10]), session(2, [50, 50, 50])]
    assert is_ready_to_advance(sessions, LEVEL3).ready is False

    edited_sessions = [session(1, [50, 50, 50]), session(2, [50, 50, 50])]
    assert is_ready_to_advance(edited_sessions, LEVEL3).ready is True


def test_ready_flips_false_after_simulated_delete():
    sessions = [session(1, [50, 50, 50]), session(2, [50, 50, 50])]
    assert is_ready_to_advance(sessions, LEVEL3).ready is True

    after_delete = [session(1, [50, 50, 50])]
    assert is_ready_to_advance(after_delete, LEVEL3).ready is False


# ---------- compute_caution ----------


def test_caution_no_prior_sessions():
    new = session(1, [50, 50, 50])
    result = compute_caution(new, [])
    assert result == CautionResult(caution=False, reason=None)


def test_caution_broken_form():
    new = session(1, [50, 50, 50], form_good=False)
    prior = [session(2, [50, 50, 50])]
    result = compute_caution(new, prior)
    assert result.caution is True
    assert "form" in result.reason


def test_caution_best_set_more_than_30_percent_below_average():
    prior = [session(2, [100]), session(3, [100])]  # avg best = 100
    new = session(1, [65])  # 35% below 100
    result = compute_caution(new, prior)
    assert result.caution is True


def test_caution_within_threshold_no_caution():
    prior = [session(2, [100]), session(3, [100])]
    new = session(1, [75])  # exactly 25% below, within threshold
    result = compute_caution(new, prior)
    assert result.caution is False


def test_caution_exactly_30_percent_below_boundary_is_not_caution():
    prior = [session(2, [100]), session(3, [100])]
    new = session(1, [70])  # exactly 30% below -> boundary, strictly-less comparison used
    result = compute_caution(new, prior)
    assert result.caution is False


def test_caution_fewer_than_three_prior_sessions():
    prior = [session(2, [100])]
    new = session(1, [50])  # 50% below the single prior session
    result = compute_caution(new, prior)
    assert result.caution is True


# ---------- progress_percent ----------


def test_progress_percent_index_zero():
    assert progress_percent(0, 11) == 0.0


def test_progress_percent_last_index():
    assert progress_percent(10, 11) == 100.0


def test_progress_percent_mid_range():
    assert progress_percent(5, 11) == 50.0


def test_progress_percent_single_exercise_family():
    assert progress_percent(0, 1) == 100.0
