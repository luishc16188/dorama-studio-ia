"""
Artifact Store - High-level interface for storing and retrieving artifacts.
Provides a clean API for the pipeline to interact with the persistence layer.
"""

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from .models import Artifact
from .repository import ArtifactRepository

logger = logging.getLogger(__name__)


class ArtifactStore:
    """
    High-level artifact storage interface.
    Handles serialization, versioning, and retrieval of pipeline artifacts.
    """

    def __init__(self, session: Session, base_path: str = "artifacts"):
        self.session = session
        self.repository = ArtifactRepository(session)
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        project_id: str,
        content: Any,
        season_id: str = None,
        episode_id: str = None,
        metadata: dict[str, Any] = None
    ) -> Artifact:
        """
        Save an artifact to the database.

        Args:
            artifact_id: Unique identifier for the artifact
            artifact_type: Type of artifact (script, video, audio, etc.)
            project_id: Project identifier
            content: The artifact content (will be JSON serialized)
            season_id: Optional season identifier
            episode_id: Optional episode identifier
            metadata: Optional metadata dictionary

        Returns:
            Created Artifact object
        """
        # Serialize content if it's not a string
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = str(content)

        artifact_data = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "project_id": project_id,
            "season_id": season_id,
            "episode_id": episode_id,
            "content": content_str,
            "metadata_json": metadata or {}
        }

        artifact = self.repository.create(artifact_data)
        self.session.commit()
        logger.info(f"Saved artifact: {artifact_id} ({artifact_type})")
        return artifact

    def load_artifact(self, artifact_id: str) -> Artifact | None:
        """
        Load an artifact by ID.

        Returns:
            Artifact object or None if not found
        """
        return self.repository.get_by_id(artifact_id)

    def load_artifact_content(self, artifact_id: str) -> Any | None:
        """
        Load and deserialize artifact content.

        Returns:
            Deserialized content (dict/list/str) or None if not found
        """
        artifact = self.load_artifact(artifact_id)
        if not artifact:
            return None

        try:
            return json.loads(artifact.content)
        except json.JSONDecodeError:
            return artifact.content

    def get_artifacts_by_project(self, project_id: str, limit: int = 100) -> list[Artifact]:
        """Get all artifacts for a project."""
        return self.repository.get_by_project(project_id, limit)

    def get_artifacts_by_season(self, project_id: str, season_id: str) -> list[Artifact]:
        """Get all artifacts for a season."""
        return self.repository.get_by_season(project_id, season_id)

    def get_artifacts_by_episode(self, project_id: str, episode_id: str) -> list[Artifact]:
        """Get all artifacts for an episode."""
        return self.repository.get_by_episode(project_id, episode_id)

    def get_artifacts_by_type(
        self, artifact_type: str, project_id: str = None
    ) -> list[Artifact]:
        """Get artifacts by type."""
        return self.repository.get_by_type(artifact_type, project_id)

    def update_artifact(
        self, artifact_id: str, updates: dict[str, Any]
    ) -> Artifact | None:
        """Update an artifact's metadata."""
        artifact = self.repository.update(artifact_id, updates)
        if artifact:
            self.session.commit()
        return artifact

    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact."""
        result = self.repository.delete(artifact_id)
        if result:
            self.session.commit()
        return result

    def export_artifact_to_file(self, artifact_id: str, output_path: str) -> bool:
        """
        Export artifact content to a file.

        Args:
            artifact_id: Artifact to export
            output_path: Path to write file

        Returns:
            True if successful
        """
        content = self.load_artifact_content(artifact_id)
        if content is None:
            return False

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, (dict, list)):
            output_path.write_text(
                json.dumps(content, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        else:
            output_path.write_text(str(content), encoding="utf-8")

        logger.info(f"Exported artifact {artifact_id} to {output_path}")
        return True

    def import_artifact_from_file(
        self,
        artifact_id: str,
        artifact_type: str,
        project_id: str,
        file_path: str,
        season_id: str = None,
        episode_id: str = None,
        metadata: dict[str, Any] = None
    ) -> Artifact:
        """
        Import artifact from a file.

        Args:
            artifact_id: Unique identifier
            artifact_type: Type of artifact
            project_id: Project identifier
            file_path: Path to file to import
            season_id: Optional season
            episode_id: Optional episode
            metadata: Optional metadata

        Returns:
            Created Artifact object
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        # Try to parse as JSON
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = content

        return self.save_artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            project_id=project_id,
            content=parsed,
            season_id=season_id,
            episode_id=episode_id,
            metadata=metadata
        )
