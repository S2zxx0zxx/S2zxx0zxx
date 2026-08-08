<div align="center">

<img src="./assets/hero-banner.svg" alt="Satyam Kumar — Full-Stack Builder" width="100%" />

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=2800&pause=900&color=A78BFA&center=true&vCenter=true&width=780&lines=Full-Stack+Builder+%7C+AI+Product+Architect;Founder+%40+DigiRise+India;Shipping+ToolsLab+%C2%B7+BharatOS+%C2%B7+EliteHub;MBA+(Finance)+%40+CIMP+Patna+%C2%B7+Kolkata%2C+India" alt="Typing SVG" />

<br/><br/>

<img src="https://img.shields.io/badge/status-actively_shipping-22c55e?style=for-the-badge&labelColor=0d1117" />
<img src="https://img.shields.io/badge/repos-18_public-a78bfa?style=for-the-badge&labelColor=0d1117" />
<img src="https://img.shields.io/badge/focus-AI_%2B_India_first_products-38bdf8?style=for-the-badge&labelColor=0d1117" />
<img src="https://img.shields.io/badge/based_in-Kolkata%2C_India-f97316?style=for-the-badge&labelColor=0d1117" />

</div>

<br/>

<div align="center">

### `>` a builder's note, before the metrics

</div>

I don't build to look busy — I build to ship. Every project below is a real, running repo, not a portfolio placeholder. I run **DigiRise India**, a digital marketing agency serving clients across India, UAE, and the UK, and in parallel I build AI-native products under the same roof: **ToolsLab**, an AI chat SaaS with real streaming, real image generation, and tiered billing; and **BharatOS**, an attempt at building an AI "Life Operating System" for India, routed entirely through WhatsApp because that's where the actual users are. I'm also mid-MBA (Finance) at CIMP Patna, which shows up more than you'd expect in how I think about unit economics for these products.

This README is intentionally deep. If you're a recruiter, scroll to the systems. If you're a fellow builder, scroll to the architecture. If you're just curious, start at the top and enjoy the ride.

<br/>

---

<br/>

<div align="center">

## `01` Live Engineering Snapshot

<sub>Real public repository metadata — refreshed 08 Aug 2026</sub>

<br/>

| Signal | Value | Signal | Value |
|:---:|:---:|:---:|:---:|
| **Public repositories** | 18 | **Top starred project** | financeCalculator-Ind-v6.0- (11⭐) |
| **Active flagship repos** | 5 | **Core stack mix** | Static web systems + TypeScript/Next.js + AI orchestration |
| **Primary DSA language** | C++ | **Agency clients (verified)** | 6–8 real, named businesses |

</div>

<br/>

<div align="center">
<img src="./assets/repo-signals.svg" alt="Repository star signal chart" width="100%" />
</div>

<sub>**Reading this honestly:** most of these repos are early-stage or built private-first before going public, so star count isn't the real signal here — shipped complexity is. financeCalculator crossing double-digit stars organically, with 9 forks and 21 open issues, tells you people are actually using it and filing real feedback. That's worth more than a padded follower count.</sub>

<br/>

---

<br/>

<div align="center">

## `02` Skill Density Map

<sub>Self-assessed against actual shipped repos, not vibes</sub>

<br/>

<img src="./assets/skill-radar.svg" alt="Skill radar chart" width="55%" />

</div>

<br/>

---

<br/>

<div align="center">

## `03` Technology Ecosystem — The Full Stack

<sub>Every layer below is pulled from real, audited codebases — not an aspirational tech-radar</sub>

<br/>

<img src="./assets/tech-stack.svg" alt="Technology ecosystem layered diagram" width="100%" />

</div>

<br/>

<details>
<summary><b>▸ Why this stack, and not something trendier</b></summary>
<br/>

The honest answer: **static-first, edge-first, and Firebase-heavy** because I'm a solo founder shipping across three simultaneous products (ToolsLab, BharatOS, DigiRise) without a team. Cloudflare Workers give me backend logic without server management. Firebase gives me auth + database + hosting without DevOps overhead. Vanilla JS SPAs mean zero build-step fragility on India's inconsistent mobile networks — a real constraint, not a stylistic choice, since a meaningful share of my end users are on Snapdragon 4xx/6xx-class Android devices on 4G.

The move to typed stacks (Next.js + TypeScript + Prisma in EliteHub, App Router in Bharat-OS) happens exactly when product complexity crosses a threshold that vanilla JS can't hold safely anymore — multi-tier memberships, multi-agent orchestration, things where a type error in production is expensive.

</details>

<br/>

---

<br/>

<div align="center">

## `04` Multi-Product System Flow

<sub>How a single request actually moves through the live portfolio</sub>

