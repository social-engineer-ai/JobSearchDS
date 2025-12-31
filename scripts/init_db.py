"""Initialize the database with all tables."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from webapp.app.database import engine, Base

# Import all models to ensure they're registered
from webapp.app.models import (
    Candidate,
    Company,
    Job,
    Application,
    Skill,
    CandidateSkill,
    JobSkill,
    Interaction
)


def init_db():
    """Create all database tables."""
    print("Initializing database...")

    # Ensure data directory exists
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")
    print(f"Database location: {data_dir / 'jobmatch.db'}")


if __name__ == "__main__":
    init_db()
