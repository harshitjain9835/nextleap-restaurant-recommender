# AI-Powered Restaurant Recommendation System

Zomato-inspired restaurant recommendations using structured data from Hugging Face and an LLM for ranking and explanations.

## Documentation

| File | Description |
|------|-------------|
| [context.md](./context.md) | Product context |
| [architecture.md](./architecture.md) | Technical architecture |
| [implementation-plan.md](./implementation-plan.md) | Phased build plan |
| [edge-cases.md](./edge-cases.md) | Edge case handling |
| [SETUP.md](./SETUP.md) | Windows Python setup |

## Requirements

- Python 3.12+ (use `py` on Windows — see [SETUP.md](./SETUP.md))
- Internet access for first Hugging Face dataset download

## Quick start

```powershell
cd g:\nextleap\projects
.\scripts\setup-python.ps1
copy .env.example .env
```

### Phase 1: Load catalog sample

```powershell
py scripts\load_catalog_sample.py
```

First run downloads ~51k rows from [Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) and writes `data/restaurants.parquet` for faster restarts.

### Phase 3: LLM smoke test (requires `LLM_API_KEY` in `.env`)

```powershell
py scripts\smoke_llm.py -l Bangalore -b medium -c Italian -r 4.0 --limit 8
```

### Phase 5: Run the Streamlit UI

```powershell
streamlit run app/ui/app.py
```

### Phase 2: Probe filters

```powershell
py scripts\probe_filters.py -l Bangalore -b medium -c Italian -r 4.0
py scripts\probe_filters.py -l Delhi -b medium -c Italian
```

### Run tests

```powershell
py -m pytest
```

Integration test (slow, hits Hugging Face):

```powershell
py -m pytest -m integration
```

## Project layout

```
app/
  config.py          # Settings (HF_DATASET_ID, budget thresholds, …)
  models.py          # Pydantic domain models
  data/
    loader.py        # HF load + parquet cache
    normalize.py     # Row → Restaurant mapping
    store.py         # Singleton catalog (load_catalog, get_all)
scripts/
  load_catalog_sample.py
tests/
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_DATASET_ID` | `ManikaSaini/zomato-restaurant-recommendation` | Dataset on HF Hub |
| `BUDGET_LOW_MAX` | `300` | Max INR (for two) for **low** tier |
| `BUDGET_MEDIUM_MAX` | `600` | Max INR for **medium** tier |
| `USE_PARQUET_CACHE` | `true` | Cache normalized data under `data/` |

## Phase status

- [x] Phase 0 — Foundation (models, config, logging)
- [x] Phase 1 — Data ingestion & store
- [x] Phase 2 — Filter engine
- [x] Phase 3 — LLM recommendation engine
- [x] Phase 4 — Orchestration
- [x] Phase 5 — UI
- [ ] Phase 6 — Quality & deployment

## Normalization policies (Phase 1)

- **Missing rating** (`None`, `NEW`, `-`): row **excluded** ([edge-cases.md](./edge-cases.md) DATA-05)
- **City**: parsed from address tail; aliases → `Bangalore`, `Delhi`, etc.
- **Budget tier**: derived from numeric cost vs `BUDGET_LOW_MAX` / `BUDGET_MEDIUM_MAX`
- **IDs**: stable SHA-256 hash from name + city + area + row index
