# SHL Assessment Recommendation System

## Overview

This system provides an intelligent recommendation engine for SHL assessments based on natural language queries or job descriptions. The solution leverages Retrieval-Augmented Generation (RAG) techniques, combining semantic search with intent classification to deliver relevant assessment recommendations that balance hard and soft skills as required by the query.

## Problem Statement

Hiring managers and recruiters often struggle to find appropriate assessments for specific roles. Traditional keyword-based search systems are time-consuming and inefficient. This system addresses this challenge by understanding the intent behind natural language queries and recommending the most relevant SHL assessments from a catalog of 376 individual test solutions.

## System Architecture

The recommendation system follows a three-stage pipeline:

1. **Intent Classification**: Analyzes user queries using LLM-based intent extraction to identify categories, explicit keywords, behavioral requirements, duration constraints, and entry-level indicators.

2. **Multi-Stage Retrieval**: Implements hybrid retrieval combining:
   - Primary vector search using FAISS for semantic similarity
   - Dynamic query expansion based on detected intents
   - Context-aware candidate pool generation

3. **Intelligent Reranking**: Applies domain-specific scoring and interleaving logic to ensure balanced recommendations across different assessment types (hard skills vs soft skills) when queries span multiple domains.

## Key Features

- Semantic search using sentence transformers and FAISS
- LLM-powered intent classification via LangChain and Ollama
- Dynamic query expansion for improved recall
- Domain-aware scoring for category relevance
- Balanced recommendation algorithm for multi-domain queries
- Support for duration and entry-level constraints
- RESTful API with FastAPI

## Technology Stack

- **Framework**: FastAPI, Uvicorn
- **ML/AI**: 
  - Sentence Transformers (all-MiniLM-L6-v2)
  - FAISS (vector similarity search)
  - LangChain (LLM orchestration)
  - Ollama (local LLM inference)
- **Data Processing**: Pandas, BeautifulSoup, lxml
- **Data Validation**: Pydantic

## Project Structure

```
shl/
├── app.py                  # FastAPI application and API endpoints
├── requirements.txt        # Python dependencies
├── scraper/
│   └── scrape_catalog.py  # Web scraper for SHL catalog
├── pipeline/
│   └── catalog.py         # Catalog enrichment pipeline
├── rag/
│   ├── indexing.py        # FAISS index construction
│   ├── retriever.py       # Vector retrieval implementation
│   └── utils/
│       ├── models.py      # Pydantic data models
│       ├── intent.py      # Intent classification
│       ├── keywords.py    # Keyword normalization
│       └── rerank.py      # Reranking and scoring logic
├── evaluation/
│   └── recallcsv.py       # Evaluation metrics computation
├── utils/
│   └── gen.py            # Batch prediction generator
└── data/
    ├── raw/              # Raw scraped data
    ├── processed/        # Processed catalog and indices
    └── train/            # Training and validation datasets
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Ollama installed and running locally with llama3 model

### Ollama Setup

This system requires Ollama for LLM-based intent classification. Follow these steps to set up Ollama:

1. **Install Ollama**:
   - Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your operating system
   - Follow the installation instructions for your platform

2. **Start Ollama Service**:
   - Ollama runs as a background service after installation
   - Verify it's running by opening a terminal and running:
   ```bash
   ollama --version
   ```

3. **Download llama3 Model**:
   ```bash
   ollama pull llama3
   ```
   This may take several minutes depending on your internet connection as the model is approximately 4.7GB.

4. **Verify Model Installation**:
   ```bash
   ollama list
   ```
   You should see `llama3` in the list of available models.

5. **Test Ollama** (optional):
   ```bash
   ollama run llama3
   ```
   Type a test message and press Enter. Type `/bye` to exit.

**Important Notes:**
- Ollama must be running when you start the API server
- The system uses Ollama's REST API, which is available at `http://localhost:11434` by default
- If you need to use a different port, you can set the `OLLAMA_BASE_URL` environment variable
- The llama3 model will be loaded on first use, which may take a few seconds

