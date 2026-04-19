# -*- coding: utf-8 -*-
import os
import time
import requests
import json
import re
import feedparser
import logging
import sys
from datetime import datetime
from typing import List
from concurrent.futures import ThreadPoolExecutor

# 부모 디렉토리를 경로에 추가하여 공통 모듈 임포트 가능하게 함
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common_utils import normalize_url, clean_text
from schemas import HarvestedArticle
from quality_filter import QualityFilter

# V2 전용 라이브러리
import trafilatura
from newspaper import Article

logger = logging.getLogger("LegoSia.HarvesterV4")

class HarvesterV4:
    """
    [LEGO-SIA V4.0 Advanced Intelligence Harvester]
    - Trafilatura: 고정밀 본문 추출 (Markdown)
    - Newspaper4k: 메타데이터 및 대표 이미지 확보
    - 병렬 처리: ThreadPoolExecutor를 통한 고속 전문 수집
    """
    def __init__(self, test_mode=False):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        automation_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(automation_dir)
        
        self.config_path = os.path.join(project_root, "docs_private", "rss_feeds.json")
        self.cache_path = os.path.join(automation_dir, "cache", "seen_urls.json")
        
        self.test_mode = test_mode
        self.seen_urls = self._load_cache()
        
        self.source_tiers = {
            "tier1": ["Ars Technica", "AnandTech", "Tom's Hardware", "Reuters", "Bloomberg", "TechPowerUp", "ExtremeTech", "IEEE Spectrum"],
            "tier2": ["TechCrunch", "The Verge", "Engadget", "VentureBeat", "Forbes", "Wired", "ZDNet", "ZDNET"],
            "tier3": ["9to5Mac", "Gizmodo", "TNW", "How-To Geek", "ZDNet", "Eurogamer", "IGN", "PC Gamer"]
        }

        self.categories_config = {
            "ai-models": {"kor_name": "AI 모델·트렌드"},
            "ai-tools": {"kor_name": "AI 도구·사용법"},
            "gpu-chips": {"kor_name": "GPU·반도체"},
            "pc-robotics": {"kor_name": "AI PC·로봇"},
            "game-optimization": {"kor_name": "게임 최적화·엔진"},
            "ai-gameplay": {"kor_name": "AI 게임 기술"},
            "tutorials": {"kor_name": "실전 튜토리얼"},
            "compare": {"kor_name": "성능 비교"}
        }

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save_cache(self):
        try:
            list_cache = list(self.seen_urls)[-5000:]
            with open(self.cache_path, "w", encoding='utf-8') as f:
                json.dump(list_cache, f)
        except Exception as e:
            logger.error(f" [!] Cache Save Fail: {e}")

    def _get_source_weight(self, source_name):
        if not source_name: return 0.6
        name_l = source_name.lower()
        if any(s.lower() in name_l for s in self.source_tiers["tier1"]): return 1.0
        if any(s.lower() in name_l for s in self.source_tiers["tier2"]): return 0.8
        return 0.6

    def _normalize_item(self, article, source_name, cat_slug):
        raw_url = article.get("url") or article.get("link", "")
        norm_url = normalize_url(raw_url)
        
        if norm_url in self.seen_urls:
            return None
            
        self.seen_urls.add(norm_url)
        
        return HarvestedArticle(
            title=clean_text(article.get("title", "")),
            description=clean_text(article.get("description", "") or article.get("snippet", ""))[:400],
            url=raw_url,
            normalized_url=norm_url,
            publishedAt=article.get("publishedAt") or article.get("pubDate") or datetime.now().isoformat(),
            source_name=source_name,
            eng_category_slug=cat_slug,
            source_weight=self._get_source_weight(source_name)
        )

    def fetch_rss(self, limit_per_source=50):
        all_items = []
        if not os.path.exists(self.config_path):
            logger.warning(f" [!] RSS Config Missing: {self.config_path}")
            return []

        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                feeds_config = json.load(f)
            
            for cat_slug, sources in feeds_config.items():
                for source in sources:
                    try:
                        logger.info(f" [*] Fetching RSS: {source['name']} ({cat_slug})")
                        feed = feedparser.parse(source["url"])
                        if not feed.entries: continue
                            
                        for entry in feed.entries[:limit_per_source]:
                            item = self._normalize_item(entry, source["name"], cat_slug)
                            if item: all_items.append(item)
                    except Exception as e:
                        logger.warning(f" [!] RSS Source Fail ({source['name']}): {e}")
        except Exception as e:
            logger.error(f" [!] RSS Loader Critical Fail: {e}")

        return all_items

    def _enrich_article(self, article: HarvestedArticle):
        """[V2 핵심] Newspaper4k + Trafilatura를 이용한 데이터 강화"""
        try:
            # 1. Newspaper4k: 메타데이터 및 이미지
            ns_article = Article(article.url)
            ns_article.download()
            ns_article.parse()
            article.top_image = ns_article.top_image
            
            # 2. Trafilatura: 전문 추출 (Markdown)
            downloaded = trafilatura.fetch_url(article.url)
            if downloaded:
                markdown_content = trafilatura.extract(downloaded, output_format='markdown', include_links=True)
                if markdown_content:
                    article.full_content = markdown_content
                    # description이 부실할 경우 추출된 본문 앞부분으로 교체
                    if len(article.description) < 50:
                        article.description = markdown_content[:400].replace('\n', ' ')
            
            logger.debug(f" [ENRICHED] {article.title[:30]}... (Img: {'Y' if article.top_image else 'N'}, Content: {len(article.full_content)} chars)")
            return True
        except Exception as e:
            logger.warning(f" [!] Enrichment Fail ({article.url}): {e}")
            return False

    def enrich_batch(self, articles: List[HarvestedArticle], max_workers=5):
        """병렬로 기사 내용 강화"""
        logger.info(f" [ENRICH] Starting parallel enrichment for {len(articles)} articles...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self._enrich_article, articles))
        logger.info(" [ENRICH] Completed.")

    def fetch_all(self, limit_per_cat=15):
        logger.info(" [>>>] Starting Harvester V4.0 (Advanced) Cycle")
        rss_items = self.fetch_rss()
        
        results = []
        stats = {cat: 0 for cat in self.categories_config}
        
        for item in rss_items:
            cat = item.eng_category_slug
            if stats[cat] < limit_per_cat * 2: 
                results.append(item)
                stats[cat] += 1
        
        self._save_cache()
        logger.info(f" [+++] RSS Harvest Initial: {len(results)} items found")

        # 2-Pass Quality Filtering
        qf = QualityFilter()
        filtered_results = []
        
        for cat in self.categories_config:
            cat_articles = [a for a in results if a.eng_category_slug == cat]
            if not cat_articles: continue
                
            logger.info(f" [FILTER] Processing {cat} ({len(cat_articles)} items)...")
            selected = qf.execute_pipeline(cat_articles, cat, limit=limit_per_cat)
            filtered_results.extend(selected)

        # 필터링된 기사들에 대해서만 전문 추출 및 이미지 확보 (고효율)
        if filtered_results:
            self.enrich_batch(filtered_results)
            
            # [V4.1] 전문 추출 실패한 기사 제외 (사용자 요청: 본문 없는 기사는 분석 의미 없음)
            original_count = len(filtered_results)
            filtered_results = [a for a in filtered_results if a.full_content.strip()]
            if len(filtered_results) < original_count:
                logger.info(f" [CLEANUP] Removed {original_count - len(filtered_results)} articles due to extraction failure.")

        logger.info(f" [>>>] Filtered & Enriched Harvest Complete: {len(filtered_results)} items selected")
        return filtered_results

    def dump_to_category_files(self, limit_per_cat=15):
        results = self.fetch_all(limit_per_cat=limit_per_cat)
        
        grouped = {cat: [] for cat in self.categories_config}
        for item in results:
            cat = item.eng_category_slug
            if cat in grouped:
                grouped[cat].append(item)
                
        output_files = {}
        os.makedirs("scratch", exist_ok=True)
        
        for cat, items in grouped.items():
            if not items: continue
            
            filepath = f"scratch/v2_{cat}_enriched_dump.md"
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# LEGO-SIA V2 ENRICHED SOURCE DATA: {cat}\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for idx, a in enumerate(items, 1):
                        f.write(f"## 📰 [ID:{idx}] {a.title}\n")
                        f.write(f"**Meta Info**\n")
                        f.write(f"- **Source:** {a.source_name}\n")
                        f.write(f"- **Date:** {a.publishedAt[:10]}\n")
                        f.write(f"- **URL:** {a.url}\n")
                        f.write(f"- **Original Top Image:** {a.top_image if a.top_image else 'None'}\n")
                        f.write(f"- **Quality Score:** {a.quality_score if a.quality_score else 'N/A'}/10\n\n")
                        
                        f.write(f"**[FULL CONTENT]**\n")
                        f.write(f"{a.full_content}\n\n")
                        f.write("---\n\n")
                
                output_files[cat] = filepath
                logger.info(f" [DUMP] Saved {len(items)} enriched articles to {filepath}")
            except Exception as e:
                logger.error(f" [!] Failed to dump {cat}: {e}")
                
        return output_files

    def dump_to_single_file(self, limit_per_cat=15):
        """[V2.1] 모든 카테고리 기사를 하나의 통합 소스 파일로 저장 (분류 권한을 NLM에게 위임하기 위함)"""
        results = self.fetch_all(limit_per_cat=limit_per_cat)
        if not results:
            return None
            
        os.makedirs("scratch", exist_ok=True)
        filepath = "scratch/v2_macro_source_all.md"
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# LEGO-SIA V2 INTEGRATED SOURCE DATA\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total Articles:** {len(results)}\n\n")
                f.write("당신은 이 소스 데이터에 포함된 각 기사를 분석하여 가장 적합한 카테고리로 분류해야 합니다.\n\n")
                
                for idx, a in enumerate(results, 1):
                    f.write(f"## 📰 [ID:{idx}] {a.title}\n")
                    f.write(f"**Meta Info**\n")
                    f.write(f"- **Initial Source Category:** {a.eng_category_slug}\n")
                    f.write(f"- **Source Name:** {a.source_name}\n")
                    f.write(f"- **Date:** {a.publishedAt[:10]}\n")
                    f.write(f"- **URL:** {a.url}\n")
                    f.write(f"- **Original Top Image:** {a.top_image if a.top_image else 'None'}\n")
                    f.write(f"- **Quality Score:** {a.quality_score if a.quality_score else 'N/A'}/10\n\n")
                    
                    f.write(f"**[FULL CONTENT]**\n")
                    f.write(f"{a.full_content}\n\n")
                    f.write("---\n\n")
            
            logger.info(f" [DUMP] Saved all {len(results)} enriched articles to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f" [!] Failed to dump integrated file: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    harvester = HarvesterV4()
    harvester.dump_to_category_files(limit_per_cat=5)
