# -*- coding: utf-8 -*-
import os
import time
import random
import sys
import logging

# 현재 디렉토리를 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ai_writer import AIWriter
from harvester_v3 import HarvesterV3

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(current_dir, "stable_runner.log"), encoding='utf-8')
    ]
)
logger = logging.getLogger("LegoSia.StableRunner")

def run():
    logger.info("=== [LEGO-SIA V2.0] Production Prototype Stable Runner Started ===")
    
    writer = AIWriter()
    harvester = HarvesterV3(test_mode=True)
    
    # 8-Category Taxonomy Validation
    target_categories = list(harvester.categories_config.keys())
    
    while True:
        try:
            logger.info(" [1/3] Intelligence Phase: Harvesting from Tiered Sources...")
            # Harvest 30 items across all categories from RSS
            raw_news, stats = harvester.fetch_all(limit_per_cat=5)
            
            if not raw_news:
                logger.warning(" [!] No new intelligence found. Sleeping for 10 minutes...")
                time.sleep(600)
                continue
                
            logger.info(f" [2/3] Selection Phase: News harvested. Stats: {stats}")
            
            # Select one target from the pool (weighted by source_weight)
            # Tier 1 sources get more priority
            selected_item = random.choices(raw_news, weights=[it['source_weight'] for it in raw_news], k=1)[0]
            
            topic = selected_item['title']
            category = selected_item['eng_category_slug']
            source = selected_item['source_name']
            
            logger.info(f" [OK] Selected Target: [{category}] {topic} (Source: {source})")
            
            logger.info(" [3/3] Production Phase: Generating High-Quality Professional Article...")
            content = writer.generate_content(keyword=topic, category=category)
            
            if content:
                # Add source credit at the end
                if "Source:" not in content:
                    content += f"\n\n---\n*Source: {source}*"
                
                filename = f"auto-{int(time.time())}.md"
                writer.save_post(content, filename)
                logger.info(f" [SUCCESS] Article Published: {filename}")
            else:
                logger.error(" [!] Generation failed or empty content returned.")

            # API Quota Guard: 2-Hour Strategy (Approx 120 articles/day -> 1 article every 12 mins)
            # Local test mode sleep: 5-8 mins
            sleep_time = random.randint(300, 480) 
            logger.info(f" [*] Strategy: Waiting for cooldown... ({sleep_time}s)")
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f" [CRITICAL] Loop Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    run()
