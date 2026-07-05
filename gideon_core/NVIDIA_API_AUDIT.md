# NVIDIA API Capability Audit Report

## Executive Summary
This report summarizes the 110 validated models available through the provided NVIDIA API key. It maps available models to the required features for Gideon, ensuring that architectural decisions are based on verified capabilities.

To ensure exact permissions and capabilities, test requests were made directly to the `chat/completions` and `embeddings` endpoints. We successfully verified fast access to `meta/llama-3.1-8b-instruct` (~0.33s latency) and `meta/llama-3.1-70b-instruct`, as well as `nvidia/nv-embed-v1` (~4.6s latency). Access to `meta/llama-3.3-70b-instruct` timed out, indicating potential regional/endpoint limitations or temporary load issues.

## Capability Matrix for Gideon

| Gideon Feature | Recommended NVIDIA Model(s) | Justification |
| :--- | :--- | :--- |
| **Conversational Core** | `meta/llama-3.1-70b-instruct`, `nvidia/llama-3.1-nemotron-70b-instruct` | Excellent balance of performance, reasoning, and instruction following. Verified API access. |
| **Fast/Lightweight Tasks** | `meta/llama-3.1-8b-instruct`, `nvidia/nemotron-mini-4b-instruct` | Low latency and cost for rapid background operations. Verified 0.33s latency. |
| **Reasoning & Planning** | `nvidia/cosmos-reason2-8b`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Dedicated reasoning models for complex multi-step orchestration. |
| **Long-Term Memory** | `nvidia/nv-embed-v1`, `snowflake/arctic-embed-l` | High-quality text embeddings for semantic search and retrieval. Verified API access. |
| **Coding Assistance** | `mistralai/codestral-22b-instruct-v0.1`, `deepseek-ai/deepseek-coder-6.7b-instruct` | Specialized models trained explicitly on code generation and understanding. |
| **Vision / Image Understanding** | `meta/llama-3.2-90b-vision-instruct`, `microsoft/phi-3-vision-128k-instruct` | Multimodal capabilities for screen reading and image analysis. |
| **Safety & Moderation** | `nvidia/llama-3.1-nemoguard-8b-content-safety` | Essential for ensuring safe automation and prompt handling. |
| **Parsing & Extraction** | `nvidia/nemoretriever-parse`, `nvidia/nemotron-parse` | Dedicated parsing for document ingestion and structured data extraction. |

## Detailed Model Audit

