import os
from yt_dlp import YoutubeDL
from langchain_ollama import OllamaLLM  # Importação atualizada
from moviepy.editor import VideoFileClip  # Importação corrigida
import whisper
import json
import tempfile

class YouTubeHighlightExtractor:
    def __init__(self, output_folder=os.path.abspath("highlights")):
        """Initialize the highlight extractor with output folder."""
        self.output_folder = output_folder
        self.llm = OllamaLLM(model="mistral")
        self.whisper_model = whisper.load_model("base")
        
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    def download_video(self, url):
        """Download YouTube video using yt-dlp."""
        try:
            temp_path = tempfile.gettempdir()
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': os.path.join(temp_path, 'temp_video.mp4'),  # Nome fixo
                'quiet': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                downloaded_file = os.path.join(temp_path, 'temp_video.mp4')  # Caminho garantido
                return downloaded_file, "highlight"  # Título não é mais usado
        except Exception as e:
            print(f"Erro no download: {e}")
            return None, None

    def transcribe_video(self, video_path):
        """Transcribe video audio using Whisper."""
        try:
            result = self.whisper_model.transcribe(video_path)
            print(f"[DEBUG] Transcrição: {result['text']}")  # Log para verificar a transcrição
            return result["segments"]
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            return None

    def analyze_segments(self, segments):
        """Analyze segments using Ollama to identify highlights."""
        highlights = []
        chunk_size = 3  # Reduza o tamanho do chunk para mais precisão
        for i in range(0, len(segments), chunk_size):
            chunk = segments[i:i + chunk_size]
            chunk_text = " ".join([seg["text"] for seg in chunk])
            
            # Prompt otimizado para respostas binárias
            prompt = f"""
            **Instruções Estritas**:
            1. Analise o texto abaixo.
            2. Responda APENAS com 'SIM' ou 'NÃO'.
            3. 'SIM' apenas se o texto contiver:
               - Emoção forte (alegria, raiva, surpresa)
               - Informação importante (dica, conclusão, revelação)
               - Resumo ou chamada para ação

            Texto: {chunk_text}
            """
            
            try:
                response = self.llm.invoke(prompt).strip().lower()
                print(f"Segmento {i}: {response}")  # Debug
                
                # Fallback manual se o JSON falhar
                if "sim" in response:
                    highlights.append({
                        "start_time": chunk[0]['start'],
                        "end_time": chunk[-1]['end'],
                        "reason": "Momento relevante detectado"
                    })
                    
            except Exception as e:
                print(f"Erro: {e}")
                continue
                
        return highlights

    def extract_highlights(self, video_path, highlights, original_title):
        """Extract highlight clips from the video."""
        try:
            with VideoFileClip(video_path) as video:  # Gerenciamento de contexto
                for idx, highlight in enumerate(highlights):
                    start_time = highlight["start_time"]
                    end_time = highlight["end_time"]
                    print(f"[DEBUG] Processando destaque {idx+1}: {start_time}s -> {end_time}s")  # Log
                    
                    # Extract the clip
                    clip = video.subclip(start_time, end_time)
                    
                    # Generate output filename
                    output_filename = f"{original_title}_highlight_{idx + 1}.mp4"
                    output_path = os.path.join(self.output_folder, output_filename)
                    
                    # Save the clip
                    clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
                    
                    # Save highlight metadata
                    metadata_filename = f"{original_title}_highlight_{idx + 1}_metadata.json"
                    metadata_path = os.path.join(self.output_folder, metadata_filename)
                    with open(metadata_path, 'w') as f:
                        json.dump({
                            "timestamp": f"{start_time:.2f} - {end_time:.2f}",
                            "reason": highlight["reason"]
                        }, f, indent=4)
        except Exception as e:
            print(f"Erro ao extrair destaques: {e}")

    def process_video(self, url):
        """Process a YouTube video and extract highlights."""
        # Download video
        video_path, title = self.download_video(url)
        if not video_path:
            return
        
        try:
            # Transcribe video
            print("Transcrevendo vídeo...")
            segments = self.transcribe_video(video_path)
            if not segments:
                return
            
            # Analyze segments
            print("Analisando conteúdo...")
            highlights = self.analyze_segments(segments)
            
            if not highlights:  # Validação crítica
                print("Nenhum destaque identificado. Verifique o prompt ou o modelo.")
                os.remove(video_path)
                return
            
            # Extract highlights
            print("Extraindo destaques...")
            self.extract_highlights(video_path, highlights, title)
            
            # Cleanup
            if os.path.exists(video_path):
                os.remove(video_path)
            print(f"Processamento concluído! Destaques salvos em {self.output_folder}")
            
        except Exception as e:
            print(f"Erro ao processar vídeo: {e}")
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except PermissionError:
                    print("Arquivo ainda em uso. Tente novamente mais tarde.")

def main():
    extractor = YouTubeHighlightExtractor()
    url = input("Insira a URL do YouTube: ")
    extractor.process_video(url)

if __name__ == "__main__":
    main()