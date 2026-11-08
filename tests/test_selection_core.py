"""Example tests (happy path only). They import only selection_core: the lesson 4 test rule."""
import pytest

import selection_core


@pytest.mark.req("REQ-SEL-01")
def test_valid_selection_is_returned(sample_event):
    selection = selection_core.submit_selection(sample_event, "cli_100", ["med_1"], ["add_to_album"])
    assert selection["media_ids"] == ["med_1"]
    assert selection["service_codes"] == ["add_to_album"]


@pytest.mark.req("REQ-SEL-01")
def test_valid_selection_is_recorded_on_the_event(sample_event):
    selection_core.submit_selection(sample_event, "cli_100", ["med_1", "med_2"], ["add_to_album"])
    assert len(sample_event["selections"]) == 1


@pytest.mark.req("REQ-SEL-03")
def test_available_services_lists_enabled_services_only(sample_event):
    assert selection_core.available_services(sample_event) == ["add_to_album"]
