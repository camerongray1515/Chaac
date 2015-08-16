import bcrypt

from functools import wraps
from flask import jsonify

def require_authentication_key(request, client):
    def decorator(f):
        @wraps(f)
        def authentication_key_valid(*args, **kwargs):
            authentication_key = request.args.get("key")

            if authentication_key:
                authentication_key = authentication_key.encode("ascii")
            else:
                # Cause the hash function to fail and prevent authentication
                authentication_key = b""

            correct_key_hash = client.config["CONFIG"]["Security"]\
                    ["authentication_key_hash"].encode("ascii")

            valid = bcrypt.hashpw(authentication_key, correct_key_hash)\
                    == correct_key_hash

            if valid:
                return f(*args, **kwargs)
            else:
                return jsonify(success=False, message="Authentication key "
                        "incorrect")
        return authentication_key_valid
    return decorator
