import os
import sys
import tarfile
import zipfile
import urllib.request
import platform
from typing import Tuple

LIB_NAME = "vanadium-index"
LIB_VERSION = "0.0.3"

MODULE_NAME = LIB_NAME.replace("-", "")
LIB_DIR = os.path.join(os.path.dirname(__file__), MODULE_NAME, "lib")
BASE_URL = f"https://github.com/monochromegane/{LIB_NAME}/releases"
GITHUB_RELEASE_BASE_URL = f"{BASE_URL}/download/v{LIB_VERSION}"


def _detect_platform_and_arch() -> Tuple[str, str]:
    plat: str = sys.platform
    arch: str = platform.machine().lower()

    if plat == "darwin":
        os_part = "darwin"
    elif plat.startswith("linux"):
        os_part = "linux"
    elif plat == "win32":
        os_part = "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {plat}")

    if arch in ("arm64", "aarch64"):
        arch_part = "arm64"
    elif arch in ("x86_64", "amd64"):
        arch_part = "amd64"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch}")

    return os_part, arch_part


def _get_archive_name() -> str:
    os_part, arch_part = _detect_platform_and_arch()
    ext = "tar.gz" if os_part == "linux" else "zip"
    return f"{LIB_NAME}_v{LIB_VERSION}_{os_part}_{arch_part}.{ext}"


def download_and_extract() -> None:
    archive_name = _get_archive_name()

    url = f"{GITHUB_RELEASE_BASE_URL}/{archive_name}"
    archive_path = os.path.join(LIB_DIR, archive_name)

    os.makedirs(LIB_DIR, exist_ok=True)

    print(f"Downloading {url} ...")
    try:
        urllib.request.urlretrieve(url, archive_path)
    except urllib.error.URLError as e:
        msg = f"Failed to download library: {url}\nError: {e.reason}"
        raise RuntimeError(msg)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Library not found (HTTP {e.code}): {url}")

    print(f"Extracting {archive_path} ...")
    if archive_name.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(LIB_DIR)
    elif archive_name.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(LIB_DIR)
    else:
        raise RuntimeError("Unknown archive format")

    os.remove(archive_path)


if __name__ == "__main__":
    download_and_extract()
