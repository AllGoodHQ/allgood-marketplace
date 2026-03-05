# allgood-marketplace

A Claude Code plugin marketplace by [AllGood](https://allgoodhq.com/) featuring **Mary**, an AI-powered Marketo Email Performance Analyzer.

[![Download Mary Skill](https://img.shields.io/github/v/release/AllGoodHQ/allgood-marketplace?label=mary-email-performance.skill&style=flat-square)](https://github.com/AllGoodHQ/allgood-marketplace/releases/latest/download/mary-email-performance.skill)

## Install

```shell
/plugin marketplace add <owner>/<repo>
/plugin install allgood-plugin@allgood-marketplace
```

## What It Does

When you upload a Marketo Email Performance Report (XLS, XLSX, or CSV), Mary analyzes the data and produces a branded DOCX report containing:

- **Executive Summary** with an overall program health score
- **Key Findings** organized by severity (action required, caution, healthy)
- **Performance by Campaign Type** with type-specific benchmarks
- **Per-Email Breakdown** with traffic-light status indicators
- **A/B Test Analysis** with winner declarations
- **Benchmark Comparisons** against SaaS industry averages
- **Recommendations & Action Plan** across immediate, 30-day, and 90-day horizons

## How It Works

Mary classifies emails by type (marketing, triggered, onboarding, event follow-up, re-engagement, nurture), applies type-specific SaaS benchmarks, and uses volume-weighted metrics to avoid skewing results. Emails with fewer than 100 sends are excluded from analysis as statistically unreliable.

Key analysis features:
- Campaign series funnel analysis (Email 1 → 2 → 3 drop-off)
- A/B test variant comparison with winner selection
- Data anomaly detection (e.g., CTR > open rate)
- Volume-weighted program-level metrics

## Marketplace Structure

```
.claude-plugin/
  marketplace.json                     # Marketplace catalog
plugins/
  allgood-plugin/
    .claude-plugin/
      plugin.json                      # Plugin manifest
    skills/
      mary-email-performance/
        SKILL.md                       # Skill definition and workflow
        assets/
          mary-logo.png                # Mary branding
          allgood-logo.png             # AllGood branding
        references/
          benchmarks.md                # SaaS email performance benchmarks
          email-types.md               # Email classification rules
          report-writing.md            # DOCX structure and style guide
```

## Usage

After installing, trigger the skill by uploading a Marketo email report and asking Claude to analyze it. Example prompts:

- "Analyze my email report"
- "How are my emails performing?"
- "Build a report from this XLS"
- "Compare nurture vs. event emails"
- "Quick summary of this Marketo data"

## Author

**Mary AllGood** — [LinkedIn](https://www.linkedin.com/in/maryallgood/) | [allgoodhq.com](https://allgoodhq.com/)
