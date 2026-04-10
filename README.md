<img width="1024" height="1536" alt="logo-new" src="https://github.com/user-attachments/assets/e40c011f-f397-458f-901f-eebee4f95f98" />
# 🧬 HelixCortex AI

<p align="center">
  <img src="https://raw.githubusercontent.com/vidushichouksey8-ai/helixcortex-ai/main/assets/logo-new.png" width="260"/>
</p>

<p align="center">
  <b>Production-grade AI healthcare system combining multi-agent orchestration, biomedical RAG, and scalable data architecture for intelligent clinical decision support.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Multi--Agent-orange"/>
  <img src="https://img.shields.io/badge/LLM-Gemini-blue"/>
  <img src="https://img.shields.io/badge/Backend-FastAPI-green"/>
  <img src="https://img.shields.io/badge/Deploy-Cloud%20Run-black"/>
</p>

---

## 🚀 Live Demo

🌐 **API Endpoint**  
👉 https://helixcortexv3-960764783949.asia-south1.run.app/analyze/p1  

---

## 🧠 System Overview

HelixCortex AI is a **cloud-native, multi-agent AI platform** designed to simulate real-world healthcare intelligence systems.

It integrates:

- 🧠 Multi-agent orchestration  
- 🔎 Biomedical Retrieval-Augmented Generation (RAG)  
- 🤖 Gemini (Vertex AI) reasoning  
- 📊 ML-based risk scoring  
- ☁️ Cloud Run deployment  

---

## 🏗️ Architecture

```mermaid
graph TD

User[User] --> API[FastAPI API Layer]
API --> Agents[Multi-Agent System]

Agents --> ML[ML Agent]
Agents --> RAG[RAG Agent]
Agents --> Gemini[Gemini Agent]

RAG --> Vector[(FAISS Vector DB)]
Agents --> DB[(PostgreSQL)]
Agents --> Lake[(Iceberg Lakehouse)]

Gemini --> Output[LLM Insights]
Output --> Response[Final Response]
