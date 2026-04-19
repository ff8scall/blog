# Lego-Sia Intelligence Taxonomy Guide (V1.0)

This document defines the categorization rules for the automated news pipeline.

## 1. Top-Level Clusters (Main Menus)

| Cluster ID | KR Name | EN Name | Primary Focus |
| :--- | :--- | :--- | :--- |
| **intelligence** | AI 인텔리전스 | Intelligence | Pure AI progress, LLMs, Algorithms, AI Tools |
| **hardware** | 차세대 하드웨어 | Hardware | Silicon, GPUs, Data Centers, Robotics |
| **game-tech** | 게임 테크 | Game Tech | Gaming Engines, Graphics, Gaming Industry AI |
| **insights** | 인사이트 | Insights | Practical Guides, Tutorials, Comparisons |
| **trends** | 메가트렌드 | Trends | Macro Economics, Geopolitics, Big Tech Strategy |

---

## 2. Sub-Category Mapping

| Category ID | Parent Cluster | Description |
| :--- | :--- | :--- |
| **ai-models** | `intelligence` | New models (GPT, Claude, Gemini) |
| **ai-tools** | `intelligence` | AI-powered productivity software |
| **gpu-chips** | `hardware` | H100, B200, AMD/Intel hardware reviews |
| **pc-robotics** | `hardware` | Humanoids, Autonomous robots, HW components |
| **game-optimization** | `game-tech` | Graphics optimization, Engine updates |
| **ai-gameplay** | `game-tech` | NPC AI, Procedural generation in games |
| **tutorials** | `insights` | "How-to" guides for tech users |
| **compare** | `insights` | Product VS Product, Market comparisons |
| **daily-macro** | `trends` | Global tech market movements |

---

## 3. Classification Priority Rules

To prevent "AI Models" or "Optimization" from appearing in wrong places, the following priority is applied:

1. **Keyword "Game/Gaming"** -> Always map to `game-tech`.
2. **Keyword "Robot/Humanoid/Chip/Semiconductor"** -> Always map to `hardware`.
3. **Keyword "Price/Inflation/Market/Stock"** -> Map to `trends`.
4. **Pure Software/LLM/Chatbot** -> Map to `intelligence`.
5. **Tutorial/Guide/Comparison** -> Map to `insights`.

---

## 4. Automation Strategy (nlm_parser.py)

- **Input**: `CATEGORY` or `CLUSTER` fields from NotebookLM.
- **Normalization**: If input doesn't match the IDs above, use fuzzy mapping.
- **Default**: `intelligence` / `ai-models`.
