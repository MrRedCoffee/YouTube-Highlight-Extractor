# YouTube Highlight Extractor

Um script Python que identifica e extrai automaticamente os momentos mais relevantes de vídeos do YouTube usando:
- Transcrição de áudio com Whisper (OpenAI)
- Análise de conteúdo com Mistral via Ollama
- Edição de vídeo com MoviePy

## 🌟 Funcionalidades
- Download de vídeos do YouTube
- Transcrição automática do áudio
- Identificação de momentos-chave usando IA
- Geração de clipes destacados
- Metadados descritivos para cada highlight

## 📋 Requisitos
- Python 3.8+
- Ollama rodando localmente ([instalação](https://ollama.ai/))
- ffmpeg (`sudo apt install ffmpeg` no Linux)

## ⚙️ Instalação
1. Clone o repositório:
```bash
git clone github.com/MrRedCoffee/YouTube-Highlight-Extractor/youtube-highlight-extractor.git
cd youtube-highlight-extractor
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Uso
1. Inicie o Ollama em outro terminal:
```bash
ollama serve
```

2. Execute o script:
```bash
python youtube-cut-v1.py
```

3. Cole a URL do YouTube quando solicitado

Os destaques serão salvos na pasta `/highlights` com:
- Vídeo clipado (.mp4)
- Metadados correspondentes (.json)

## ⚙️ Configuração
Personalize no código:
```python
# Para mudar o modelo LLM
self.llm = OllamaLLM(model="outro-modelo")  # Ex: llama2

# Para alterar pasta de saída
extractor = YouTubeHighlightExtractor(output_folder="/caminho/alternativo")
```

## 📌 Limitações
- Qualidade da transcrição depende do modelo Whisper (base)
- Precisão na detecção varia com o conteúdo
- Processamento pode ser demorado para vídeos longos

