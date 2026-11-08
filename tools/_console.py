"""Console helpers shared by the course tools (UTF-8 safe output on Windows)."""
import sys


def setup_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def bad(msg: str) -> None:
    print(f"  [!!]   {msg}")


def info(msg: str) -> None:
    print(f"         {msg}")
