# 🎓 Video RAG Tutor

> O seu tutor inteligente com **consciência temporal** que transforma vídeos do YouTube em experiências ativas de aprendizado.

**Video RAG Tutor** é uma extensão avançada aliada a um poderoso motor de Inteligência Artificial local. Ele foi projetado para ir além de um simples "resumidor de vídeos". O projeto cria uma camada interativa sobre o YouTube, permitindo que você tire dúvidas, exija contextos históricos e peça explicações detalhadas enquanto assiste às suas aulas — tudo processado na sua máquina, garantindo **privacidade absoluta** e **zero custo de API**.

---

## 🚀 Funcionalidades Principais

- **Consciência Temporal ("O Durante"):** O tutor sabe exatamente em qual segundo do vídeo você está. Faça uma pergunta aos 10:15 e ele analisará cirurgicamente a janela de contexto daquele exato momento (um raio de 60 segundos), focando exclusivamente no assunto atual da aula.
- **Busca Global Vetorial ("O Depois"):** Pause o vídeo e faça perguntas abrangentes. A IA vasculha a transcrição inteira usando *Retrieval-Augmented Generation (RAG)* para conectar informações e formular uma resposta coesa.
- **Cérebro Multilíngue:** O sistema utiliza o poderoso modelo de embeddings `paraphrase-multilingual-MiniLM-L12-v2` nativamente no ChromaDB, garantindo alta precisão semântica para aulas em **Português do Brasil**.
- **Histórico Persistente:** Fechou a aba por engano? Mudou de vídeo? A extensão usa `chrome.storage.local` para salvar as suas conversas atreladas ao ID de cada vídeo. Suas sessões de estudo nunca são perdidas.
- **Experiência Nativa:** Interface limpa em *glassmorphism* (fundo translúcido escuro) que se adapta perfeitamente ao layout do YouTube. Suporte completo a formatação Markdown profissional via `marked.js`.

---

## 🏗️ Arquitetura e Stack Tecnológica

O produto é fortemente desacoplado, separando a fluidez do frontend do processamento pesado.

1. **Extensão (Chrome/Edge):** HTML/CSS/JS nativo e ultraleve manipulando a DOM dinamicamente.
2. **Backend Orquestrador:** API assíncrona robusta construída em **FastAPI**, com middlewares de CORS e tratamento de corrida de processamento de GPU (`threading.Lock`).
3. **Ingestão Leve:** Utilização do `yt-dlp` para baixar exclusivamente a faixa de áudio otimizada.
4. **Speech-to-Text Preciso:** O `faster-whisper` traduz o áudio em texto estruturado com marcações de *timestamps* milimétricas (agrupadas inteligentemente em *chunks* de 30 segundos para otimizar a IA).
5. **Cérebro RAG:** O texto mapeado é vetorizado e gravado em um volume persistente do **ChromaDB**. O framework **LangChain** se conecta ao LLM via **Ollama**.

---

## 🛠️ Instalação e Uso

Todo o sistema roda de forma conteinerizada via **Docker**, para não poluir sua máquina.

### 1. Inicie a Infraestrutura de IA
Na pasta raiz deste projeto, suba a frota de containers:
```bash
docker-compose up --build
```
> **Nota:** A imagem Docker foi otimizada para aproveitar placas NVIDIA (CUDA) para acelerar radicalmente as transcrições e o processamento vetorial.

Se for o seu primeiro acesso, abra outro terminal e baixe o modelo Llama 3 no Ollama:
```bash
docker exec -it video-rag-ollama-1 ollama run llama3
```
*(Dica: ajuste o nome do container `video-rag-ollama-1` caso o seu docker-compose o nomeie diferente).*

### 2. Ative a Extensão
1. No Chrome ou Edge, acesse o painel de gerenciamento de extensões (`chrome://extensions` ou `edge://extensions`).
2. Ative a chave **Modo do Desenvolvedor** no canto inferior ou superior direito (dependendo do navegador).
3. Clique em **Carregar sem compactação** (Load Unpacked) e selecione a pasta `extension/` deste repositório.

### 3. Turbine o YouTube
1. Acesse qualquer vídeo no YouTube. O painel lateral escuro aparecerá automaticamente.
2. Clique em **Processar** e acompanhe o log pelo console do seu Docker (Você verá métricas em tempo real (Timeperf) da ingestão, whisper e banco de dados).
3. Faça suas perguntas e bons estudos!

---
*Construído para acelerar o seu ritmo de aprendizado com Inteligência Artificial.*
