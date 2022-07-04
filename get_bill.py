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
        default="rei-prod",
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


def client(profile):
    session = boto3.Session(profile_name=profile)
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
        print(item)
        data_to_write = [item["TimePeriod"]["Start"], item["TimePeriod"]["End"], item["Total"]["BlendedCost"]["Amount"]]
        p_data.append(data_to_write)

        table = AsciiTable(p_data)
        table.inner_row_border = True

        print(table.table)


def main():
    logger.info("Application started")
    args = parse_args()
    ce_client = client(args.profile)

    start_date = args.start
    end_date   = args.end

    data = get_bill_by_period(ce_client, start_date, end_date)

    pretty_console_output(data)

    logger.info("Application finished")


if __name__ == "__main__":
    main()