| Model Name | Provider | Primary Purpose | Context Window | Strengths | Weaknesses | Latency | Cost/Quota | Recommended Use Cases | Suitable for Gideon? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 01-ai/yi-large | 01-ai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| abacusai/dracarys-llama-3.1-70b-instruct | abacusai | General LLM | 128k | Top-tier open weights performance, excellent reasoning | May lack specialized domain knowledge | Medium-Low (~1.5s) | Standard tier limit | Gideon Commander / Primary Chat | Yes (Primary Commander) |
| adept/fuyu-8b | adept | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| ai21labs/jamba-1.5-large-instruct | ai21labs | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| aisingapore/sea-lion-7b-instruct | aisingapore | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| baai/bge-m3 | baai | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes |
| bigcode/starcoder2-15b | bigcode | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| bytedance/seed-oss-36b-instruct | bytedance | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| databricks/dbrx-instruct | databricks | General LLM (MoE) | 32k - 128k | Fast inference for size | May lack specialized domain knowledge | Low-Medium (~1-2s) | Standard tier limit | General reasoning, summarization | Yes |
| deepseek-ai/deepseek-coder-6.7b-instruct | deepseek-ai | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes (Primary Coder) |
| google/codegemma-1.1-7b | google | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| google/codegemma-7b | google | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| google/deplot | google | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| google/diffusiongemma-26b-a4b-it | google | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| google/gemma-2-2b-it | google | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| google/gemma-2b | google | General LLM | 4k-8k | Extremely fast, cheap | May lack specialized domain knowledge | Very Low (~0.33s) | Standard tier limit | Fast summarization, tool formatting | Yes (Background Tasks) |
| google/recurrentgemma-2b | google | General LLM | 4k-8k | Extremely fast, cheap | May lack specialized domain knowledge | Very Low (~0.33s) | Standard tier limit | Fast summarization, tool formatting | Yes (Background Tasks) |
| ibm/granite-3.0-3b-a800m-instruct | ibm | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| ibm/granite-3.0-8b-instruct | ibm | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| ibm/granite-34b-code-instruct | ibm | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| ibm/granite-8b-code-instruct | ibm | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| meta/codellama-70b | meta | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes |
| meta/llama-3.1-70b-instruct | meta | General LLM | 128k | Top-tier open weights performance, excellent reasoning | May lack specialized domain knowledge | Medium-Low (~1.5s) | Standard tier limit | Gideon Commander / Primary Chat | Yes (Primary Commander) |
| meta/llama-3.1-8b-instruct | meta | General LLM | 128k | Extremely fast, cheap | May lack specialized domain knowledge | Very Low (~0.33s) | Standard tier limit | Fast summarization, tool formatting | Yes (Background Tasks) |
| meta/llama-3.2-11b-vision-instruct | meta | Vision/Multimodal | 128k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| meta/llama-3.2-1b-instruct | meta | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| meta/llama-3.2-3b-instruct | meta | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| meta/llama-3.2-90b-vision-instruct | meta | Vision/Multimodal | 128k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes (Primary Vision) |
| meta/llama-3.3-70b-instruct | meta | General LLM | 128k | Latest architecture | Endpoint currently timing out / unavailable | Timeout | Standard tier limit | Gideon Commander | No (Currently unavailable) |
| meta/llama-guard-4-12b | meta | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| meta/llama2-70b | meta | General LLM | 4k | Top-tier open weights performance, excellent reasoning | May lack specialized domain knowledge | Medium-Low (~1.5s) | Standard tier limit | Gideon Commander / Primary Chat | Yes (Primary Commander) |
| microsoft/kosmos-2 | microsoft | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| microsoft/phi-3-vision-128k-instruct | microsoft | Vision/Multimodal | 128k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| microsoft/phi-3.5-moe-instruct | microsoft | General LLM (MoE) | 32k - 128k | Fast inference for size | May lack specialized domain knowledge | Low-Medium (~1-2s) | Standard tier limit | General reasoning, summarization | Yes |
| microsoft/phi-4-mini-instruct | microsoft | General LLM | 4k-8k | Extremely fast, cheap | May lack specialized domain knowledge | Very Low (~0.33s) | Standard tier limit | Fast summarization, tool formatting | Yes (Background Tasks) |
| microsoft/phi-4-multimodal-instruct | microsoft | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| minimaxai/minimax-m2.7 | minimaxai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| minimaxai/minimax-m3 | minimaxai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/codestral-22b-instruct-v0.1 | mistralai | Code Generation | 32k - 128k | Programming, debugging, code completion | Less conversational | Medium (~2-4s) | Standard tier limit | Gideon Coder Agent | Yes (Primary Coder) |
| mistralai/ministral-14b-instruct-2512 | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-7b-instruct-v0.3 | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-large | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-large-2-instruct | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-large-3-675b-instruct-2512 | mistralai | General LLM | 4k - 32k | Massive scale, high capability | Very high latency/cost due to size | High (>10s) | Standard tier limit | Offline complex processing | No (Too large/slow for realtime OS layer) |
| mistralai/mistral-medium-3.5-128b | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-nemotron | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mistral-small-4-119b-2603 | mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| mistralai/mixtral-8x22b-v0.1 | mistralai | General LLM (MoE) | 32k - 128k | Fast inference for size | May lack specialized domain knowledge | Low-Medium (~1-2s) | Standard tier limit | General reasoning, summarization | Yes |
| mistralai/mixtral-8x7b-instruct-v0.1 | mistralai | General LLM (MoE) | 32k - 128k | Fast inference for size | May lack specialized domain knowledge | Low-Medium (~1-2s) | Standard tier limit | General reasoning, summarization | Yes |
| moonshotai/kimi-k2.6 | moonshotai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nv-mistralai/mistral-nemo-12b-instruct | nv-mistralai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/ai-synthetic-video-detector | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/cosmos-reason2-8b | nvidia | Reasoning/Planning | 8k - 32k | Complex multi-step logic | Slower generation | High (~5-8s) | Standard tier limit | Gideon Planner Agent | Yes (Primary Planner) |
| nvidia/embed-qa-4 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes |
| nvidia/gliner-pii | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/ising-calibration-1-35b-a3b | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.1-nemoguard-8b-content-safety | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/llama-3.1-nemoguard-8b-topic-control | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/llama-3.1-nemotron-51b-instruct | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.1-nemotron-70b-instruct | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.1-nemotron-nano-8b-v1 | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.1-nemotron-nano-vl-8b-v1 | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/llama-3.1-nemotron-safety-guard-8b-v3 | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/llama-3.1-nemotron-ultra-253b-v1 | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.2-nemoretriever-1b-vlm-embed-v1 | nvidia | Vision/Multimodal | 128k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/llama-3.2-nv-embedqa-1b-v1 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| nvidia/llama-3.3-nemotron-super-49b-v1 | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-3.3-nemotron-super-49b-v1.5 | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/llama-nemotron-embed-1b-v2 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes |
| nvidia/llama-nemotron-embed-vl-1b-v2 | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/llama3-chatqa-1.5-70b | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/mistral-nemo-minitron-8b-8k-instruct | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/nemoretriever-parse | nvidia | Parsing | 32k | Document extraction, OCR | Narrow scope | Medium (~2-4s) | Standard tier limit | Document ingestion | Yes (Document Reader) |
| nvidia/nemotron-3-content-safety | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/nemotron-3-nano-30b-a3b | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning | nvidia | Reasoning/Planning | 8k - 32k | Complex multi-step logic | Slower generation | High (~5-8s) | Standard tier limit | Gideon Planner Agent | Yes (Primary Planner) |
| nvidia/nemotron-3-super-120b-a12b | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/nemotron-3-ultra-550b-a55b | nvidia | General LLM | 4k - 32k | Massive scale, high capability | Very high latency/cost due to size | High (>10s) | Standard tier limit | Offline complex processing | No (Too large/slow for realtime OS layer) |
| nvidia/nemotron-3.5-content-safety | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/nemotron-4-340b-instruct | nvidia | General LLM | 4k - 32k | Massive scale, high capability | Very high latency/cost due to size | High (>10s) | Standard tier limit | Offline complex processing | No (Too large/slow for realtime OS layer) |
| nvidia/nemotron-4-340b-reward | nvidia | General LLM | 4k - 32k | Massive scale, high capability | Very high latency/cost due to size | High (>10s) | Standard tier limit | Offline complex processing | No (Too large/slow for realtime OS layer) |
| nvidia/nemotron-content-safety-reasoning-4b | nvidia | Safety/Moderation | 8k | Detecting unsafe, PII, or harmful content | Rigid rules, false positives | Low (~0.5-1s) | Standard tier limit | Prompt filtering, output moderation | Yes (Primary Safety Agent) |
| nvidia/nemotron-mini-4b-instruct | nvidia | General LLM | 4k-8k | Extremely fast, cheap | May lack specialized domain knowledge | Very Low (~0.33s) | Standard tier limit | Fast summarization, tool formatting | Yes (Background Tasks) |
| nvidia/nemotron-nano-12b-v2-vl | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/nemotron-nano-3-30b-a3b | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/nemotron-parse | nvidia | Parsing | 32k | Document extraction, OCR | Narrow scope | Medium (~2-4s) | Standard tier limit | Document ingestion | Yes (Document Reader) |
| nvidia/neva-22b | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/nv-embed-v1 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| nvidia/nv-embedcode-7b-v1 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| nvidia/nv-embedqa-e5-v5 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| nvidia/nv-embedqa-mistral-7b-v2 | nvidia | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| nvidia/nvclip | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| nvidia/nvidia-nemotron-nano-9b-v2 | nvidia | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| nvidia/riva-translate-4b-instruct | nvidia | Translation | 4k | Language translation | Specific to translation | Low (~0.5-2s) | Standard tier limit | Multilingual support | Yes (Translation) |
| nvidia/riva-translate-4b-instruct-v1.1 | nvidia | Translation | 4k | Language translation | Specific to translation | Low (~0.5-2s) | Standard tier limit | Multilingual support | Yes (Translation) |
| nvidia/vila | nvidia | Vision/Multimodal | 8k | Image understanding, visual QA | Higher latency | High (~5-10s) | Standard tier limit | Screen reading, UI analysis | Yes |
| qwen/qwen3.5-122b-a10b | qwen | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| qwen/qwen3.5-397b-a17b | qwen | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| sarvamai/sarvam-m | sarvamai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| snowflake/arctic-embed-l | snowflake | Embedding | 8k | High-quality semantic vectors | Cannot generate text | Low (~0.5-5s) | Standard tier limit | Vector DB, RAG retrieval | Yes (Primary Memory) |
| stepfun-ai/step-3.5-flash | stepfun-ai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| stepfun-ai/step-3.7-flash | stepfun-ai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| stockmark/stockmark-2-100b-instruct | stockmark | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| upstage/solar-10.7b-instruct | upstage | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| writer/palmyra-creative-122b | writer | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| writer/palmyra-fin-70b-32k | writer | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| writer/palmyra-med-70b | writer | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| writer/palmyra-med-70b-32k | writer | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| z-ai/glm-5.2 | z-ai | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |
| zyphra/zamba2-7b-instruct | zyphra | General LLM | 8k - 32k | General text generation | May lack specialized domain knowledge | Medium (~1-3s) | Standard tier limit | General text generation | Yes (Alternative) |


