from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Union
from pydantic import BaseModel
from database import Base, Server, Integration, ServerIntegration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///pulsemcp.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class IntegrationModel(BaseModel):
    name: str
    slug: str
    url: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj, from_attributes=True)

class ServerIntegrationModel(BaseModel):
    slug: str

    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj, from_attributes=True)

class ServerModel(BaseModel):
    name: str
    url: Optional[str] = None
    external_url: Optional[str] = None
    short_description: Optional[str] = None
    source_code_url: Optional[str] = None
    github_stars: Optional[int] = None
    package_registry: Optional[str] = None
    package_name: Optional[str] = None
    package_download_count: Optional[int] = None
    EXPERIMENTAL_ai_generated_description: Optional[str] = None
    integrations: List[ServerIntegrationModel] = []

    @classmethod
    def from_orm(cls, obj):
        # Manually map `integrations` relationship
        integrations = [
            ServerIntegrationModel(slug=integration.integration_slug)
            for integration in obj.integrations
        ]
        # Add integrations to the validated model
        return cls.model_validate(
            {**obj.__dict__, "integrations": integrations},
            from_attributes=True,
        )

@router.get("/integrations", response_model=List[IntegrationModel])
async def get_integrations(db: Session = Depends(get_db)):
    """
    Fetch a list of integrations from the database.

    Returns:
        List of integrations.
    """
    integrations = db.query(Integration).all()
    return [IntegrationModel.from_orm(integration) for integration in integrations]

@router.get("/servers", response_model=Dict[str, Union[List[ServerModel], bool, int]])
async def get_servers(offset: int = 0, count_per_page: int = 500, db: Session = Depends(get_db)):
    """
    Fetch a paginated list of servers from the database.

    Args:
        offset: The starting index for the server list.
        count_per_page: Number of servers to fetch per page.

    Returns:
        A dictionary containing the servers and pagination metadata.
    """
    total_servers = db.query(Server).count()
    servers = (
        db.query(Server)
        .offset(offset)
        .limit(count_per_page)
        .all()
    )
    return {
        "servers": [ServerModel.from_orm(server) for server in servers],
        "next": offset + count_per_page < total_servers,
        "total": total_servers
    }
