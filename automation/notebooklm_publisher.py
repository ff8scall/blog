import os
import json
import time
import logging
import re
from datetime import datetime
from notebooklm_prep import NotebookLMApp
from common_utils import send_telegram_report
from ai_writer import AIWriter

# Reuse existing logic from news_main
import news_main as nm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NotebookLM_Publisher")

class NotebookLMPublisher:
    def __init__(self):
        self.app = NotebookLMApp()
        self.writer = AIWriter()
        self.jobs_file = "automation/premium_jobs.json"
        self.output_dir = "scratch/premium_reports"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_jobs(self):
        if os.path.exists(self.jobs_file):
            with open(self.jobs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_jobs(self, jobs):
        with open(self.jobs_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=4, ensure_ascii=False)

    def process_pending_jobs(self):
        jobs = self.load_jobs()
        if not jobs:
            logger.info("No pending premium jobs found.")
            return

        for cat, job in jobs.items():
            if job.get("status") == "published":
                continue

            nb_id = job["notebook_id"]
            logger.info(f"Checking status for {cat} ({nb_id})...")
            
            status_res = self.app.check_status(nb_id)
            if not status_res or not isinstance(status_res, list):
                continue

            # Find completed reports
            reports = [a for a in status_res if a.get("type") == "report" and a.get("status") == "completed"]
            
            if not reports:
                logger.warning(f"No completed report artifacts found for {cat} yet.")
                continue

            # Pick the most recent one (last in the list usually)
            report_artifact = reports[-1]
            
            logger.info(f" [DONE] Report found ({report_artifact['id']}) for {cat}. Downloading...")
            filepath = os.path.join(self.output_dir, f"{cat}_editorial.md")
            # Confirming absolute path for download
            abs_filepath = os.path.abspath(filepath)
            
            download_res = self.app.run_cmd(["download", "report", nb_id, "--output", abs_filepath], use_json=False)
            
            if os.path.exists(abs_filepath):
                success = self.publish_to_hugo(cat, abs_filepath, job)
                if success:
                    job["status"] = "published"
                    job["published_at"] = datetime.now().isoformat()
                    logger.info(f" [SUCCESS] Category '{cat}' has been published (KO + EN).")
                else:
                    logger.error(f" [RETRY] Category '{cat}' failed to publish completely.")
            else:
                logger.error(f" Failed to download report for {cat}")

        self.save_jobs(jobs)

    def publish_to_hugo(self, category, filepath, job_info):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return

        # Parse content
        # NotebookLM output starts with # [심층 사설] Title...
        title_line = lines[0].replace("#", "").strip()
        # Remove common prefixes like [심층 사설]
        title = re.sub(r'^\[.*?\]\s*', '', title_line)
        body = "".join(lines[1:]).strip()
        
        # Simple extraction of first paragraph for description
        paragraphs = [p for p in body.split("\n\n") if p.strip()]
        description = paragraphs[0][:200] + "..." if paragraphs else title

        # Create Article Data object compatible with news_main.create_hugo_post
        # Use job info or title but try to keep it English-friendly for URLs
        date_str_slug = datetime.now().strftime("%Y-%m-%d")
        slug = f"megatrend-{category}-{date_str_slug}"
        
        # Generate Image Prompt based on title and category
        image_prompt = f"Abstract 3D digital art representing {title}, high-tech, cinematic, {category} theme"
        
        date_iso = datetime.now().isoformat()
        image_path = f"/images/posts/{datetime.now().strftime('%Y/%m/%d')}/{slug}_gen.jpg"
        
        article_data = {
            "sync_slug": slug,
            "category": category,
            "categories": [category],
            "tags": [category, "Megatrend", "Premium"],
            "cluster": "megatrend", # Special cluster for premium content
            "date": date_iso,
            "image": image_path,
            "kor_title": title,
            "kor_description": description,
            "kor_summary": [description[:100]], # Dummy summary
            "kor_keywords": [category, "Megatrend", "Premium"],
            "kor_content": body,
            "kor_insight_title": "에디터 초이스: 인사이트 분석",
            "kor_insight": "제공된 리포트의 내용을 바탕으로 하단에 추가 분석 세션을 구성할 수도 있습니다.",
            "image_prompt_core": image_prompt,
            "featured": True
        }

        # Use news_main's robust post creator
        nm.create_hugo_post(article_data, lang='ko')
        
        msg = f"🚀 [Premium Alert] New Editorial Published!\nCategory: {category}\nTitle: {title}\nLanguages: KO + EN"
        send_telegram_report(msg)
        
        # 2. Generate and Publish English Version
        logger.info(f" [GEN] Translating '{title}' to English...")
        eng_md = self.generate_english_version(article_data)
        if eng_md:
            self._publish_raw_md(eng_md, slug, lang='en')
            logger.info(f" [SUCCESS] English version of '{title}' published.")
            return True
        else:
            logger.error(f" [FAIL] English translation failed for '{title}'.")
            return False

    def generate_english_version(self, kor_data):
        """Generate the full English Hugo post using Gemini."""
        prompt = f"""
        [TASK]: Transform this professional Korean tech editorial into a high-quality global tech article (English).
        - Persona: TechCrunch/Wired Senior Editor.
        - Maintain the same markdown depth and 3-D tech aesthetic in your writing.
        - Output the COMPLETE Hugo post including Frontmatter.
        
        [KO TITLE]: {kor_data['kor_title']}
        [KO CONTENT]: {kor_data['kor_content']}
        [KO INSIGHT]: {kor_data['kor_insight']}
        
        [FRONTMATTER DETAILS]:
        - title: "(Professional English Title - MUST be wrapped in double quotes)"
        - date: {kor_data['date']}
        - description: (SEO summary)
        - image: {kor_data['image']}
        - clusters: ["megatrend"]
        - categories: ["{kor_data['categories'][0]}"]
        - tags: {json.dumps(kor_data['tags'])}
        - featured: true
        
        [OUTPUT]: One single block of Markdown with YAML frontmatter.
        """
        # Use AIWriter's fallback pool for premium writing (Gemini -> Groq -> etc.)
        res = self.writer.generate_content(prompt, role="writing")
        
        if not res or len(res) < 500:
            logger.error(f"Translation result too short or empty: {len(res) if res else 0} chars.")
            return None
            
        # Extract markdown block if present, else take whole text
        match = re.search(r'---(.*?)---(.*)', res, re.DOTALL)
        if match:
            logger.info("Extracted formatted Markdown with Frontmatter from translation.")
            return res.strip()
            
        logger.warning("No standard Frontmatter delimiters found in translation, using raw result.")
        return res.strip()

    def _publish_raw_md(self, content, slug, lang='en'):
        """Directly save a raw markdown string to Hugo."""
        date_path = datetime.now().strftime('%Y/%m/%d')
        base_path = f"content/{lang}/posts/{date_path}"
        os.makedirs(base_path, exist_ok=True)
        full_path = os.path.join(base_path, f"{slug}.md")
        with open(full_path, "w", encoding="utf-8-sig") as f:
            f.write(content)
        return True

if __name__ == "__main__":
    publisher = NotebookLMPublisher()
    publisher.process_pending_jobs()
