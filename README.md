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

# 🚀 Live Systems

### 🌐 Production API (Cloud Run)
👉 https://helixcortexv3-960764783949.asia-south1.run.app/analyze/p1  

### 🧪 Cloud Swagger
👉 https://helixcortexv3-960764783949.asia-south1.run.app/docs  

### 💻 Local Swagger
👉 http://127.0.0.1:8001/docs  

### 🧠 Web App (Clinical Cortex UI)
👉 https://clinical-cortex--vidushi8.replit.app/  

---

# 🧠 What is HelixCortex?

HelixCortex AI is a **multi-agent clinical intelligence system** designed for:

- Real-time patient monitoring  
- Biomedical reasoning using RAG  
- Explainable AI-driven healthcare decisions  

Unlike traditional systems, it **decouples intelligence from data**, enabling:

✔ Modular AI agents  
✔ Continuous learning via RAG  
✔ Clinical auditability  

---

# 🏗️ Architecture (Agentic + Lakehouse)

```mermaid
graph TD

User --> API
API --> Agents

Agents --> ML
Agents --> RAG
Agents --> Gemini

RAG --> VectorDB
Agents --> Postgres
Agents --> Iceberg

Gemini --> Output
Output --> Response
