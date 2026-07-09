import sys
import auth
import models
from database import SessionLocal

def reset(email, new_password):
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            print(f"Error: User with email {email} not found.")
            return
        user.hashed_password = auth.get_password_hash(new_password)
        db.commit()
        print(f"Success: Password for {email} has been reset successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py <email> <new_password>")
    else:
        reset(sys.argv[1], sys.argv[2])