<br/>

<img src="./assets/architecture-flow.svg" alt="Multi-product architecture flow diagram" width="100%" />

</div>

<br/>

---

<br/>

<div align="center">

## `05` Portfolio Maturity Dashboard

<sub>Where each flagship project actually stands — including the parts that aren't done yet</sub>

<br/>

<img src="./assets/project-dashboard.svg" alt="Portfolio maturity dashboard" width="100%" />

</div>

<br/>

---

<br/>

## `06` Deep Dive — Flagship Projects

<br/>

### 🧠 ToolsLab / Toolshub — AI Chat SaaS

<table>
<tr>
<td width="60%">

**What it is:** A multi-model AI chat platform with real streaming responses, real image generation (SDXL), voice input, offline PWA support, and snapshot-based conversation branching. Billed via Razorpay across four tiers.

**Architecture:** Vanilla JS SPA → Cloudflare Worker backend → Firebase (Auth + Firestore). LLM traffic routes through **OmniRoute**, a self-hosted proxy, with Cloudflare Workers AI as an always-on L3 fallback layer. RAG is powered by Cloudflare Vectorize with server-side UID filtering — so retrieval is genuinely scoped per user, not just filtered client-side.

**What's confirmed solid** (from a full 383-file codebase audit):
- Razorpay HMAC signature verification — real, not stubbed
- Firestore security rules correctly block client writes to subscription/plan/credits fields
- DOMPurify sanitization on all markdown rendering
- Real streaming, real SDXL image generation, working offline PWA

**What's honestly still broken** (also from that same audit — I'd rather flag it here than have a user find it first):
- Agent Mode's execution loop is imported but never actually called in the live send path
- Deep Research has zero backend implementation despite being marketed as a paid Max-tier feature
- The Settings → API Keys screen writes data that's never read back by the app — currently misleading to users

**Models:** Digilite, DigiPro, Maya, Maya Pro · **Domain:** toolslab.studio · **Pricing:** Free / Starter / Pro ₹349 / Max ₹999

</td>
<td width="40%">

```
┌─────────────────────────┐
│   VANILLA JS SPA (UI)   │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  Cloudflare Worker (API) │
└──┬──────────────────┬────┘
   │                  │
┌──▼──────┐    ┌──────▼──────┐
│ Firebase│    │  OmniRoute  │
│ Auth/DB │    │  LLM Proxy  │
└─────────┘    └──────┬──────┘
                       │
              ┌────────▼────────┐
              │ CF Workers AI   │
              │ (L3 fallback)   │
              └─────────────────┘
```

**Known infra risk:** OmniRoute currently depends on a personal machine staying online via a `trycloudflare.com` tunnel. That's the single biggest pre-launch fragility point.

</td>
</tr>
</table>

