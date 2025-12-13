"""Service pour la génération de vidéos."""

import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip

from app.models.video_model import VideoGenerationRequest, VideoGenerationResponse


class VideoService:
    """Service pour générer des vidéos."""

    def __init__(self):
        """Initialise le service vidéo."""
        self.resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        self.template_dir = os.path.join(self.resources_dir, "video-template")
        
        # S'assurer que le répertoire de templates existe
        os.makedirs(self.template_dir, exist_ok=True)

    def _select_random_template(self) -> str:
        """Sélectionner un template vidéo aléatoire.
        
        Returns:
            Chemin absolu du template sélectionné
            
        Raises:
            ValueError: Si aucun template n'est trouvé
        """
        try:
            files = os.listdir(self.template_dir)
            # Filtrer pour ne garder que les fichiers vidéo
            video_files = [f for f in files if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
            
            if not video_files:
                raise ValueError("No video templates found")
            
            template_paths = [os.path.join(self.template_dir, f) for f in video_files]
            selected = random.choice(template_paths)
            
            print(f"✅ Selected template: {os.path.basename(selected)}")
            return selected
            
        except FileNotFoundError:
            raise ValueError(f"Template directory not found: {self.template_dir}")

    async def render_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Génère une vidéo à partir d'un audio et d'un template.
        
        Cette méthode:
        1. Sélectionne un template vidéo aléatoire
        2. Charge l'audio depuis le chemin absolu
        3. Boucle la vidéo pour correspondre à la durée audio
        4. Ajoute l'audio à la vidéo
        5. Exporte la vidéo au chemin spécifié
        
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
        
        try:
            # Vérifier que l'audio existe
            if not os.path.exists(request.audio_path):
                raise ValueError(f"Audio file not found: {request.audio_path}")
            
            # Sélectionner un template vidéo
            print("📹 Sélection d'un template vidéo aléatoire...")
            template_path = self._select_random_template()
            
            # Charger l'audio et obtenir sa durée
            print("🎵 Chargement de l'audio...")
            audio_clip = AudioFileClip(request.audio_path)
            audio_duration_sec = audio_clip.duration
            print(f"✅ Audio chargé: {audio_duration_sec:.2f}s")
            
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
            
            # Ajouter l'audio à la vidéo
            print("🎧 Ajout de l'audio à la vidéo...")
            final_video = video_clip.set_audio(audio_clip)
            
            # S'assurer que le répertoire de sortie existe
            output_dir = os.path.dirname(request.video_absolute_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Exporter la vidéo
            print("⏳ Exportation de la vidéo (cela peut prendre plusieurs minutes)...")
            print(f"   Codec: libx264 | Audio: aac | FPS: {request.fps} | Preset: medium")
            
            final_video.write_videofile(
                request.video_absolute_path,
                codec='libx264',
                audio_codec='aac',
                fps=request.fps,
                preset='medium',
                threads=4,
                logger=None
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
