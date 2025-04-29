import tempfile

import pytest

from vanadiumindex.index import (  # isort: skip
    AsFlat,
    AsIVF,
    AsPQ,
    VanadiumIndex,
    WithFlat,
    WithPQ,
)


@pytest.mark.parametrize(
    "type_with_options",
    [
        AsFlat(),
        AsPQ(num_subspaces=1, num_clusters=4),
        AsIVF(num_clusters=1, sub_index=WithFlat()),
        AsIVF(
            num_clusters=1,
            sub_index=WithPQ(
                num_subspaces=1,
                num_clusters=4,
            ),
        ),
    ],
)
def test_index(type_with_options):
    vec = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    query = [[0.3, 0.4], [0.7, 0.8]]
    d = 2
    k = 1

    index = VanadiumIndex(
        num_features=d,
        type_with_options=type_with_options,
    )
    index.train(vec)
    index.add(vec)
    results, dists = index.search(query, k)

    assert len(results) == len(query)
    assert len(dists) == len(query)
    assert all(isinstance(x, list) for x in results)
    assert all(isinstance(x, list) for x in dists)
    assert len(results[0]) == k
    assert len(results[1]) == k
    assert len(dists[0]) == k
    assert len(dists[1]) == k
    assert results[0][0] == 1
    assert results[1][0] == 3
    assert dists[0][0] == 0.0
    assert dists[1][0] == 0.0

    # Save and load test
    with tempfile.NamedTemporaryFile() as tmp:
        index.save(tmp.name)
        loaded_index = VanadiumIndex.load(tmp.name)

    loaded_results, loaded_dists = loaded_index.search(query, k)
    assert results == loaded_results
    assert dists == loaded_dists


def test_error():
    with pytest.raises(RuntimeError):
        VanadiumIndex(
            num_features=0,
            type_with_options=AsFlat(),
        )
