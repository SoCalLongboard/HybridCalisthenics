import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.catalog import family_names, get_exercise_at_index, get_exercise_list
from app.deps import get_current_user, get_db
from app.models import FamilyProgress, User, WorkoutSession
from app.progression import Level, SessionRecord, is_ready_to_advance, progress_percent
from app.schemas import AdvanceResult, FamilyProgressOut, ProgressOut

router = APIRouter(prefix="/api/progress", tags=["progress"])


def get_or_create_progress(db: Session, user: User, family: str) -> FamilyProgress:
    progress = (
        db.query(FamilyProgress)
        .filter(FamilyProgress.user_id == user.id, FamilyProgress.family == family)
        .first()
    )
    if progress is None:
        progress = FamilyProgress(user_id=user.id, family=family, exercise_index=0)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def _level_from_dict(level: dict) -> Level:
    return Level(sets=level["sets"], reps=level["reps"], unit=level["unit"], per_side=level["perSide"])


def _sessions_for_current_exercise(
    db: Session, user: User, family: str, exercise_name: str
) -> list[SessionRecord]:
    rows = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.family == family,
            WorkoutSession.exercise_name == exercise_name,
        )
        .all()
    )
    return [
        SessionRecord(id=r.id, date=r.date, sets=json.loads(r.sets), form_good=r.form_good) for r in rows
    ]


def _build_family_progress_out(db: Session, user: User, family: str) -> FamilyProgressOut:
    progress = get_or_create_progress(db, user, family)
    exercises = get_exercise_list(family)
    exercise = get_exercise_at_index(family, progress.exercise_index)

    sessions = _sessions_for_current_exercise(db, user, family, exercise["name"])
    level3 = _level_from_dict(exercise["level3"])
    readiness = is_ready_to_advance(sessions, level3)

    return FamilyProgressOut(
        family=family,
        exercise_index=progress.exercise_index,
        exercise_name=exercise["name"],
        total_exercises=len(exercises),
        progress_percent=progress_percent(progress.exercise_index, len(exercises)),
        milestone=exercise["level3"]["raw"],
        ready_to_advance=readiness.ready,
        readiness_reason=readiness.reason,
    )


@router.get("", response_model=ProgressOut)
def get_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProgressOut:
    families = [_build_family_progress_out(db, user, family) for family in family_names()]
    return ProgressOut(families=families)


@router.post("/{family}/advance", response_model=AdvanceResult)
def advance_family(
    family: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdvanceResult:
    if family not in family_names():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown family")

    progress = get_or_create_progress(db, user, family)
    exercises = get_exercise_list(family)
    exercise = get_exercise_at_index(family, progress.exercise_index)

    if progress.exercise_index >= len(exercises) - 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already at the final exercise in this family",
        )

    sessions = _sessions_for_current_exercise(db, user, family, exercise["name"])
    level3 = _level_from_dict(exercise["level3"])
    readiness = is_ready_to_advance(sessions, level3)

    if not readiness.ready:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=readiness.reason)

    progress.exercise_index += 1
    db.commit()
    db.refresh(progress)

    new_exercise = get_exercise_at_index(family, progress.exercise_index)
    return AdvanceResult(
        family=family,
        exercise_index=progress.exercise_index,
        exercise_name=new_exercise["name"],
    )
