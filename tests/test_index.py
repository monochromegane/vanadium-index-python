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
    index.search(query, k)

    assert True
