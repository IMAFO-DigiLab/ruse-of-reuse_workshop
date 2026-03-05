# Ruse of Reuse: Hackathon Starter Kit

Here you'll find everything you need to get started with the Ruse of Reuse hackathon, including data access, method development, and evaluation tools.

## Content
- [Installation Local Development](#installation-local-development)
- [Installation Google Colab](#installation-google-colab)
- [Downloaded Data Structure](#downloaded-data-structure)
- [Reproducing Ground Truth Construction](#reproducing-ground-truth-construction)
- [Biblical Embedding Collections](#biblical-embedding-collections)
- [Tweaking Your Method](#tweaking-your-method)

## Installation Local Development

#### 1. Installation
* Open your terminal and navigate to the project repository.
* Install the package in editable mode by running:
  ```bash
  python -m pip install -e .
  ```

#### 2. Quick Start Pipeline
Run the following commands in your terminal to initialize the project data.

* **Download Data:** Fetch the initial data bundle required for the project.
  ```bash
  python -m ruse_of_reuse download
  ```
* **Rebuild Task Files (Optional):** Recreate the task files from the raw XML sources.
  ```bash
  python -m ruse_of_reuse preprocess
  ```
* **Build Embeddings (Optional):** Build additional biblical embedding collections using Hugging Face and OpenAI models. For more information see the "Biblical Embedding Collections" section below.
  ```bash
  python -m ruse_of_reuse vectorstore \
    --hf-model bowphs/LaBerta \
    --openai-model text-embedding-3-large
  ```

## Installation Google Colab
#### 1. Import the Notebook
* Go to the [repository link] and download the `notebooks/method_evaluation.ipynb` file to your computer.
* Open [Google Colab](https://colab.research.google.com/).
* From the welcome dialog, select the **Upload** tab.
* Drag and drop the `method_evaluation.ipynb` file into the upload area.

#### 2. Enable GPU Acceleration (CUDA)
To speed up model execution, you should enable a GPU instance:
  * In the top menu bar, click on Runtime.
  * Select Change runtime type.
  * Under the Hardware accelerator dropdown, select a GPU (e.g., T4 GPU).
  * Click Save to apply the changes.

#### 3. Configure Environment Secrets
The notebook requires access tokens to download the necessary models and datasets.
* Click the **🔑 Secrets** icon in the left sidebar of your Colab notebook.
* Click **Add new secret** to create the following two credentials:
  * **`HF_TOKEN`**: Your Hugging Face access token. [Guide on creating one here](https://huggingface.co/docs/hub/en/security-tokens).
  * **`GITHUB_TOKEN`**: Your GitHub personal access token. [Guide on creating one here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
* Make sure to toggle the **Notebook access** switch on for both secrets so the code can read them.

#### 4. Initialize and Run
* Locate the initialization cell (marked with the **▶️ emoji** for Data Environment Preparation) and click its play button to run it. This will authenticate your session and download all required dependencies.
* Once the setup is complete, navigate to the top menu and select **Runtime > Run all** to execute the rest of the notebook.
* Verify that all cells execute successfully. Once confirmed, you are ready to start tweaking the code!

## Downloaded Data Structure
After `python -m ruse_of_reuse download`, data is organized under `data/`:

```text
data/
  raw/                  # Source XML + mapping files + bible.tsv
  task/                 # Competition-ready dataset
    problems/*.txt      # Plain texts to solve
    solutions/*.json    # Ground truth spans + resolved biblical references
    preprocess_report.json
    validation_preview.tsv
    validation_preview.html
  vectorstores/
    chroma/             # ChromaDB with biblical verse embeddings
      chroma.sqlite3
      collection2model.json / biblical_collection_mapping.json
```

`data/task` is the main folder for method development and evaluation.

## Reproducing Ground Truth Construction
`python -m ruse_of_reuse preprocess` creates `data/preprocessed/` from `data/raw/`.

- `data/preprocessed/problems` and `data/preprocessed/solutions` mirror the task format.
- Use `validation_preview.html` for quick manual checks of extracted spans.

## Biblical Embedding Collections
Precomputed collections are provided in `data/vectorstores/chroma`.

To add or rebuild collections:
```bash
python -m ruse_of_reuse vectorstore \
  --hf-model bowphs/LaBerta \
  --hf-model comma-project/modernbert-sentembeddings \
  --openai-model text-embedding-3-large \
  ç
```

Collection names include provider/model information, and model-to-collection mapping is saved to:
- `data/vectorstores/chroma/collection2model.json` or
- `data/vectorstores/chroma/biblical_collection_mapping.json`

## Tweaking Your Method
All tunable parameters are in the final two cells of `notebooks/method_evaluation.ipynb`.

### 1. Model / Provider Selection (`build_embedding_method_context`)

| Parameter | Options | Effect |
|-----------|---------|--------|
| `provider` | `"hf"`, `"openai"` | Embedding backend |
| `model_name` | e.g. `"bowphs/LaBerta"`, `"text-embedding-3-large"` | Must match a precomputed Chroma collection |

Available precomputed collections are listed in `data/vectorstores/chroma/biblical_collection_mapping.json`.

### 2. Chunking & Retrieval (`participant_method` → `simple_embedding_method`)

| Parameter | Default | Effect |
|-----------|---------|--------|
| `mode` | `"sentence"` | How problem text is split: `"sentence"`, `"sentence_window"`, or `"char"` |
| `sentences_per_chunk` | `2` | *(sentence_window only)* sentences per sliding window |
| `sentence_stride` | `1` | *(sentence_window only)* step between windows — lower = more overlap |
| `char_chunk_size` | `500` | *(char only)* characters per chunk |
| `char_chunk_overlap` | `100` | *(char only)* overlap between char chunks |
| `min_chunk_chars` | `30` | Chunks shorter than this are dropped |
| `top_k` | `5` | Bible verses retrieved per chunk |
| `similarity_threshold` | `0.825` | Minimum cosine similarity to accept a verse — **most impactful parameter** |

**Suggested tuning order:**
1. `similarity_threshold` — lower it to improve recall, raise it for precision
2. `top_k` — more candidates per chunk increases recall at the cost of precision
3. `mode` — `"sentence_window"` often outperforms single sentences for longer allusions
4. Model — swap to a multilingual or domain-specific model if the language warrants it

### 3. Fast Iteration Tip

Use `max_problems=5` in `run_method_on_dataset` while tuning, then remove the limit for final scoring:

```python
predictions = run_method_on_dataset(
    participant_method,
    problems,
    model_context,
    max_problems=5,   # remove this line for full evaluation
    show_progress=True,
)
```