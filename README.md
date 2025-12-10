# 🌐 NeoSeek: The Future of Ethical Search (Beta v0.1)

> **Beyond Keywords: Privacy, Quality & Intelligence.**
> *An open-source alternative to DuckDuckGo, powered by Semantic AI.*

![NeoSeek Banner](https://img.shields.io/badge/Status-Beta_v0.1-blue?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge) ![Built With](https://img.shields.io/badge/Built_With-Next.js_&_Python-black?style=for-the-badge)

## 🚀 What is NeoSeek?

NeoSeek is a **100% open-source, autonomous search engine** designed to fix the broken state of modern search. We don't just index everything; we curate quality.

Unlike traditional engines that rely heavily on SEO keywords, NeoSeek uses a proprietary **Semantic Authority Scoring (SRAS)** system and an **Intelligent Crawler** to prioritize authoritative content while strictly filtering out spam, misinformation, and unsafe content.

**Our Mission:** To provide a safe, privacy-focused, and highly relevant search experience for the French (FR) and English (EN) web.

---

## 🧠 Key Innovations (The "Revolutionary" Part)

### 1. 🛡️ The Security Veto (Safety First)
NeoSeek is built to be a safe haven. Our crawler integrates a **Mega-Blacklist** that acts as an immediate veto against:
* ❌ Explicit/Pornographic content.
* ❌ Extremist ideologies & Hate speech.
* ❌ Phishing, Malware, and Scams.

### 2. 🤖 Similarity-Based Crawler ("The Brain")
Instead of blindly crawling the web, our Python crawler uses a **"Seed Learning"** approach:
* It starts with a curated list of high-quality "Seed" domains.
* It analyzes new links based on **Semantic Similarity ($S$ Score)**.
* It only indexes pages that match the quality standards of our seeds, ignoring low-quality farms.

### 3. 📊 Semantic Authority Scoring (SRAS)
We don't just count backlinks. The SRAS algorithm evaluates the *contextual authority* of a page. A high SRAS score means the content is trustworthy and deep, not just popular.

---

## 🛠️ Tech Stack

* **Frontend:** Next.js (React) - *Fast, modern UI.*
* **Search Engine:** Meilisearch - *Lightning-fast, typo-tolerant search.*
* **Crawler & AI:** Python 3.9+ - *Custom crawler with Scikit-learn (TF-IDF) & NLP logic.*
* **Infrastructure:** Optimized for NVMe VPS (e.g., OVHcloud).

---

## ⚡ Getting Started (Run it Locally)

Want to contribute or test the "Brain"? Follow these steps.

### Prerequisites
* Node.js (v18+)
* Python (v3.9+)
* Meilisearch (Installed locally or via Docker)

### 1. Clone the Repo
```bash
git clone [https://github.com/votre-pseudo/neoseek.git](https://github.com/FortilexYT/neoseek.git)
cd neoseek

