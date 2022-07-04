## Script for getting billing data from AWS Cost Explorer  
## How to use  
### Install dependencies

```python
pip3 install -r requirements.txt 
```
### To use AWS profile (profile must be configured)
```python
python3 ./get_bill.py --profile=rei-prod --start='2022-01-01' --end='2022-06-01'
```

### To use role
```python
python3 ./get_bill.py --role='arn:aws:iam::948691256895:role/su-get-bill-data-access' --start='2022-01-01' --end='2022-06-01'
```

### Script arguments
| Name                 | Description    | Default    |
| -------------------  | ---------------|------------|
| `--profile`          | AWS profile to get access to the Cost Explorer | default |
| `--profile`          | The default AWS Region to use | eu-west-2 |
| `--role_arn`         | AWS role to get access to the Cost Explorer | none |
| `--start`            | The beginning of the time period | 2022-01-01 |
| `--end`              | The end of the time period | 2022-06-01 |