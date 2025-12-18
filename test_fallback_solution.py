#!/usr/bin/env python3
"""Test de la solution avec fallback."""

import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.insert(0, '/app')

from app.services.video_service import VideoService
from app.models.video_model import VideoGenerationRequest

print("🎬 Test de la solution avec stratégie de fallback")
print("=" * 60)
print()

# Préparer les chemins
audio_path = "/app/test_resources/audio/final_audio.mp3"
template_path = "/app/test_resources/video-template/test_template.mp4"
background_music_path = "/app/test_resources/audio/background_music.mp3"
output_path = "/app/test_resources/output/test_fallback_solution.mp4"

# Créer le service
service = VideoService()

# Créer la requête
request = VideoGenerationRequest(
    audio_path=audio_path,
    video_template_path=template_path,
    video_absolute_path=output_path,
    video_relative_path="test_fallback_solution.mp4",
    background_music=background_music_path,
    fps=30
)

print(f"📂 Audio: {request.audio_path}")
print(f"📂 Template: {request.video_template_path}")
print(f"📂 Musique de fond: {request.background_music}")
print(f"📂 Output: {request.video_absolute_path}")
print()

try:
    # Tester la génération
    import asyncio
    result = asyncio.run(service.render_video(request))
    
    print()
    print("=" * 60)
    print("✅ GÉNÉRATION RÉUSSIE!")
    print("=" * 60)
    print(f"📊 Status: {result.status}")
    print(f"📊 Message: {result.message}")
    print(f"📊 Durée: {result.duration:.2f}s")
    print(f"📊 Video URL: {result.video_url}")
    
    # Vérifier le fichier
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"📊 Taille du fichier: {size_mb:.2f} MB")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ GÉNÉRATION ÉCHOUÉE")
    print("=" * 60)
    print(f"Erreur: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
