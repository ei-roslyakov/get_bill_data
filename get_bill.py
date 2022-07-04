import argparse

import boto3

from botocore.exceptions import ClientError

import loguru

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
        default=None,
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

    assumed_role = client.assume_role(
        RoleArn=role,
        RoleSessionName="AssumeRoleSession1",
        DurationSeconds=1800
    )
    session = boto3.Session(
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken'],
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


def pretty_console_output(data: list) -> None:

    header = ["Start", "End", "Total"]
    p_data = [header]

    for item in data["ResultsByTime"]:
        data_to_write = [item["TimePeriod"]["Start"], item["TimePeriod"]["End"], item["Total"]["BlendedCost"]["Amount"]]
        p_data.append(data_to_write)

    table = AsciiTable(p_data)
    table.inner_row_border = True

    print(table.table)


def main():
    logger.info("Application started")
    args = parse_args()

    if not args.role:
        ce_client = client_profile(args.profile, args.region)
    ce_client = client_role(args.profile, args.region)

    data = get_bill_by_period(ce_client, args.start, args.end)

    pretty_console_output(data)

    logger.info("Application finished")


if __name__ == "__main__":
    main()
