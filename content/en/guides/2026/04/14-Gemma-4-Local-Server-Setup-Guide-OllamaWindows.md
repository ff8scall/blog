---
title: "[Practical Guide] Gemma 4 Local Server Setup Guide (Ollama/Windows) Perfect Implementation"
date: "2026-04-14T00:00:00+09:00"
description: "Follow this guide to successfully install and run the Gemma 4 model locally on your Windows machine via Ollama and FastAPI."
clusters: ["guides"]
categories: ["tutorials"]
tags: ["guide", "tutorial", "practical"]
difficulty: "Intermediate"
time_to_complete: "25 minutes"
---

## 🎯 Guide Goal
By the end of this guide, you will have successfully set up a local API endpoint running the Gemma 4 model. This allows you to interact with the powerful LLM programmatically from any Python application on your local machine.

## 📋 Prerequisites (Prerequisites)
* **Required Software/Version:**
    * NVIDIA GPU (RTX 3060 or better with 12GB VRAM recommended).
    * NVIDIA Drivers (Latest stable version).
    * CUDA Toolkit (Version 12.1 or higher).
    * Python 3.10+
    * Ollama (Latest stable release).
* **Required Environment:**
    * Command Line Interface (Windows Terminal or PowerShell).
    * A dedicated virtual environment for the API wrapper.

## 🚀 Practical Application Steps (Step-by-Step)

### Phase 1. Initial Setup and Model Pull
* **Estimated Time:** 10 minutes
* **Step 1-1. Install Ollama:**
  * **Action:** Click the official Ollama download link and run the Windows installer.
  * **Expected Result:** Ollama service is installed and running in the background. A new command prompt session is available.
* **Step 1-2. Verify Ollama Installation:**
  * **Action:** Open your Command Prompt/PowerShell and type the following command:
    ```bash
    ollama run gemma:2b
    ```
  * **Expected Result:** Ollama will download the `gemma:2b` model weights. After download, you will see a prompt like `>>>` indicating the model is ready for chat interaction. Type `/bye` to exit the chat.
* **Step 1-3. Set up the Python Environment (API Wrapper):**
  * **Action:** Create and activate a virtual environment in your desired project folder.
    ```bash
    python -m venv venv_gemma
    .\venv_gemma\Scripts\activate
    ```
  * **Action:** Install the necessary libraries (FastAPI and Uvicorn).
    ```bash
    pip install fastapi uvicorn pydantic
    ```
  * **Expected Result:** The terminal prompt changes to `(venv_gemma)`, confirming the isolated environment is active.

### Phase 2. Running the Local API Server
* **Estimated Time:** 15 minutes
* **Step 2-1. Create the API Script:**
  * **Action:** Inside your project folder, create a file named `api_server.py` and paste the following content (This script serves as the wrapper):
    ```python
    # api_server.py
    from fastapi import FastAPI
    import requests
    import os

    app = FastAPI()

    @app.post("/generate")
    def generate_text(prompt: str):
        # Assuming Ollama is running on default port 11434
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "gemma:2b",
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status() # Raise HTTPError for bad responses
            return response.json().get("response", "Error: No response received.")
        except requests.exceptions.ConnectionError:
            return "ERROR: Ollama service is not running. Please ensure Ollama is running in the background."

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
    ```
  * **Expected Result:** The file `api_server.py` is successfully created and contains the necessary FastAPI structure.
* **Step 2-2. Start the API Server:**
  * **Action:** Ensure Ollama is running in the background (or run `ollama serve` in a separate terminal). In the same terminal where your virtual environment is active, run:
    ```bash
    python api_server.py
    ```
  * **Expected Result:** The terminal will display logs indicating the server has started, typically showing `Uvicorn running on http://127.0.0.1:8000`.
* **Step 2-3. Test the API Endpoint:**
  * **Action:** Open a *new* terminal window (or use a tool like Postman) and send a POST request to `http://127.0.0.1:8000/generate` with a JSON body:
    ```json
    {
      "prompt": "Explain the concept of a local LLM server in three sentences."
    }
    ```
  * **Expected Result:** The server terminal will show logs indicating the request was processed, and the client will receive a structured JSON response containing the generated text (e.g., `"response": "A local LLM server allows you to run large language models offline..."`).

## ✅ Final Verification (Checklist)
* [x] The `gemma:2b` model was successfully pulled and tested using `ollama run`.
* [x] The virtual environment is active and contains `fastapi` and `uvicorn`.
* [x] The API server started successfully and is listening on `http://127.0.0.1:8000`.
* [x] Sending a test request to the API endpoint yields a coherent text response from Gemma 4.

## ⚠️ Troubleshooting (Common Error Resolution)
* **Q. `ConnectionError: HTTPConnectionPool(...) Failed to establish a new connection`**
* **A.** This means your Python script cannot reach the Ollama service.
    1. **Check Ollama Status:** Ensure the Ollama background service is actively running on your Windows machine.
    2. **Check Port:** Verify that no other service is running on port `11434`. If necessary, stop the conflicting service or change the `url` in `api_server.py`.

* **Q. `ModuleNotFoundError: No module named 'requests'`**
* **A.** This indicates the necessary library was not installed in your active virtual environment.
    1. **Re-activate:** Ensure you run `.\venv_gemma\Scripts\activate`.
    2. **Re-install:** Run `pip install requests` to explicitly install the requests library.