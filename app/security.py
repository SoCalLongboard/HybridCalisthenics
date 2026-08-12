from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext

from app.config import SECRET_KEY

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="session-cookie")

COOKIE_NAME = "session"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_session_token(user_id: int) -> str:
    return _serializer.dumps({"user_id": user_id})


def read_session_token(token: str, max_age: int) -> int | None:
    try:
        data = _serializer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("user_id")
