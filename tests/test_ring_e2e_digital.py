"""Continuation VII — RING_END_TO_END_DIGITAL_INPUT_PASS."""

from __future__ import annotations

from edge_io_node.ring_e2e import E2E_TOKEN, PHYSICAL_TOKEN, RingEndToEndDigital


def test_ring_end_to_end_digital_input_pass():
    report = RingEndToEndDigital().run()
    assert report.ok, report.as_dict()
    assert report.token == E2E_TOKEN
    assert report.physical_token == PHYSICAL_TOKEN
    assert report.physical_boot is False
    assert report.evidence_class == "SOFTWARE_SIMULATED"
    for key in (
        "keyboard",
        "pointer",
        "scroll",
        "click",
        "chord",
        "game_button",
        "analog",
        "destructive",
        "low_confidence_destructive",
        "replay",
        "lost_ring",
        "reconnect",
    ):
        assert report.exercised.get(key), f"missing exercise {key}: {report.exercised}"
    d = report.as_dict()
    assert E2E_TOKEN in d["tokens"]
    assert PHYSICAL_TOKEN in d["tokens"]
