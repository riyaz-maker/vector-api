# Vector API

 [Watch the Demonstration Video](https://www.loom.com/share/990ff76539a646c392b114fa87ed7d9a?sid=175b8134-b054-4437-b8d6-e0834e8ca1ee)

 [Watch the Video on Design Choices](https://www.loom.com/share/19fbfe8575b84868af43997dc3d73a17?sid=6b4e3307-8da1-4402-a72c-e164fd24b046)

This README explains what this project does, the architectural choices, the indexing algorithms implemented, their complexity and trade-offs, and how to run the system locally (including a one-shot init that populates a demo database).

---

## TL;DR (one-command happy path)

Run everything (build image, seed demo data, and start the API):

```bash
docker compose up --build
```

When that finishes the API will be available at: http://localhost:8000 and the interactive docs at http://localhost:8000/docs

If you prefer to run the init separately (populate & verify) and then start the web service:

```bash
docker compose run --rm init
docker compose up web
```

The `init` service runs `populate_db.py` and `verify_data.py` once and writes the database and index files into the project `./data/` folder and `./vector_db.sqlite` file on the host. Those files are persisted as host-mounted volumes so restarting the container will resume from the last checkpoint.

---

## Problem statement

This project is a small, self-contained vector search API. It stores Libraries that can contain Documents, which in turn contain Chunks. Each Chunk has text and an embedding vector. The service exposes CRUD endpoints and supports indexing/searching those vectors.

The primary engineering goals were:
- Demonstrate simple, testable vector indexing implementations (no external indexing libraries required).
- Provide a persistence and restart behavior so the service can be restarted and continue serving from the last checkpoint. (extra)

---

## Architecture

- FastAPI application serves the REST API (`app/main.py`).
- Pydantic models define the data shapes (`app/models/models.py`).
- Repositories encapsulate direct DB access (SQLite) (`app/repositories/*`).
- Services contain business logic and orchestration (`app/services/*`).
- Index implementations are in `app/indexing/` (Flat and HNSW) and share a `BaseIndex` interface.
- Persistence: metadata in `vector_db.sqlite` (SQLite) and large binary artifacts (vectors `.npy` and serialized indexes `.pkl`) in `./data/`.
- Docker-compose includes an `init` one-shot service to seed demo data and a `web` service that runs the API.

---

## Indexing algorithms implemented

Two algorithms are included to illustrate trade-offs:

1) Flat (brute-force) index

- Implementation: store all vectors in a NumPy array and compute distance or similarity to every stored vector at query time.
- Correctness: exact — returns the true nearest neighbors.
- Time complexity:
  - Build: O(N) to append/store vectors (amortized) where N is number of vectors.
  - Query: O(N * d) to compute distances for N vectors of dimension d, plus O(N log k) to select the top-k (can be reduced to O(N) with selection algorithms).
- Space complexity: O(N * d) for vectors + O(N) for IDs/metadata references.
- When to use: small datasets or situations where exact results are required and latency is acceptable.

2) HNSW (approximate) index — simplified in-repo implementation

- Implementation: Hierarchical Navigable Small World graphs. Each element is inserted into layers; higher layers have fewer points and connections between nodes approximate small-world graph structure. Search performs greedy/beam-like descent across levels.
- Correctness: approximate nearest neighbors; tradeoff parameters let you tune recall vs latency.
- Time complexity (practical/expected):
  - Build (incremental): roughly O(N log N) expected, because each insertion performs a search that is sub-linear in the current index size.
  - Query: sub-linear on average; practical behavior often near O(log N) or depends on `ef_search` and `M` parameters (higher `ef_search` → higher recall but slower query).
- Space complexity: O(N * d) for vector storage + O(N * M) for graph adjacency (M = average neighbors per node).
- When to use: larger datasets where query latency matters and approximate results are acceptable.

Why these two?
- Flat is the simplest reference implementation and always returns exact results. It is robust and easy to validate.
- HNSW demonstrates a practical, production-class approximate nearest neighbor method with substantially lower query latency on larger collections. Implementing HNSW in-code demonstrates algorithmic understanding and provides a useful default for moderate datasets.

---

## Metadata filtering (kNN + filters)

This project supports applying metadata filters on top of kNN searches so you can restrict results to chunks that match properties like creation date, source, or arbitrary metadata fields attached to chunks.

What it does
- You provide a kNN search request with a `query_embedding`, `k`, and an optional `metadata_filter` object. The system runs a nearest-neighbor search (Flat or HNSW) and then applies the `metadata_filter` to the matched chunks before returning results. This allows queries such as "top-5 nearest chunks where `source == 'test'`" or "nearest chunks created after 2025-01-01".

Supported operators
- The `metadata_filter` accepts either a simple equality value or an operator object. Supported operators implemented in `app/services/query_service.py::_matches_metadata_filter` include:
  - `$eq` — equals
  - `$ne` — not equals
  - `$gt`, `$gte` — greater than / greater than or equal (numeric or datetime values)
  - `$lt`, `$lte` — less than / less than or equal
  - `$in` — membership in a list
  - `$nin` — not in list
  - `$contains` — substring match for string metadata

How it's implemented
- Metadata for chunks is stored as JSON in the SQLite `chunks` table and reconstructed as plain dicts when reading rows (`app/repositories/chunk_repository.py`).
- The `SearchRequest` model (`app/models/models.py`) accepts an optional `metadata_filter` dict. After `index.search()` returns indices and scores, the `QueryService.search()` method maps the index results to chunk objects and calls `_matches_metadata_filter` for each candidate chunk. Only chunks that pass the filter are included in the final SearchResult list.
- The code attempts to coerce Pydantic metadata models to plain dicts before filtering so comparisons work reliably (see `query_service.py` where `model_dump()` is used when available).

