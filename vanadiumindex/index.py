from dataclasses import dataclass


@dataclass
class AsOption: ...  # noqa: E701


@dataclass
class SubIndexOption: ...  # noqa: E701


@dataclass
class AsFlat(AsOption): ...  # noqa: E701


@dataclass
class WithFlat(SubIndexOption): ...  # noqa: E701


@dataclass
class AsPQ(AsOption):
    num_subspaces: int
    num_clusters: int
    max_iterations: int = 0
    tolerance: float = 0.0


@dataclass
class WithPQ(SubIndexOption):
    num_subspaces: int
    num_clusters: int
    max_iterations: int = 0
    tolerance: float = 0.0


@dataclass
class AsIVF(AsOption):
    num_clusters: int
    sub_index: SubIndexOption
    max_iterations: int = 0
    tolerance: float = 0.0


class VanadiumIndex:
    def __init__(self, num_features, type_with_options): ...

    def train(self, data): ...

    def add(self, data): ...

    def search(self, queries, k): ...

    def save(self, path): ...

    @classmethod
    def load(cls, path): ...

    def __del__(self): ...
