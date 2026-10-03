"""
Master Timeline Agent - Fase 16
Coordina la línea de tiempo maestra de producción para episodios y temporadas.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class TimelineStatus(str, Enum):
    """Estados de la línea de tiempo."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    DELAYED = "delayed"
    ON_HOLD = "on_hold"


@dataclass
class TimelineMilestone:
    """Hito en la línea de tiempo de producción."""
    milestone_id: str
    description: str
    target_date: float  # timestamp
    completed_date: float | None = None
    status: TimelineStatus = TimelineStatus.PLANNING
    dependencies: list[str] = field(default_factory=list)  # IDs de hitos previos
    assigned_to: list[str] = field(default_factory=list)  # agentes responsables
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MasterTimeline:
    """Línea de tiempo maestra para una temporada o proyecto."""
    timeline_id: str
    project_id: str
    season_id: str | None = None
    title: str = ""
    description: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    milestones: list[TimelineMilestone] = field(default_factory=list)
    current_phase: str = ""
    overall_progress: float = 0.0  # 0-100%
    status: TimelineStatus = TimelineStatus.PLANNING
    metadata: dict[str, Any] = field(default_factory=dict)


class MasterTimelineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Agente de Línea de Tiempo Maestra que:
    - Crea y mantiene la línea de tiempo de producción para proyectos y temporadas
    - Coordina dependencias entre episodios y tareas
    - Rastrea progreso y identifica bloqueos
    - Sugiere ajustes de línea de tiempo basado en desempeño real
    """

    def __init__(self):
        super().__init__("MasterTimelineAgent")
        self.timelines: dict[str, MasterTimeline] = {}
        self.dependency_graph: dict[str, list[str]] = {}  # milestone_id -> [depends_on]

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Procesa solicitudes de gestión de línea de tiempo.

        Args:
            validated_input: Dict con:
                - action: "create" | "update" | "query" | "blocked" | "advance"
                - project_id: ID del proyecto
                - season_id: ID de la temporada (opcional)
                - timeline_data: datos específicos de la acción
                - episode_data: datos de episodio para actualizar progreso

        Returns:
            Dict con resultado de la operación y estado de la línea de tiempo
        """
        action = validated_input.get("action", "query")
        project_id = validated_input.get("project_id", "default_project")
        season_id = validated_input.get("season_id")

        timeline_key = f"{project_id}_{season_id or 'no_season'}"

        if action == "create":
            return self._create_timeline(validated_input, timeline_key)
        elif action == "update":
            return self._update_timeline(validated_input, timeline_key)
        elif action == "query":
            return self._query_timeline(validated_input, timeline_key)
        elif action == "blocked":
            return self._identify_blocked_items(validated_input, timeline_key)
        elif action == "advance":
            return self._advance_timeline(validated_input, timeline_key)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
                "available_actions": ["create", "update", "query", "blocked", "advance"]
            }

    def _create_timeline(
        self,
        data: dict[str, Any],
        timeline_key: str
    ) -> dict[str, Any]:
        """Crea una nueva línea de tiempo maestra."""
        project_id = data.get("project_id", "default_project")
        season_id = data.get("season_id")
        title = data.get("title", f"Timeline for {project_id}")
        description = data.get("description", "")

        timeline = MasterTimeline(
            timeline_id=f"tl_{int(time.time())}_{hash(project_id) % 10000}",
            project_id=project_id,
            season_id=season_id,
            title=title,
            description=description
        )

        # Crear hitos iniciales basado en los datos de entrada
        initial_milestones = data.get("initial_milestones", [])
        for ms_data in initial_milestones:
            milestone = TimelineMilestone(
                milestone_id=ms_data.get("id", f"ms_{int(time.time())}"),
                description=ms_data.get("description", ""),
                target_date=ms_data.get("target_date", time.time() + 86400),  # 1 día por defecto
                dependencies=ms_data.get("dependencies", []),
                assigned_to=ms_data.get("assigned_to", []),
                metadata=ms_data.get("metadata", {})
            )
            timeline.milestones.append(milestone)
            self.dependency_graph[milestone.milestone_id] = milestone.dependencies

        self.timelines[timeline_key] = timeline

        return {
            "status": "created",
            "timeline_id": timeline.timeline_id,
            "project_id": project_id,
            "season_id": season_id,
            "milestones_count": len(timeline.milestones),
            "message": f"Master timeline created for {project_id}" + (f" season {season_id}" if season_id else "")
        }

    def _update_timeline(
        self,
        data: dict[str, Any],
        timeline_key: str
    ) -> dict[str, Any]:
        """Actualiza una línea de tiempo existente."""
        if timeline_key not in self.timelines:
            return {
                "status": "error",
                "message": f"Timeline not found for key: {timeline_key}"
            }

        timeline = self.timelines[timeline_key]
        timeline.updated_at = time.time()

        # Actualizar título y descripción si se proporcionan
        if "title" in data:
            timeline.title = data["title"]
        if "description" in data:
            timeline.description = data["description"]

        # Actualizar o añadir hitos
        if "milestones" in data:
            # Eliminar hitos existentes y reemplazar con los nuevos
            timeline.milestones = []
            self.dependency_graph = {}
            for ms_data in data["milestones"]:
                milestone = TimelineMilestone(
                    milestone_id=ms_data.get("id", f"ms_{int(time.time())}"),
                    description=ms_data.get("description", ""),
                    target_date=ms_data.get("target_date", time.time() + 86400),
                    dependencies=ms_data.get("dependencies", []),
                    assigned_to=ms_data.get("assigned_to", []),
                    metadata=ms_data.get("metadata", {})
                )
                timeline.milestones.append(milestone)
                self.dependency_graph[milestone.milestone_id] = milestone.dependencies

        # Actualizar fase actual
        if "current_phase" in data:
            timeline.current_phase = data["current_phase"]

        # Recalcular progreso basado en hitos completados
        self._calculate_progress(timeline)

        return {
            "status": "updated",
            "timeline_id": timeline.timeline_id,
            "project_id": timeline.project_id,
            "season_id": timeline.season_id,
            "milestones_count": len(timeline.milestones),
            "progress": timeline.overall_progress,
            "current_phase": timeline.current_phase
        }

    def _query_timeline(
        self,
        data: dict[str, Any],
        timeline_key: str
    ) -> dict[str, Any]:
        """Consulta el estado actual de una línea de tiempo."""
        if timeline_key not in self.timelines:
            return {
                "status": "error",
                "message": f"Timeline not found for key: {timeline_key}"
            }

        timeline = self.timelines[timeline_key]

        # Obtener hitos pendientes, en progreso y completados
        pending = [m for m in timeline.milestones if m.status == TimelineStatus.PLANNING]
        in_progress = [m for m in timeline.milestones if m.status == TimelineStatus.IN_PROGRESS]
        completed = [m for m in timeline.milestones if m.status == TimelineStatus.COMPLETED]
        blocked = [m for m in timeline.milestones if m.status == TimelineStatus.BLOCKED]

        return {
            "status": "success",
            "timeline_id": timeline.timeline_id,
            "project_id": timeline.project_id,
            "season_id": timeline.season_id,
            "title": timeline.title,
            "description": timeline.description,
            "overall_progress": timeline.overall_progress,
            "current_phase": timeline.current_phase,
            "timeline_status": timeline.status.value,
            "milestones": {
                "total": len(timeline.milestones),
                "pending": len(pending),
                "in_progress": len(in_progress),
                "completed": len(completed),
                "blocked": len(blocked)
            },
            "next_milestones": [
                {
                    "id": m.milestone_id,
                    "description": m.description,
                    "target_date": m.target_date,
                    "assigned_to": m.assigned_to
                }
                for m in sorted(pending, key=lambda x: x.target_date)[:3]  # próximos 3
            ],
            "recently_completed": [
                {
                    "id": m.milestone_id,
                    "description": m.description,
                    "completed_date": m.completed_date
                }
                for m in sorted(completed, key=lambda x: x.completed_date or 0, reverse=True)[:3]
            ]
        }

    def _identify_blocked_items(
        self,
        data: dict[str, Any],
        timeline_key: str
    ) -> dict[str, Any]:
        """Identifica hitos bloqueados y sus dependencias no cumplidas."""
        if timeline_key not in self.timelines:
            return {
                "status": "error",
                "message": f"Timeline not found for key: {timeline_key}"
            }

        timeline = self.timelines[timeline_key]
        blocked_milestones = []

        for milestone in timeline.milestones:
            if milestone.status == TimelineStatus.BLOCKED:
                # Verificar qué dependencias no están completadas
                unmet_deps = []
                for dep_id in milestone.dependencies:
                    dep_milestone = next((m for m in timeline.milestones if m.milestone_id == dep_id), None)
                    if not dep_milestone or dep_milestone.status != TimelineStatus.COMPLETED:
                        unmet_deps.append(dep_id)

                blocked_milestones.append({
                    "milestone_id": milestone.milestone_id,
                    "description": milestone.description,
                    "unmet_dependencies": unmet_deps,
                    "assigned_to": milestone.assigned_to,
                    "target_date": milestone.target_date
                })

        return {
            "status": "success",
            "blocked_count": len(blocked_milestones),
            "blocked_milestones": blocked_milestones,
            "recommendations": self._get_unblocking_recommendations(blocked_milestones, timeline)
        }

    def _advance_timeline(
        self,
        data: dict[str, Any],
        timeline_key: str
    ) -> dict[str, Any]:
        """Avanza la línea de tiempo marcando hitos como completados."""
        if timeline_key not in self.timelines:
            return {
                "status": "error",
                "message": f"Timeline not found for key: {timeline_key}"
            }

        timeline = self.timelines[timeline_key]
        completed_milestone_ids = data.get("completed_milestones", [])

        newly_completed = []
        for milestone_id in completed_milestone_ids:
            milestone = next((m for m in timeline.milestones if m.milestone_id == milestone_id), None)
            if milestone and milestone.status != TimelineStatus.COMPLETED:
                milestone.status = TimelineStatus.COMPLETED
                milestone.completed_date = time.time()
                newly_completed.append(milestone_id)

        # Recalcular progreso
        self._calculate_progress(timeline)

        # Verificar si podemos avanzar hitos bloqueados cuyos dependientes están ahora completados
        newly_unblocked = []
        for milestone in timeline.milestones:
            if milestone.status == TimelineStatus.BLOCKED:
                # Verificar si todas las dependencias están completadas
                all_deps_complete = all(
                    any(m.milestone_id == dep_id and m.status == TimelineStatus.COMPLETED
                        for m in timeline.milestones)
                    for dep_id in milestone.dependencies
                )
                if all_deps_complete:
                    milestone.status = TimelineStatus.IN_PROGRESS
                    newly_unblocked.append(milestone.milestone_id)

        return {
            "status": "advanced",
            "timeline_id": timeline.timeline_id,
            "project_id": timeline.project_id,
            "season_id": timeline.season_id,
            "newly_completed": newly_completed,
            "newly_unblocked": newly_unblocked,
            "progress": timeline.overall_progress,
            "message": f"Advanced {len(newly_completed)} milestones, unblocked {len(newly_unblocked)}"
        }

    def _calculate_progress(self, timeline: MasterTimeline) -> None:
        """Calcula el progreso general basado en hitos completados."""
        if not timeline.milestones:
            timeline.overall_progress = 0.0
            return

        completed_count = sum(1 for m in timeline.milestones if m.status == TimelineStatus.COMPLETED)
        timeline.overall_progress = (completed_count / len(timeline.milestones)) * 100

        # Actualizar estado basado en progreso
        if timeline.overall_progress >= 100:
            timeline.status = TimelineStatus.COMPLETED
        elif timeline.overall_progress > 0:
            timeline.status = TimelineStatus.IN_PROGRESS
        else:
            timeline.status = TimelineStatus.PLANNING

    def _get_unblocking_recommendations(
        self,
        blocked_milestones: list[dict],
        timeline: MasterTimeline
    ) -> list[str]:
        """Genera recomendaciones para desbloquear hitos."""
        recommendations = []

        # Contar dependencias más comunes que no están completadas
        dep_counter = {}
        for ms in blocked_milestones:
            for dep_id in ms.get("unmet_dependencies", []):
                dep_counter[dep_id] = dep_counter.get(dep_id, 0) + 1

        # Las dependencias más frecuentemente faltantes son candidatos para priorizar
        if dep_counter:
            most_common_dep = max(dep_counter.items(), key=lambda x: x[1])[0]
            dep_milestone = next((m for m in timeline.milestones if m.milestone_id == most_common_dep), None)
            if dep_milestone:
                recommendations.append(
                    f"Priorizar completion de hito '{dep_milestone.description}' "
                    f"(ID: {most_common_dep}) para desbloquear {dep_counter[most_common_dep]} hitos dependientes"
                )

        # Recomendación general
        if len(blocked_milestones) > 3:
            recommendations.append(
                f"Considere una revisión de línea de tiempo - {len(blocked_milestones)} hitos bloqueados simultáneamente"
            )

        if not recommendations:
            recommendations.append("Resolver dependencias de hitos bloqueados para continuar progreso")

        return recommendations

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta el agente de línea de tiempo maestra."""
        return self.process(input_data)


# Funciones de conveniencia
def create_master_timeline(
    project_id: str,
    season_id: str | None = None,
    title: str | None = None,
    description: str = "",
    initial_milestones: list[dict] | None = None
) -> dict[str, Any]:
    """
    Función de conveniencia para crear una línea de tiempo maestra.
    """
    agent = MasterTimelineAgent()
    return agent.run({
        "action": "create",
        "project_id": project_id,
        "season_id": season_id,
        "title": title or f"Timeline for {project_id}",
        "description": description,
        "initial_milestones": initial_milestones or []
    })


def get_timeline_status(
    project_id: str,
    season_id: str | None = None
) -> dict[str, Any]:
    """
    Función de conveniencia para consultar el estado de una línea de tiempo.
    """
    agent = MasterTimelineAgent()
    return agent.run({
        "action": "query",
        "project_id": project_id,
        "season_id": season_id
    })
