import os
import sys
from cffi import FFI

ffibuilder = FFI()

LIB_NAME = "vanadium-index"
MODULE_NAME = LIB_NAME.replace("-", "")

current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(current_dir, MODULE_NAME, "lib")

if sys.platform == "win32":
    libraries = [LIB_NAME]
    library_dirs = [lib_dir]
    extra_objects = [] 
else:
    ext = "dylib" if sys.platform == "darwin" else "so"
    libraries: list[str] = []
    library_dirs: list[str] = []
    extra_objects = [os.path.join(lib_dir, f"{LIB_NAME}.{ext}")]

ffibuilder.set_source(
    module_name=f"{MODULE_NAME}.lib.libvanadium",
    source=f"""
        #include "{LIB_NAME}.h"
    """,
    include_dirs=[lib_dir],
    libraries=libraries,
    library_dirs=library_dirs,
    extra_objects=extra_objects,
    extra_link_args = [],
)

# flake8: noqa: E501
ffibuilder.cdef(
    csource="""
    extern int NewFlatIndex(unsigned long* handle, char** errMsg, int numFeatures);
    extern int NewPQIndex(unsigned long* handle, char** errMsg, int numFeatures, int numSubspaces, int numClusters, int maxIterations, float tolerance);
    extern int NewIVFFlatIndex(unsigned long* handle, char** errMsg, int numFeatures, int numClusters, int maxIterations, float tolerance);
    extern int NewIVFPQIndex(unsigned long* handle, char** errMsg, int numFeatures, int numClusters, int numSubspaces, int numClustersPerSubspace, int maxIterations, float tolerance, int pqMaxIterations, float pqTolerance);
    extern void FreeIndex(unsigned long handle);
    extern void FreeMemory(void* ptr);
    extern int Train(unsigned long handle, char** errMsg, float* data, int dataLength);
    extern int Add(unsigned long handle, char** errMsg, _Bool keepData, float* data, int dataLength);
    extern int Search(unsigned long handle, char** errMsg, float* query, int queryLength, int k, int** outIndices, float** outDistances, int* outOffsets, int* outLengths);
    extern int NumVectors(unsigned long handle);
    extern int Save(unsigned long handle, char** errMsg, char* path);
    extern int Load(unsigned long* handle, char** errMsg, char* path);
    """
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
