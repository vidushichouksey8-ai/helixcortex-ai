<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:6a11cb,100:f7971e&height=200&section=header&text=HelixCortex%20AI&fontSize=40&fontColor=ffffff"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/e40c011f-f397-458f-901f-eebee4f95f98" width="260"/>
</p>

<h1 align="center">🧬 HelixCortex AI</h1>

<p align="center">
  <b>
    Production-grade AI healthcare system combining multi-agent orchestration, 
    biomedical RAG, and scalable data architecture for intelligent clinical decision support.
  </b>
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

### 🔬 Core Capabilities

- 🧠 Multi-agent orchestration (modular AI agents)
- 🔎 Biomedical RAG (FAISS + embeddings)
- 🤖 Gemini (Vertex AI) reasoning
- 📊 ML-based risk scoring
- ☁️ Cloud-native deployment (Google Cloud Run)

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
Output --> Response[Final Response]<img width="1024" height="1536" alt="logo-new" src="https://github.com/user-attachments/assets/3631d81c-83fb-43ee-8114-e817351308c0" />
<img width="1024" height="1536" alt="logo-new" src="https://github.com/user-attachments/assets/39de0ae5-b6c0-4f69-8a14-96ea17e592ba" />
