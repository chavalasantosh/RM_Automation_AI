from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, User
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt."""
    return pwd_context.hash(password)

# Database URL from config
SQLALCHEMY_DATABASE_URL = "sqlite:///./rme_new.db"  # Using a new database file

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create superuser if not exists
        db = SessionLocal()
        superuser = db.query(User).filter(User.is_superuser == True).first()
        if not superuser:
            superuser = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True,
                department="IT",
                role="System Administrator"
            )
            db.add(superuser)
            db.commit()
            logger.info("Superuser created successfully")
        db.close()
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_superuser(email: str, username: str, password: str, full_name: str):
    """Create a new superuser."""
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if user:
            raise ValueError("User with this email or username already exists")
        
        # Create superuser
        superuser = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True,
            department="IT",
            role="System Administrator"
        )
        db.add(superuser)
        db.commit()
        logger.info(f"Superuser {username} created successfully")
        return superuser
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating superuser: {str(e)}")
        raise
    finally:
        db.close() 