Example search payloads
- Simple equality (match source):
```json
{
  "query_embedding": [0.1, 0.2, ...],
  "k": 5,
  "metadata_filter": { "source": "test" }
}
```
- Operator-based (created after a date):
```json
{
  "query_embedding": [0.1, 0.2, ...],
  "k": 10,
  "metadata_filter": { "created_at": {"$gt": "2025-01-01T00:00:00"} }
}
```
- Membership (source in a set):
```json
{
  "query_embedding": [0.1, 0.2, ...],
  "k": 5,
  "metadata_filter": { "source": {"$in": ["test", "imported"]} }
}
```

Limitations and performance notes
- Current implementation applies the metadata filter after the index search: the system first retrieves the top-`k` (or candidate) results from the vector index and then filters them. This has two practical consequences:
  - If many nearest neighbors do not match the metadata filter, you may receive fewer than `k` results. One mitigation is to request a larger `k` and then filter down to the desired count in the application.
  - For large datasets and selective filters, pre-filtering vectors before performing kNN (i.e., constructing sub-indexes or using index-time metadata partitioning) would be more efficient. That is a suggested enhancement for future work.
- Date/time comparisons expect ISO-8601 strings if metadata stores timestamps as strings. The comparison code checks numeric types first; if you store datetimes as strings, the service tries to compare them lexically (which works for ISO-8601). For full correctness we should consider storing timestamps as numeric epoch seconds or normalizing on ingestion.

Where to look in the code
- `app/services/query_service.py` — `search()` and `_matches_metadata_filter()` contain the logic for mapping index hits to chunks and applying filters.
- `app/repositories/chunk_repository.py` — shows how metadata is stored as JSON and returned as a dict when loading chunks.

Suggested improvements
- Pre-filtering: query the DB for chunk IDs that match metadata and then run kNN against only that subset of vectors (requires an index or mapping from DB ids to vector positions). This ensures accurate `k` results and improves efficiency for selective filters.
- Index partitioning: maintain per-metadata-value partitions (for example, per-library, per-source) so searches can target a specific partition; useful when there are natural sharding keys.

---


---

## Concurrency, consistency and persistence design

Goal: avoid corruption and enable fast restart while maintaining a reasonable balance between performance and durability.

Persistence choices
- SQLite (`vector_db.sqlite`) for metadata (libraries, documents, chunks). SQLite is ACID and simple to manage in a single-container deployment.
- Host-mounted persistence: we mount `./vector_db.sqlite` and `./data` into the container via `docker-compose.yml` so files live on the host. This makes them inspectable (DB Browser) and ensures data survives container restarts.
- Index & vectors on disk: vectors saved as `.npy` files and index data pickled (and saved atomically) into `./data/`.

Atomic writes and corruption avoidance
- When writing index files, the code writes to a temporary file and then renames it into place (atomic on POSIX). This prevents partial files if the process dies mid-write.
- Optionally use file locks when writing index files to prevent concurrent writers (the code uses an in-process lock and the project includes a small locking util for multi-process safety).

SQLite tuning for concurrency
- Use WAL (Write-Ahead Logging) mode to allow concurrent readers during writes: `PRAGMA journal_mode=WAL;` This improves read concurrency for read-mostly workloads.

Durability vs performance tradeoffs
- Default settings favor availability and performance with reasonable durability: WAL + synchronous=NORMAL is a common balance. If your use case needs the highest durability, switch to synchronous=FULL (slower) and ensure safe filesystem semantics.

Restart/resume semantics
- Because both DB and `./data` are host-mounted, restarting the container preserves the last checkpoint. On startup the app will load existing index files (if present) and the DB.
- If the index file is missing or corrupted, the system can rebuild the index from vectors stored in `./data` or from DB rows with embeddings. This favors recoverability.

---

## How the codebase is organized

- `app/main.py` — FastAPI app + lifespan startup behavior
- `app/models/models.py` — Pydantic models (Library, Document, Chunk, SearchRequest, SearchResult)
- `app/repositories/*` — DB access layer for libraries, documents, chunks
- `app/services/*` — business logic and orchestration that routers call
- `app/indexing/*` — `base_index.py`, `flat_index.py`, `hnsw_index.py` implementations
- `app/routers/*` — HTTP endpoints that call services
- `populate_db.py` — sample population script used by the `init` docker service
- `verify_data.py` — simple script that checks DB and data files
- `docker-compose.yml` — includes `init` (one-shot) and `web` services

---

## How to run locally

Prerequisites: Docker & Docker Compose

1) From project root run:

```bash
docker compose up --build
```

2) Watch `init` logs — it runs population and verification. After it exits the `web` service will start.

3) Browse interactive docs: http://localhost:8000/docs

4) Inspect the database:

- Use DB Browser for SQLite to open `vector_db.sqlite` in the project root.
- Run queries against `libraries`, `documents`, and `chunks` tables.

5) Re-run population / repair indexes if needed:

```bash
docker compose run --rm init
```

6) Run tests inside the container:

```bash
docker compose exec web pytest -q
```

---

## Troubleshooting & operational notes

- If index load errors appear: remove the corrupted index file from `./data` and run `docker compose run --rm init` to rebuild.
- If SQLite locks appear: ensure host file permissions are correct and consider enabling WAL mode.

---

## Final thoughts (why I made these choices)

- The pair (Flat + HNSW) shows a spectrum: simple exact search for correctness and a performant approximate search for scale. This demonstrates trade-offs engineers make when moving from prototypes to production.
- Persisting DB + index data on the host allows reproducible demos and makes it easy for reviewers to inspect state with familiar tools (DB Browser).
- Using a one-shot `init` keeps image builds fast and deterministic while still giving the reviewer a single-command demo.
