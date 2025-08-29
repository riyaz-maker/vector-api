import numpy as np

from app.indexing.hnsw_index import HNSWIndex


def test_hnsw_build_and_search():
    # reproducible small dataset
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(10, 8)).astype(np.float32)

    idx = HNSWIndex()

    # build index should return True
    built = idx.build_index(vectors)
    assert built is True or idx.built is True

    # pick a query (first vector) and search
    query = vectors[0].tolist()
    indices, distances = idx.search(query, k=3)

    # results must be non-empty and distances must be numeric
    assert isinstance(indices, list)
    assert isinstance(distances, list)
    assert len(indices) > 0
    assert len(distances) > 0
    # distance for the top-1 should be numeric and finite
    assert np.isfinite(distances[0])
