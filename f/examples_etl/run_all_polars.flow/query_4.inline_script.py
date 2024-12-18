#requirements:
#polars==0.19.19
#wmill>=0.218.1
#s3fs==2023.12.0
import wmill
import polars as pl
import s3fs
import datetime

s3object = dict


def main(scale_factor: str):
    s3_resource_path = "f/examples_etl/windmill-cloud-demo"
    s3 = s3fs.S3FileSystem(
        **wmill.polars_connection_settings(s3_resource_path)["s3fs_args"]
    )
    bucket = wmill.get_resource(s3_resource_path)["bucket"]

    lineitem_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "lineitem.parquet"
    )

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_4.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(lineitem_uri, mode="rb") as lineitem_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        lineitem = pl.read_parquet(lineitem_ipt).lazy()

        output_df = (
            lineitem.filter(pl.col("L_SHIPDATE") >= datetime.datetime(1994, 1, 1))
            .filter(
                pl.col("L_SHIPDATE")
                < datetime.datetime(1994, 1, 1) + datetime.timedelta(days=365)
            )
            .filter((pl.col("L_DISCOUNT").is_between(0.06 - 0.01, 0.06 + 0.01)))
            .filter(pl.col("L_QUANTITY") < 24)
            .select(
                [(pl.col("L_EXTENDEDPRICE") * pl.col("L_DISCOUNT")).alias("REVENUE")]
            )
            .sum()
            .collect()
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
