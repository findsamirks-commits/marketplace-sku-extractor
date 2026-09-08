# Marketplace SKU Extractor 🚀

An automated AI pipeline designed to ingest unstructured vendor catalogs (PDFs, raw emails, messy Excel sheets), normalize the data into strict tabular formats, and calculate category-specific retail economics. 

Built to accelerate marketplace expansion by eliminating manual data entry and instantly validating supplier cost against required margin thresholds.

## 🛠️ The Architecture

* **Multi-Format Ingestion:** Utilizes LangChain document loaders (`PyPDFLoader`, `UnstructuredEmailLoader`, `UnstructuredExcelLoader`) to route and strip formatting from incoming pitches regardless of how disorganized the source file is.
* **Deterministic LLM Extraction:** Binds Gemini 2.5 Flash to a strict Pydantic model (`SupplierSKU`). Operating at a temperature of `0.0`, the agent behaves as a data entry clerk rather than a conversational bot—extracting only factual attributes (Brand, Pack Size, Origin) without hallucinating missing data.
* **Economic Validation:** Applies custom business logic to calculate the exact Minimum Retail Price required to hit category-specific margin targets (e.g., 40% for Auto Care, 50% for Home Improvement).
* **Batch Processing & Export:** Loops through multiple vendor pitches simultaneously and exports the cleaned, validated data into a structured CSV ready for master catalog ingestion.

## 💻 Tech Stack

* **Language:** Python
* **LLM Engine:** Google Gemini (`gemini-2.5-flash`)
* **Orchestration:** LangChain (`langchain-core`, `langchain-community`)
* **Data Validation:** Pydantic V2 (`model_dump`)
* **Data Export:** Pandas

## 🚀 Usage

1. **Environment Setup:** Store your Google API key in your terminal session or a hidden `.env` file to ensure security. 
2. **Execution:** Run `python catalog_agent.py` to trigger the batch processing.
3. **Output:** The script autonomously parses the unstructured pitches and generates `marketplace_new_skus.csv` containing the structured database.