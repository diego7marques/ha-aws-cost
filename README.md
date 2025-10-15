# 💰 AWS Cost for Home Assistant 

The ha-aws-cost custom component interacts with AWS to get the month to date cost and forecast cost and make it available on Home Assistant. It adds three new entities:

* **Month to date cost:** The current cost of your AWS account 
* **Forecasted month costs:** The forecasted cost based in your current consumption 
* **Last month costs:** The cost of the last closed month

It was created to give you easy access to the current cost of your AWS account.

## Pre-requirements
1. You'll need an 'Access Key ID' and a 'Secret Access Key' to set the integration up. I strongly recommend you to create a new IAM user and policy with the following permissions:

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "ce:GetCostAndUsage",
                    "ce:GetCostForecast"
                ],
                "Resource": "*"
            }
        ]
    }
    ```

In case you don't know how to generate the credentials, please read the following documentation: [Managing access keys for IAM users
](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)


## Installation

### Option 1: HACS

First, install the custom integration using [HACS](https://hacs.xyz/).

1. Add the integration using HACS
2. Restart Home Assistant

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=diego7marques&repository=ha-aws-cost&category=integration)

### Option 2: Manual installation

1. Download and copy the `custom_components/aws_cost` directory into the `custom_components` folder on your home assistant installation.

2. Restart Home Assistant

## Setup

Once installed, go to `Settings > Devices & services > + Add integration > AWS Cost`. The setup will request 4 inputs:

1. **AWS Access Key ID**: _Access key generated for the IAM user._
2. **AWS Secret Access key**: _Access Secret key generated for the IAM User._
3. **AWS Region**: _Your default region. As Cost Explorer is a global resource, the region will only be used to adquire the token._
4. **Update Frequency**: _How many times you want your data to be updated a day. The options are: `Daily`, `Every 12 hours` and `Every 6 hours`._

## Considerations

* AWS charges $0.01 for any request done to AWS Cost Explorer API. For more information: [AWS Cost Explorer Pricing](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/pricing/#:~:text=Cost%20Explorer%20offers%20hourly%20granularity,specific%20resource%20and%20usage%20type.)

    _NOTE: Each pooling to update the entity state makes two requests to AWS CostExplorer API, using the `GetCostandUsage` and `GetCostForecast` operations._

* The costs shown may not always be up-to-date, as AWS explains:

    >"Cost Explorer refreshes your cost data at least once every 24 hours. However, this depends on your upstream data from your billing applications, and some data might be updated later than 24 hours."

    Reference: [Analyzing your costs with AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)

## Example cards
![image](https://github.com/user-attachments/assets/cc7aaaf2-b72a-435b-845d-2f02a85b16af)

<details>
  <summary>🔧 Code</summary>
    
  ```yaml
  type: horizontal-stack
  cards:
    - type: custom:mini-graph-card
      name: AWS Cost
      entities:
        - entity: sensor.month_to_date_cost
          name: Cost
      icon: mdi:aws
      hours_to_show: 72
      show:
        icon: true
        name: true
        state: true
        legend: false
    - type: custom:mini-graph-card
      name: AWS Forecasted Cost
      entities:
        - entity: sensor.forecasted_month_costs
          name: Forecast
      icon: mdi:aws
      hours_to_show: 72
      show:
        icon: true
        name: true
        state: true
        legend: false
  ```
</details>

![image](https://github.com/user-attachments/assets/3835c842-d036-409b-a92c-2ff1cf9e562d)

<details>
  <summary>🔧 Code</summary>
    
  ```yaml
  type: custom:mushroom-chips-card
  chips:
  - type: entity
    entity: sensor.month_to_date_cost
    icon_color: orange
    icon: mdi:aws
  ```
</details>

Cards used:
* 🍄 [Mushroom](https://github.com/piitaya/lovelace-mushroom)
* [Horizontal stack card
](https://www.home-assistant.io/dashboards/horizontal-stack/)
  
