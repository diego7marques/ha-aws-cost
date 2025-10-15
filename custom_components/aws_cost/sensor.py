# """Platform for sensor integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntryNotReady

import logging
# from typing import Any

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from homeassistant.const import CURRENCY_DOLLAR, CURRENCY_EURO

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AWSCostDataUpdateCoordinator

_LOGGING = logging.getLogger(__name__)


@dataclass(frozen=True)
class AWSCostSensorEntityDescription(SensorEntityDescription):
    """Describes an AWS Cost Explorer sensor entity."""

    state: Callable[[dict]] | None = None


SENSORS: tuple[AWSCostSensorEntityDescription, ...] = (
    AWSCostSensorEntityDescription(
        key="month_to_date_cost",
        name="Month to Date Cost",
        device_class=SensorDeviceClass.MONETARY,
        state=lambda data: round(float(data["month_to_date"]), 2),
    ),
    AWSCostSensorEntityDescription(
        key="forecasted_month_costs",
        name="Forecasted month costs",
        device_class=SensorDeviceClass.MONETARY,
        state=lambda data: round(float(data["forecast"]), 2),
    ),
)


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Set up AWS Cost sensors based on a config entry."""
    # Get coordinator from hass.data (created in __init__.py)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGING.error("Error setting up AWS Cost integration: %s", err)
        raise ConfigEntryNotReady from err

    async_add_entities(
        AWSCostSensorEntity(
            entry_id=config_entry.entry_id,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSORS
    )


class AWSCostSensorEntity(
    CoordinatorEntity[AWSCostDataUpdateCoordinator], SensorEntity
):
    """Defines an AWS Cost sensor."""

    entity_description: AWSCostSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        entry_id: str,
        coordinator: AWSCostDataUpdateCoordinator,
        entity_description: AWSCostSensorEntityDescription,
    ) -> None:
        """Initialize AWS Cost sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self.entity_id = f"{SENSOR_DOMAIN}.{entity_description.key}"
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="AWS",
            model="AWS Cost Explorer",
            name="AWS Cost",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://aws.amazon.com",
        )

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of the sensor."""

        if self.coordinator.data["currency"] == "EUR":
            return CURRENCY_EURO
        else:
            return CURRENCY_DOLLAR

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.state is None:
            state: StateType = self.coordinator.data[self.entity_description.key]
        else:
            state = self.entity_description.state(self.coordinator.data)

        return state
