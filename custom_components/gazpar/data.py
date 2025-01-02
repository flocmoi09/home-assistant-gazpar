"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import WebLoginSource
    from .coordinator import GazparDataUpdateCoordinator


type GazparConfigEntry = ConfigEntry[GazparData]


@dataclass
class GazparData:
    """Data for the Blueprint integration."""

    client: WebLoginSource
    coordinator: GazparDataUpdateCoordinator
    integration: Integration