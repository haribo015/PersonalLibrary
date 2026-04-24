from passlib.hash import bcrypt

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_long_password_can_be_hashed_and_verified() -> None:
    password = "motdepasse-tres-long-" * 8

    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password) is True


def test_bcrypt_hashes_remain_supported() -> None:
    legacy_hash = bcrypt.hash("motdepasse-court")

    assert verify_password("motdepasse-court", legacy_hash) is True


def test_access_token_round_trip_preserves_subject() -> None:
    token = create_access_token({"sub": "reader@example.com"})

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "reader@example.com"


def test_decode_access_token_returns_none_for_invalid_token() -> None:
    assert decode_access_token("not-a-token") is None
