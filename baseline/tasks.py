"""Lesson 4 homework: baseline tasks.

Replace each `raise NotImplementedError` with your implementation.
You may use AI, as long as you can explain every line.
"""


def count_selected(media_ids: list[str]) -> int:
    """Return the number of DIFFERENT media ids."""
    raise NotImplementedError


def group_by_gallery(media: list[dict]) -> dict[str, list[str]]:
    """Group media items {"gallery_id": ..., "id": ...} by gallery.

    Return a dict: gallery id -> list of media ids, in input order.
    """
    raise NotImplementedError


def total_price(prices_minor: list[int | None]) -> int:
    """Return the sum of the prices (in agorot), ignoring None."""
    raise NotImplementedError


def first_missing(required: list[str], present: list[str]) -> str | None:
    """Return the first item of `required` that is not in `present`, or None."""
    raise NotImplementedError


def load_events(path) -> list[dict]:
    """Read a JSON file encoded in UTF-8 and return its content (a list of events)."""
    raise NotImplementedError
