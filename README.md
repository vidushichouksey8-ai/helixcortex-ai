# 🏥 HelixCortex AI

<p align="center">
  <img src="logo.png" width="160"/>
</p>

**Production-grade AI system combining multi-agent orchestration, biomedical RAG, and scalable data architecture for intelligent clinical decision support.**

---

## 🧠 Architecture Overview

```mermaid
graph TD

User --> API
API --> Agents
Agents --> ML
Agents --> RAG
RAG --> LLM
Agents --> DB
Agents --> Lake

User[User]
API[FastAPI]
Agents[Multi-Agent System]
ML[ML Prediction]
RAG[RAG Pipeline]
LLM[LLM]
DB[(PostgreSQL)]
Lake[(Iceberg Lakehouse)]
