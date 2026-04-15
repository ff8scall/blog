# NotebookLM MCP Integration (V2.0) Execution Tasks

- [x] Clear out Gemini-based legacy scripts (deleted `mega_synthesis.py` and reverted `ai_news_editor.py`).
- [x] Create MCP Data Preparation Script (`automation/notebooklm_prep.py`) to aggregate 50 articles into a single Markdown source file.
- [x] Run the Prep Script to generate `scratch/notebooklm_source.md`.
- [/] Wait for user to configure `notebooklm-mcp` locally.
- [ ] Call the MCP Tools (`notebooklm_create_notebook`, `notebooklm_upload_source`, etc.) to upload the file to Google NotebookLM.
- [ ] Ask NotebookLM to generate the Mega-Trend report.
- [ ] Parse NotebookLM's response, format into Hugo Markdown with Frontmatter, and save to `content/ko/guides/`.
