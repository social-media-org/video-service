#!/usr/bin/env python3
"""Test avec musique de fond comme dans le vrai cas d'usage."""

import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

# Chemins
audio_path = "/app/test_resources/audio/final_audio.mp3"
template_path = "/app/test_resources/video-template/test_template.mp4"

# Créer une fausse musique de fond (5 secondes de la même audio)
print("🎵 Création d'une musique de fond de test...")
music_clip = AudioFileClip(audio_path).subclip(0, 5)
music_path = "/app/test_resources/audio/background_music.mp3"
music_clip.write_audiofile(music_path, verbose=False, logger=None)
music_clip.close()
print(f"✅ Musique de fond créée: {music_path}")
print()

print("🎬 Test de génération vidéo AVEC musique de fond")
print()

try:
    # Charger l'audio principal
    print("🎵 Chargement de l'audio principal...")
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    print(f"✅ Audio principal chargé: {audio_duration:.2f}s")
    
    # Charger et préparer la musique de fond
    print("🎵 Chargement de la musique de fond...")
    background_music_clip = AudioFileClip(music_path)
    background_music_clip = background_music_clip.volumex(0.3)
    
    # Boucler la musique de fond
    if background_music_clip.duration < audio_duration:
        n_loops = int(audio_duration / background_music_clip.duration) + 1
        clips = [background_music_clip] * n_loops
        background_music_clip = concatenate_audioclips(clips)
    
    background_music_clip = background_music_clip.subclip(0, audio_duration)
    
    # Mixer l'audio principal avec la musique de fond
    print("🔊 Création du CompositeAudioClip...")
    final_audio = CompositeAudioClip([audio_clip, background_music_clip])
    print(f"✅ CompositeAudioClip créé")
    print(f"   Type: {type(final_audio).__name__}")
    print(f"   Duration: {final_audio.duration:.2f}s")
    print()
    
    # Charger la vidéo
    print("📽️ Chargement du template vidéo...")
    video_clip = VideoFileClip(template_path)
    
    # Boucler et couper la vidéo
    if video_clip.duration < audio_duration:
        n_loops = int(audio_duration / video_clip.duration) + 1
        video_clip = video_clip.loop(n=n_loops)
    video_clip = video_clip.subclip(0, audio_duration)
    
    # Ajouter l'audio composite
    print("🎧 Ajout de l'audio composite à la vidéo...")
    final_video = video_clip.set_audio(final_audio)
    print(f"✅ Audio attaché: {final_video.audio is not None}")
    print(f"   Audio type: {type(final_video.audio).__name__}")
    print()
    
    # TEST avec verbose=False et logger=None (cas problématique)
    print("=" * 60)
    print("TEST: verbose=False, logger=None (AVEC COMPOSITE AUDIO)")
    print("=" * 60)
    try:
        output_path = "/app/test_resources/output/test_composite_original.mp4"
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4,
            verbose=False,
            logger=None,
            temp_audiofile="temp_audio_composite.m4a",
            remove_temp=True
        )
        print(f"✅ TEST RÉUSSI! Fichier: {output_path}")
        print(f"   Taille: {os.path.getsize(output_path)/1024/1024:.2f} MB")
    except Exception as e:
        print(f"❌ TEST ÉCHOUÉ: {type(e).__name__}: {str(e)}")
        import traceback
        print("\n📋 Stack trace complet:")
        traceback.print_exc()
    print()
    
    # TEST avec verbose=True et logger='bar' (correction proposée)
    print("=" * 60)
    print("TEST: verbose=True, logger='bar' (AVEC COMPOSITE AUDIO)")
    print("=" * 60)
    try:
        output_path = "/app/test_resources/output/test_composite_corrected.mp4"
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4,
            verbose=True,
            logger='bar',
            temp_audiofile="temp_audio_composite2.m4a",
            remove_temp=True
        )
        print(f"✅ TEST RÉUSSI! Fichier: {output_path}")
        print(f"   Taille: {os.path.getsize(output_path)/1024/1024:.2f} MB")
    except Exception as e:
        print(f"❌ TEST ÉCHOUÉ: {type(e).__name__}: {str(e)}")
        import traceback
        print("\n📋 Stack trace complet:")
        traceback.print_exc()
    
    # Nettoyer
    print("\n🧹 Nettoyage...")
    final_video.close()
    audio_clip.close()
    background_music_clip.close()
    video_clip.close()

except Exception as e:
    print(f"\n❌ ERREUR GÉNÉRALE: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ Tests terminés")
