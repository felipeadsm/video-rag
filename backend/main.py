import os
import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Importações dos serviços (serão criados na sequência)
from services.youtube import download_audio, extract_video_id
from services.transcriber import transcribe_audio
from services.rag import add_to_vector_db, query_rag, is_video_processed

app = FastAPI(title="Video RAG Tutor API")

# Habilitar CORS para permitir requisições da extensão rodando no YouTube
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Para desenvolvimento, permitimos tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento simples em memória para rastrear o status do processamento
processing_status = {}

# Conjunto para rastrear vídeos que estão atualmente em processamento (evitar duplicação)
active_processing_videos = set()

class ProcessRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    video_id: str
    query: str
    current_time: float | None = None

def process_video_task(task_id: str, url: str, video_id: str):
    """
    Tarefa em background que orquestra o pipeline de ingestão, transcrição e indexação.
    """
    print(f"\n[🚀 INÍCIO] Iniciando processamento do vídeo: {video_id}")
    try:
        print(f"[⬇️ DOWNLOAD] Baixando áudio do YouTube...")
        processing_status[task_id] = {"status": "downloading", "video_id": video_id}
        audio_path, _ = download_audio(url)
        print(f"[✅ DOWNLOAD] Download concluído: {audio_path}")
        
        print(f"[🎙️ WHISPER] Iniciando transcrição de áudio...")
        processing_status[task_id] = {"status": "transcribing", "video_id": video_id}
        segments = transcribe_audio(audio_path)
        print(f"[✅ WHISPER] Transcrição concluída! Segmentos gerados: {len(segments)}")
        
        print(f"[🧠 VECTOR DB] Iniciando indexação no ChromaDB...")
        processing_status[task_id] = {"status": "vectorizing", "video_id": video_id}
        add_to_vector_db(video_id, segments)
        print(f"[✅ VECTOR DB] Indexação concluída para o vídeo {video_id}!")
        
        # Limpeza do arquivo de áudio temporário após a indexação
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"[🗑️ CLEANUP] Arquivo temporário removido: {audio_path}")
            
        processing_status[task_id] = {"status": "completed", "video_id": video_id}
        print(f"[🎉 SUCESSO] Processamento do vídeo {video_id} finalizado com sucesso!\n")
    except Exception as e:
        print(f"[❌ ERRO] Falha no processamento do vídeo {video_id}: {str(e)}\n")
        processing_status[task_id] = {"status": "failed", "error": str(e), "video_id": video_id}
    finally:
        if video_id in active_processing_videos:
            active_processing_videos.remove(video_id)

@app.post("/process")
async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):
    video_id = extract_video_id(request.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="URL inválida. Não foi possível extrair o ID do vídeo.")
        
    # 1. Verifica se já está indexado no banco vetorial
    if is_video_processed(video_id):
        print(f"[⏭️ SKIP] Vídeo {video_id} já estava processado no banco!")
        # Cria uma task falsa completa para o frontend conseguir pegar o video_id no poll
        pseudo_task_id = str(uuid.uuid4())
        processing_status[pseudo_task_id] = {"status": "completed", "video_id": video_id}
        return {"task_id": pseudo_task_id, "status": "completed", "video_id": video_id}
        
    # 2. Verifica se já está sendo processado no momento por outra requisição
    if video_id in active_processing_videos:
        # Encontra a task_id que está processando este vídeo e a retorna para o usuário acompanhar
        for t_id, status in processing_status.items():
            if status.get("video_id") == video_id and status.get("status") not in ["completed", "failed"]:
                return {"task_id": t_id, "status": status.get("status"), "video_id": video_id}
                
    # 3. Caso não esteja em nenhum, inicia uma nova task
    active_processing_videos.add(video_id)
    task_id = str(uuid.uuid4())
    processing_status[task_id] = {"status": "queued", "video_id": video_id}
    background_tasks.add_task(process_video_task, task_id, request.url, video_id)
    return {"task_id": task_id, "status": "queued", "video_id": video_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return processing_status[task_id]

@app.post("/chat")
async def chat(request: ChatRequest):
    response = query_rag(request.video_id, request.query, request.current_time)
    return {"response": response}
