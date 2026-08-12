import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.catalog import family_names, get_exercise_list
from app.deps import get_current_user, get_db
from app.models import User, WorkoutSession
from app.progression import SessionRecord, compute_caution
from app.routers.progress import get_or_create_progress
from app.schemas import SessionCreate, SessionCreateResult, SessionOut, SessionUpdate

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _to_out(ws: WorkoutSession) -> SessionOut:
    return SessionOut(
        id=ws.id,
        family=ws.family,
        exercise_name=ws.exercise_name,
        date=ws.date,
        sets=json.loads(ws.sets),
        form_good=ws.form_good,
        notes=ws.notes,
    )


def _to_record(ws: WorkoutSession) -> SessionRecord:
    return SessionRecord(id=ws.id, date=ws.date, sets=json.loads(ws.sets), form_good=ws.form_good)


def _validate_family(family: str) -> None:
    if family not in family_names():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Unknown family")


def _get_owned_session(db: Session, user: User, session_id: int) -> WorkoutSession:
    ws = (
        db.query(WorkoutSession)
        .filter(WorkoutSession.id == session_id, WorkoutSession.user_id == user.id)
        .first()
    )
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return ws


@router.get("", response_model=list[SessionOut])
def list_sessions(
    family: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SessionOut]:
    if family is not None:
        _validate_family(family)

    query = db.query(WorkoutSession).filter(WorkoutSession.user_id == user.id)
    if family is not None:
        query = query.filter(WorkoutSession.family == family)
    rows = query.order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc()).all()
    return [_to_out(r) for r in rows]


@router.post("", response_model=SessionCreateResult, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionCreateResult:
    _validate_family(payload.family)

    progress = get_or_create_progress(db, user, payload.family)
    exercises = get_exercise_list(payload.family)
    exercise_name = exercises[progress.exercise_index]["name"]

    prior_rows = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.family == payload.family,
            WorkoutSession.exercise_name == exercise_name,
        )
        .order_by(WorkoutSession.date.desc(), WorkoutSession.id.desc())
        .limit(3)
        .all()
    )
    prior_records = [_to_record(r) for r in prior_rows]

    ws = WorkoutSession(
        user_id=user.id,
        family=payload.family,
        exercise_name=exercise_name,
        date=payload.date,
        sets=json.dumps(payload.sets),
        form_good=payload.form_good,
        notes=payload.notes,
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)

    new_record = _to_record(ws)
    caution = compute_caution(new_record, prior_records)

    return SessionCreateResult(session=_to_out(ws), caution=caution.caution, caution_reason=caution.reason)


@router.patch("/{session_id}", response_model=SessionOut)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionOut:
    ws = _get_owned_session(db, user, session_id)

    if payload.date is not None:
        ws.date = payload.date
    if payload.sets is not None:
        ws.sets = json.dumps(payload.sets)
    if payload.form_good is not None:
        ws.form_good = payload.form_good
    if payload.notes is not None:
        ws.notes = payload.notes

    db.commit()
    db.refresh(ws)
    return _to_out(ws)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    ws = _get_owned_session(db, user, session_id)
    db.delete(ws)
    db.commit()
