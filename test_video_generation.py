#!/usr/bin/env python3
"""Script de test pour reproduire l'erreur MoviePy."""

import os
import sys
from moviepy.editor import VideoFileClip, AudioFileClip

# Chemins de test
audio_path = "/app/test_resources/audio/final_audio.mp3"
template_path = "/app/test_resources/video-template/test_template.mp4"
output_path = "/app/test_resources/output/test_output.mp4"

print("🎬 Test de génération vidéo avec MoviePy")
print(f"📂 Audio: {audio_path}")
print(f"📂 Template: {template_path}")
print(f"📂 Output: {output_path}")
print()

try:
    # Charger l'audio
    print("🎵 Chargement de l'audio...")
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    print(f"✅ Audio chargé: {audio_duration:.2f}s")
    print()
    
    # Charger la vidéo template
    print("📽️ Chargement du template vidéo...")
    video_clip = VideoFileClip(template_path)
    print(f"✅ Template chargé: {video_clip.duration:.2f}s")
    print()
    
    # Boucler la vidéo pour correspondre à la durée audio
    if video_clip.duration < audio_duration:
        print(f"🔄 Bouclage de la vidéo...")
        n_loops = int(audio_duration / video_clip.duration) + 1
        video_clip = video_clip.loop(n=n_loops)
    
    # Couper à la durée exacte
    video_clip = video_clip.subclip(0, audio_duration)
    print(f"✅ Vidéo ajustée à {video_clip.duration:.2f}s")
    print()
    
    # Ajouter l'audio
    print("🎧 Ajout de l'audio à la vidéo...")
    final_video = video_clip.set_audio(audio_clip)
    print(f"✅ Audio attaché: {final_video.audio is not None}")
    print()
    
    # Test 1: Avec verbose=False et logger=None (version originale - devrait échouer)
    print("=" * 60)
    print("TEST 1: verbose=False, logger=None (VERSION ORIGINALE)")
    print("=" * 60)
    try:
        final_video.write_videofile(
            "/app/test_resources/output/test_v1_original.mp4",
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4,
            verbose=False,
            logger=None,
            temp_audiofile="temp_audio_v1.m4a",
            remove_temp=True
        )
        print("✅ TEST 1 RÉUSSI!")
    except Exception as e:
        print(f"❌ TEST 1 ÉCHOUÉ: {type(e).__name__}: {str(e)}")
    print()
    
    # Test 2: Avec verbose=True et logger='bar' (version corrigée)
    print("=" * 60)
    print("TEST 2: verbose=True, logger='bar' (VERSION CORRIGÉE)")
    print("=" * 60)
    try:
        final_video.write_videofile(
            "/app/test_resources/output/test_v2_corrected.mp4",
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4,
            verbose=True,
            logger='bar',
            temp_audiofile="temp_audio_v2.m4a",
            remove_temp=True
        )
        print("✅ TEST 2 RÉUSSI!")
    except Exception as e:
        print(f"❌ TEST 2 ÉCHOUÉ: {type(e).__name__}: {str(e)}")
    print()
    
    # Test 3: Sans logger ni verbose (laisser les defaults)
    print("=" * 60)
    print("TEST 3: Sans spécifier logger/verbose (DEFAULTS)")
    print("=" * 60)
    try:
        final_video.write_videofile(
            "/app/test_resources/output/test_v3_defaults.mp4",
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4,
            temp_audiofile="temp_audio_v3.m4a",
            remove_temp=True
        )
        print("✅ TEST 3 RÉUSSI!")
    except Exception as e:
        print(f"❌ TEST 3 ÉCHOUÉ: {type(e).__name__}: {str(e)}")
    print()
    
    # Nettoyer
    print("🧹 Nettoyage...")
    final_video.close()
    audio_clip.close()
    video_clip.close()
    
    print()
    print("=" * 60)
    print("🎉 TESTS TERMINÉS")
    print("=" * 60)
    
    # Lister les fichiers générés
    print("\n📁 Fichiers générés:")
    for file in os.listdir("/app/test_resources/output"):
        filepath = os.path.join("/app/test_resources/output", file)
        size = os.path.getsize(filepath)
        print(f"   - {file} ({size/1024/1024:.2f} MB)")

except Exception as e:
    print(f"❌ ERREUR GÉNÉRALE: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
