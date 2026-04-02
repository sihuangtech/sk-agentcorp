"""
SK AgentCorp — Role Registry & Loader

Loads role definitions from YAML files in the roles/ directory.
Provides a typed role registry for the crew builder to use.
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from backend.config import get_settings

logger = logging.getLogger(__name__)


class RoleDefinition:
    """A parsed role definition from YAML."""

    def __init__(self, data: dict[str, Any], file_path: str = ""):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.title: str = data.get("title", "")
        self.department: str = data.get("department", "general")
        self.description: str = data.get("description", "")
        self.system_prompt: str = data.get("system_prompt", "")
        self.backstory: str = data.get("backstory", "")
        self.tools: list[str] = data.get("tools", [])
        self.reports_to: str = data.get("reports_to", "")
        self.default_llm_provider: str = data.get("default_llm_provider", "")
        self.default_llm_model: str = data.get("default_llm_model", "")
        self.category: str = data.get("category", "")
        self.skills: list[str] = data.get("skills", [])
        self.responsibilities: list[str] = data.get("responsibilities", [])
        self.file_path = file_path

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "department": self.department,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "backstory": self.backstory,
            "tools": self.tools,
            "reports_to": self.reports_to,
            "default_llm_provider": self.default_llm_provider,
            "default_llm_model": self.default_llm_model,
            "category": self.category,
            "skills": self.skills,
            "responsibilities": self.responsibilities,
        }


class RoleRegistry:
    """
    Registry of all available agent roles.

    Loads YAML files recursively from the roles/ directory on init.
    """

    def __init__(self, roles_dir: str | None = None):
        self.roles: dict[str, RoleDefinition] = {}
        roles_path = Path(roles_dir) if roles_dir else Path(get_settings().roles_dir)
        self._load_roles(roles_path)

    def _load_roles(self, roles_path: Path) -> None:
        """Recursively load all .yaml/.yml files from the roles directory."""
        if not roles_path.exists():
            logger.warning(f"Roles directory not found: {roles_path}")
            return

        for yaml_file in sorted(roles_path.rglob("*.yaml")):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if data and isinstance(data, dict) and "id" in data:
                    role = RoleDefinition(data, str(yaml_file))
                    self.roles[role.id] = role
                    logger.debug(f"Loaded role: {role.id} ({role.name})")
            except Exception as e:
                logger.error(f"Failed to load role from {yaml_file}: {e}")

        for yaml_file in sorted(roles_path.rglob("*.yml")):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if data and isinstance(data, dict) and "id" in data:
                    role = RoleDefinition(data, str(yaml_file))
                    self.roles[role.id] = role
            except Exception as e:
                logger.error(f"Failed to load role from {yaml_file}: {e}")

        logger.info(f"Loaded {len(self.roles)} roles from {roles_path}")

    def get_role(self, role_id: str) -> dict[str, Any] | None:
        """Get a role definition by ID."""
        role = self.roles.get(role_id)
        return role.to_dict() if role else None

    def list_roles(self) -> list[dict[str, Any]]:
        """List all available roles."""
        return [r.to_dict() for r in self.roles.values()]

    def get_roles_by_department(self, department: str) -> list[dict[str, Any]]:
        """Get all roles in a specific department."""
        return [
            r.to_dict() for r in self.roles.values()
            if r.department == department
        ]

    def get_departments(self) -> list[str]:
        """Get list of all departments."""
        return sorted(set(r.department for r in self.roles.values()))


# ── Singleton ────────────────────────────────────────────────────────

_registry: RoleRegistry | None = None


def get_role_registry() -> RoleRegistry:
    """Get or create the singleton role registry."""
    global _registry
    if _registry is None:
        _registry = RoleRegistry()
    return _registry


def reload_role_registry() -> RoleRegistry:
    """Force reload the role registry."""
    global _registry
    _registry = RoleRegistry()
    return _registry
