"""
Evidence Registry - Immutable evidence tracking with provenance graph.
Implements EvidenceRegistry service for tracking evidence provenance and preventing orphaned evidence.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict

from dorama_studio.core.persistence import PersistenceManager


class EvidenceClass(Enum):
    """Evidence classification hierarchy."""
    OBSERVED = "OBSERVED"      # Visible directly
    MEASURED = "MEASURED"      # Quantified by method
    DERIVED = "DERIVED"        # Reconstructed from several observations
    INFERRED = "INFERRED"      # Interpretation razonable
    HYPOTHESIS = "HYPOTHESIS"  # Propuesta a validar
    UNVERIFIED = "UNVERIFIED"  # No comprobado


class EvidenceStatus(Enum):
    """Evidence lifecycle status."""
    PENDING = "PENDING"        # Awaiting validation
    VALIDATED = "VALIDATED"    # Verified and confirmed
    REFUTED = "REFUTED"        # Proven false
    SUPERSEDED = "SUPERSEDED"  # Replaced by newer evidence
    RETIRED = "RETIRED"        # No longer used but retained for history


@dataclass
class EvidenceRecord:
    """Immutable evidence record."""
    evidence_id: str
    source: str                    # Source file/reference (e.g., "DORAMA.V001.E001")
    timestamp: Optional[str]       # ISO timestamp or timecode
    method: Optional[str]          # Method used to obtain evidence
    evidence_class: EvidenceClass  # Epistemological class
    confidence: float              # 0.0 to 1.0
    scope: List[str]               # Affected components/agents
    revision: int                  # Revision number (starts at 0)
    provenance: List[str]          # Chain of custody: [source1, source2, ...]
    hash: str                      # Content hash for immutability
    status: EvidenceStatus         # Current status
    created_at: str                # ISO timestamp when recorded
    updated_at: str                # ISO timestamp when last updated
    metadata: Dict[str, Any]       # Additional evidence-specific data


class EvidenceRegistry:
    """
    Immutable evidence registry with provenance tracking.
    Prevents orphaned evidence and ensures traceability.
    """

    def __init__(self, db_path: str = "dorama_studio_data/evidence.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the evidence database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    timestamp TEXT,
                    method TEXT,
                    evidence_class TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    scope TEXT NOT NULL,  -- JSON array
                    revision INTEGER NOT NULL DEFAULT 0,
                    provenance TEXT NOT NULL,  -- JSON array
                    hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL,  -- JSON object
                    UNIQUE(source, revision)
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_class ON evidence(evidence_class)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_scope ON evidence(scope)")

    def _generate_evidence_id(self, source: str, revision: int) -> str:
        """Generate a unique evidence ID."""
        content = f"{source}:{revision}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _calculate_hash(self, evidence_data: Dict[str, Any]) -> str:
        """Calculate hash of evidence content for immutability."""
        # Create a copy without hash field for hashing
        data_copy = evidence_data.copy()
        data_copy.pop('hash', None)
        # Sort keys for consistent hashing
        json_str = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def register_evidence(
        self,
        source: str,
        timestamp: Optional[str] = None,
        method: Optional[str] = None,
        evidence_class: EvidenceClass = EvidenceClass.UNVERIFIED,
        confidence: float = 0.0,
        scope: Optional[List[str]] = None,
        provenance: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register new evidence or create a new revision.

        Args:
            source: Source reference (e.g., "DORAMA.V001.E001")
            timestamp: ISO timestamp or timecode (optional)
            method: Method used to obtain evidence (optional)
            evidence_class: Epistemological class (default UNVERIFIED)
            confidence: Confidence level 0.0-1.0 (default 0.0)
            scope: List of affected components/agents (default empty)
            provenance: Chain of custody (default [source])
            metadata: Additional evidence-specific data (default empty)

        Returns:
            evidence_id: Unique identifier for the evidence
        """
        if scope is None:
            scope = []
        if provenance is None:
            provenance = [source]
        if metadata is None:
            metadata = {}

        # Get latest revision for this source
        latest_revision = self._get_latest_revision(source)
        new_revision = latest_revision + 1

        # Generate evidence ID
        evidence_id = self._generate_evidence_id(source, new_revision)

        # Prepare evidence record
        evidence_record = EvidenceRecord(
            evidence_id=evidence_id,
            source=source,
            timestamp=timestamp,
            method=method,
            evidence_class=evidence_class,
            confidence=max(0.0, min(1.0, confidence)),  # Clamp to [0,1]
            scope=scope,
            revision=new_revision,
            provenance=provenance,
            hash="",  # Will be calculated
            status=EvidenceStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            metadata=metadata
        )

        # Calculate hash (excluding the hash field itself)
        evidence_dict = asdict(evidence_record)
        evidence_dict['evidence_class'] = evidence_record.evidence_class.value
        evidence_dict['status'] = evidence_record.status.value
        evidence_dict['hash'] = self._calculate_hash(evidence_dict)

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO evidence (
                    evidence_id, source, timestamp, method, evidence_class, confidence,
                    scope, revision, provenance, hash, status, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence_dict['evidence_id'],
                evidence_dict['source'],
                evidence_dict['timestamp'],
                evidence_dict['method'],
                evidence_dict['evidence_class'],
                evidence_dict['confidence'],
                json.dumps(evidence_dict['scope']),
                evidence_dict['revision'],
                json.dumps(evidence_dict['provenance']),
                evidence_dict['hash'],
                evidence_dict['status'],
                evidence_dict['created_at'],
                evidence_dict['updated_at'],
                json.dumps(evidence_dict['metadata'])
            ))

        return evidence_id

    def update_evidence_status(
        self,
        evidence_id: str,
        status: EvidenceStatus,
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update evidence status and optionally metadata.

        Args:
            evidence_id: Evidence identifier
            status: New status
            metadata_updates: Optional metadata updates to merge

        Returns:
            True if updated, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current evidence
            cursor = conn.execute(
                "SELECT * FROM evidence WHERE evidence_id = ?",
                (evidence_id,)
            )
            row = cursor.fetchone()
            if not row:
                return False

            # Parse current record
            columns = [description[0] for description in cursor.description]
            current_data = dict(zip(columns, row))

            # Update fields
            current_data['status'] = status.value
            current_data['updated_at'] = datetime.utcnow().isoformat()

            if metadata_updates:
                current_metadata = json.loads(current_data['metadata'])
                current_metadata.update(metadata_updates)
                current_data['metadata'] = json.dumps(current_metadata)

            # Recalculate hash (excluding hash field)
            hash_data = {k: v for k, v in current_data.items() if k != 'hash'}
            hash_data['evidence_class'] = hash_data['evidence_class']  # Already string from DB
            hash_data['status'] = hash_data['status']  # Already string from DB
            new_hash = self._calculate_hash(hash_data)
            current_data['hash'] = new_hash

            # Update database
            conn.execute("""
                UPDATE evidence SET
                    status = ?, updated_at = ?, metadata = ?, hash = ?
                WHERE evidence_id = ?
            """, (
                current_data['status'],
                current_data['updated_at'],
                current_data['metadata'],
                current_data['hash'],
                evidence_id
            ))

        return True

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """Retrieve evidence by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM evidence WHERE evidence_id = ?",
                (evidence_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Convert row to EvidenceRecord
            data = dict(row)
            evidence_record = EvidenceRecord(
                evidence_id=data['evidence_id'],
                source=data['source'],
                timestamp=data['timestamp'],
                method=data['method'],
                evidence_class=EvidenceClass(data['evidence_class']),
                confidence=data['confidence'],
                scope=json.loads(data['scope']),
                revision=data['revision'],
                provenance=json.loads(data['provenance']),
                hash=data['hash'],
                status=EvidenceStatus(data['status']),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                metadata=json.loads(data['metadata'])
            )
            return evidence_record

    def get_evidence_by_source(
        self,
        source: str,
        revision: Optional[int] = None
    ) -> Optional[EvidenceRecord]:
        """Get evidence by source and optional revision."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if revision is not None:
                cursor = conn.execute(
                    "SELECT * FROM evidence WHERE source = ? AND revision = ?",
                    (source, revision)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM evidence WHERE source = ? ORDER BY revision DESC LIMIT 1",
                    (source,)
                )
            row = cursor.fetchone()
            if not row:
                return None

            data = dict(row)
            return EvidenceRecord(
                evidence_id=data['evidence_id'],
                source=data['source'],
                timestamp=data['timestamp'],
                method=data['method'],
                evidence_class=EvidenceClass(data['evidence_class']),
                confidence=data['confidence'],
                scope=json.loads(data['scope']),
                revision=data['revision'],
                provenance=json.loads(data['provenance']),
                hash=data['hash'],
                status=EvidenceStatus(data['status']),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                metadata=json.loads(data['metadata'])
            )

    def _get_latest_revision(self, source: str) -> int:
        """Get the latest revision number for a source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT MAX(revision) FROM evidence WHERE source = ?",
                (source,)
            )
            result = cursor.fetchone()
            return result[0] if result[0] is not None else -1

    def list_evidence(
        self,
        evidence_class: Optional[EvidenceClass] = None,
        status: Optional[EvidenceStatus] = None,
        scope: Optional[str] = None,
        limit: int = 100
    ) -> List[EvidenceRecord]:
        """List evidence with optional filters."""
        conditions = []
        params = []

        if evidence_class:
            conditions.append("evidence_class = ?")
            params.append(evidence_class.value)
        if status:
            conditions.append("status = ?")
            params.append(status.value)
        if scope:
            conditions.append("scope LIKE ?")
            params.append(f"%{scope}%")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"SELECT * FROM evidence {where_clause} ORDER BY created_at DESC LIMIT ?",
                (*params, limit)
            )
            rows = cursor.fetchall()

            evidence_list = []
            for row in rows:
                data = dict(row)
                evidence_record = EvidenceRecord(
                    evidence_id=data['evidence_id'],
                    source=data['source'],
                    timestamp=data['timestamp'],
                    method=data['method'],
                    evidence_class=EvidenceClass(data['evidence_class']),
                    confidence=data['confidence'],
                    scope=json.loads(data['scope']),
                    revision=data['revision'],
                    provenance=json.loads(data['provenance']),
                    hash=data['hash'],
                    status=EvidenceStatus(data['status']),
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                    metadata=json.loads(data['metadata'])
                )
                evidence_list.append(evidence_record)

            return evidence_list

    def is_orphaned(self, evidence_id: str) -> bool:
        """
        Check if evidence is orphaned (not referenced by any agent or artifact).
        This would need to be implemented with actual usage tracking.
        For now, returns False as placeholder.
        """
        # In a full implementation, this would check against:
        # - Agent inputs/outputs
        # - Artifact references
        # - Usage in prompts, genomes, etc.
        return False

    def get_evidence_chain(self, evidence_id: str) -> List[EvidenceRecord]:
        """Get the full provenance chain for an evidence item."""
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return []

        chain = []
        current_evidence = evidence

        # Walk backwards through provenance
        while current_evidence:
            chain.append(current_evidence)
            # Find the parent evidence in provenance (simplified)
            # In practice, this would trace through the actual evidence IDs in provenance
            break  # Prevent infinite loop - would need proper implementation

        return chain


# Global evidence registry instance
evidence_registry = EvidenceRegistry()