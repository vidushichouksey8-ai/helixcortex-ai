# 🧬 HelixCortex AI

<p align="center">
  <img src="assets/logo-new.png" width="260"/>
</p>

<p align="center">
  <b>Production-grade AI healthcare system combining multi-agent orchestration, biomedical RAG, and scalable data architecture for intelligent clinical decision support.</b>
</p>

---
## 🚀 Live Demo

🌐 API:
https://helixcortexv3-960764783949.asia-south1.run.app/analyze/p1
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
