"""Modèles Pydantic pour la génération de vidéos."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ImageScene(BaseModel):
    """Modèle pour une scène d'image."""
    prompt: str = Field(..., description="Prompt de génération")
    url: str | None = Field(None, description="URL de l'image générée")


class VideoGenerationRequest(BaseModel):
    """Requête pour générer la vidéo finale."""
    audio_path: str = Field(..., description="Chemin absolu de l'audio final (obligatoire)")
    video_absolute_path: str = Field(..., description="Chemin absolu pour la vidéo de sortie (obligatoire)")
    video_relative_path: str = Field(..., description="Chemin relatif de la vidéo par rapport à RESSOURCE_DIR (obligatoire)")
    images: Optional[List[ImageScene]] = Field(
        [],
        description="Liste des images avec URLs (optionnel, défaut: liste vide)"
    )
    resolution: Optional[str] = Field(
        "1080p",
        description="Résolution de la vidéo (optionnel, défaut: 1080p)"
    )
    fps: Optional[int] = Field(
        30,
        ge=24,
        le=60,
        description="Images par seconde (optionnel, défaut: 30)"
    )
    video_template_path: Optional[str] = Field(
        None,
        description="Chemin absolu du template vidéo (optionnel, défaut: None)"
    )
    background_music: Optional[str] = Field(
        None,
        description="chemin absolue ou rul de la musique de fond (optionnel, défaut: none)"
    )


class VideoGenerationResponse(BaseModel):
    """Réponse de génération vidéo."""
    video_url: str = Field(..., description="URL de la vidéo générée")
    thumbnail: str = Field(..., description="URL de la miniature")
    duration: float = Field(..., description="Durée de la vidéo en secondes")
    status: str = Field(default="success", description="Statut de la génération")
    message: Optional[str] = Field(None, description="Message d'information")