### Setup Instructions

1. **Clone the repository**:
```bash
git clone <repository-url>
cd shl
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify Ollama is running**:
   Ensure Ollama is installed and the llama3 model is available (see Ollama Setup section above).

## Data Pipeline

### Step 1: Scrape SHL Catalog

Extract assessment metadata from the SHL website:

```bash
python scraper/scrape_catalog.py
```

This generates `data/raw/catalog_metadata.json` containing assessment URLs, names, test types, and support features.

### Step 2: Enrich Catalog Data

Fetch detailed descriptions and duration information:

```bash
python pipeline/catalog.py
```

This produces `data/processed/catalog.json` with complete assessment information.

### Step 3: Build Vector Index

Create FAISS index for semantic search:

```bash
python rag/indexing.py
```

This generates:
- `data/processed/faiss.index` (vector index)
- `data/processed/faiss_meta.json` (assessment metadata)

## API Usage

### Starting the Server

**Prerequisites**: Ensure Ollama is running with the llama3 model available (see Installation section).

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Troubleshooting**: If you encounter errors related to Ollama:
- Verify Ollama is running: `ollama list`
- Ensure llama3 model is installed: `ollama pull llama3`
- Check Ollama service is accessible at `http://localhost:11434`

### Endpoints

#### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

#### Assessment Recommendation

```http
POST /recommend
Content-Type: application/json

{
  "query": "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes.",
  "top_k": 10
}
```

