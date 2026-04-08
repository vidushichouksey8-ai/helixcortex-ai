# 🏥 HelixCortex AI

<p align="center">
  <img src="./logo-new.png" width="220"/>
</p>

<p align="center">
<b>Production-grade AI system combining multi-agent orchestration, biomedical RAG, and scalable data architecture for intelligent clinical decision support.</b>
</p>

---

## 🧠 Architecture Overview

```mermaid
graph TD

User[User] --> API[FastAPI]
API --> Agents[Multi-Agent System]
Agents --> ML[ML Prediction]
Agents --> RAG[RAG Pipeline]
RAG --> LLM[LLM]
Agents --> DB[(PostgreSQL)]
Agents --> Lake[(Iceberg Lakehouse)]