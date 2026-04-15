# -*- coding: utf-8 -*-
import os
import time
import requests
import json
import re
import feedparser
import random
import logging
from datetime import datetime
from common_utils import normalize_url, clean_text, extract_domain

logger = logging.getLogger("LegoSia.HarvesterV3")

class HarvesterV3:
    """
    [LEGO-SIA V3.0 Strategic Intelligence Harvester]
    - Hybrid Architecture: RSS (Speed/Direct) + API (Diversity)
    - Advanced Deduplication: Persistent URL caching
    - Taxonomy Mapping: Native 8-category support
    - Common Module Integration: standardized cleaning and normalization
    """
    def __init__(self, test_mode=False):
        self.keys = {
            "newsapi": os.getenv("NEWSAPI_ORG_KEY"),
            "gnews": os.getenv("GNEWS_API_KEY")
        }
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(os.path.dirname(current_dir), "docs_private", "rss_feeds.json")
        self.cache_path = os.path.join(current_dir, "cache", "seen_urls.json")
        
        # Ensure cache directory exists
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        self.test_mode = test_mode
        self.exhausted = set()
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
            # Keep only last 5000 URLs to prevent file bloat
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
        
        return {
            "title": clean_text(article.get("title", "")),
            "description": clean_text(article.get("description", "") or article.get("snippet", ""))[:300],
            "url": raw_url,
            "normalized_url": norm_url,
            "image": article.get("urlToImage") or article.get("image_url") or article.get("image"),
            "publishedAt": article.get("publishedAt") or article.get("pubDate") or datetime.now().isoformat(),
            "source_name": source_name,
            "eng_category_slug": cat_slug,
            "source_weight": self._get_source_weight(source_name)
        }

    def fetch_rss(self):
        """
        Directly fetch from high-authority RSS feeds (Tier 1 & 2)
        """
        all_items = []
        if not os.path.exists(self.config_path):
            logger.error(f" [!] RSS Config Missing: {self.config_path}")
            return []

        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                feeds_config = json.load(f)
            
            for cat_slug, sources in feeds_config.items():
                for source in sources:
                    try:
                        logger.info(f" [*] Fetching RSS: {source['name']} ({cat_slug})")
                        feed = feedparser.parse(source["url"])
                        
                        # Handle Eurogamer etc timeout implicitly by checking if entries exist
                        if not feed.entries:
                            continue
                            
                        for entry in feed.entries[:10]:
                            item = self._normalize_item(entry, source["name"], cat_slug)
                            if item:
                                all_items.append(item)
                    except Exception as e:
                        logger.warning(f" [!] RSS Source Fail ({source['name']}): {e}")
        except Exception as e:
            logger.error(f" [!] RSS Loader Critical Fail: {e}")

        return all_items

    def fetch_all(self, limit_per_cat=3, rss_only=False):
        """
        Main harvesting entry point
        - First gets everything from RSS
        - Then pads with API results if needed
        """
        logger.info(" [>>>] Starting Harvester V3.0 Cycle")
        rss_items = self.fetch_rss()
        
        results = []
        stats = {cat: 0 for cat in self.categories_config}
        
        # Process RSS items first
        for item in rss_items:
            cat = item['eng_category_slug']
            if stats[cat] < limit_per_cat * 2: # Allow more from high-quality RSS
                results.append(item)
                stats[cat] += 1
        
        # Save cache after RSS phase
        self._save_cache()
        
        logger.info(f" [+++] RSS Harvest Complete: {len(results)} items found")
        return results, stats
