---
title: "Intel 18A Manufacturing Deep Dive: PowerVia, RibbonFET, and VLSI 2025 Digital Twins"
date: "2026-04-23T19:55:39Z"
description: "Intel’s 18A process node is the existential cornerstone of the 'IDM 2.0' strategy. At the VLSI 2025 conference, Intel and other industry leaders outlined the future of sub-2nm manufacturing, where the primary battleground has shifted from simple transistor shrinking to complex interconnect and power delivery architectures. Central to the 18A value proposition is the combination of RibbonFET (Intel’s version of Gate-All-Around) and PowerVia. While competitors like TSMC are taking a more conservative approach to backside power delivery, Intel has positioned PowerVia as its primary competitive ed..."
image: "/images/fallbacks/ai-agent.jpg"
clusters: ["hardware"]
tags: []
featured: false
---
## Executive Summary
- Intel’s 18A process node is the existential cornerstone of the "IDM 2.0" strategy. At the VLSI 2025 conference, Intel and other industry leaders outlined the future of sub-2nm manufacturing, where the primary battleground has shifted from simple transistor shrinking to complex interconnect and power delivery architectures. Central to the 18A value proposition is the combination of RibbonFET (Intel’s version of Gate-All-Around) and PowerVia. While competitors like TSMC are taking a more conservative approach to backside power delivery, Intel has positioned PowerVia as its primary competitive ed...

## Strategic Deep-Dive

Intel’s 18A process node is the existential cornerstone of the "IDM 2.0" strategy. At the VLSI 2025 conference, Intel and other industry leaders outlined the future of sub-2nm manufacturing, where the primary battleground has shifted from simple transistor shrinking to complex interconnect and power delivery architectures. Central to the 18A value proposition is the combination of RibbonFET (Intel’s version of Gate-All-Around) and PowerVia.

While competitors like TSMC are taking a more conservative approach to backside power delivery, Intel has positioned PowerVia as its primary competitive edge.

Backside power delivery (PowerVia) solves a critical bottleneck in modern chip design: signal and power congestion on the front side of the wafer. By moving the power delivery network to the back, Intel can reduce the voltage droop and interference that typically plague high-performance logic at these scales. However, the yield ramp for PowerVia is notoriously difficult.

This is where the concept of "Digital Twins" from atoms to fabs becomes essential. As discussed at VLSI 2025, modern fabs are increasingly relying on atomistic-level simulations to predict how materials behave under these new manufacturing paradigms before a single physical wafer is ever run. This digital modeling reduces the astronomical costs of R&D for nodes as complex as 18A.

Furthermore, the conference highlighted the inevitable transition in the memory sector from 4F2 DRAM structures to true 3D DRAM. The traditional 2D scaling of DRAM cells has reached a physical dead end; 4F2 was the last stop before a vertical leap. Similar to the NAND flash transition years ago, DRAM is moving toward vertical stacking to maintain density gains.

We also observed innovations from non-Western regions, such as China’s FlipFET, indicating that the race for novel transistor architectures is global despite geopolitical friction. Intel’s success with 18A will ultimately be measured not just by its gate density, but by its ability to maintain competitive pricing in the face of these rising manufacturing complexities. If PowerVia delivers on its performance promises without destroying yield, Intel may finally close the gap with TSMC.


