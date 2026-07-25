import os
import chromadb

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Inicializa o ChromaDB com persistência na pasta do volume Docker
chroma_client = chromadb.PersistentClient(path="/app/chromadata")

# Inicializa o LLM via Ollama. 
# O base_url é configurado via var de ambiente no docker-compose (apontando pro container do ollama)
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
llm = OllamaLLM(model="llama3", base_url=ollama_host) 

def add_to_vector_db(video_id: str, segments: list):
    """
    Armazena os segmentos transcritos no banco de dados vetorial (ChromaDB).
    Os timestamps são salvos como metadados associados a cada bloco de texto.
    """
    collection = chroma_client.get_or_create_collection(name=f"video_{video_id}")
    
    documents = []
    metadatas = []
    ids = []
    
    for i, seg in enumerate(segments):
        documents.append(seg["text"])
        metadatas.append({"start": seg["start"], "end": seg["end"]})
        ids.append(f"seg_{i}")
        
    if documents:
        # O Chroma baixa automaticamente um modelo leve de embeddings (all-MiniLM-L6-v2) 
        # para vetorizar os documentos caso nenhum embedding_function específico seja passado.
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

def is_video_processed(video_id: str) -> bool:
    """Verifica se o vídeo já foi indexado no banco vetorial."""
    try:
        collection = chroma_client.get_collection(name=f"video_{video_id}")
        return collection.count() > 0
    except Exception:
        return False

def query_rag(video_id: str, query: str, current_time: float | None = None) -> str:
    """
    Consulta o LLM com base na transcrição.
    Implementa a lógica do "Durante" (Sliding Window) vs "Depois" (Busca Global).
    """
    try:
        collection = chroma_client.get_collection(name=f"video_{video_id}")
    except Exception:
        return "Desculpe, não encontrei a base de dados para este vídeo. O processamento já terminou?"
    
    context = ""
    
    if current_time is not None:
        # Lógica 'Durante' (Sliding Window Context):
        # Filtramos blocos num raio de ~60 segundos em volta do momento atual.
        window_start = max(0, current_time - 60)
        window_end = current_time + 60
        
        # Busca no ChromaDB via metadados puros, sem usar vetor (é uma query exata de tempo)
        results = collection.get(
            where={"$and": [
                {"start": {"$gte": window_start}},
                {"start": {"$lte": window_end}}
            ]}
        )
        
        if results and results["documents"]:
            # Ordenar pelo start_time já que o .get pode retornar fora de ordem
            sorted_results = sorted(zip(results["documents"], results["metadatas"]), key=lambda x: x[1]["start"])
            context = " ".join([doc for doc, meta in sorted_results])
            
    else:
        # Lógica 'Depois' (Global Search):
        # Busca por similaridade vetorial na transcrição inteira
        results = collection.query(
            query_texts=[query],
            n_results=5 # Pega os 5 blocos mais relevantes
        )
        
        if results and results["documents"]:
            context = " ".join(results["documents"][0])
            
    if not context:
        context = "[Nenhum contexto encontrado no vídeo para este momento/pergunta]"
            
    # Prompt do Tutor Especialista (Enriquecimento)
    prompt = PromptTemplate.from_template(
        "Você é um tutor especialista altamente didático. Sua missão é responder à pergunta do aluno com base no trecho da transcrição do vídeo fornecido.\n\n"
        "Diretrizes:\n"
        "1. Baseie-se primeiramente no 'TRECHO DO VÍDEO' para a sua resposta.\n"
        "2. Se o trecho não contiver a informação necessária, avise o aluno, mas tente ajudar usando seus conhecimentos gerais.\n"
        "3. Enriqueça a explicação com exemplos práticos, analogias e contexto relevante (evite se restringir apenas a 'contexto histórico', a não ser que faça sentido).\n"
        "4. Formate sua resposta em Markdown, utilizando negrito, listas e parágrafos curtos para facilitar a leitura.\n"
        "5. Responda sempre de forma encorajadora e em Português do Brasil.\n\n"
        "TRECHO DO VÍDEO:\n{context}\n\n"
        "PERGUNTA DO ALUNO: {query}\n\n"
        "SUA EXPLICAÇÃO:"
    )
    
    formatted_prompt = prompt.format(context=context, query=query)
    
    # Chama o Ollama localmente
    response = llm.invoke(formatted_prompt)
    return response
