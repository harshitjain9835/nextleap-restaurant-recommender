# Project Context: AI-Powered Restaurant Recommendation System

## Overview

Build an **AI-powered restaurant recommendation service** inspired by **Zomato**. The system combines **structured restaurant data** with a **Large Language Model (LLM)** to deliver personalized, human-like suggestions based on user preferences.

---

## Primary Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM to generate personalized, natural-language recommendations
4. Displays clear, useful results to the user

---

## Data Source

| Item | Detail |
|------|--------|
| **Dataset** | Zomato restaurant data on Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related attributes |

### Data Ingestion Responsibilities

- Load and preprocess the dataset from Hugging Face
- Extract and normalize fields needed for filtering and display

---

## User Input

Collect the following preferences from the user:

| Preference | Examples / Notes |
|------------|------------------|
| **Location** | Delhi, Bangalore, etc. |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese, etc. |
| **Minimum rating** | Numeric or threshold filter |
| **Additional preferences** | family-friendly, quick service, etc. |

---

## System Workflow

### 1. Data Ingestion

- Load the Zomato dataset from Hugging Face
- Preprocess and extract: name, location, cuisine, cost, rating, etc.

### 2. User Input

- Gather preferences listed above via the application UI or input layer

### 3. Integration Layer

- Filter restaurant data according to user preferences
- Prepare a structured subset of candidates for the LLM
- Design a prompt that enables the LLM to reason over and rank options

### 4. Recommendation Engine (LLM)

The LLM should:

- **Rank** restaurants by fit to user preferences
- **Explain** why each recommendation matches
- **Optionally** summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format with:

| Field | Description |
|-------|-------------|
| Restaurant Name | From dataset |
| Cuisine | From dataset |
| Rating | From dataset |
| Estimated Cost | From dataset |
| AI-generated explanation | LLM-produced rationale for the match |

---

## Architecture Summary

```
[Hugging Face Dataset] → [Preprocess / Filter] → [Structured candidates]
                                                        ↓
[User preferences] ──────────────────────────→ [LLM Prompt + Rank/Explain]
                                                        ↓
                                              [Formatted recommendations]
```

---

## Key Design Considerations

- **Hybrid approach**: Deterministic filtering on structured data first; LLM for ranking, explanation, and optional summary—not as the sole data source.
- **Prompt design**: Critical for quality; must include filtered restaurant context and user criteria so the model can reason and justify picks.
- **Transparency**: Each recommendation should include an AI-generated “why this fits” explanation.
- **Reference product**: Behavior and UX should feel similar to Zomato-style discovery (location, budget, cuisine, ratings).

---

## Success Criteria

- [ ] Dataset loads and preprocesses correctly from Hugging Face
- [ ] User can specify location, budget, cuisine, minimum rating, and extra preferences
- [ ] Filtering narrows candidates before LLM invocation
- [ ] LLM ranks options and provides per-restaurant explanations
- [ ] UI (or output layer) shows name, cuisine, rating, cost, and explanation clearly

---

## Out of Scope (unless extended later)

This document reflects only what is stated in the problem statement. Implementation choices (framework, LLM provider, deployment, auth, etc.) are left to the build phase unless specified elsewhere.