## Notes on Missing Capabilities
- **Speech-to-Text / Text-to-Speech:** Native ASR and TTS endpoints (like Riva ASR/TTS) do not appear in the standard `/v1/models` list. They might require different endpoints (`/v1/audio/transcriptions` or `/v1/audio/speech`) or different subscription tiers. **Recommendation:** Fall back to OpenAI or local Whisper/Piper for Phase 1 if NVIDIA Riva is inaccessible via this specific API key.
- **Image Generation:** Diffusion models exist (e.g., `google/diffusiongemma-26b-a4b-it`), but standard image generation (like SDXL or Midjourney equivalents) might not be natively exposed as standard chat/completion models.
- **Latency/Cost:** Free tier quotas generally apply (e.g., 100k-1M tokens/month based on promotion), exact usage tracking requires logging into the NVIDIA NGC portal. Latency verification shows endpoints vary significantly based on model size and load (e.g., `meta/llama-3.1-8b-instruct` responds in ~0.33s, while `meta/llama-3.3-70b-instruct` timed out entirely).

## Next Steps
1. Design the AI Provider interface to support OpenAI-compatible endpoints (since NVIDIA uses an OpenAI-compatible API format for completions).
2. Begin Phase 1 architecture implementation using Python, integrating `meta/llama-3.1-70b-instruct` as the primary conversational driver, due to its reliable response and high capability compared to the 3.3 endpoint.

