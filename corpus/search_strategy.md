# Search Strategy and Screening Criteria

Released alongside the corpus per Section 3.4 of the companion manuscript so
that any reader can replicate the corpus selection.

## Venues and window

- IEEE Xplore, ACM Digital Library, MDPI journals.
- January 2020 – May 2026. Final search: 29 May 2026.
- Preprint repositories (incl. arXiv) excluded: every cited study must have
  passed formal peer review.
- ACM DL coverage includes peer-reviewed works cross-listed from publisher
  partners (select Elsevier/Springer journals indexed through ACM DL).

## Search strings

Group A (AI methodology), intersected with Group B (IoT cybersecurity):

- Group A: "large language model" OR "LLM" OR "agentic AI" OR "multi-agent"
  OR "ReAct" OR "chain-of-thought" OR "tool use"
- Group B: "IoT" OR "Internet of Things" OR "IIoT" OR "edge security" OR
  "intrusion detection" OR "threat detection" OR "anomaly detection" OR
  "vulnerability discovery" OR "honeypot" OR "SOAR"

Targeted anchor queries: "Edge-IIoTset", "CICIoT2023", "TON_IoT",
"CICIoMT2024", "quantization", "distillation", "pruning",
"small language model", "prompt injection", "hallucination",
"federated learning".

## Inclusion criteria

(a) peer-reviewed, indexed in IEEE Xplore / ACM DL / MDPI;
(b) published January 2020 – May 2026;
(c) addresses LLMs/agentic AI for IoT cybersecurity, or security of LLM/agentic
    systems in IoT contexts, or foundational techniques (datasets, efficiency
    methods, benchmarks) the field demonstrably builds on.

## Exclusion criteria

(a) AI techniques unrelated to language models or agents (pre-2022 pure
    CNN/RNN IDS retained only as foundational baselines);
(b) no empirical evaluation;
(c) duplicates, errata, editorial commentary.

## Flow (PRISMA 2020)

487 records (IEEE 198, ACM 142, MDPI 147) → 63 duplicates removed →
424 title/abstract screened → 218 excluded out-of-scope →
206 full-text screened → 53 excluded (31 insufficient empirical validation,
14 under 2 pages of substantive content, 7 non-English, 1 out-of-window) →
**153 included** (IEEE 58, ACM 39, MDPI 56).

Screening: first author screened all records; senior author independently
re-screened a 15% random sample at each stage (Cohen's kappa = 0.84,
agreement = 90.4%); 7 inclusion decisions adjusted; 1 paper reclassified
out-of-window on full-text re-screen.
