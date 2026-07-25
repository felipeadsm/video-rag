import threading
from faster_whisper import WhisperModel

# Mudamos de "base" para "small" para ter muito mais precisão, especialmente em português
# E ativamos novamente a aceleração via CUDA e float16
model = WhisperModel("small", device="cuda", compute_type="float16")

# Lock para evitar que duas requisições rodem model.transcribe() simultaneamente e estourem a VRAM
transcribe_lock = threading.Lock()

def transcribe_audio(audio_path: str):
    """
    Transcreve o arquivo de áudio utilizando faster-whisper.
    Retorna uma lista de dicionários contendo os campos start, end e text.
    """
    with transcribe_lock:
        # Forçamos o idioma para "pt" para evitar confusões de detecção e melhorar a pontuação
        segments, info = model.transcribe(audio_path, beam_size=5, language="pt")
    
    result = []
    current_chunk_text = ""
    current_chunk_start = 0.0
    current_chunk_end = 0.0
    
    # Vamos agrupar (chunk) os segmentos curtos do Whisper em blocos de até 30 segundos
    # Isso melhora imensamente o contexto para o LLM na busca vetorial.
    segments_list = list(segments)
    
    for i, segment in enumerate(segments_list):
        if not current_chunk_text:
            current_chunk_start = segment.start
            
        current_chunk_text += segment.text + " "
        current_chunk_end = segment.end
        
        if (current_chunk_end - current_chunk_start) >= 30.0 or i == len(segments_list) - 1:
            result.append({
                "start": current_chunk_start,
                "end": current_chunk_end,
                "text": current_chunk_text.strip()
            })
            current_chunk_text = ""
            
    return result
