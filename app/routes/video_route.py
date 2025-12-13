"""Endpoints pour la génération de vidéos."""

from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_video_service
from app.models.video_model import VideoGenerationRequest, VideoGenerationResponse
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post(
    "/render",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Générer une vidéo",
    description="Génère une vidéo à partir d'un audio et d'un template avec les chemins spécifiés.",
)
async def render_video(
    request: VideoGenerationRequest,
    service: Annotated[VideoService, Depends(get_video_service)],
) -> VideoGenerationResponse:
    """Génère une vidéo à partir d'un audio et d'un template.
    
    Args:
        request: Requête de génération vidéo avec les chemins absolus et relatifs
        service: Service vidéo injecté
        
    Returns:
        VideoGenerationResponse: Réponse avec l'URL de la vidéo générée
        
    Raises:
        HTTPException: Si une erreur survient lors de la génération
    """
    try:
        return await service.render_video(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de la vidéo: {str(e)}"
        )
