#requirements:
#polars==0.19.19
#wmill>=0.218.1
#s3fs==2023.12.0
import wmill
import polars as pl
import s3fs
import os

s3object = dict


def main(scale_factor: str, s3_file: s3object):
    table_name = os.path.basename(s3_file["s3"]).replace(".csv", "")
    print("Importing file '{}' into table '{}'".format(s3_file["s3"], table_name))

    s3_resource_path = "f/examples_etl/windmill-cloud-demo"
    s3 = s3fs.S3FileSystem(
        **wmill.polars_connection_settings(s3_resource_path)["s3fs_args"]
    )
    bucket = wmill.get_resource(s3_resource_path)["bucket"]

    input_uri = "s3://{}/{}".format(bucket, s3_file["s3"])
    output_filename = "tpc-h/{}/raw/{}.parquet".format(scale_factor, table_name)
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    print("Downloading CSV file to local filesystem")
    local_csv_file_path = "./file_tmp.csv"
    s3.download(input_uri, local_csv_file_path)

    print("Writing DataFrame to parquet file on local filesystem")
    input_df = pl.scan_csv(
        local_csv_file_path,
        separator="|",
        has_header=False,
        schema=get_schema(table_name),
    )
    local_parquet_file_path = "./file_tmp.parquet"
    input_df.sink_parquet(local_parquet_file_path)

    print("Uploading parquet file to S3")
    # s3.upload(local_parquet_file_path, output_uri)

    print("Cleanup")
    os.remove(local_csv_file_path)
    os.remove(local_parquet_file_path)

    return s3object({"s3": output_filename})


def get_schema(table_name: str):
    schema = {
        "nation": {
            "N_NATIONKEY": pl.Int64,
            "N_NAME": pl.Utf8,
            "N_REGIONKEY": pl.Int64,
            "N_COMMENT": pl.Utf8,
        },
        "region": {
            "R_REGIONKEY": pl.Int64,
            "R_NAME": pl.Utf8,
            "R_COMMENT": pl.Utf8,
        },
        "part": {
            "P_PARTKEY": pl.Int64,
            "P_NAME": pl.Utf8,
            "P_MFGR": pl.Utf8,
            "P_BRAND": pl.Utf8,
            "P_TYPE": pl.Utf8,
            "P_SIZE": pl.Int64,
            "P_CONTAINER": pl.Utf8,
            "P_RETAILPRICE": pl.Float64,
            "P_COMMENT": pl.Utf8,
        },
        "supplier": {
            "S_SUPPKEY": pl.Int64,
            "S_NAME": pl.Utf8,
            "S_ADDRESS": pl.Utf8,
            "S_NATIONKEY": pl.Int64,
            "S_PHONE": pl.Utf8,
            "S_ACCTBAL": pl.Float64,
            "S_COMMENT": pl.Utf8,
        },
        "partsupp": {
            "PS_PARTKEY": pl.Int64,
            "PS_SUPPKEY": pl.Int64,
            "PS_AVAILQTY": pl.Int64,
            "PS_SUPPLYCOST": pl.Float64,
            "PS_COMMENT": pl.Utf8,
        },
        "customer": {
            "C_CUSTKEY": pl.Int64,
            "C_NAME": pl.Utf8,
            "C_ADDRESS": pl.Utf8,
            "C_NATIONKEY": pl.Int64,
            "C_PHONE": pl.Utf8,
            "C_ACCTBAL": pl.Float64,
            "C_MKTSEGMENT": pl.Utf8,
            "C_COMMENT": pl.Utf8,
        },
        "orders": {
            "O_ORDERKEY": pl.Int64,
            "O_CUSTKEY": pl.Int64,
            "O_ORDERSTATUS": pl.Utf8,
            "O_TOTALPRICE": pl.Float64,
            "O_ORDERDATE": pl.Date,
            "O_ORDERPRIORITY": pl.Utf8,
            "O_CLERK": pl.Utf8,
            "O_SHIPPRIORITY": pl.Int64,
            "O_COMMENT": pl.Utf8,
        },
        "lineitem": {
            "L_ORDERKEY": pl.Int64,
            "L_PARTKEY": pl.Int64,
            "L_SUPPKEY": pl.Int64,
            "L_LINENUMBER": pl.Int64,
            "L_QUANTITY": pl.Float64,
            "L_EXTENDEDPRICE": pl.Float64,
            "L_DISCOUNT": pl.Float64,
            "L_TAX": pl.Float64,
            "L_RETURNFLAG": pl.Utf8,
            "L_LINESTATUS": pl.Utf8,
            "L_SHIPDATE": pl.Date,
            "L_COMMITDATE": pl.Date,
            "L_RECEIPTDATE": pl.Date,
            "L_SHIPINSTRUCT": pl.Utf8,
            "L_SHIPMODE": pl.Utf8,
            "L_COMMENT": pl.Utf8,
        },
    }
    return schema[table_name]
