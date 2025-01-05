from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer

# API base URL
BASE_URL = "https://api.pulsemcp.com/v0beta"


# Define the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


class Server(Base):
    __tablename__ = "servers"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_code_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    github_stars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    package_registry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    package_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    package_download_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    experimental_ai_generated_description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    integrations: Mapped[List["ServerIntegration"]] = relationship(
        back_populates="server", cascade="all, delete-orphan"
    )


class Integration(Base):
    __tablename__ = "integrations"

    slug: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    servers: Mapped[List["ServerIntegration"]] = relationship(
        back_populates="integration"
    )


class ServerIntegration(Base):
    __tablename__ = "server_integrations"

    server_name: Mapped[str] = mapped_column(
        ForeignKey("servers.name"), primary_key=True
    )
    integration_slug: Mapped[str] = mapped_column(
        ForeignKey("integrations.slug"), primary_key=True
    )

    server: Mapped["Server"] = relationship(back_populates="integrations")
    integration: Mapped["Integration"] = relationship(back_populates="servers")
