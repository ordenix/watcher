from sqlalchemy.orm import Session
from database import *


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
