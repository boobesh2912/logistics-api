from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import SHIPMENT_DB_URL, AUTH_DB_URL

shipment_engine = create_engine(SHIPMENT_DB_URL)
auth_engine = create_engine(AUTH_DB_URL)

ShipmentSession = sessionmaker(autocommit=False, autoflush=False, bind=shipment_engine)
AuthSession = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)

Base = declarative_base()


def get_shipment_db():
    db = ShipmentSession()
    try:
        yield db
    finally:
        db.close()


def get_auth_db():
    db = AuthSession()
    try:
        yield db
    finally:
        db.close()
