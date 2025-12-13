"""Dependency injection for API layer."""

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.services.video_service import VideoService


def get_video_service() -> VideoService:
    """Get Video service instance.

    Returns:
        VideoService: Service instance
    """
    return VideoService()
