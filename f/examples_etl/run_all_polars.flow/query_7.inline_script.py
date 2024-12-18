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
    part_uri = "s3://{}/tpc-h/{}/raw/{}".format(bucket, scale_factor, "part.parquet")

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_7.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(lineitem_uri, mode="rb") as lineitem_ipt,
        s3.open(part_uri, mode="rb") as part_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        lineitem = pl.read_parquet(lineitem_ipt).lazy()
        part = pl.read_parquet(part_ipt).lazy()

        output_df = (
            lineitem.join(part, left_on="L_PARTKEY", right_on="P_PARTKEY")
            .filter(pl.col("L_SHIPDATE") >= datetime.datetime(1995, 9, 1))
            .filter(
                pl.col("L_SHIPDATE")
                < datetime.datetime(1995, 9, 1) + datetime.timedelta(days=30)
            )
            .select(
                [
                    (
                        100
                        * (
                            pl.when(pl.col("P_TYPE").str.starts_with("PROMO"))
                            .then(
                                pl.col("L_EXTENDEDPRICE") * (1 - pl.col("L_DISCOUNT"))
                            )
                            .otherwise(0)
                        ).sum()
                        / (pl.col("L_EXTENDEDPRICE") * (1 - pl.col("L_DISCOUNT"))).sum()
                    ).alias("PROMO_REVENUE")
                ]
            )
            .collect()
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
