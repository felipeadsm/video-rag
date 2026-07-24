import os
import chromadb

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# Inicializa o ChromaDB com persistência na pasta do volume Docker
chroma_client = chromadb.PersistentClient(path="/app/chromadata")

# Inicializa o LLM via Ollama. 
# O base_url é configurado via var de ambiente no docker-compose (apontando pro container do ollama)
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
llm = Ollama(model="llama3", base_url=ollama_host) 

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

def query_rag(video_id: str, query: str, current_time: float | None = None) -> str:
    """
    Consulta o LLM com base na transcrição.
    Implementa a lógica do "Durante" (Sliding Window) vs "Depois" (Busca Global).
    """
    try:
        collection = chroma_client.get_collection(name=f"video_{video_id}")
    except ValueError:
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
        "Você é um tutor especialista altamente didático. Use o trecho da transcrição do vídeo fornecida como base para responder a pergunta do aluno.\n"
        "O aluno está estudando este vídeo. Não se limite apenas ao texto fornecido; enriqueça a explicação trazendo contexto histórico, exemplos práticos e clareza, mas mantenha o vínculo com o assunto principal do vídeo.\n\n"
        "TRECHO DO VÍDEO:\n{context}\n\n"
        "PERGUNTA DO ALUNO: {query}\n\n"
        "SUA EXPLICAÇÃO DIDÁTICA E ENRIQUECEDORA:"
    )
    
    formatted_prompt = prompt.format(context=context, query=query)
    
    # Chama o Ollama localmente
    response = llm.invoke(formatted_prompt)
    return response
