import argparse
import os.path

import boto3

from botocore.exceptions import ClientError

import loguru

import pandas as pd

from terminaltables import AsciiTable

logger = loguru.logger


def parse_args():
    parsers = argparse.ArgumentParser()

    parsers.add_argument(
        "--profile",
        required=False,
        type=str,
        default="default",
        action="store",
        help="AWS Profile"
    )
    parsers.add_argument(
        "--project",
        required=False,
        type=str,
        default="no_name",
        action="store",
        help="The project name"
    )
    parsers.add_argument(
        "--report",
        required=False,
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="If true, will create exel report in folder report"
    )
    parsers.add_argument(
        "--region",
        required=False,
        type=str,
        default="eu-west-2",
        action="store",
        help="AWS Profile"
    )
    parsers.add_argument(
        "--role",
        required=False,
        type=str,
        action="store",
        help="AWS Profile"
    )
    parsers.add_argument(
        "--start",
        required=False,
        type=str,
        default="2022-01-01",
        action="store",
        help="The beginning of the time period"
    )
    parsers.add_argument(
        "--end",
        required=False,
        type=str,
        default="2022-06-01",
        action="store",
        help="The end of the time period"
    )

    return parsers.parse_args()


def client_profile(profile, region):

    session = boto3.Session(profile_name=profile, region_name=region)
    ce_client = session.client("ce")

    return ce_client


def client_role(role, region):

    sts_client = boto3.client("sts")
    assumed_role = sts_client.assume_role(
        RoleArn=role,
        RoleSessionName="AssumeRoleSession1",
        DurationSeconds=1800
    )
    session = boto3.Session(
        aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
        aws_session_token=assumed_role["Credentials"]["SessionToken"],
        region_name=region
    )
    ce_client = session.client("ce")

    return ce_client


def get_bill_by_period(ce_client, start: str, end: str) -> list:

    logger.info(f"Getting data for period {start} - {end}")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod = {
                "Start": start,
                "End":  end },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
        )
        return response
    except ClientError as e:
        logger.exception(f"Something went wrong {e.response['Error']['Message']}")


def get_bill_by_period_per_service(ce_client, start: str, end: str) -> list:

    logger.info(f"Getting data for period {start} - {end}")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod = {
                "Start": start,
                "End":  end },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy = [
                {
                    "Type": "DIMENSION",
                    "Key": "SERVICE"
                }
            ]
        )
        return response
    except ClientError as e:
        logger.exception(f"Something went wrong {e.response['Error']['Message']}")


def pretty_console_output_bill_by_period(data: list) -> None:

    header = ["TimePeriod", "Total"]
    ordered_data = [header]

    for item in data["ResultsByTime"]:
        data_to_write = [f"{item['TimePeriod']['Start']} - {item['TimePeriod']['End']}", item["Total"]["BlendedCost"]["Amount"]]
        ordered_data.append(data_to_write)

    table = AsciiTable(ordered_data)
    table.inner_row_border = True

    print(table.table)


def pretty_console_output_bill_by_period_per_service(data: list) -> None:

    header = ["Service", "Total", "Unit", "TimePeriod"]

    for item in data["ResultsByTime"]:
        ordered_data = [header]
        time_period = f"{item['TimePeriod']['Start']} - {item['TimePeriod']['End']}"
        for item in item["Groups"]:
            data_to_write = [
                item["Keys"][0],
                item["Metrics"]["BlendedCost"]["Amount"],
                item["Metrics"]["BlendedCost"]["Unit"],
                time_period
            ]
            ordered_data.append(data_to_write)
        table = AsciiTable(ordered_data)
        table.inner_row_border = False

        print(table.table)


def write_data(project: str, data: list) -> None:

    ordered_data = []
    time_period = None

    for item in data["ResultsByTime"]:
        time_period = f"{item['TimePeriod']['Start']} - {item['TimePeriod']['End']}"
        time_period = time_period
        for item in item["Groups"]:
            data_to_write = {
                "Service" : item["Keys"][0],
                "Total" : item["Metrics"]["BlendedCost"]["Amount"],
                "Unit" : item["Metrics"]["BlendedCost"]["Unit"],
                "TimePeriod" : time_period
            }
            ordered_data.append(data_to_write)

    df = pd.DataFrame(ordered_data)

    if not os.path.exists(f"./report/{project}.xlsx"):
        logger.info("File is missing, I will create one for you")
        with pd.ExcelWriter(f"./report/{project}.xlsx", engine="openpyxl",) as writer:
            df.to_excel(writer, sheet_name=time_period)
    else:
        with pd.ExcelWriter(f"./report/{project}.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=time_period)


def main():

    logger.info("Application started")
    args = parse_args()

    try:
        if args.role:
            ce_client = client_role(args.role, args.region)
        else:
            ce_client = client_profile(args.profile, args.region)
    except ClientError as e:
        logger.exception(f"Something went wrong {e}")

    data = get_bill_by_period(ce_client, args.start, args.end)
    pretty_console_output_bill_by_period(data)

    data_per_service = get_bill_by_period_per_service(ce_client, args.start, args.end)
    pretty_console_output_bill_by_period_per_service(data_per_service)

    if args.report:
        write_data(args.project, data_per_service)

    logger.info("Application finished")


if __name__ == "__main__":
    main()
