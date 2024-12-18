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
    customer_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "customer.parquet"
    )
    lineitem_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "lineitem.parquet"
    )

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_2.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(lineitem_uri, mode="rb") as lineitem_ipt,
        s3.open(customer_uri, mode="rb") as customer_ipt,
        s3.open(orders_uri, mode="rb") as orders_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        lineitem = pl.read_parquet(lineitem_ipt).lazy()
        customer = pl.read_parquet(customer_ipt).lazy()
        orders = pl.read_parquet(orders_ipt).lazy()

        output_df = (
            lineitem.join(orders, left_on="L_ORDERKEY", right_on="O_ORDERKEY")
            .join(customer, left_on="O_CUSTKEY", right_on="C_CUSTKEY")
            .filter(pl.col("C_MKTSEGMENT") == "BUILDING")
            .filter(pl.col("O_ORDERDATE") < datetime.datetime(1995, 3, 15))
            .filter(pl.col("L_SHIPDATE") > datetime.datetime(1995, 3, 15))
            .group_by(["L_ORDERKEY", "O_ORDERDATE", "O_SHIPPRIORITY"])
            .agg([pl.col("L_EXTENDEDPRICE").sum().alias("REVENUE")])
            .sort(["REVENUE", "O_ORDERDATE"], descending=[True, False])
            .limit(10)
            .collect()
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