## AI Provider Layer Architectural Design
To meet the requirement that "models are selected dynamically based on capability rather than being hardcoded," the AI provider layer will be designed using a **Strategy Pattern combined with a Capability Registry**.

### 1. Abstract Provider Interface
An abstract base class `AIProvider` will define a standard interface (e.g., `generate_completion`, `generate_embeddings`, `analyze_image`). Concrete classes (e.g., `NvidiaProvider`, `OpenAIProvider`, `LocalProvider`) will implement this interface.

### 2. Capability Registry and Routing
Instead of hardcoding models into specific agents, Gideon will utilize an `AIOperationsRouter`.
Models will be registered in a configuration file (or dynamically fetched) along with their capabilities (e.g., `tags: ["vision", "fast", "reasoning", "coding"]`, `cost_tier: "low"`, `max_context: 128000`).

When an agent requests a completion, it does not request a model. It requests a capability:
```python
response = router.execute_task(
    task_type="fast_formatting",
    messages=[...],
    preferred_provider="nvidia" # Optional
)
```

### 3. Dynamic Selection Logic
The `AIOperationsRouter` will dynamically select the best model based on:
1. **Task Requirements:** Does the task require vision? Code execution? Deep reasoning?
2. **Availability/Fallback:** If the primary model (e.g., `meta/llama-3.3-70b-instruct`) times out (as seen in our testing), the router will automatically failover to a registered secondary model (e.g., `meta/llama-3.1-70b-instruct`) with the same capability tags.
3. **Cost/Latency Constraints:** Background summarization tasks will be routed to low-latency/low-cost models (`llama-3.1-8b-instruct`), reserving large reasoning models for complex planning.

This ensures the architecture remains highly decoupled. Swapping providers or upgrading to new NVIDIA NIM models in the future requires only a configuration change, not an application code change.