[**→ github.com/S2zxx0zxx/Toolshub**](https://github.com/S2zxx0zxx/Toolshub)

<br/>

### 🇮🇳 BharatOS — India's AI Life Operating System

<table>
<tr>
<td width="60%">

**What it is:** An 11-module multi-agent system covering Health, Legal, Agriculture, Education, Finance, Construction, Logistics, Food Business, Cybersecurity, Creator Economy, and Government Schemes — accessed primarily through **WhatsApp Business API**, because that's where non-urban Indian users actually are, not in a native app they'd need to download.

**Orchestration:** A Master Router Agent identifies the domain of a query, then fans it out to a parallel agent swarm built on **Ruflo** (github.com/ruvnet/ruflo), using:
- `ruflo-agentdb` — HNSW vector search, 384-dim ONNX embeddings, 32× memory reduction
- `ruflo-goals` — GOAP-based A* planning for multi-step task execution
- `ruflo-aidefence` — detects and redacts 14 categories of PII, AES-256-GCM encrypted
- `ruflo-federation` — mTLS + ed25519 signed inter-agent trust, 5-tier

**Cost architecture:** a 3-tier model router — Tier 1 deterministic rules (~1ms, $0), Tier 2 Haiku-class (~500ms, ~$0.0002/call), Tier 3 Sonnet/Opus for genuinely hard reasoning (2–5s). This is the difference between a WhatsApp bot that's economically viable at India-scale pricing and one that isn't.

**Monetization ladder:** Free (10 queries/day) → Pro ₹199/mo → Business ₹999/mo → Enterprise → Marketplace → eventual government white-label.

**Where it stands:** Phase 1 MVP — NyayBot (legal) + JanSeva (govt schemes) + Swasthya (health) — targeting real users in Bihar, UP, and Rajasthan. A working Next.js prototype is live at `bharat-os-opal.vercel.app`.

</td>
<td width="40%">

```
     User (WhatsApp)
          │
   ┌──────▼───────┐
   │ Master Router │
   │     Agent     │
   └──────┬───────┘
          │
   ┌──────┴───────────┐
   │  Parallel Agent   │
   │  Swarm (Ruflo)    │
   └──┬────┬────┬──────┘
      │    │    │
   Health Legal Finance
   Agri  Edu  ...8 more
          │
   ┌──────▼───────┐
   │ 3-Tier Model  │
   │   Routing     │
   └───────────────┘
```

**Build environment:** `C:\Bharatos\`, Antigravity IDE, Node v24.10.0

</td>
</tr>
</table>

[**→ github.com/S2zxx0zxx/Bharat-OS**](https://github.com/S2zxx0zxx/Bharat-OS)

<br/>

### 💎 EliteHub — Creator Monetization Platform

<table>
<tr>
<td width="60%">

**What it is:** An India-first creator monetization SaaS — public creator profiles with a 3-tab layout (Membership / Feed / About), a multi-tier `MembershipTier` database model, an Explore page built with Next.js intercepting routes, and a full admin panel. Glossy-white light theme with Fraunces serif type and coral/navy accents — deliberately not another dark-mode SaaS clone.

**Stack:** Next.js 14 (App Router) · Prisma · Clerk v5 · Cloudflare R2 · Razorpay

**Real bugs found and fixed during build:**
- Clerk v5's `auth()` is async — a missing `await` was silently breaking auth checks
- An N+1 query explosion inside `ranking.ts` was quietly murdering performance at scale
- Inverted CSS design tokens were flipping light/dark contrast in specific components

Dark mode was fully removed after testing — the light glossy theme tested better for the creator-economy audience this targets. 10 Indian demo creators are seeded for realistic testing.

</td>
<td width="40%">

```
┌──────────────────────┐
│   Next.js 14 (App    │
│   Router) + Prisma    │
└──────────┬────────────┘
           │
   ┌───────┴────────┐
   │  Clerk v5 Auth  │
   └───────┬────────┘
           │
┌──────────▼───────────┐
│  Membership Tiers DB  │
│  + Explore (interc.   │
│  routes) + Admin      │
└──────────┬────────────┘
           │
   ┌───────▼────────┐
   │  R2 + Razorpay  │
   └─────────────────┘
```

**Location:** `C:\elitehub` — kept fully separate from DigiRise/ToolsLab.

</td>
</tr>
</table>

[**→ github.com/S2zxx0zxx/elitehub**](https://github.com/S2zxx0zxx/elitehub)

<br/>

### 💰 financeCalculator-Ind-v6.0- — The Quiet Star of the Portfolio

<table>
<tr>
<td width="60%">

**What it is:** A zero-dependency, static-first finance utility platform — EMI, SIP, tax, and GST-class calculators — wrapped in a PWA shell, with a blog and podcast content layer attached for organic reach. No framework, no build step, no backend. Just fast, correct math shipped as a static site.

**Why it's the strongest signal in the portfolio:** 11 stars, 9 forks, and 21 open issues isn't a huge number in absolute terms — but for a personal finance utility with zero paid marketing, it means real people are using it, forking it, and caring enough to file issues. That's a far more honest adoption signal than a polished demo with zero users behind it.

</td>
<td width="40%">

```
┌────────────────────┐
│  Static HTML/CSS/JS │
│   (zero build step) │
└──────────┬───────────┘
           │
   ┌───────▼────────┐
   │  Calculator      │
   │  Engines (EMI,   │
   │  SIP, Tax, GST)  │
   └───────┬────────┘
           │
   ┌───────▼────────┐
   │  PWA + Blog/    │
   │  Podcast layer  │
   └─────────────────┘
```

</td>
</tr>
</table>

[**→ github.com/S2zxx0zxx/financeCalculator-Ind-v6.0-**](https://github.com/S2zxx0zxx/financeCalculator-Ind-v6.0-)

<br/>

### 🎮 GameMartStudios — No-Backend Commerce, On Purpose

A gaming commerce funnel built entirely as static web + WhatsApp checkout flow — deliberately **no backend at all**. 6 stars on a project with this little infrastructure is proof of a real pattern I keep coming back to: for a specific class of small-scale commerce, a no-backend static funnel with a WhatsApp handoff converts just fine, and skipping the backend means skipping an entire category of things that can break.

[**→ github.com/S2zxx0zxx/GameMartStudios**](https://github.com/S2zxx0zxx/GameMartStudios)

<br/>

---

<br/>

<div align="center">

## `07` DSA & Competitive Programming

<sub>Consistent practice, not a one-time interview cram</sub>

<br/>

<img src="./assets/dsa-matrix.svg" alt="DSA pattern coverage matrix" width="100%" />

</div>

<br/>

---

<br/>

<div align="center">

## `08` DigiRise India — The Agency Behind the Products

</div>

DigiRise India is a full-service digital marketing agency I founded, serving real clients across **India, UAE, and the UK**. It funds and grounds the AI-product work — client delivery pays the bills, and the operational patterns I learn running client campaigns (what actually converts, what actually gets read, what a real SMB owner will and won't pay for) feed directly back into how I design ToolsLab and BharatOS.

<table>
<tr><th>Real, verified clients</th><th>What DigiRise actually delivers</th></tr>
<tr><td>

- LAL Sweets
- Kirtilals
- TradeScribe
- FarmFres
- Murzban
- The Liquid Lounge
- Vidya Mandir Classes
- PTJM SVM

</td><td>

- Full website builds (custom HTML/CSS/JS, no templated builders)
- WhatsApp-first conversion funnels
- SEO / AEO / GEO-optimized content and blog infrastructure
- Partner OS with commission tracking and referral management
- Lead scoring and outreach systems for B2B/SMB acquisition

</td></tr>
</table>

I run a strict **reality-sweep policy** on every DigiRise property — no fabricated case studies, no inflated ratings, no fake "ROI Guarantee" language. Earlier drafts of the site had exactly that kind of padding, and I stripped it out down to the real six-to-eight client roster and a single honest guarantee: **"100% Deliverables Guarantee."** It's less flashy than "3x ROI or your money back," but it's true, and that matters more to me than the extra conversion percentage the fake version might have bought.

**Contact:** digiriseindia@gmail.com · +91 74391 33880 · [@digiriseindia](https://instagram.com/digiriseindia)

<br/>

---

<br/>

<div align="center">

## `09` Engineering Principles

</div>

<table>
<tr>
<td width="50%" valign="top">

**🏗️ Build fast with static foundations**
Ship on vanilla web tech first. Reach for a framework only when the product's actual complexity — not ego — demands it.

**🔒 Security is not optional polish**
HMAC verification, Firestore rules, PII redaction, and auth checks get built before the feature that needs them, not after.

**📊 Data honesty over marketing gloss**
If a feature isn't built, the README/marketing copy doesn't claim it exists. Fabricated metrics get found and removed, every time, across every property I run.

</td>
<td width="50%" valign="top">

**🇮🇳 Design for the real constraint set**
Snapdragon 4xx/6xx Android devices, 4G networks, WhatsApp as the default interface — not flagship-device assumptions.

**🧩 Typed architecture when complexity earns it**
Vanilla JS SPAs for lean products, TypeScript + Prisma when the data model gets genuinely complex enough to need it.

**📝 Docs as a system-level asset**
READMEs, `.ai-brain.md` ledgers, and audit trails aren't afterthoughts — they're how a solo founder keeps three products moving in parallel without losing the plot.

</td>
</tr>
</table>

<br/>

---

<br/>

<div align="center">

## `10` Connect

<br/>

<a href="https://github.com/S2zxx0zxx"><img src="https://img.shields.io/badge/GitHub-S2zxx0zxx-181717?style=for-the-badge&logo=github&logoColor=white&labelColor=0d1117" /></a>
<a href="https://x.com/satzzxzxx"><img src="https://img.shields.io/badge/X-@satzzxzxx-000000?style=for-the-badge&logo=x&logoColor=white&labelColor=0d1117" /></a>
<a href="https://instagram.com/__.satzzxzxx"><img src="https://img.shields.io/badge/Instagram-@__.satzzxzxx-E4405F?style=for-the-badge&logo=instagram&logoColor=white&labelColor=0d1117" /></a>
<a href="https://instagram.com/digiriseindia"><img src="https://img.shields.io/badge/DigiRise-@digiriseindia-E4405F?style=for-the-badge&logo=instagram&logoColor=white&labelColor=0d1117" /></a>

<br/><br/>

<img src="https://github-readme-stats.vercel.app/api?username=S2zxx0zxx&show_icons=true&theme=dark&hide_border=true&bg_color=0d1117&title_color=a78bfa&icon_color=38bdf8&text_color=cbd5e1" width="49%" />
<img src="https://github-readme-streak-stats.herokuapp.com/?user=S2zxx0zxx&theme=dark&hide_border=true&background=0d1117&stroke=0d1117&ring=a78bfa&fire=f97316&currStreakLabel=38bdf8" width="49%" />

<br/><br/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=S2zxx0zxx&theme=react-dark&hide_border=true&bg_color=0d1117&color=38bdf8&line=a78bfa&point=f97316" width="100%" />

<br/><br/>

<sub>Built with real data, honest gaps included. Last structural refresh: 08 Aug 2026.</sub>

</div>
