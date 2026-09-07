import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("username")
    @classmethod
    def username_no_whitespace(cls, v: str) -> str:
        if v != v.strip() or not v:
            raise ValueError("username must not have leading/trailing whitespace")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    must_change_password: bool

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=200)


class AdminUserOut(BaseModel):
    id: int
    username: str
    created_at: dt.datetime
    last_login_at: dt.datetime | None
    is_admin: bool
    is_active: bool
    must_change_password: bool

    model_config = ConfigDict(from_attributes=True)


class AdminPasswordResetOut(BaseModel):
    temporary_password: str


class FamilyProgressOut(BaseModel):
    family: str
    exercise_index: int
    exercise_name: str
    total_exercises: int
    progress_percent: float
    milestone: str
    ready_to_advance: bool
    readiness_reason: str


class ProgressOut(BaseModel):
    families: list[FamilyProgressOut]


class AdvanceResult(BaseModel):
    family: str
    exercise_index: int
    exercise_name: str


class SessionCreate(BaseModel):
    family: str
    date: dt.date
    sets: list[int] = Field(min_length=1)
    form_good: bool
    notes: str | None = None

    @field_validator("sets")
    @classmethod
    def sets_non_negative(cls, v: list[int]) -> list[int]:
        if any(s < 0 for s in v):
            raise ValueError("reps must be non-negative integers")
        return v


class SessionUpdate(BaseModel):
    date: dt.date | None = None
    sets: list[int] | None = Field(default=None, min_length=1)
    form_good: bool | None = None
    notes: str | None = None

    @field_validator("sets")
    @classmethod
    def sets_non_negative(cls, v: list[int] | None) -> list[int] | None:
        if v is not None and any(s < 0 for s in v):
            raise ValueError("reps must be non-negative integers")
        return v


class SessionOut(BaseModel):
    id: int
    family: str
    exercise_name: str
    date: dt.date
    sets: list[int]
    form_good: bool
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class SessionCreateResult(BaseModel):
    session: SessionOut
    caution: bool
    caution_reason: str | None
