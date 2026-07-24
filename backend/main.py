import os
import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Importações dos serviços (serão criados na sequência)
from services.youtube import download_audio
from services.transcriber import transcribe_audio
from services.rag import add_to_vector_db, query_rag

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

class ProcessRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    video_id: str
    query: str
    current_time: float | None = None

def process_video_task(task_id: str, url: str):
    """
    Tarefa em background que orquestra o pipeline de ingestão, transcrição e indexação.
    """
    try:
        processing_status[task_id] = {"status": "downloading"}
        audio_path, video_id = download_audio(url)
        
        processing_status[task_id] = {"status": "transcribing"}
        segments = transcribe_audio(audio_path)
        
        processing_status[task_id] = {"status": "vectorizing"}
        add_to_vector_db(video_id, segments)
        
        # Limpeza do arquivo de áudio temporário após a indexação
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        processing_status[task_id] = {"status": "completed", "video_id": video_id}
    except Exception as e:
        processing_status[task_id] = {"status": "failed", "error": str(e)}

@app.post("/process")
async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    processing_status[task_id] = {"status": "queued"}
    background_tasks.add_task(process_video_task, task_id, request.url)
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return processing_status[task_id]

@app.post("/chat")
async def chat(request: ChatRequest):
    response = query_rag(request.video_id, request.query, request.current_time)
    return {"response": response}
