# Video RAG Tutor

> Um sistema para extração, transcrição e enriquecimento de conteúdo de vídeos do YouTube, projetado para atuar como um tutor interativo e acelerar o aprendizado.

A ideia central deste projeto é ir além de um simples "resumidor de vídeos". O objetivo é criar um tutor inteligente com **consciência temporal** e capacidade de **enriquecimento de contexto**, conectando o que é falado no vídeo com conhecimentos externos.

## 🚀 Arquitetura e Fases do Projeto

O sistema foi desenhado com foco em desacoplamento e isolamento, utilizando princípios de Arquitetura Hexagonal. A lógica de negócio (sessão de estudo) atua como orquestrador, independente das ferramentas externas (LLM, Whisper, YouTube).

### 1. Ingestão e Processamento
Responsável por baixar e preparar os dados brutos.
- **Ferramentas:** `yt-dlp` e `FFmpeg`.
- **Estratégia:** Baixar apenas a stream de áudio (ignorando o vídeo) e converter para um formato padronizado (ex: `.wav`, 16kHz) ideal para o modelo de transcrição.

### 2. Transcrição (Speech-to-Text)
Converte o áudio em texto estruturado com alta precisão e performance local.
- **Ferramentas:** `faster-whisper` (baseado em CTranslate2).
- **Estratégia:** Uso do modelo localmente. Geração de blocos de texto contendo **timestamps exatos** de cada fala (Ex: `{"start": 600, "end": 630, "text": "..."}`).

### 3. Pós-Processamento, RAG e Tutor (LLM)
O núcleo inteligente do sistema, responsável por interagir com o usuário e formatar as respostas.
- **Formatos:** Vetores/Embeddings em um Vector DB (ex: ChromaDB, FAISS).
- **O Enriquecimento ("O Engrandecimento"):** 
  Em vez de limitar a LLM ao conteúdo do vídeo, os *System Prompts* instruem o modelo a agir como um **tutor especialista**. Ele usa o contexto do vídeo como base, mas é livre para trazer contextos históricos, exemplos práticos e informações relevantes para expandir o conhecimento.
- **A Consciência Temporal:**
  - **O cenário "Durante" (Sliding Window):** Se o usuário faz uma pergunta enquanto assiste (ex: no minuto 10:15), o sistema envia para a LLM apenas a janela de texto daquele momento (ex: de 09:15 a 11:15). Isso garante que o modelo responda com foco no que está sendo discutido na tela.
  - **O cenário "Depois" (Visão Global):** Após o vídeo, o sistema utiliza busca vetorial tradicional (RAG) em toda a transcrição, conectando conceitos e respondendo de forma macro.

## 🐳 Isolamento de Ambiente

Para lidar com as dependências de Machine Learning e processamento de mídia (Python, FFmpeg, PyTorch), o sistema roda inteiramente em **Docker**.
- Utilização de containers dedicados para o Worker de transcrição, API e banco de dados.
- Garante que a máquina host permaneça limpa e que o pipeline rode perfeitamente em qualquer lugar.

## 🚧 Próximos Passos
- [ ] Configurar a estrutura base de containers (Docker / Docker Compose).
- [ ] Desenvolver o módulo de ingestão (`yt-dlp` + `FFmpeg`).
- [ ] Integrar o `faster-whisper` para gerar transcrições mapeadas temporalmente.
- [ ] Subir o banco vetorial para o RAG.
- [ ] Criar o backend orquestrador que lida com o estado "Durante" vs "Depois".
- [ ] Definir a interface de usuário (Terminal ou Web/Player Embutido).
