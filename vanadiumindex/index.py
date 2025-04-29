from dataclasses import dataclass

from vanadiumindex.lib.libvanadium import ffi, lib  # type: ignore


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
    def __init__(self, num_features, type_with_options):
        handle = ffi.new("unsigned long *")
        err = ffi.new("char **")

        match type_with_options:
            case AsFlat():
                ret = lib.NewFlatIndex(handle, err, num_features)
            case AsPQ(
                num_subspaces=num_subspaces,
                num_clusters=num_clusters,
                max_iterations=max_iterations,
                tolerance=tolerance,
            ):
                ret = lib.NewPQIndex(
                    handle,
                    err,
                    num_features,
                    num_subspaces,
                    num_clusters,
                    max_iterations,
                    tolerance,
                )
            case AsIVF(
                num_clusters=num_clusters,
                max_iterations=max_iterations,
                tolerance=tolerance,
                sub_index=sub_index,
            ):
                match sub_index:
                    case WithFlat():
                        ret = lib.NewIVFFlatIndex(
                            handle,
                            err,
                            num_features,
                            num_clusters,
                            max_iterations,
                            tolerance,
                        )
                    case WithPQ(
                        num_subspaces=pq_num_subspaces,
                        num_clusters=pq_num_clusters,
                        max_iterations=pq_max_iterations,
                        tolerance=pq_tolerance,
                    ):
                        ret = lib.NewIVFPQIndex(
                            handle,
                            err,
                            num_features,
                            num_clusters,
                            pq_num_subspaces,
                            pq_num_clusters,
                            max_iterations,
                            tolerance,
                            pq_max_iterations,
                            pq_tolerance,
                        )
                    case _:
                        raise TypeError("Unknown sub index type")
            case _:
                raise TypeError("Unknown index type")

        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)
        self.handle = handle

    def train(self, data):
        c_data = ffi.new("float[]", data)
        err = ffi.new("char **")
        ret = lib.Train(self.handle[0], err, c_data, len(data))
        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)

    def add(self, data):
        c_data = ffi.new("float[]", data)
        err = ffi.new("char **")
        ret = lib.Add(self.handle[0], err, True, c_data, len(data))
        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)

    def search(self, queries, k):
        flatten_queries = sum(queries, [])
        c_query = ffi.new("float[]", flatten_queries)
        err = ffi.new("char **")
        out = ffi.new("int**")
        dist = ffi.new("float**")
        offsets = ffi.new("int[]", len(queries))
        lengths = ffi.new("int[]", len(queries))
        ret = lib.Search(
            self.handle[0],
            err,
            c_query,
            len(flatten_queries),
            k,
            out,
            dist,
            offsets,
            lengths,
        )
        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)

        flat = out[0]
        results = [
            [flat[offsets[i] + j] for j in range(lengths[i])]
            for i in range(len(queries))
        ]
        lib.FreeMemory(out[0])

        flat = dist[0]
        dists = [
            [flat[offsets[i] + j] for j in range(lengths[i])]
            for i in range(len(queries))
        ]
        lib.FreeMemory(dist[0])
        return (results, dists)

    def save(self, path):
        c_path = ffi.new("char[]", path.encode("utf-8"))
        err = ffi.new("char **")
        ret = lib.Save(self.handle[0], err, c_path)
        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)

    @classmethod
    def load(cls, path):
        handle = ffi.new("unsigned long *")
        err = ffi.new("char **")
        c_path = ffi.new("char[]", path.encode("utf-8"))
        ret = lib.Load(handle, err, c_path)
        if ret != 0:
            error_message = ffi.string(err[0]).decode()
            lib.FreeMemory(err[0])
            raise RuntimeError(error_message)
        index = cls.__new__(cls)
        index.handle = handle
        return index

    def __del__(self):
        if hasattr(self, "handle"):
            lib.FreeIndex(self.handle[0])
