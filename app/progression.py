"""Pure progression-logic module. No FastAPI or SQLAlchemy imports allowed here —
callers convert ORM rows to the dataclasses below and convert results back."""

from dataclasses import dataclass
from datetime import date

CAUTION_DROP_THRESHOLD = 0.30  # "more than 30% below" triggers a caution


@dataclass(frozen=True)
class Level:
    sets: int
    reps: int
    unit: str
    per_side: bool


@dataclass(frozen=True)
class SessionRecord:
    id: int
    date: date
    sets: list[int]
    form_good: bool


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    reason: str


@dataclass(frozen=True)
class CautionResult:
    caution: bool
    reason: str | None


def best_set(session: SessionRecord) -> int:
    return max(session.sets)


def meets_standard(session: SessionRecord, level: Level) -> bool:
    """Sort the session's sets descending, take the top `level.sets` entries.
    Meets the standard iff exactly that many sets exist, every one of them is
    >= level.reps, and form was good. Broken form always fails."""
    if not session.form_good:
        return False

    top_n = sorted(session.sets, reverse=True)[: level.sets]
    if len(top_n) < level.sets:
        return False

    return all(value >= level.reps for value in top_n)


def _two_most_recent(sessions: list[SessionRecord]) -> list[SessionRecord]:
    return sorted(sessions, key=lambda s: (s.date, s.id), reverse=True)[:2]


def is_ready_to_advance(sessions_for_exercise: list[SessionRecord], level3: Level) -> ReadinessResult:
    """`sessions_for_exercise` must already be filtered to the current exercise by
    the caller. Ready iff the two MOST RECENT sessions both meet the level-3
    standard. Always recompute this live from current data — never cache the
    result, since sessions can be edited or deleted after logging."""
    if len(sessions_for_exercise) < 2:
        return ReadinessResult(ready=False, reason="needs at least 2 logged sessions")

    two_most_recent = _two_most_recent(sessions_for_exercise)
    passes = [meets_standard(s, level3) for s in two_most_recent]

    if all(passes):
        return ReadinessResult(ready=True, reason="last 2 sessions both meet level 3")

    num_passing = sum(passes)
    return ReadinessResult(
        ready=False,
        reason=f"only {num_passing} of the last 2 sessions meet level 3",
    )


def compute_caution(new_session: SessionRecord, prior_sessions: list[SessionRecord]) -> CautionResult:
    """`prior_sessions` should be the 2-3 sessions immediately before `new_session`
    on the same exercise (caller's responsibility to select/order them).
    Informational only — never mutates progression state."""
    if not new_session.form_good:
        return CautionResult(caution=True, reason="form was marked broken")

    if not prior_sessions:
        return CautionResult(caution=False, reason=None)

    prior_best_avg = sum(best_set(s) for s in prior_sessions) / len(prior_sessions)
    new_best = best_set(new_session)

    if new_best < prior_best_avg * (1 - CAUTION_DROP_THRESHOLD):
        return CautionResult(
            caution=True,
            reason="best set is more than 30% below your recent average — consider a lighter session",
        )

    return CautionResult(caution=False, reason=None)


def progress_percent(exercise_index: int, total_exercises_in_family: int) -> float:
    if total_exercises_in_family <= 1:
        return 100.0
    return round(100.0 * exercise_index / (total_exercises_in_family - 1), 1)
