# TicTaxFlow
TicTaxFlow - AI Agent for Tax Deduction Management

## **Core Features**

1. Upload & Extract:
    - User upload file (JPG/PDF)
    - AI fetch the data: `Date`, `Amount`, `Issuer Name`, `Tax ID` then display the result
2. Auto-Classification:
    - AI define detail in invoice such as Life Insurance, Donation, Easy - E-Receipt
3. Validation & Rules:
    - AI has simple logic such as if it's Health in ถ้าหมวด "ประกันสุขภาพ" ยอดรวมต้องไม่เกิน 15,000 (หรือ 25,000 ตามกฎปีนั้นๆ) แจ้งเตือนถ้าเกิน
4. Dashboard:
    - แสดงกราฟวงกลมว่าตอนนี้ลดหย่อนไปกี่บาทแล้ว ขาดอีกกี่บาทจะเต็มสิทธิ์

## **Tech Stack**
    - Core: Python
    - LLM & Vision: Gemini 1.5 Pro
    - Agent Framework: LangGraph
    - Knowledge Base (RAG): เก็บไฟล์ PDF คู่มือลดหย่อนภาษีของกรมสรรพากร
    - Database: Supabase
    - UI: React + TailwindCSS



# Set up the project & Start Backend server

1. Going into the frontend folder
    ```
        cd frontend
    ```
2. Install packages
    ```
        npm i
    ```
3. Run frontend server
    ```
        npm run dev -- --port 3001
    ```



# Set up the project & Start Backend server

1. Going into the frontend folder
    ```
        cd frontend
    ```

2. Create Virtual Environment for Python 3.10 version
   - Linux / macOS
       ```
       python3.10 -m venv .venv
       ```
   - Windows
        ```
        py -3.10 -m venv .venv
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

5. Run to test
    ```
    python main.py
    ```