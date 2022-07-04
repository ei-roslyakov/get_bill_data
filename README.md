## Script for getting billing data from AWS Cost Explorer  
## How to use  
### Install dependencies

```python
pip3 install -r requirements.txt 
```
### Run the script
```python
python3 ./get_bill.py --profile=rei-prod --start='2022-01-01' --end='2022-06-01'
```

### Script arguments
| Name                 | Description    | Default    |
| -------------------  | ---------------|------------|
| `--profile`          | AWS profile to get access to the Cost Explorer | default |
| `--role_arn`         | AWS role to get access to the Cost Explorer | none |
| `--start`            | The beginning of the time period | 2022-01-01 |
| `--end`              | The end of the time period | 2022-06-01 |