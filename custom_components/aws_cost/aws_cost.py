"""The Integration with AWS Cost Explorer API"""

import boto3
from datetime import date, timedelta
import logging
import calendar

_LOGGER = logging.getLogger(__name__)


class AWSCostExplorer:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        _LOGGER.debug(
            "Initializing AWSCostClient with AWS access key: %s and region: %s",
            aws_access_key_id,
            region_name,
        )

        self.client = boto3.client(
            "ce",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def get_month_to_date_cost(self):
        """Interacts with GetCostAndUsage operation from AWS Cost Explorer API"""
        try:
            start = str(date.today().replace(day=1))

            if (
                date.today().day
                == calendar.monthrange(date.today().year, date.today().month)[1]
            ):
                end = str(date.today())
            else:
                end = str(date.today() + timedelta(days=1))

            _LOGGER.debug("######### Start: %s", start)
            _LOGGER.debug("######### End: %s", end)

            response = self.client.get_cost_and_usage(
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metrics=["BlendedCost"],
            )

            _LOGGER.debug("Received response from AWS Cost Explorer: %s", response)

            amount = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
            currency = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Unit"]

            return amount, currency

        except Exception as e:
            _LOGGER.error(
                "Error occurred while fetching month to date cost data: %s", e
            )

    def get_cost_forecast(self):
        """Interacts with GetCostAndUsage operation from AWS Cost Explorer API"""
        try:
            if (
                date.today().day
                == calendar.monthrange(date.today().year, date.today().month)[1]
            ):
                start = str(date.today() - timedelta(days=1))
            else:
                start = str(date.today())

            end = str(
                date.today().replace(
                    day=calendar.monthrange(date.today().year, date.today().month)[1]
                )
            )

            _LOGGER.debug("######### Start: %s", start)
            _LOGGER.debug("######### End: %s", end)

            response = self.client.get_cost_forecast(
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metric="BLENDED_COST",
            )

            _LOGGER.debug(
                "Received response from AWS Cost Explorer Forecast: %s", response
            )
            amount = response["Total"]["Amount"]
            currency = response["Total"]["Unit"]

            return amount, currency
        except Exception as e:
            _LOGGER.error("Error occurred while fetching forecast cost data: %s", e)

    def get_last_month_cost(self):
        """Gets the cost for the previous month"""
        try:
            # Calculate the first day of last month
            today = date.today()
            first_day_current_month = today.replace(day=1)
            last_day_last_month = first_day_current_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)

            start = str(first_day_last_month)
            end = str(first_day_current_month)

            _LOGGER.debug("######### Last Month Start: %s", start)
            _LOGGER.debug("######### Last Month End: %s", end)

            response = self.client.get_cost_and_usage(
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metrics=["BlendedCost"],
            )

            _LOGGER.debug(
                "Received response from AWS Cost Explorer for last month: %s", response
            )

            amount = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
            currency = response["ResultsByTime"][0]["Total"]["BlendedCost"]["Unit"]

            return amount, currency

        except Exception as e:
            _LOGGER.error("Error occurred while fetching last month cost data: %s", e)
