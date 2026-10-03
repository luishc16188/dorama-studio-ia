"""
Human-in-the-loop (HITL) management for DORAMA STUDIO orchestration.
Handles approval workflows, notifications, and human feedback integration.
"""

import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalPriority(Enum):
    """Priority level for approval requests."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApprovalRequest:
    """Request for human approval."""
    request_id: str = field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:12]}")
    stage: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    priority: ApprovalPriority = ApprovalPriority.NORMAL
    timeout_seconds: int = 3600  # 1 hour default
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout_seconds)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def time_remaining(self) -> int:
        """Seconds remaining until expiry."""
        remaining = (self.expires_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))


@dataclass
class ApprovalResponse:
    """Response to an approval request."""
    request_id: str
    status: ApprovalStatus
    approved: bool
    notes: str = ""
    modified_payload: dict[str, Any] | None = None
    responder: str = "human"
    responded_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Notification Channels
# ============================================================

class NotificationChannel(ABC):
    """Abstract base for notification channels."""

    @abstractmethod
    def send(self, request: ApprovalRequest) -> bool:
        """Send approval request notification."""
        pass

    @abstractmethod
    def send_response(self, response: ApprovalResponse) -> bool:
        """Send response notification."""
        pass


class ConsoleNotificationChannel(NotificationChannel):
    """Console-based notification (for development)."""

    def send(self, request: ApprovalRequest) -> bool:
        print(f"\n{'='*60}")
        print(f"🔔 APPROVAL REQUEST: {request.request_id}")
        print(f"   Stage: {request.stage}")
        print(f"   Priority: {request.priority.value}")
        print(f"   Timeout: {request.timeout_seconds}s")
        print(f"   Payload: {request.payload}")
        print(f"   Expires: {request.expires_at.isoformat()}")
        print(f"{'='*60}\n")
        return True

    def send_response(self, response: ApprovalResponse) -> bool:
        print(f"\n{'='*60}")
        print(f"✅ APPROVAL RESPONSE: {response.request_id}")
        print(f"   Status: {response.status.value}")
        print(f"   Approved: {response.approved}")
        print(f"   Notes: {response.notes}")
        if response.modified_payload:
            print(f"   Modified Payload: {response.modified_payload}")
        print(f"{'='*60}\n")
        return True


class WebhookNotificationChannel(NotificationChannel):
    """Webhook-based notification for external systems."""

    def __init__(
        self,
        webhook_url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 10,
    ):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout

    def send(self, request: ApprovalRequest) -> bool:
        import requests
        try:
            payload = {
                "type": "approval_request",
                "request_id": request.request_id,
                "stage": request.stage,
                "priority": request.priority.value,
                "timeout_seconds": request.timeout_seconds,
                "payload": request.payload,
                "created_at": request.created_at.isoformat(),
                "expires_at": request.expires_at.isoformat() if request.expires_at else None,
                "metadata": request.metadata,
            }
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False

    def send_response(self, response: ApprovalResponse) -> bool:
        import requests
        try:
            payload = {
                "type": "approval_response",
                "request_id": response.request_id,
                "status": response.status.value,
                "approved": response.approved,
                "notes": response.notes,
                "modified_payload": response.modified_payload,
                "responder": response.responder,
                "responded_at": response.responded_at.isoformat(),
                "metadata": response.metadata,
            }
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook response notification failed: {e}")
            return False


class EmailNotificationChannel(NotificationChannel):
    """Email-based notification (placeholder)."""

    def __init__(self, smtp_config: dict[str, Any], recipients: list[str]):
        self.smtp_config = smtp_config
        self.recipients = recipients

    def send(self, request: ApprovalRequest) -> bool:
        # Implementation would use smtplib
        logger.info(f"Email notification sent to {self.recipients} for {request.request_id}")
        return True

    def send_response(self, response: ApprovalResponse) -> bool:
        logger.info(f"Email response sent for {response.request_id}")
        return True


# ============================================================
# HITL Manager
# ============================================================

class HumanInLoopManager:
    """
    Manages human-in-the-loop approval workflows.

    Usage:
        manager = HumanInLoopManager()
        manager.add_channel(ConsoleNotificationChannel())

        # Request approval
        request = manager.request_approval(
            stage="season_bible",
            payload={"season_arc": "..."},
            priority=ApprovalPriority.HIGH
        )

        # Wait for response (blocking)
        response = manager.wait_for_response(request.request_id, timeout=3600)

        # Or register callback
        manager.on_response(request.request_id, my_callback)
    """

    def __init__(self):
        self.channels: list[NotificationChannel] = []
        self.pending_requests: dict[str, ApprovalRequest] = {}
        self.responses: dict[str, ApprovalResponse] = {}
        self.callbacks: dict[str, list[Callable[[ApprovalResponse], None]]] = {}
        self.default_timeout = 3600

    def add_channel(self, channel: NotificationChannel) -> None:
        """Add a notification channel."""
        self.channels.append(channel)

    def request_approval(
        self,
        stage: str,
        payload: dict[str, Any],
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        timeout_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        """Create and send an approval request."""
        request = ApprovalRequest(
            stage=stage,
            payload=payload,
            priority=priority,
            timeout_seconds=timeout_seconds or self.default_timeout,
            metadata=metadata or {},
        )

        self.pending_requests[request.request_id] = request

        # Send to all channels
        for channel in self.channels:
            try:
                channel.send(request)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.__class__.__name__}: {e}")

        logger.info(f"Approval requested: {request.request_id} for stage '{stage}'")
        return request

    def wait_for_response(
        self,
        request_id: str,
        timeout: int | None = None,
        poll_interval: float = 1.0,
    ) -> ApprovalResponse:
        """
        Block until response received or timeout.

        Args:
            request_id: Request ID to wait for
            timeout: Max seconds to wait (None = use request timeout)
            poll_interval: Seconds between checks

        Returns:
            ApprovalResponse

        Raises:
            TimeoutError: If timeout expires
            ValueError: If request not found
        """
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        timeout = timeout or request.timeout_seconds
        start_time = time.time()

        while True:
            # Check for response
            if request_id in self.responses:
                return self.responses[request_id]

            # Check expiration
            if request.is_expired():
                response = ApprovalResponse(
                    request_id=request_id,
                    status=ApprovalStatus.EXPIRED,
                    approved=False,
                    notes="Request expired",
                )
                self._handle_response(response)
                return response

            # Check global timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Approval timeout after {timeout}s")

            time.sleep(poll_interval)

    def submit_response(self, response: ApprovalResponse) -> None:
        """Submit a response to an approval request."""
        request = self.pending_requests.get(response.request_id)
        if not request:
            logger.warning(f"Response for unknown request: {response.request_id}")
            return

        # Check expiration
        if request.is_expired():
            logger.warning(f"Response for expired request: {response.request_id}")
            response.status = ApprovalStatus.EXPIRED
            response.approved = False

        self.responses[response.request_id] = response
        self._handle_response(response)

    def _handle_response(self, response: ApprovalResponse) -> None:
        """Process a response."""
        request_id = response.request_id

        # Remove from pending
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]

        # Store response
        self.responses[request_id] = response

        # Notify channels
        for channel in self.channels:
            try:
                channel.send_response(response)
            except Exception as e:
                logger.error(f"Failed to send response notification: {e}")

        # Execute callbacks
        for callback in self.callbacks.get(request_id, []):
            try:
                callback(response)
            except Exception as e:
                logger.error(f"Callback error for {request_id}: {e}")

        # Clean up callbacks
        if request_id in self.callbacks:
            del self.callbacks[request_id]

        logger.info(f"Approval response received: {request_id} - {response.status.value}")

    def on_response(self, request_id: str, callback: Callable[[ApprovalResponse], None]) -> None:
        """Register callback for when response received."""
        if request_id not in self.callbacks:
            self.callbacks[request_id] = []
        self.callbacks[request_id].append(callback)

    def cancel_request(self, request_id: str, reason: str = "Cancelled") -> bool:
        """Cancel a pending approval request."""
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]

        response = ApprovalResponse(
            request_id=request_id,
            status=ApprovalStatus.CANCELLED,
            approved=False,
            notes=reason,
        )

        self._handle_response(response)
        return True

    def get_pending(self) -> list[ApprovalRequest]:
        """Get all pending approval requests."""
        return list(self.pending_requests.values())

    def get_response(self, request_id: str) -> ApprovalResponse | None:
        """Get response for a request."""
        return self.responses.get(request_id)

    def cleanup_expired(self) -> int:
        """Remove expired requests and return count cleaned."""
        expired_ids = [
            rid for rid, req in self.pending_requests.items()
            if req.is_expired()
        ]

        for rid in expired_ids:
            response = ApprovalResponse(
                request_id=rid,
                status=ApprovalStatus.EXPIRED,
                approved=False,
                notes="Request expired during cleanup",
            )
            self._handle_response(response)

        return len(expired_ids)

    @contextmanager
    def approval_context(
        self,
        stage: str,
        payload: dict[str, Any],
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        timeout_seconds: int | None = None,
    ):
        """Context manager for approval workflow."""
        request = self.request_approval(stage, payload, priority, timeout_seconds)
        try:
            yield request
            response = self.wait_for_response(request.request_id)
            if not response.approved:
                raise RuntimeError(f"Approval rejected: {response.notes}")
        finally:
            if request.request_id in self.pending_requests:
                self.cancel_request(request.request_id, "Context exited")


# ============================================================
# Pre-configured HITL Nodes for LangGraph
# ============================================================

def create_hitl_node(
    manager: HumanInLoopManager,
    stage: str,
    payload_extractor: Callable[[dict[str, Any]], dict[str, Any]],
    priority: ApprovalPriority = ApprovalPriority.NORMAL,
    timeout_seconds: int | None = None,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """
    Create a LangGraph node function for HITL approval.

    Args:
        manager: HITL manager instance
        stage: Stage name for approval
        payload_extractor: Function to extract payload from state
        priority: Approval priority
        timeout_seconds: Timeout in seconds

    Returns:
        Node function compatible with LangGraph
    """
    def hitl_node(state: dict[str, Any]) -> dict[str, Any]:
        # Extract payload from state
        payload = payload_extractor(state)

        # Request approval
        request = manager.request_approval(
            stage=stage,
            payload=payload,
            priority=priority,
            timeout_seconds=timeout_seconds,
        )

        # Wait for response (blocking)
        response = manager.wait_for_response(request.request_id)

        # Update state with response
        state["human_approval"] = {
            "stage": stage,
            "approved": response.approved,
            "notes": response.notes,
            "modified_payload": response.modified_payload,
            "timestamp": response.responded_at.isoformat(),
        }

        if response.modified_payload:
            # Merge modified payload back into state
            state.update(response.modified_payload)

        return state

    return hitl_node


# Common payload extractors
def extract_season_bible_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "season_bible_ref": state.get("season_bible_ref"),
        "season_arc": state.get("season_arc"),
    }

def extract_episode_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_number": state.get("episode_number"),
        "blueprint_id": state.get("blueprint_id"),
        "hook_id": state.get("hook_id"),
    }

def extract_final_qc_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode_number": state.get("episode_number"),
        "quality_report": state.get("final_qc_id"),
        "quality_issues": state.get("active_quality_issues", []),
    }


# Default HITL manager instance
default_hitl_manager = HumanInLoopManager()
default_hitl_manager.add_channel(ConsoleNotificationChannel())
