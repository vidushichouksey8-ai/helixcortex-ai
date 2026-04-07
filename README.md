# 🏥 HelixCortex AI

<p align="center">
  <img src="logo.png" width="160"/>
</p>

**Production-grade AI system combining multi-agent orchestration, biomedical RAG, and scalable data architecture for intelligent clinical decision support.**

---

## 🧠 Architecture Overview

```md
```mermaid
graph TD

User[User] --> API[FastAPI]
API --> Agents[Multi-Agent System]
Agents --> ML[ML Prediction]
Agents --> RAG[RAG Pipeline]
RAG --> LLM[LLM]
Agents --> DB[(PostgreSQL)]
Agents --> Lake[(Iceberg Lakehouse)]
