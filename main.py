"""Entry point: copy the page this repository holds into the graded output.

The grader runs this twice in a fresh sandbox with no network and gives it a
writable output directory. Both runs must write the same bytes, so the program
does no drawing of its own: it copies entry.png, which the drawing script in
tools/ produced, straight through.
"""

import os
import shutil
import sys

SOURCE = "entry.png"


def output_dir():
    """The writable directory the grader asks for, /output by default."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def looks_like_png(path):
    """Cheap check that the copy source really is a PNG, not a truncated file."""
    with open(path, "rb") as handle:
        return handle.read(8) == b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE)
    if not os.path.isfile(source):
        sys.stderr.write("missing %s beside main.py\n" % SOURCE)
        return 1
    if not looks_like_png(source):
        sys.stderr.write("%s is not a PNG\n" % SOURCE)
        return 1

    target_dir = output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source, target)
    sys.stdout.write("wrote %s (%d bytes)\n" % (target, os.path.getsize(target)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