Response:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "name": "Java 8 (New)",
      "adaptive_support": "No",
      "description": "Multi-choice test that measures the knowledge of Java programming...",
      "duration": 25,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    },
    {
      "url": "https://www.shl.com/products/product-catalog/view/interpersonal-communications/",
      "name": "Interpersonal Communications",
      "adaptive_support": "No",
      "description": "Assesses communication skills in workplace settings...",
      "duration": 20,
      "remote_support": "Yes",
      "test_type": ["Personality & Behaviour"]
    }
  ]
}
```

### Batch Processing

Generate predictions for multiple queries:

```bash
python utils/gen.py
```

This reads from `data/train/val.csv` and writes results to `data/train/result.csv`.

## Evaluation

### Metrics

The system is evaluated using Mean Recall@10, which measures the proportion of relevant assessments retrieved in the top 10 recommendations, averaged across all test queries.

### Performance Results

The system achieves **Mean Recall@10: 0.3700 (37.0%)** on the validation set consisting of 10 unique queries.

**Per-Query Performance:**
- Best performing query: 0.800 (Java developers with collaboration skills)
- Lowest performing query: 0.000 (ICICI Bank Assistant Admin)
- Average: 0.370 across all queries

**Observation:** The system demonstrates strong performance on queries requiring both technical and behavioral assessments (e.g., Java developers with collaboration needs), achieving 80% recall. Performance varies based on query specificity and domain complexity, with specialized or highly constrained queries showing lower recall.

### Running Evaluation

```bash
python evaluation/recallcsv.py
```

This computes Mean Recall@10 by comparing predictions in `data/train/result.csv` against ground truth in `data/train/val.csv`.

## Recommendation Algorithm

### Intent Classification

The system extracts structured intent from queries:
- **Categories**: Domain classifications (tech, sales, admin, leadership, marketing, finance, hr, operations)
- **Explicit Keywords**: Specific skills or technologies mentioned
- **Behavioral Flag**: Indicates need for soft skills assessments
- **Duration Constraint**: Maximum acceptable assessment duration
- **Entry Level Flag**: Indicates entry-level position requirements

### Retrieval Strategy

1. **Primary Retrieval**: Vector search retrieves 100 candidates using cosine similarity
2. **Query Expansion**: Additional queries generated based on detected categories
3. **Deduplication**: Removes duplicate assessments from expanded candidate pool

### Reranking Logic

Candidates are scored using a multi-factor approach:

- **Keyword Matching**: Exact matches in assessment names (30 points) or descriptions (10 points)
- **Category Relevance**: Domain-specific scoring for tech, sales, leadership, admin, marketing, finance, and HR categories
- **Test Type Alignment**: Boosts assessments matching expected test types (K, S, A for hard skills; P, B, C for soft skills)
- **Behavioral Boost**: Increases scores for personality and competency tests when behavioral skills are required
- **Entry Level Boost**: Prioritizes entry-level assessments when applicable
- **Duration Compliance**: Rewards assessments within duration constraints, penalizes those exceeding limits
- **Negative Filtering**: Reduces scores for irrelevant categories (e.g., customer service tests for developer roles)

### Balancing Algorithm

When queries require both hard and soft skills, the system interleaves recommendations:
- Hard skills assessments (Knowledge, Simulation, Ability types)
- Soft skills assessments (Personality, Biodata, Competency types)

This ensures a balanced representation when queries span multiple domains, as specified in the requirements.

## Test Type Mapping

The system maps SHL test type codes to full names:

- A: Ability & Aptitude
- B: Biodata & Situational Judgement
- C: Competencies
- D: Development & 360
- E: Assessment Exercises
- K: Knowledge & Skills
- P: Personality & Behaviour
- S: Simulations

## Performance Optimization

### Initial Approach

The initial implementation used basic vector search with minimal reranking, achieving limited recall on complex queries requiring domain-specific knowledge.

### Improvements

1. **Intent-Based Query Expansion**: Expanded queries based on detected categories improved recall for specialized roles (e.g., leadership, sales)

2. **Multi-Stage Retrieval**: Increased primary retrieval pool from 20 to 100 candidates, then expanded with category-specific queries to capture domain-relevant assessments

3. **Enhanced Scoring**: Implemented category-aware scoring that understands domain-specific relevance patterns (e.g., OPQ tests for leadership roles, Verify tests for aptitude assessments)

4. **Keyword Normalization**: Added abbreviation expansion (e.g., "js" → "javascript", "ml" → "machine learning") to improve keyword matching

5. **Balanced Interleaving**: Implemented interleaving algorithm to ensure queries requiring both technical and behavioral assessments receive balanced recommendations

6. **Duration Constraint Handling**: Softened penalty thresholds and added tolerance windows to better handle duration constraints while maintaining relevance

These optimizations improved Mean Recall@10 from initial baseline to current performance levels while maintaining recommendation quality and balance.

## Data Statistics

- **Total Assessments**: 376 individual test solutions (catalog contains all available individual assessments from SHL website)
- **Catalog Coverage**: All assessments include name, URL, description, duration, remote support, adaptive support, and test types
- **Training Queries**: 10 labeled queries for validation and iteration
- **Test Queries**: 9 unlabeled queries for final evaluation

## Configuration

Key parameters can be adjusted in the code:

- `retrieval_k` (app.py): Primary retrieval pool size (default: 100)
- `rerank_top_k` (rag/utils/rerank.py): Final recommendation count (default: 5-10)
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- LLM model: `llama3` (via Ollama)

## Limitations and Future Enhancements

- LLM dependency on local Ollama instance - requires Ollama to be installed and running locally (consider cloud-based alternatives for production deployment)
- Static keyword normalization mappings (could benefit from learned embeddings)
- Fixed scoring weights (could be optimized through hyperparameter tuning)
- No caching layer for frequent queries
- Limited evaluation on edge cases and domain-specific scenarios

Potential improvements:
- Fine-tuned embedding models on assessment domain data
- Learning-to-rank models for reranking
- Multi-query retrieval strategies
- Real-time catalog updates and synchronization
- A/B testing framework for recommendation strategies

## License

This project is developed as part of a take-home assessment. Please refer to the assignment guidelines for usage restrictions.

## Contact

For questions or issues, please refer to the repository documentation or contact the development team.
