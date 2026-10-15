import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, joinedload
from sqlalchemy.ext.declarative import declarative_base
from page import HTML

#db
DB_URL = "sqlite:///" + os.environ.get("GYM_DB", "./gym.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbsession = Annotated[Session, Depends(get_db)]

#app
app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return HTML


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    sets = relationship("Sets", back_populates="exercise", cascade="all, delete-orphan")

class Sets(Base):
    __tablename__ = "sets"

    id = Column(String, primary_key=True, index=True)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)

    exercise_id = Column(String, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)

    exercise = relationship("Exercise", back_populates="sets")


class SetCreate(BaseModel):
    reps: int
    weight: float | None = None

class SetResponse(BaseModel):
    id: str
    reps: int
    weight: float | None = None

    class Config:
        from_attributes = True

class SetUpdate(BaseModel):
    reps: int | None = None
    weight: float | None = None

class ExerciseCreate(BaseModel):
    name: str
    sets: list[SetCreate] | None = None

class ExerciseResponse(BaseModel):
    id: str
    name: str
    sets: list[SetResponse] = []

    class Config:
        from_attributes = True

class ExerciseUpdate(BaseModel):
    name: str | None = None


@app.post("/exercise", response_model=ExerciseResponse)
def create_exercise(data: ExerciseCreate, db: dbsession):
    new_exercise = Exercise(id=str(uuid4()), name=data.name)

    if data.sets:
        for set_data in data.sets:
            new_set = Sets(id=str(uuid4()), reps=set_data.reps, weight=set_data.weight)
            new_exercise.sets.append(new_set)

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

@app.get("/exercise", response_model=list[ExerciseResponse])
def show_exercise(db: dbsession):
    return db.query(Exercise).options(joinedload(Exercise.sets)).all()


@app.patch("/exercise/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: str, ex_data: ExerciseUpdate, db: dbsession):
    exercise_for_update = db.get(Exercise, exercise_id)
    if not exercise_for_update:
        raise HTTPException(status_code=404, detail="Exercise Not Found")
    if ex_data.name is not None:
        exercise_for_update.name = ex_data.name
    db.commit()
    db.refresh(exercise_for_update)
    return exercise_for_update

@app.delete("/exercise/{exercise_id}")
def delete_exercise(exercise_id: str, db: dbsession):
    exercise_for_delete = db.get(Exercise, exercise_id)
    if not exercise_for_delete:
        raise HTTPException(status_code=404, detail="Exercise Not Found")
    db.delete(exercise_for_delete)
    db.commit()
    return {"status": "success", "message": "Exercise Deleted"}

@app.post("/exercise/{exercise_id}/sets", response_model=SetResponse)
def create_set(exercise_id: str, data: SetCreate, db: dbsession):
    set_for_create = db.get(Exercise, exercise_id)
    if not set_for_create:
        raise HTTPException(status_code=404, detail="Exercise Not Found")
    new_set = Sets(id=str(uuid4()), reps=data.reps, weight=data.weight, exercise_id=exercise_id)
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set

@app.patch("/set/{set_id}", response_model=SetResponse)
def update_set(set_id: str, set_data: SetUpdate, db: dbsession):
    set_for_update = db.get(Sets, set_id)
    if not set_for_update:
        raise HTTPException(status_code=404, detail="Set Not Found")
    if set_data.reps is not None:
        set_for_update.reps = set_data.reps
    if set_data.weight is not None:
        set_for_update.weight = set_data.weight
    db.commit()
    db.refresh(set_for_update)
    return set_for_update

@app.delete("/set/{set_id}")
def delete_set(set_id: str, db: dbsession):
    set_for_delete = db.get(Sets, set_id)
    if not set_for_delete:
        raise HTTPException(status_code=404, detail="Set Not Found")
    db.delete(set_for_delete)
    db.commit()
    return {"status": "success", "message": "Set Deleted"}
