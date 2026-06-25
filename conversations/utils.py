from django.core.cache import cache
from django.contrib.auth.models import User

LOCK_KEY_PREFIX = "lock:conversation:"
LOCK_TTL = 300


def get_lock_key(conversation_id):
    return f"{LOCK_KEY_PREFIX}{conversation_id}"


def get_conversation_lock(conversation_id):
    key = get_lock_key(conversation_id)
    locked_by_id = cache.get(key)

    if locked_by_id is None:
        return {
            "is_locked": False,
            "locked_by_id": None,
            "locked_by_email": None,
            "expires_in": None
        }

    try:
        ttl = cache.ttl(key)
        if ttl is None or ttl <= 0:
            ttl = 0

    except AttributeError:
        ttl = LOCK_TTL

    try:
        locked_by_user = User.objects.get(id=locked_by_id)
        locked_by_email = locked_by_user.email
    except User.DoesNotExist:
        locked_by_email = "Unknown"

    return {
        "is_locked": True,
        "locked_by_id": locked_by_id,
        "locked_by_email": locked_by_email,
        "expires_in": ttl
    }


def acquire_conversation_lock(conversation_id, user_id, ttl=LOCK_TTL):
    key = get_lock_key(conversation_id)
    current_lock = cache.get(key)

    if current_lock is not None and current_lock != user_id:
        return False

    cache.set(key, user_id, ttl)
    return True


def release_conversation_lock(conversation_id, user_id):
    key = get_lock_key(conversation_id)
    current_lock = cache.get(key)

    if current_lock is None:
        return True

    if current_lock == user_id:
        cache.delete(key)
        return True

    return False
