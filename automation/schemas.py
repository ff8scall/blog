# -*- coding: utf-8 -*-
"""
[schemas.py] LEGO-SIA Pipeline v5.0 Data Schemas
==================================================
표준 라이브러리 dataclasses 기반 — 추가 의존성 없음.
AI 코딩 에디터의 자동완성/타입 힌트를 극대화합니다.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HarvestedArticle:
    """RSS에서 수집된 원시 기사 데이터"""
    title: str
    url: str
    normalized_url: str
    description: str = ""
    source_name: str = "Unknown"
    eng_category_slug: str = "ai-models"
    publishedAt: str = ""
    image: Optional[str] = None
    source_weight: float = 0.6
    # v5.0: 품질 필터링에서 채워지는 필드
    quality_score: Optional[int] = None
    quality_tags: List[str] = field(default_factory=list)


@dataclass
class FilterResult:
    """필터링 파이프라인 결과 메타데이터 (로깅/디버깅용)"""
    total_input: int = 0
    pass1_survived: int = 0
    pass2_selected: int = 0
    api_calls_used: int = 0
    model_used: str = "none"
    selected_ids: List[int] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"[FilterResult] Input={self.total_input} → "
            f"Pass1={self.pass1_survived} → "
            f"Pass2={self.pass2_selected} | "
            f"API calls={self.api_calls_used} ({self.model_used})"
        )
