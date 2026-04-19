# -*- coding: utf-8 -*-
"""
[quality_filter.py] 2-Pass News Quality Filter
=============================================
1단계: Rule-based (키워드/도메인 필터링) - 비용 0원
2단계: LLM-based (Gemini Flash-Lite 배치 스코어링) - 저비용/고효율
"""

import json
import re
import logging
from typing import List
from schemas import HarvestedArticle, FilterResult
from ai_writer import AIWriter

logger = logging.getLogger("LegoSia.QualityFilter")

class QualityFilter:
    def __init__(self, writer=None):
        self.writer = writer if writer else AIWriter()
        
        # 카테고리별 핵심 키워드 (Pass 1)
        self.category_keywords = {
            "ai-models": ["AI", "LLM", "GPT", "Gemini", "Claude", "Llama", "transformer", "fine-tune", "MoE", "parameter", "DeepMind", "OpenAI", "Anthropic", "Mistral"],
            "ai-tools": ["AI", "copilot", "chatgpt", "midjourney", "stable diffusion", "productivity", "agent", "workflow", "assistant", "automation", "integration"],
            "gpu-chips": ["GPU", "NVIDIA", "AMD", "TSMC", "HBM", "NVLink", "3nm", "chiplet", "Blackwell", "Instinct", "GeForce", "Radeon", "Intel", "Gaudi"],
            "pc-robotics": ["NPU", "Snapdragon", "Core Ultra", "Ryzen AI", "Robot", "Humanoid", "AI PC", "Laptop", "Windows 11", "Copilot+", "ASUS", "MSI", "Dell"],
            "game-optimization": ["DLSS", "FSR", "XeSS", "Ray Tracing", "Path Tracing", "Unreal Engine", "Unity", "Frame Gen", "Performance", "Optimization", "Patch", "Benchmark", "NVIDIA", "AMD"],
            "ai-gameplay": ["NPC AI", "Procedural", "Generative AI in games", "behavior tree", "reinforcement learning", "LLM in games", "AI NPCs"],
            "tutorials": ["How to", "Guide", "Tutorial", "Step by step", "Setup", "Install", "Tips", "Tricks", "Best", "Fix"],
            "compare": ["Benchmark", "vs", "Comparison", "Review", "Speed test", "Efficiency", "Analysis", "Head to head"]
        }
        
        # 제외 키워드 (클릭베이트, 루머 등)
        self.blacklist_keywords = ["rumor", "leak", "unconfirmed", "sale", "deal", "discount", "price cut", "giveaway"]

    def pass1_rule_filter(self, articles: List[HarvestedArticle]) -> List[HarvestedArticle]:
        """Pass 1: 키워드 및 도메인 기반 필터링 (Zero Cost)"""
        survived = []
        for a in articles:
            text = (a.title + " " + a.description).lower()
            
            # 블랙리스트 체크
            if any(blk in text for blk in self.blacklist_keywords):
                continue
                
            # 카테고리별 키워드 체크
            cat = a.eng_category_slug
            keywords = self.category_keywords.get(cat, [])
            
            # 키워드가 하나라도 포함되어 있거나, 소스 비중이 높으면 생존
            matched_kw = [kw for kw in keywords if kw.lower() in text]
            if matched_kw or a.source_weight >= 0.9:
                survived.append(a)
                if matched_kw:
                    a.quality_tags.append(f"kw:{matched_kw[0]}")
            else:
                logger.debug(f" [PASS 1 REJECT] {cat} | {a.title[:30]}... (No keywords matched)")
                
        return survived

    def pass2_llm_score(self, articles: List[HarvestedArticle], category: str, top_n: int = 10) -> List[HarvestedArticle]:
        """Pass 2: Gemini Flash-Lite 배치 스코어링 (배치당 20개씩 분할 처리)"""
        if not articles:
            return []
            
        all_final_selection = []
        
        # 20개씩 배치로 나누어 처리
        for batch_idx in range(0, len(articles), 20):
            batch = articles[batch_idx : batch_idx + 20]
            items_str = ""
            for i, a in enumerate(batch):
                items_str += f"ID {i}: {a.title} | Source: {a.source_name} | Desc: {a.description[:150]}\n"
                
            prompt = f"""
[TASK]: Score these news items for the '{category}' category based on Technical Depth, Insight, and Trend Relevance.
[CRITERIA]: 
 - 8-10: Groundbreaking news, deep technical analysis, or major industry shift.
 - 5-7: Standard tech news, solid updates.
 - 1-4: Minor updates, rumor, marketing-heavy, or off-topic.
[ITEMS]:
{items_str}

[OUTPUT]: Strictly JSON format with 'selected_ids' (top IDs) and 'scores' (dictionary of ID: score).
Example: {{"selected_ids": [0, 2], "scores": {{"0": 9, "1": 4, "2": 8}}}}
"""
            
            res_raw = self.writer.score_articles(prompt)
            if not res_raw:
                logger.warning(f"Pass 2 batch {batch_idx//20} failed for {category}. Skipping batch.")
                continue
                
            try:
                # JSON 추출
                match = re.search(r'\{.*\}', res_raw, re.DOTALL)
                if not match:
                    continue
                    
                res_json = json.loads(match.group())
                selected_ids = res_json.get("selected_ids", [])
                scores_map = res_json.get("scores", {})
                
                for s_id in selected_ids:
                    try:
                        idx = int(s_id)
                        if idx < len(batch):
                            article = batch[idx]
                            article.quality_score = int(scores_map.get(str(idx), 7))
                            all_final_selection.append(article)
                    except (ValueError, TypeError):
                        continue
            except Exception as e:
                logger.error(f"Pass 2 batch {batch_idx//20} Parse Error: {e}")
                
        # 스코어 순으로 정렬 후 상위 top_n개 반환
        all_final_selection.sort(key=lambda x: x.quality_score, reverse=True)
        return all_final_selection[:top_n]

    def execute_pipeline(self, raw_articles: List[HarvestedArticle], category: str, limit: int = 10) -> List[HarvestedArticle]:
        """전체 2-Pass 필터링 파이프라인 실행"""
        result_meta = FilterResult(total_input=len(raw_articles))
        
        # 1단계
        survived = self.pass1_rule_filter(raw_articles)
        
        # [Fallback] 만약 키워드 필터링으로 다 날아갔는데 원본은 있다면, 
        # 상위 소스 가중치 순으로 최소 3개는 살려서 2단계로 보냄 (품질 제어는 LLM이 할 것)
        if not survived and raw_articles:
            logger.warning(f" [FALLBACK] Pass 1 empty for {category}. Picking top source-weighted items.")
            sorted_raw = sorted(raw_articles, key=lambda x: x.source_weight, reverse=True)
            survived = sorted_raw[:max(3, limit // 2)]
            
        result_meta.pass1_survived = len(survived)
        
        # 2단계
        final = self.pass2_llm_score(survived, category, top_n=limit)
        result_meta.pass2_selected = len(final)
        
        # 메타 정보 업데이트
        result_meta.model_used = "gemini-2.5-flash-lite"
        result_meta.api_calls_used = 1 if survived else 0
        
        logger.info(result_meta.summary())
        return final
