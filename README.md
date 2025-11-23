# ContactLens AI

**An Intelligent, AI-Powered Contact Management System.**  
*Transform physical business cards into digital connections using Computer Vision and LLMs.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange?logo=google)

## Project Description

**ContactLens AI** is a next-generation contact manager designed to solve the friction of manual data entry. Instead of typing out details from business cards, users simply upload an image. The application uses **Multimodal LLMs (Google Gemini 2.5 Pro)** to "see" the card, extract text, infer context (like industry tags and missing job titles), and structure the data into a clean digital format.

Unlike traditional OCR tools that simply read text, ContactLens AI understands context—it can distinguish between a company tagline and a job title, fix formatting errors automatically, and even visualize your professional network.

---

## Features

### Core Capabilities
*   **AI Vision Extraction:** Upload any business card (JPG/PNG). The AI extracts Name, Email, Phone, Company, Address, and Job Title with high accuracy.
*   **Interactive Contact List:** View, sort, and manage your contacts in a clean data table.
*   **Pydantic Validation:** Strict schema validation ensures that the AI returns structured JSON, not random text.

### AI Innovations
*   **Semantic Deduplication:** The system doesn't just check for matching emails. It uses an LLM to compare new contacts against your existing list to detect if "Bob Smith" and "Robert Smith" are the same person.
*   **One-Click Auto-Improvement:** An "AI Auto-Improve" button normalizes phone numbers to international standards (E.164), fixes capitalization, and infers missing details.
*   **Profile Enrichment:** The AI automatically infers **Professional Skills** and potential **Social Media** handles based on the job title and company context.
*   **Network Graph Visualization:** Visualize your connections! The app dynamically builds a knowledge graph clustering people by their Company and Industry.
*   **Privacy-Aware Mode:** A global toggle that automatically masks PII (emails and phone numbers) in the UI for safe demos/screenshots.

---

## Tools & Libraries Used

*   **Frontend:** [Streamlit](https://streamlit.io/) (UI/UX)
*   **AI Model:** [Google Gemini 2.5 Pro](https://ai.google.dev/) (Vision & Reasoning)
*   **Data Validation:** [Pydantic](https://docs.pydantic.dev/) (Schema enforcement)
*   **Visualization:** `streamlit-agraph` (Network Graph)
*   **Data Handling:** Pandas (Dataframes)
*   **Async Processing:** Python `asyncio` for non-blocking AI calls.

---

## Instructions to Run Locally

### Prerequisites
*   Conda installed.
*   A Google Cloud API Key (for Gemini).

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Usman-Bajwa1/contact-lens-ai.git
    cd contact-lens-ai
    ```

2.  **Create Conda Environment**
    ```bash
    conda create -n contact-lens-ai python=3.12 -y
    conda activate contact-lens-ai
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**
    Create a `.env` file in the root directory:
    ```bash
    GOOGLE_API_KEY=your_actual_api_key_here
    GOOGLE_MODEL=gemini-2.5-pro
    ```

5.  **Run the Application**
    ```bash
    streamlit run main.py
    ```

---

## AI Innovations & Privacy

This project implements several advanced patterns to ensure robustness and privacy:

1.  **Structured Outputs:** Instead of relying on Regex to parse AI text, we use Pydantic models to force the LLM to output strict JSON. This prevents the UI from crashing due to "hallucinated" formatting.
2.  **Stateless Architecture:** For security, images are processed in memory and discarded immediately after extraction. No images are stored on disk.
3.  **Semantic Logic:** Deduplication is performed by sending the candidate profile and a simplified version of the existing list to a LLM to reason about identity, rather than relying on exact string matching.

---

## Limitations

*   **Persistence:** Currently, data is stored in `st.session_state` (In-Memory). If you refresh the browser tab, the contact list disappears. This is by design for the demo but would require a database (PostgreSQL/MongoDB) for production.
*   **API Rate Limits:** Heavy usage may hit Google Gemini's free tier rate limits.
*   **Graph Performance:** The Network Graph visualization may become slow if the contact list exceeds 100+ nodes.

---

## Future Improvements

1.  **Database Integration:** Connect to Supabase or Firebase for persistent user storage.
2.  **CRM Export:** Add buttons to export contacts directly to HubSpot or Salesforce via API.
3.  **RAG Chat:** Add a "Chat with your Network" feature allowing users to ask "Who do I know in Finance?" using RAG (Retrieval-Augmented Generation).
4.  **Mobile Support:** Wrap the application in a PWA container for easier mobile camera access.

---