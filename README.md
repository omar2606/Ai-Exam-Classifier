# 📚 AI-Powered Exam Question Classifier

An end-to-end system that takes past exam PDFs and a syllabus, and automatically generates a categorized **question bank** — each question sorted under the syllabus chapter it belongs to.

## How it works

```
Streamlit frontend  →  ngrok tunnel  →  FastAPI backend (Kaggle T4 GPU)
                                              │
                                              ├── PyMuPDF → renders each exam page as an image
                                              ├── Qwen2.5-VL-7B-Instruct → reads each question image
                                              │   and describes the topic being tested
                                              ├── FAISS + sentence-transformers → retrieves the
                                              │   most relevant syllabus chapter (RAG)
                                              ├── Structured output parsing → classifies each
                                              │   question into a single chapter with confidence
                                              └── ReportLab → assembles a formatted PDF question
                                                  bank, grouped by chapter
```

**Frontend:** Streamlit app where a user uploads exam PDFs and pastes the syllabus.

**Backend:** A FastAPI server running inside a Kaggle notebook (using its free T4 GPU), exposed publicly via ngrok. Processing runs as a background job — the frontend submits a job, polls its status, and downloads the finished PDF once ready, so long GPU processing times never break the connection.

**Model:** [Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct), a vision-language model, reads each exam question directly as an image and describes the concept being tested — no manual transcription needed.

**Classification:** The generated description is embedded and matched against syllabus chapters using a FAISS vector store, then a structured (Pydantic-validated) classification step assigns the single best-matching chapter with a confidence score and reasoning.

## Project structure

```
.
├── app.py                  # Streamlit frontend
├── final-project.ipynb     # Kaggle notebook: model, RAG pipeline, FastAPI backend
├── requirements.txt        # Frontend dependencies
└── .gitignore
```

## Running it

### Backend (Kaggle)
1. Open `final-project.ipynb` in a Kaggle notebook with GPU (T4) enabled.
2. Add your ngrok auth token as a Kaggle Secret named `NGROK_TOKEN` (Add-ons → Secrets).
3. Run all cells. The last cells start the FastAPI server and print a public ngrok URL.

### Frontend (local)
```bash
pip install -r requirements.txt
```
Update `BACKEND_URL` in `app.py` to match your current ngrok URL, then:
```bash
streamlit run app.py
```

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn, ngrok |
| Vision LLM | Qwen2.5-VL-7B-Instruct (Transformers) |
| Retrieval | LangChain, FAISS, sentence-transformers |
| PDF I/O | PyMuPDF (reading), ReportLab (generating) |
| Compute | Kaggle T4 GPU |

## Notes

- This is a demo/portfolio project — the backend runs on a temporary Kaggle session + free ngrok tunnel, so the public URL changes on restart and isn't meant for production use.
- Classification is AI-generated and may occasionally mis-categorize questions; confidence scores and reasoning are included in the pipeline for transparency.