---
title: "Next-Gen Silicon: Ironwood GA and the Dual-Architecture Strategy of TPU v8"
date: "2026-04-24T01:59:24Z"
description: "Google announced the general availability of its seventh-generation TPU, Ironwood, while previewing the TPU v8 architecture, which shifts from a general-purpose design to specialized chips for training (Sunfish) and inference (Zebrafish)."
image: "/images/fallbacks/ai-tech.jpg"
clusters: ["hardware"]
tags: ["Ironwood", "TPU v8", "TSMC 2nm"]
featured: false
---
## Executive Summary
- Google announced the general availability of its seventh-generation TPU, Ironwood, while previewing the TPU v8 architecture, which shifts from a general-purpose design to specialized chips for training (Sunfish) and inference (Zebrafish).

## Strategic Deep-Dive

### Performance Metrics and General Availability of Ironwood

At Cloud Next 2026, Google announced the general availability of Ironwood, its seventh-generation TPU. Designed to handle the rigors of the Agentic Era, each Ironwood chip delivers 4.6 petaFLOPS of compute. When scaled into a massive 9,216-chip superpod configuration, the system achieves a peak performance of 42.5 exaFLOPS.

This scale is critical for enterprises training and deploying frontier-class models that require consistent, high-bandwidth interconnects and massive memory pools.

### TPU v8: The Philosophical Shift to Specialized Silicon

The preview of the eighth-generation TPU marks a significant departure from Google’s previous 'one-size-fits-all' hardware approach. As AI models move from experimental training to mass-market inference, Google is splitting its architecture into two distinct streams to optimize for cost and performance.

*   TPU 8t (Sunfish): Developed in collaboration with Broadcom, this training-centric chip is optimized for maximum throughput and parallel processing, essential for the initial development of next-gen Gemini models.
*   TPU 8i (Zebrafish): Partnered with MediaTek, this inference-specific variant focuses on power efficiency and low-latency response, aimed at serving billions of users at a fraction of current costs.

Both variants target the TSMC 2nm process node with a projected delivery in late 2027. This dual-track strategy allows Google to tailor its hardware specifically to the economic realities of the AI lifecycle, ensuring that training remains fast while serving agents remains affordable.


