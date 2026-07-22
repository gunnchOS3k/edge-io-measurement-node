"""Consent lifecycle for Edge-IO measurement sessions."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


ConsentStatus = Literal["pending", "active", "withdrawn"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_receipt_id(site_id: str, run_id: str) -> str:
    """Non-identifying session receipt (no device serial / advertising ID)."""
    material = f"{site_id}|{run_id}|{secrets.token_hex(8)}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()[:16]
    return f"rcpt_{digest}"


@dataclass
class ConsentRecord:
    status: ConsentStatus = "pending"
    receipt_id: str | None = None
    withdrawal_supported: bool = True
    captured_at: str | None = None
    withdrawn_at: str | None = None
    summary_acknowledged: bool = False
    collection_summary: str = (
        "This session collects application, device, network, and workload metrics only. "
        "It does not collect GPS coordinates, email, phone number, student ID, IMEI, IMSI, "
        "MAC address, advertising ID, or other direct identifiers."
    )

    def require_opt_in(self, *, site_id: str, run_id: str, affirmative: bool) -> None:
        if not affirmative:
            raise PermissionError(
                "Affirmative opt-in is required before collection can start"
            )
        if not self.summary_acknowledged:
            raise PermissionError(
                "Collection summary must be acknowledged before opt-in"
            )
        self.status = "active"
        self.receipt_id = make_receipt_id(site_id, run_id)
        self.captured_at = utc_now_iso()
        self.withdrawn_at = None

    def acknowledge_summary(self) -> None:
        self.summary_acknowledged = True

    def withdraw(self) -> None:
        if self.status != "active":
            raise RuntimeError("No active consent to withdraw")
        self.status = "withdrawn"
        self.withdrawn_at = utc_now_iso()

    def ensure_active_for_collection(self) -> None:
        if self.status != "active":
            raise PermissionError(
                f"Collection blocked: consent.status={self.status!r} (required: active)"
            )
        if not self.receipt_id or not self.captured_at:
            raise PermissionError("Active consent is missing receipt metadata")

    def to_dict(self) -> dict:
        if not self.receipt_id or not self.captured_at:
            raise ValueError("Consent metadata incomplete")
        payload = {
            "status": self.status if self.status != "pending" else "pending",
            "receipt_id": self.receipt_id,
            "withdrawal_supported": self.withdrawal_supported,
            "captured_at": self.captured_at,
        }
        if self.withdrawn_at:
            payload["withdrawn_at"] = self.withdrawn_at
        return payload
