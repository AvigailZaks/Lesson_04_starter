"""Lesson 4 homework: baseline tasks.

Replace each `raise NotImplementedError` with your implementation.
You may use AI, as long as you can explain every line.
"""
import json

def count_selected(media_ids: list[str]) -> int:
    """Return the number of DIFFERENT media ids."""
    return len(set(media_ids))


def group_by_gallery(media: list[dict]) -> dict[str, list[str]]:
    """Group media items {"gallery_id": ..., "id": ...} by gallery.

    Return a dict: gallery id -> list of media ids, in input order.
    """
    result = {}
    for dic in media:
        if(dic["gallery_id"] not in result):
            result[dic["gallery_id"]] = list()
        result[dic["gallery_id"]].append(dic["id"])
    return result


def total_price(prices_minor: list[int | None]) -> int:
    """Return the sum of the prices (in agorot), ignoring None."""
    total = 0
    for money in prices_minor:
        if (money != None):
            total = total + money
    return total


def first_missing(required: list[str], present: list[str]) -> str | None:
    """Return the first item of `required` that is not in `present`, or None."""
    for req in required:
        if(req not in present):
            return req
    return None


def load_events(path) -> list[dict]:
    """Read a JSON file encoded in UTF-8 and return its content (a list of events)."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

