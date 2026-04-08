from functools import wraps
from flask import abort
from flask_login import current_user

def require_crud(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        if not getattr(current_user, "can_write", False):
            return abort(403)
        return fn(*args, **kwargs)
    return wrapper