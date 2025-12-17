"""Service pour la génération de vidéos."""

import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

from app.models.video_model import VideoGenerationRequest, VideoGenerationResponse


class VideoService:
    """Service pour générer des vidéos."""

    def __init__(self):
        """Initialise le service vidéo."""
        self.resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        self.template_dir = os.path.join(self.resources_dir, "video-template")
        
        # S'assurer que le répertoire de templates existe
        os.makedirs(self.template_dir, exist_ok=True)

    def _validate_template_path(self, template_path: str) -> str:
        """Valider le chemin du template vidéo.
        
        Args:
            template_path: Chemin du template spécifié
            
        Returns:
            Chemin absolu du template validé
            
        Raises:
            ValueError: Si le template n'existe pas
        """
        if not template_path:
            raise ValueError("Video template path is required")
        
        if not os.path.exists(template_path):
            raise ValueError(f"Video template not found: {template_path}")
        
        print(f"✅ Utilisation du template vidéo: {os.path.basename(template_path)}")
        return template_path

    def _add_background_music(self, audio_clip: AudioFileClip, background_music_path: str) -> CompositeAudioClip:
        """Ajouter une musique de fond à l'audio principal.
        
        Args:
            audio_clip: Clip audio principal
            background_music_path: Chemin de la musique de fond
            
        Returns:
            Clip audio mixé avec la musique de fond
        """
        print("🎵 Chargement de la musique de fond...")
        background_music_clip = AudioFileClip(background_music_path)
        
        # Ajuster le volume de la musique de fond (30% du volume)
        background_music_clip = background_music_clip.volumex(0.1 )
        
        audio_duration_sec = audio_clip.duration
        
        # Boucler la musique de fond pour correspondre à la durée audio
        if background_music_clip.duration < audio_duration_sec:
            n_loops = int(audio_duration_sec / background_music_clip.duration) + 1
            # Créer une liste de clips répétés
            clips = [background_music_clip] * n_loops
            # Concaténer les clips pour créer une boucle
            background_music_clip = concatenate_audioclips(clips)
        
        # Couper à la durée exacte de l'audio principal
        background_music_clip = background_music_clip.subclip(0, audio_duration_sec)
        
        # Mixer l'audio principal avec la musique de fond
        print("🔊 Mixage de l'audio principal avec la musique de fond...")
        final_audio = CompositeAudioClip([audio_clip, background_music_clip])
        print(f"✅ Musique de fond ajoutée (volume: 30%)")
        
        # Fermer le clip de musique de fond (il est maintenant intégré dans CompositeAudioClip)
        background_music_clip.close()
        
        return final_audio

    async def render_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Génère une vidéo à partir d'un audio et d'un template.
        
        Cette méthode:
        1. Valide le chemin du template vidéo
        2. Charge l'audio depuis le chemin absolu
        3. Ajoute la musique de fond si spécifiée
        4. Boucle la vidéo pour correspondre à la durée audio
        5. Ajoute l'audio à la vidéo
        6. Exporte la vidéo au chemin spécifié
        
        Args:
            request: Requête de génération vidéo contenant les chemins et paramètres
            
        Returns:
            VideoGenerationResponse: Réponse avec les informations de la vidéo générée
            
        Raises:
            ValueError: Si les fichiers nécessaires n'existent pas
        """
        print(f"🎬 Début de la génération vidéo")
        print(f"📂 Audio: {request.audio_path}")
        print(f"📂 Vidéo sortie: {request.video_absolute_path}")
        print(f"📂 Template vidéo: {request.video_template_path if request.video_template_path else 'Non spécifié'}")
        print(f"🎵 Musique de fond: {request.background_music if request.background_music else 'Aucune'}")
        
        try:
            # Vérifier que l'audio existe
            if not os.path.exists(request.audio_path):
                raise ValueError(f"Audio file not found: {request.audio_path}")
            
            # Valider le chemin du template vidéo
            template_path = self._validate_template_path(request.video_template_path)
            
            # Charger l'audio principal et obtenir sa durée
            print("🎵 Chargement de l'audio principal...")
            audio_clip = AudioFileClip(request.audio_path)
            audio_duration_sec = audio_clip.duration
            print(f"✅ Audio principal chargé: {audio_duration_sec:.2f}s")
            
            # Gérer la musique de fond si spécifiée
            final_audio = audio_clip
            if request.background_music:
                if os.path.exists(request.background_music):
                    final_audio = self._add_background_music(audio_clip, request.background_music)
                else:
                    print(f"⚠️ Musique de fond spécifiée mais non trouvée: {request.background_music}")
            
            # Charger le template vidéo
            print("📽️ Chargement du template vidéo...")
            video_clip = VideoFileClip(template_path)
            print(f"✅ Template chargé: {video_clip.duration:.2f}s")
            
            # Boucler la vidéo pour correspondre à la durée audio
            if video_clip.duration < audio_duration_sec:
                print(f"🔄 Bouclage de la vidéo (durée template: {video_clip.duration:.2f}s → {audio_duration_sec:.2f}s)")
                n_loops = int(audio_duration_sec / video_clip.duration) + 1
                video_clip = video_clip.loop(n=n_loops)
            
            # Couper à la durée exacte de l'audio
            video_clip = video_clip.subclip(0, audio_duration_sec)
            
            # Ajouter l'audio final à la vidéo
            print("🎧 Ajout de l'audio à la vidéo...")
            final_video = video_clip.set_audio(final_audio)
            
            # Debug: Check if audio is properly attached
            print(f"✅ Audio attaché: {final_video.audio is not None}")
            if final_video.audio:
                print(f"   Durée audio: {final_video.audio.duration:.2f}s")
                # Try to get fps, but handle case where it might not exist
                try:
                    fps_value = final_video.audio.fps
                    print(f"   Sample rate: {fps_value} Hz")
                except AttributeError:
                    print(f"   Sample rate: N/A (CompositeAudioClip)")
            
            # S'assurer que le répertoire de sortie existe
            output_dir = os.path.dirname(request.video_absolute_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Exporter la vidéo
            print("⏳ Exportation de la vidéo (cela peut prendre plusieurs minutes)...")
            print(f"   Codec: libx264 | Audio: aac | FPS: {request.fps} | Preset: medium")
            
            # Use verbose logging to see any errors
            # Also try different audio codec if 'aac' fails
            final_video.write_videofile(
                request.video_absolute_path,
                codec='libx264',
                audio_codec='aac',
                fps=request.fps,
                preset='medium',
                threads=4,
                verbose=False,
                logger=None,
                temp_audiofile="temp_audio.m4a",  # Specify temp audio file
                remove_temp=True  # Remove temp file after
            )
            
            # Fermer les clips pour libérer les ressources
            final_video.close()
            audio_clip.close()
            video_clip.close()
            
            print(f"✅ Vidéo générée avec succès: {request.video_absolute_path}")
            print(f"📊 Durée finale: {audio_duration_sec:.2f}s")
            
            # Créer l'URL de la vidéo (sera construite par le ui-service)
            # On retourne juste le chemin relatif
            video_url = request.video_relative_path
            
            # Pour la thumbnail, on pourrait extraire une frame, pour l'instant on retourne un placeholder
            thumbnail_url = ""
            
            return VideoGenerationResponse(
                video_url=video_url,
                thumbnail=thumbnail_url,
                duration=audio_duration_sec,
                status="success",
                message=f"Video generated successfully at {request.video_absolute_path}"
            )
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération vidéo: {str(e)}")
            raise ValueError(f"Error generating video: {str(e)}")
