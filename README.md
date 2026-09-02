# TicTaxFlow

TicTaxFlow - AI Agent for Tax Deduction Management System 



## **Core Features**

1. Upload & Extract:
    - User upload file (JPG, PNG, WEBP, or PDF)
    - AI fetch the data: `Date`, `Amount`, `Issuer Name`, `Tax ID` then display the result
2. Auto-Classification:
    - AI define detail in invoice such as Life Insurance, Donation, Easy - E-Receipt
3. Validation & Rules:
    - AI has simple logic such as if it's Health in health category, the total amount must not exceed 15,000 (or 25,000 according to the law of the year in question) warn if exceeded
4. Dashboard:
    - Display pie chart of total deduction and remaining amount to full deduction



## **Tech Stack**
- Core: Python
- LLM & Vision: Gemini 2.5 Flash
- Agent Framework: LangGraph
- Knowledge Base (RAG): collect PDF files of tax deduction manual of the Revenue Department
- Database: Supabase
- UI: React + TailwindCSS



## **Installation**

### Run in locally

#### **Set up the project & Start Frontend server**

1. Going into the frontend folder 
    ```
    cd frontend
    ```
2. Install packages
    ```
    npm i
    ```
3. Run frontend server
    - To **start** server
        ```
        npm run dev 
        ```
    - To **stop** server
        ```
        control + C
        ```


#### **Set up the project & Start Backend server**

1. Going into the backend folder
    ```
    cd backend
    ```

2. Create Virtual Environment for Python 3.11 version
    - Linux / macOS
        ```
        python3.11 -m venv .venv
        ```
    - Windows
        ```
        py -3.11 -m venv .venv
        ```

3. Activate Virtual Environment
    - Linux / macOS
        ```
        source .venv/bin/activate
        ```
    - Windows
        ```
        .\.venv\Scripts\Activate.ps1
        ```

4. Install Dependencies
    ```
    pip install -r requirements.txt
    ```

5. Run backend server
    - To **start** server
        ```
        uvicorn main:app --reload --port 8000
        ```
    - To **stop** server
        ```
        lsof -ti:8000 | xargs kill -9
        ```

### Run in container Docker
```
docker-compose up -d --build
```

## **Rebuilding the RAG knowledge base**

The Chroma vector store (`backend/data/embeddings/`) is not committed to git —
it's a rebuildable index over the PDFs in `backend/data/documents/`, not source
of truth. After cloning, build it once:

```
cd backend
python -m app.services.document_indexer
```

This reads every PDF in `backend/data/documents/`, chunks it, and populates
the local Chroma collection at `backend/data/embeddings/` using Chroma's
default (MiniLM) embedding function — no `GEMINI_API_KEY` needed for this step.
