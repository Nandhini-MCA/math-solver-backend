from passlib.context import CryptContext

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    h = pwd_context.hash("password123")
    print(f"Hash: {h}")
except Exception as e:
    print(f"Error: {e}")
