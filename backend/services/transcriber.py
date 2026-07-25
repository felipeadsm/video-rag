from faster_whisper import WhisperModel

# Mudamos de "base" para "small" para ter muito mais precisão, especialmente em português
# E ativamos novamente a aceleração via CUDA e float16
model = WhisperModel("small", device="cuda", compute_type="float16")

def transcribe_audio(audio_path: str):
    """
    Transcreve o arquivo de áudio utilizando faster-whisper.
    Retorna uma lista de dicionários contendo os campos start, end e text.
    """
    # Forçamos o idioma para "pt" para evitar confusões de detecção e melhorar a pontuação
    segments, info = model.transcribe(audio_path, beam_size=5, language="pt")
    
    result = []
    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        
    return result
