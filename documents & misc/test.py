import subprocess
from pathlib import Path


TAG = "106"
SOURCE_DIRS = ["maps450", "maps560"]
DEST_DIR = Path(".currentMaps")


def run(cmd: list[str]):
    subprocess.run(cmd, check=True)


def copy_dir_from_tag(tag: str, source_dir: str, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)

    cmd = [
        "git",
        "archive",
        tag,
        source_dir
    ]

    tar_cmd = [
        "tar",
        "-x",
        "-C",
        str(dest)
    ]

    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(tar_cmd, stdin=p1.stdout)
    p1.stdout.close()
    p2.communicate()

    if p2.returncode != 0:
        raise RuntimeError(f"Extraction failed for {source_dir}")


def main():
    for d in SOURCE_DIRS:
        copy_dir_from_tag(TAG, d, DEST_DIR)


if __name__ == "__main__":
    main()