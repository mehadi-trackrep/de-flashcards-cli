# 🃏 de-flashcards-cli

> Data Engineering flashcards in your terminal — static, AI-powered, or from Firestore.

```
  ██████╗ ███████╗    ███████╗██╗      █████╗ ███████╗██╗  ██╗
  ██╔══██╗██╔════╝    ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║
  ██║  ██║█████╗      █████╗  ██║     ███████║███████╗███████║
  ██║  ██║██╔══╝      ██╔══╝  ██║     ██╔══██║╚════██║██╔══██║
  ██████╔╝███████╗    ██║     ███████╗██║  ██║███████║██║  ██║
  ╚═════╝ ╚══════╝    ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Static cards** | 20+ built-in flashcards across 6 topics |
| **AI-generated cards** | Fresh cards via Claude AI on any topic |
| **Firestore** | Pull community-shared cards from Firebase |
| **Topic filter** | Study only what you need |
| **Zero friction** | Just run `de-flashcards-cli` — no setup required for static mode |

---

## 📦 Installation

> This project uses [**uv**](https://docs.astral.sh/uv/) — a fast, modern Python package manager.

### Step 1 — Install uv (once, on your Mac)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via Homebrew:

```bash
brew install uv
```

---

### Option A — Clone & run locally (recommended for development)

```bash
git clone https://github.com/yourusername/de-flashcards-cli.git
cd de-flashcards-cli

# Install all dependencies + create .venv automatically
uv sync

# Run directly
uv run de-flashcards-cli
```

With Firestore support:

```bash
uv sync --extra firestore
uv run de-flashcards-cli --firestore
```

With all extras:

```bash
uv sync --extra all
```

---

### Option B — Install from GitHub (use anywhere, no clone needed)

```bash
uv tool install git+https://github.com/yourusername/de-flashcards-cli.git
```

Then use it globally from any directory:

```bash
de-flashcards-cli
de-flashcards-cli --topic sql
```

With all extras:

```bash
uv tool install "de-flashcards-cli[all] @ git+https://github.com/yourusername/de-flashcards-cli.git"
```

Upgrade later:

```bash
uv tool upgrade de-flashcards-cli
```

---

### Option C — Run without installing (one-liner)

```bash
uvx --from git+https://github.com/yourusername/de-flashcards-cli.git de-flashcards-cli
```

---

## 🚀 Usage

```bash
# Show 1 random flashcard
de-flashcards-cli

# Show 5 random cards
de-flashcards-cli -n 5

# Filter by topic
de-flashcards-cli --topic sql
de-flashcards-cli -t pipeline

# Show ALL cards for a topic
de-flashcards-cli --topic warehouse --all

# List available topics
de-flashcards-cli --list-topics

# Generate a card with Claude AI (any topic!)
de-flashcards-cli --ai
de-flashcards-cli --topic dbt --ai
de-flashcards-cli --topic spark --ai --ai-count 3

# Pull cards from Firestore
de-flashcards-cli --firestore
de-flashcards-cli --topic sql --firestore

# Combine everything!
de-flashcards-cli --topic kafka --ai --firestore -n 5

# Set API keys interactively
de-flashcards-cli config
```

If installed via `uv sync` (Option A), prefix commands with `uv run`:

```bash
uv run de-flashcards-cli --topic sql -n 3
uv run de-flashcards-cli --ai
```

---

## ⚙️ Configuration

Run the interactive setup wizard:

```bash
de-flashcards-cli config
# or
uv run de-flashcards-cli config
```

This saves your keys to `~/.de-flashcards-cli/config.json`. You can also set them as environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export FIRESTORE_PROJECT_ID="my-firebase-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Getting an Anthropic API key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account → API Keys → Create Key
3. Run `de-flashcards-cli config` and paste it in

### Setting up Firestore
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a project → Firestore Database → Start in test mode
3. Project Settings → Service Accounts → Generate new private key
4. Run `de-flashcards-cli config` with the project ID and JSON path

**Firestore card schema** (collection: `flashcards`):
```json
{
  "topic": "sql",
  "question": "What is a window function?",
  "answer": "A function that..."
}
```

---

## 🗂️ Topics (built-in)

| Topic | Cards |
|---|---|
| `sql` | Window functions, JOINs, CTEs, indexes |
| `python` | Generators, pandas, map/filter |
| `pipeline` | ETL vs ELT, Airflow, idempotency |
| `warehouse` | Fact/dim tables, dbt, SCD, partitioning |
| `streaming` | Kafka, batch vs stream, exactly-once |
| `cloud` | BigQuery, S3, data lake vs warehouse |

With `--ai`, you can generate cards on **any** topic: `dbt`, `spark`, `flink`, `databricks`, `dagster`, etc.

---

## 📁 Project Structure

```
de-flashcards-cli/
├── de_flashcards_cli/
│   ├── __init__.py
│   ├── cli.py              # Main CLI (argparse, display)
│   ├── flashcards.py       # Static card data
│   ├── ai_generator.py     # Claude AI card generation
│   ├── firestore_client.py # Firebase Firestore integration
│   └── config.py           # ~/.de-flashcards-cli/config.json manager
├── pyproject.toml          # uv-compatible project config
├── uv.lock                 # Locked dependency versions
└── README.md
```

---

## 🛠️ Development

```bash
# Install with dev tools (pytest, ruff)
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Add a new dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>
```

---

## 🛠️ Adding Your Own Static Cards

Edit `de_flashcards_cli/flashcards.py` and add to the `FLASHCARDS` list:

```python
{
    "topic": "dbt",
    "question": "What is a dbt model?",
    "answer": "A dbt model is a SELECT statement saved as a .sql file. dbt compiles and runs it in your warehouse, materializing it as a table or view."
},
```

---

## 📋 Roadmap

- [ ] Score tracking (correct/incorrect per card)
- [ ] Spaced repetition algorithm
- [ ] `de-flashcards-cli push` — contribute cards to Firestore
- [ ] `--quiz` mode with multiple choice
- [ ] Homebrew formula for one-line Mac install

---

## License

MIT
