"""
Authentication endpoints for user registration and login.
Uses JWT tokens, bcrypt password hashing, and SQLite database.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import logging
import traceback
import sys

from app.database import get_db, init_db
from app.models.user import User
from app.config import settings

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize HTTP Bearer token
security = HTTPBearer()

# Initialize router
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize database on module load
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}", exc_info=True)


# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str


class SignupResponse(BaseModel):
    success: bool
    user: UserResponse


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class ErrorResponse(BaseModel):
    error: str


# Password utilities
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    logger.debug(f"Creating access token for data: {list(data.keys())}")
    
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        logger.debug(f"Token expiration: {expire.isoformat()}")
        to_encode.update({"exp": expire})
        
        # Verify SECRET_KEY is set
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production-use-env-var":
            logger.error("SECRET_KEY is not properly configured!")
            raise ValueError("SECRET_KEY is not configured")
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Token created successfully (length: {len(encoded_jwt)} characters)")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}", exc_info=True)
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token."""
    logger.debug(f"Decoding token (length: {len(token)} characters)")
    
    try:
        # Verify SECRET_KEY is set
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production-use-env-var":
            logger.error("SECRET_KEY is not properly configured!")
            raise ValueError("SECRET_KEY is not configured")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Token decoded successfully. Payload: {list(payload.keys())}")
        return payload
    except jwt.ExpiredSignatureError as expired_error:
        logger.warning(f"Token has expired: {expired_error}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidSignatureError as sig_error:
        logger.warning(f"Invalid token signature: {sig_error}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except jwt.DecodeError as decode_error:
        logger.warning(f"Token decode error: {decode_error}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except jwt.JWTError as jwt_error:
        logger.warning(f"JWT error: {jwt_error}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error validating token"
        )


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    logger.debug("get_current_user called - validating token")
    
    token = credentials.credentials
    logger.debug(f"Token received (length: {len(token)} characters)")
    
    try:
        # Decode and verify token
        logger.debug("Decoding access token...")
        try:
            payload = decode_access_token(token)
            logger.debug(f"Token decoded successfully. Payload keys: {payload.keys()}")
        except jwt.ExpiredSignatureError as expired_error:
            logger.warning(f"Expired token attempt: {expired_error}")
            logger.debug(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as invalid_error:
            logger.warning(f"Invalid token attempt: {invalid_error}")
            logger.debug(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as decode_error:
            logger.error(f"Error decoding token: {decode_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error validating token"
            )
        
        # Extract user ID
        user_id: int = payload.get("sub")
        logger.debug(f"Extracted user ID from token: {user_id}")
        
        if user_id is None:
            logger.warning("Token missing user ID in payload")
            logger.debug(f"Token payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Query user from database
        logger.debug(f"Querying database for user ID: {user_id}")
        try:
            user = db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as db_error:
            logger.error(f"Database error while fetching user: {db_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error accessing user database"
            )
        
        if user is None:
            logger.warning(f"User {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        logger.debug(f"User authenticated successfully: {user.email} (User ID: {user.id})")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are intentional)
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting current user: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        logger.error(f"Error details - Type: {type(e)}, Args: {e.args}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Validates email is not already used, hashes password, and saves user to database.
    """
    logger.info(f"Signup attempt started for email: {request.email}")
    
    try:
        # Normalize email
        email = request.email.lower().strip()
        logger.debug(f"Normalized email: {email}")
        
        # Check if user already exists
        logger.debug(f"Checking if user exists: {email}")
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {email} (User ID: {existing_user.id})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password
        password_length = len(request.password)
        logger.debug(f"Password length: {password_length}")
        if password_length < 8:
            logger.warning(f"Signup attempt with password less than 8 characters (length: {password_length})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Hash password
        logger.debug("Hashing password...")
        try:
            password_hash = hash_password(request.password)
            logger.debug("Password hashed successfully")
        except Exception as hash_error:
            logger.error(f"Error hashing password: {hash_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )
        
        # Create new user
        logger.debug("Creating user object...")
        new_user = User(
            email=email,
            password_hash=password_hash
        )
        
        # Save to database
        logger.debug("Saving user to database...")
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"User registered successfully: {email} (User ID: {new_user.id})")
        except IntegrityError as db_error:
            logger.error(f"Database integrity error during signup: {db_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except SQLAlchemyError as db_error:
            logger.error(f"Database error during signup: {db_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving user to database"
            )
        
        return SignupResponse(
            success=True,
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                created_at=new_user.created_at.isoformat()
            )
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are intentional)
        raise
    except ValidationError as validation_error:
        logger.error(f"Validation error during signup: {validation_error}", exc_info=True)
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data"
        )
    except Exception as e:
        logger.error(f"Unexpected error during signup: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        logger.error(f"Error details - Type: {type(e)}, Args: {e.args}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user with email and password.
    
    Validates credentials and returns JWT token + user object.
    """
    logger.info(f"Login attempt started for email: {request.email}")
    
    try:
        # Normalize email
        email = request.email.lower().strip()
        logger.debug(f"Normalized email: {email}")
        
        # Find user
        logger.debug(f"Querying database for user: {email}")
        try:
            user = db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as db_error:
            logger.error(f"Database error during login query: {db_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error accessing user database"
            )
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.debug(f"User found: {email} (User ID: {user.id})")
        
        # Verify password
        logger.debug("Verifying password...")
        try:
            password_valid = verify_password(request.password, user.password_hash)
        except Exception as verify_error:
            logger.error(f"Error verifying password: {verify_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying password"
            )
        
        if not password_valid:
            logger.warning(f"Invalid password attempt for email: {email} (User ID: {user.id})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.debug("Password verified successfully")
        
        # Create access token
        logger.debug("Creating access token...")
        try:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.id},
                expires_delta=access_token_expires
            )
            logger.debug("Access token created successfully")
        except Exception as token_error:
            logger.error(f"Error creating access token: {token_error}", exc_info=True)
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating authentication token"
            )
        
        logger.info(f"User logged in successfully: {email} (User ID: {user.id})")
        
        return LoginResponse(
            token=access_token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at.isoformat()
            )
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are intentional)
        raise
    except ValidationError as validation_error:
        logger.error(f"Validation error during login: {validation_error}", exc_info=True)
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        logger.error(f"Error details - Type: {type(e)}, Args: {e.args}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    logger.info(f"get_current_user_info called for user: {current_user.email} (User ID: {current_user.id})")
    
    try:
        logger.debug(f"Preparing user response for: {current_user.email}")
        
        user_response = UserResponse(
            id=current_user.id,
            email=current_user.email,
            created_at=current_user.created_at.isoformat()
        )
        
        logger.debug(f"User info retrieved successfully for: {current_user.email}")
        return user_response
        
    except AttributeError as attr_error:
        logger.error(f"Attribute error getting user info: {attr_error}", exc_info=True)
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.error(f"User object: {current_user}, Type: {type(current_user)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting user info: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        logger.error(f"Error details - Type: {type(e)}, Args: {e.args}")
        logger.error(f"Current user object: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )
