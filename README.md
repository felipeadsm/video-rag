# Video RAG Tutor

> O seu tutor inteligente com **consciência temporal** que transforma vídeos do YouTube em experiências ativas de aprendizado.

**Video RAG Tutor** é uma extensão avançada aliada a um poderoso motor de Inteligência Artificial local. Ele foi projetado para ir muito além de um simples "resumidor de vídeos". O projeto cria uma camada interativa sobre o YouTube, permitindo que você tire dúvidas, exija contextos históricos e peça explicações detalhadas enquanto assiste às suas aulas — tudo processado na sua máquina, garantindo privacidade e zero custo de API.

## 🚀 Funcionalidades Principais

- **Consciência Temporal ("O Durante"):** O tutor sabe exatamente em qual segundo do vídeo você está. Faça uma pergunta aos 10:15 e ele analisará cirurgicamente a janela de contexto daquele exato momento, focando exclusivamente no assunto atual da aula.
- **Busca Global Vetorial ("O Depois"):** Pause o vídeo e faça perguntas abrangentes. A IA vasculha a transcrição inteira usando RAG (Retrieval-Augmented Generation) para conectar informações e formular uma resposta coesa.
- **Enriquecimento de Contexto:** Não se limite ao que foi dito no vídeo. O Llama3 atua como um tutor especialista, trazendo exemplos práticos externos e aprofundamentos para potencializar o seu estudo.
- **Experiência Nativa (Dark Mode):** A extensão injeta uma interface flutuante limpa, moderna (glassmorphism) e não-obstrutiva diretamente na página do YouTube.

## 🏗️ Arquitetura e Stack Tecnológica

O produto é fortemente desacoplado, separando a fluidez do frontend do peso do processamento pesado.

1. **Frontend (Extensão Chrome/Edge):** HTML/CSS/JS puro focado em performance, manipulando a DOM do YouTube dinamicamente.
2. **Backend Orquestrador:** API assíncrona construída em **FastAPI** para controlar a fila de processamento sem travar o cliente.
3. **Ingestão Leve:** Utilização do `yt-dlp` e `FFmpeg` para baixar exclusivamente a faixa de áudio otimizada.
4. **Speech-to-Text Preciso:** O `faster-whisper` traduz o áudio em texto estruturado com marcações de *timestamps* milimétricas.
5. **Cérebro RAG:** O texto mapeado é vetorizado e gravado no **ChromaDB**. O framework **LangChain** se conecta ao **Ollama** para formular a inteligência final.

## 🛠️ Instalação e Uso

Todo o sistema roda de forma conteinerizada via Docker, não poluindo o seu sistema operacional.

### 1. Inicie a Infraestrutura de IA
Na pasta raiz deste projeto, suba a frota de containers:
```bash
docker-compose up --build
```
Se for o seu primeiro acesso, baixe o modelo de inteligência no Ollama:
```bash
docker exec -it video-rag-ollama-1 ollama run llama3
```
*(Dica: ajuste o nome do container caso seu docker-compose o nomeie diferente).*

### 2. Ative a Extensão
1. No Chrome ou Edge, acesse o painel de gerenciamento de extensões (`chrome://extensions` ou `edge://extensions`).
2. Ative a chave **Modo do Desenvolvedor**.
3. Clique em **Carregar sem compactação** (Load Unpacked) e selecione a pasta `extension/` deste repositório.

### 3. Turbine o YouTube
1. Acesse qualquer vídeo no YouTube. O painel lateral escuro aparecerá automaticamente.
2. Clique em **Processar** e acompanhe o progresso.
3. Com o banco vetorizado e o chat liberado, faça suas perguntas (Durante ou Depois) e bons estudos!

---
*Construído para acelerar o seu ritmo de aprendizado com Inteligência Artificial.*
