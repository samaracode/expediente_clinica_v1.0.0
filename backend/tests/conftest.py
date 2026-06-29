# Patch JSONB to JSON for SQLite compatibility — MUST be before any model import
from sqlalchemy.dialects import postgresql as _pg
from sqlalchemy import types as _sa_types

_pg.JSONB = _sa_types.JSON

# Now safe to import models
import pytest
from datetime import date, datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base

# Import all models so they register with Base.metadata
import app.models.file  # noqa: F401  (referenced by FK in consent/resident)
import app.models.user  # noqa: F401
import app.models.resident  # noqa: F401
import app.models.admission  # noqa: F401
import app.models.follow_up  # noqa: F401
import app.models.treatment  # noqa: F401
import app.models.consent  # noqa: F401
import app.models.medical  # noqa: F401
import app.models.assessment  # noqa: F401
import app.models.audit  # noqa: F401
import app.models.medication  # noqa: F401
import app.models.attendance  # noqa: F401
import app.models.occupancy  # noqa: F401

from app.models.user import User, UserRole
from app.models.resident import Resident
from app.models.admission import Admission, AdmissionStatus
from app.models.follow_up import Consultation, ExitPass, PassStatus, PassType
from app.models.treatment import TreatmentPlan, TreatmentStage, StageName, StageStatus


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestSession()
    yield session
    session.close()
    engine.dispose()


# --- Factory fixtures ---

@pytest.fixture
def make_user(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {
            "full_name": f"User {counter['n']}",
            "email": f"user{counter['n']}@test.com",
            "hashed_password": "hashed",
            "role": UserRole.admin,
            "is_active": True,
        }
        defaults.update(kwargs)
        u = User(**defaults)
        db.add(u)
        db.flush()
        return u

    return _make


@pytest.fixture
def make_resident(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {
            "first_name": "Juan",
            "last_name": "Pérez",
            "code": f"ZOE-{counter['n']:04d}",
        }
        defaults.update(kwargs)
        r = Resident(**defaults)
        db.add(r)
        db.flush()
        return r

    return _make


@pytest.fixture
def make_admission(db, make_resident):
    counter = {"n": 0}

    def _make(resident=None, **kwargs):
        counter["n"] += 1
        if resident is None:
            resident = make_resident()
        defaults = {
            "resident_id": resident.id,
            "admission_number": f"ADM-{counter['n']:05d}",
            "admission_date": date(2024, 1, 1),
            "status": AdmissionStatus.treatment_active,
        }
        defaults.update(kwargs)
        a = Admission(**defaults)
        db.add(a)
        db.flush()
        return a

    return _make
