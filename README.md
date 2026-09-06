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

## **Deploy from scratch** (fresh clone → working login on any host)

No credentials ship with this repo. Each deployment brings its own Supabase
project and its own API keys.

1. **Clone.**
   ```bash
   git clone <this-repo> && cd TicTaxFlow
   ```

2. **Create a Supabase project and run the schema.** Full steps (why the
   service-role key, disabling email confirmation, seeding `tax_rules`) are in
   [`docs/supabase-setup.md`](docs/supabase-setup.md). Short version:
   - New project at https://supabase.com/dashboard
   - SQL Editor → run [`supabase/schema.sql`](supabase/schema.sql)
   - Authentication → Providers → Email → turn **Confirm email** off
   - Seed `tax_rules` with figures from [`backend/SOURCES.md`](backend/SOURCES.md)

3. **Set env vars.** Copy the template and fill it in:
   ```bash
   cp .env.example .env
   ```
   | Var | Value |
   |---|---|
   | `SUPABASE_URL` | Supabase → Settings → API → Project URL |
   | `SUPABASE_KEY` | Supabase → Settings → API → **service_role** secret (not anon) |
   | `GEMINI_API_KEY` | Google AI Studio key for `gemini-2.5-flash` |
   | `CORS_ORIGINS` | Public origin(s) of the frontend, comma-separated. e.g. `https://tictaxflow.example.com` |
   | `VITE_API_BASE_URL` | Public URL of the backend API **including `/api/v1`**. e.g. `https://api.tictaxflow.example.com/api/v1` |
   | `DEBUG_ERRORS` | `False` for anything shared |

   `VITE_API_BASE_URL` is baked into the frontend bundle at **build** time, so
   it must be set before step 4. `CORS_ORIGINS` must contain the exact origin
   the browser loads the frontend from, or the API rejects every request.

4. **Build and run.**
   ```bash
   docker compose up -d --build
   ```
   Frontend on `:3000`, backend on `:8000`. Behind a reverse proxy (Coolify,
   Traefik, nginx), point your frontend domain at the `frontend` service and
   your API domain at `backend`, and set `CORS_ORIGINS` / `VITE_API_BASE_URL`
   to those public URLs.

5. **Verify.** Open the frontend origin, register a user, log in. If login
   fails: check `CORS_ORIGINS` matches the browser origin, confirm email
   confirmation is off in Supabase, and check `docker compose logs backend`.

6. **(Optional) seed a demo user** — see [`DEMO.md`](DEMO.md):
   ```bash
   cd backend && python scripts/seed_demo.py
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
