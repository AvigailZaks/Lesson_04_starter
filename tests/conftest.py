"""Supplied fixtures for lessons 4-5. Do not edit: the grader uses its own copy."""
import copy
import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data" / "events.json"


def _event(event_id: str) -> dict:
    events = json.loads(DATA.read_text(encoding="utf-8"))
    return copy.deepcopy(next(e for e in events if e["id"] == event_id))


@pytest.fixture
def sample_event() -> dict:
    """evt_100: client cli_100; gallery with med_1, med_2, med_3;
    add_to_album enabled; print_10x15 known but disabled."""
    return _event("evt_100")


@pytest.fixture
def other_event() -> dict:
    """evt_200: client cli_200; gallery with med_9; both services enabled."""
    return _event("evt_200")
