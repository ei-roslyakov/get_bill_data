import argparse
import os.path

import boto3

from botocore.exceptions import ClientError

import loguru

import pandas as pd

from terminaltables import AsciiTable

logger = loguru.logger


REPORT_FILE_NAME = "report"


def parse_args():
    parsers = argparse.ArgumentParser()

    parsers.add_argument(
        "--profile",
        required=False,
        type=str,
        default="default",
        action="store",
        help="AWS Profile",
    )
    parsers.add_argument(
        "--report-to-file",
        required=False,
        type=bool,
        default=True,
        action=argparse.BooleanOptionalAction,
        help="If true, will create exel report in folder report",
    )
    parsers.add_argument(
        "--report-to-console",
        required=False,
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="If true, will create exel report in folder report",
    )
    parsers.add_argument(
        "--region",
        required=False,
        type=str,
        default="eu-west-2",
        action="store",
        help="AWS Profile",
    )
    parsers.add_argument(
        "--month", required=False, type=str, default="01", action="store", help="Month"
    )
    parsers.add_argument(
        "--year",
        required=False,
        type=str,
        default="2022",
        action="store",
        help="The beginning of the time period",
    )

    return parsers.parse_args()


def client_profile(profile, region: str):

    session = boto3.Session(profile_name=profile, region_name=region)
    ce_client = session.client("ce")

    return ce_client


def client_role(acc_id: str, region: str):

    sts_client = boto3.client("sts")
    assumed_role = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{acc_id}:role/su-get-bill-data-access",
        RoleSessionName="AssumeRoleSession1",
        DurationSeconds=1800,
    )
    session = boto3.Session(
        aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
        aws_session_token=assumed_role["Credentials"]["SessionToken"],
        region_name=region,
    )
    ce_client = session.client("ce")

    return ce_client


def get_bill_by_period(ce_client, start: str, end: str, project="NoN") -> list:

    logger.info(f"{project}: Getting data for period {start} - {end}")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
        )
        return response
    except ClientError as e:
        logger.exception(f"Something went wrong {e.response['Error']['Message']}")


def get_bill_by_period_per_service(
    ce_client, start: str, end: str, project="NoN"
) -> list:

    logger.info(f"{project}: Getting data for period {start} - {end}")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
        return response
    except ClientError as e:
        logger.exception(f"Something went wrong {e.response['Error']['Message']}")


def pretty_console_output_bill_by_period(project_name: str, data: list) -> None:

    header = ["ProjectName", "TimePeriod", "Amount", "Unit"]
    ordered_data = [header]

    def symbol_replace(text):
        return text.replace("-", ":")

    for item in data["ResultsByTime"]:
        data_to_write = [
            project_name,
            f"{symbol_replace(item['TimePeriod']['Start'])}-{symbol_replace(item['TimePeriod']['End'])}",
            round(float(item["Total"]["BlendedCost"]["Amount"]), 2),
            item["Total"]["BlendedCost"]["Unit"],
        ]
        ordered_data.append(data_to_write)

    table = AsciiTable(ordered_data)
    table.inner_row_border = True

    print(table.table)


def pretty_console_output_bill_by_period_per_service(data: list) -> None:

    header = ["Service", "Total", "Unit", "TimePeriod"]

    for item in data["ResultsByTime"]:
        ordered_data = [header]
        time_period = f"{item['TimePeriod']['Start']} - {item['TimePeriod']['End']}"
        for resource in item["Groups"]:
            data_to_write = [
                resource["Keys"][0],
                round(float(resource["Metrics"]["BlendedCost"]["Amount"]), 2),
                resource["Metrics"]["BlendedCost"]["Unit"],
                time_period,
            ]
            ordered_data.append(data_to_write)
        table = AsciiTable(ordered_data)
        table.inner_row_border = False

        print(table.table)


def get_date_range(year: str, month: str):

    suitable_value_for_month = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ]

    if month not in suitable_value_for_month:
        logger.exception(
            f"You have provided the wrong month number {month}, available values are {suitable_value_for_month} "
        )
        exit(1)

    if month == "01":
        start = f"{int(year) - 1}-12-01"
        end = f"{year}-{month}-01"

        return {"start": start, "end": end}

    if month != "01":
        start = f"{year}-0{int(month) - 1}-01"
        end = f"{year}-{month}-01"

        return {"start": start, "end": end}


def make_report(year: str, month: str, region: str):

    date_range = get_date_range(year, month)

    df = pd.read_excel(f"report/{REPORT_FILE_NAME}.xlsx")

    data_to_write = []
    for item in df.to_dict("records"):
        try:
            ce_client = client_role(item["AccountID"], region)
            data = get_bill_by_period(
                ce_client, date_range["start"], date_range["end"], item["AccountName"]
            )
            for amount_value in data["ResultsByTime"]:
                item[f"{year}-{month}"] = round(
                    float(amount_value["Total"]["BlendedCost"]["Amount"]), 2
                )
                data_to_write.append(item)
        except ClientError as e:
            logger.exception(f"Something went wrong {e.response['Error']['Message']}")
        except Exception as e:
            logger.exception(f"Something went wrong {e}")

    df = pd.DataFrame(data_to_write)

    try:
        logger.info("Making file backup")
        os.rename(
            f"report/{REPORT_FILE_NAME}.xlsx", f"report/{REPORT_FILE_NAME}-backup.xlsx"
        )
        with pd.ExcelWriter(
            f"report/{REPORT_FILE_NAME}.xlsx", engine="xlsxwriter"
        ) as writer:
            df.to_excel(writer, sheet_name=year, index=False)
            for column in df:
                column_width = (
                    max(df[column].astype(str).map(len).max(), len(column)) + 3
                )
                col_idx = df.columns.get_loc(column)
                writer.sheets[f"{year}"].set_column(col_idx, col_idx, column_width)

            workbook = writer.book
            worksheet = writer.sheets[year]
            position = 0

            for item in range(len(data_to_write)):
                chart = workbook.add_chart({"type": "line"})
                chart.add_series(
                    {
                        "categories": [f"{year}", 0, 2, 0, 15],
                        "values": [f"{year}", 1 + item, 2, 1 + item, 15],
                        "name": f"{df['AccountName'].values[item]}",
                        "line": {"color": "red"},
                    }
                )
                chart.set_x_axis({"name": "Month", "position_axis": "on_tick"})
                chart.set_y_axis(
                    {"name": "Price", "major_gridlines": {"visible": False}}
                )
                chart.set_legend({"position": "none"})
                worksheet.insert_chart(f"O{20 + position}", chart)
                position += 2

    except Exception as e:
        logger.exception(f"Something went wrong {e}")


def main():

    logger.info("Application started")
    args = parse_args()

    if args.report_to_console:
        try:
            ce_client = client_profile(args.profile, args.region)

            date_range = get_date_range(args.year, args.month)
            data = get_bill_by_period(ce_client, date_range["start"], date_range["end"])
            pretty_console_output_bill_by_period(args.profile, data)

            data_per_service = get_bill_by_period_per_service(
                ce_client, date_range["start"], date_range["end"]
            )
            pretty_console_output_bill_by_period_per_service(data_per_service)
        except Exception as e:
            logger.exception(f"Something went wrong {e}")

    if args.report_to_file:
        make_report(args.year, args.month, args.region)

    logger.info("Application finished")


if __name__ == "__main__":
    main()
