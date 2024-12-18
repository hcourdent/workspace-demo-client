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

    orders_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "orders.parquet"
    )
    lineitem_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "lineitem.parquet"
    )

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_6.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(lineitem_uri, mode="rb") as lineitem_ipt,
        s3.open(orders_uri, mode="rb") as orders_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        lineitem = pl.read_parquet(lineitem_ipt).lazy()
        orders = pl.read_parquet(orders_ipt).lazy()

        output_df = (
            orders.join(lineitem, left_on="O_ORDERKEY", right_on="L_ORDERKEY")
            .filter(pl.col("L_SHIPMODE").is_in(["MAIL", "SHIP"]))
            .filter(pl.col("L_SHIPDATE") < pl.col("L_COMMITDATE"))
            .filter(pl.col("L_RECEIPTDATE") >= datetime.datetime(1994, 1, 1))
            .filter(
                pl.col("L_RECEIPTDATE")
                < datetime.datetime(1994, 1, 1) + datetime.timedelta(days=365)
            )
            .group_by(["L_SHIPMODE"])
            .agg(
                [
                    (
                        pl.when(pl.col("O_ORDERPRIORITY").is_in(["1-URGENT", "2-HIGH"]))
                        .then(1)
                        .otherwise(0)
                    )
                    .sum()
                    .alias("HIGH_LINE_COUNT"),
                    (
                        pl.when(
                            pl.col("O_ORDERPRIORITY")
                            .is_in(["1-URGENT", "2-HIGH"])
                            .not_()
                        )
                        .then(1)
                        .otherwise(0)
                    )
                    .sum()
                    .alias("LOW_LINE_COUNT"),
                ]
            )
            .sort("L_SHIPMODE")
            .collect()
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
