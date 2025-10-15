"""Coordinator for AWS Cost integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .aws_cost import AWSCostExplorer
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AWSCostDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AWS Cost data from the AWS Cost Explorer API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""

        aws_access_key_id = config_entry.data["aws_access_key_id"]
        aws_secret_access_key = config_entry.data["aws_secret_access_key"]
        region_name = config_entry.data["region_name"]

        self.client = AWSCostExplorer(
            aws_access_key_id, aws_secret_access_key, region_name
        )

        if config_entry.data["update_frequency"] == "Every 6 hours":
            frequency = timedelta(hours=6)
        elif config_entry.data["update_frequency"] == "Every 12 hours":
            frequency = timedelta(hours=12)
        else:
            frequency = timedelta(hours=24)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=frequency,
        )

    async def _async_update_data(self):
        """Fetch data from AWS Cost Explorer API."""
        try:
            month_to_date = await self.hass.async_add_executor_job(
                self.client.get_month_to_date_cost
            )

            _LOGGER.debug("Month to date cost: %s", month_to_date[0])

            forecast = await self.hass.async_add_executor_job(
                self.client.get_cost_forecast
            )

            _LOGGER.debug("Forecast: %s", forecast)

            last_month = await self.hass.async_add_executor_job(
                self.client.get_last_month_cost
            )

            _LOGGER.debug("Last month cost: %s", last_month[0])

            return {
                "month_to_date": month_to_date[0],
                "forecast": forecast[0],
                "last_month": last_month[0],
                "currency": month_to_date[1],
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
