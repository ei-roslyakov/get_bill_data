![workflow](https://github.com/ei-roslyakov/get_bill_data/actions/workflows/tests.yml/badge.svg)
## Script for getting billing data from AWS Cost Explorer  
## How to use  
### Install dependencies

```python
pip3 install -r requirements.txt 
```
### To use AWS profile (profile must be configured, this option is only available with console report )
```python
python3 ./get_bill.py --profile=rei-prod --month=06 --year=2022 --report-to-console --no-report-to-file
```

### To make report and write it to the exel file
#### This is the default behavior, the application will read information from an excel file in the folder report (first two columns) and request billing data from AWS
```python
python3 ./get_bill.py --month=06 --year=2022
```
#### this command will add a new column for each project with date and amount
![report](/files/report.jpg?raw=true "report")

### Script arguments
| Name         | Description                                       | Default    |
|--------------|---------------------------------------------------|------------|
| `--profile`  | AWS profile to get access to the Cost Explorer    | default    |
| `--role_arn` | AWS role to get access to the Cost Explorer       | none       |
| `--month`    | The report will be created for this month         | 2022-01    |
| `--year`     | The report will be created for this year          | 2022-02-01 |
| `--report-to-file`   | If true, will create exel report in folder report | False      |
| `--report-to-console`   | If true, will print report to console             | False      |


### Output example
```
+-------------------------------------+-------+------+-------------------------+
| Service                             | Total | Unit | TimePeriod              |
+-------------------------------------+-------+------+-------------------------+
| AWS Key Management Service          | 0.0   | USD  | 2022-05-01 - 2022-06-01 |
| Amazon EC2 Container Registry (ECR) | 0.0   | USD  | 2022-05-01 - 2022-06-01 |
| Amazon Elastic Load Balancing       | 4.37  | USD  | 2022-05-01 - 2022-06-01 |
| Amazon Route 53                     | 1.01  | USD  | 2022-05-01 - 2022-06-01 |
| Amazon Simple Storage Service       | 0.32  | USD  | 2022-05-01 - 2022-06-01 |
| AmazonCloudWatch                    | 0.0   | USD  | 2022-05-01 - 2022-06-01 |
| Tax                                 | 0.0   | USD  | 2022-05-01 - 2022-06-01 |
+-------------------------------------+-------+------+-------------------------+

+-------------------------------------------------+----------------+------+-------------------------+
| Service                                         | Total          | Unit | TimePeriod              |
+-------------------------------------------------+----------------+------+-------------------------+
| AWS Backup                                      | 2.4361634799   | USD  | 2022-01-01 - 2022-02-01 |
| AWS CloudTrail                                  | 0              | USD  | 2022-01-01 - 2022-02-01 |
| AWS Config                                      | 0.153          | USD  | 2022-01-01 - 2022-02-01 |
| AWS Database Migration Service                  | 31.2540844324  | USD  | 2022-01-01 - 2022-02-01 |
| AWS Elemental MediaStore                        | 0.0000000042   | USD  | 2022-01-01 - 2022-02-01 |
| AWS Global Accelerator                          | 18.8355828044  | USD  | 2022-01-01 - 2022-02-01 |
| AWS Glue                                        | 274.46503788   | USD  | 2022-01-01 - 2022-02-01 |
| AWS Key Management Service                      | 1.999999968    | USD  | 2022-01-01 - 2022-02-01 |
| AWS Lambda                                      | 0              | USD  | 2022-01-01 - 2022-02-01 |
| AWS Secrets Manager                             | 0              | USD  | 2022-01-01 - 2022-02-01 |
| AWS Step Functions                              | 0.3285653011   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon CloudFront                               | 0.00070668     | USD  | 2022-01-01 - 2022-02-01 |
| Amazon DynamoDB                                 | 0.0002785018   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon EC2 Container Registry (ECR)             | 24.9731388814  | USD  | 2022-01-01 - 2022-02-01 |
| Amazon ElastiCache                              | 273.904        | USD  | 2022-01-01 - 2022-02-01 |
| EC2 - Other                                     | 572.7215141962 | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Elastic Compute Cloud - Compute          | 1059.159626294 | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Elastic Container Service for Kubernetes | 74.4           | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Elastic File System                      | 40.4046883231  | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Elastic Load Balancing                   | 80.4935761366  | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Kinesis                                  | 29.547439959   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Kinesis Firehose                         | 0.0117946642   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon OpenSearch Service                       | 676.8555039382 | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Redshift                                 | 476.02986656   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Relational Database Service              | 517.0089863991 | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Route 53                                 | 13.485527854   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Simple Email Service                     | 0.0000006404   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Simple Notification Service              | 0.0000119502   | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Simple Queue Service                     | 0              | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Simple Storage Service                   | 293.0608485769 | USD  | 2022-01-01 - 2022-02-01 |
| Amazon Virtual Private Cloud                    | 44.6431871392  | USD  | 2022-01-01 - 2022-02-01 |
| AmazonCloudWatch                                | 62.2240749597  | USD  | 2022-01-01 - 2022-02-01 |
| Tax                                             | 913.62         | USD  | 2022-01-01 - 2022-02-01 |
+-------------------------------------------------+----------------+------+-------------------------+
```