from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from datetime import datetime
from fastapi_utils.tasks import repeat_every



# Database Setup
DATABASE_URL = "sqlite:///./progress_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)  # Unique dates to prevent duplicate entries
    goals = Column(String)
    achievements = Column(String, nullable=True)
    challenges = Column(String, nullable=True)
    lessons = Column(String, nullable=True)
    tasks = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    mood = Column(Integer, nullable=True)
    reflection = Column(String, nullable=True)

# Create Tables
Base.metadata.create_all(bind=engine)

# FastAPI Setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
@repeat_every(seconds=86400)  # Run every 24 hours (at midnight)
def delete_incomplete_entries(db: Session = next(get_db())):
    """Deletes entries without goals after the date ends."""
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        # Query for entries with an expired date that don't have goals
        incomplete_entries = db.query(Progress).filter(
            Progress.date < today, Progress.goals == ""
        ).all()

        # Delete each incomplete entry
        for entry in incomplete_entries:
            db.delete(entry)
        
        db.commit()
        print(f"Deleted {len(incomplete_entries)} incomplete entries.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"An error occurred while deleting entries: {str(e)}")


# Route to Display Home Page with All Entries Sorted by Date
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        entries = db.query(Progress).order_by(Progress.date.desc()).all()
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "An error occurred while retrieving the entries."}
        )
    return templates.TemplateResponse("home.html", {"request": request, "entries": entries})

# Route to Display the Form to Add Data
@app.get("/add", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Route to Handle Form Submission
@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    date: str = Form(...),
    goals: str = Form(...),
    achievements: Optional[str] = Form(None),
    challenges: Optional[str] = Form(None),
    lessons: Optional[str] = Form(None),
    tasks: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    mood: Optional[str] = Form(None),  # Accept mood as a string initially
    reflection: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Check for duplicate date entries
        existing_entry = db.query(Progress).filter(Progress.date == date).first()
        if existing_entry:
            raise HTTPException(status_code=400, detail="An entry for this date already exists.")

        # Convert mood to an integer if provided, otherwise set to None
        mood_value = int(mood) if mood and mood.isdigit() else None

        new_entry = Progress(
            date=date,
            goals=goals,
            achievements=achievements or "",
            challenges=challenges or "",
            lessons=lessons or "",
            tasks=tasks or "",
            notes=notes or "",
            mood=mood_value,
            reflection=reflection or ""
        )
        db.add(new_entry)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "message": "An error occurred while saving the entry."}
        )
    return templates.TemplateResponse(
        "success.html", 
        {"request": request, "message": "Progress entry saved successfully!"}
    )

# Route to View Entry by Date
@app.get("/entries/{entry_date}", response_class=HTMLResponse)
async def view_entry_by_date(entry_date: str, request: Request, db: Session = Depends(get_db)):
    try:
        entry = db.query(Progress).filter(Progress.date == entry_date).first()
        if not entry:
            return templates.TemplateResponse(
                "error.html", {"request": request, "message": "Entry not found."}
            )
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "An error occurred while retrieving the entry."}
        )
    return templates.TemplateResponse("entry.html", {"request": request, "entry": entry})

# Route to Delete an Entry by Date
@app.post("/delete/{entry_date}", response_class=HTMLResponse)
async def delete_entry(entry_date: str, request: Request, db: Session = Depends(get_db)):
    try:
        entry = db.query(Progress).filter(Progress.date == entry_date).first()
        if not entry:
            return templates.TemplateResponse(
                "error.html", {"request": request, "message": "Entry not found."}
            )
        db.delete(entry)
        db.commit()
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "An error occurred while deleting the entry."}
        )
    return templates.TemplateResponse(
        "success.html", {"request": request, "message": "Entry deleted successfully!"}
    )



# Route to View All Entries
@app.get("/entries", response_class=HTMLResponse)
async def view_entries(request: Request, db: Session = Depends(get_db)):
    try:
        entries = db.query(Progress).order_by(Progress.date.desc()).all()
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "An error occurred while retrieving the entries."}
        )
    return templates.TemplateResponse("entries.html", {"request": request, "entries": entries})



# Route to Load the Update Form
@app.get("/update/{entry_date}", response_class=HTMLResponse)
async def load_update_form(entry_date: str, request: Request, db: Session = Depends(get_db)):
    entry = db.query(Progress).filter(Progress.date == entry_date).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return templates.TemplateResponse("update_form.html", {"request": request, "entry": entry})

# Route to Handle Entry Updates
@app.post("/update/{entry_date}", response_class=HTMLResponse)
async def update_entry(
    entry_date: str,
    request: Request,
    goals: str = Form(...),
    achievements: str = Form(""),
    challenges: str = Form(""),
    lessons: str = Form(""),
    tasks: str = Form(""),
    notes: str = Form(""),
    mood: int = Form(None),
    reflection: str = Form(""),
    db: Session = Depends(get_db)
):
    today = datetime.now().strftime("%Y-%m-%d")
    if entry_date != today:
        raise HTTPException(status_code=400, detail="You can only update today's entries.")

    entry = db.query(Progress).filter(Progress.date == entry_date).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")

    entry.goals = goals
    entry.achievements = achievements
    entry.challenges = challenges
    entry.lessons = lessons
    entry.tasks = tasks
    entry.notes = notes
    entry.mood = mood
    entry.reflection = reflection

    db.commit()
    return templates.TemplateResponse(
        "success.html", {"request": request, "message": "Entry updated successfully!"}
    )

# Background Task to Delete Incomplete Entries
