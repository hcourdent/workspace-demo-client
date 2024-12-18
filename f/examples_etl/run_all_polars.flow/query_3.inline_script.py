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
    supplier_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "supplier.parquet"
    )
    nation_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "nation.parquet"
    )
    region_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "region.parquet"
    )

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_3.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(lineitem_uri, mode="rb") as lineitem_ipt,
        s3.open(customer_uri, mode="rb") as customer_ipt,
        s3.open(orders_uri, mode="rb") as orders_ipt,
        s3.open(supplier_uri, mode="rb") as supplier_ipt,
        s3.open(nation_uri, mode="rb") as nation_ipt,
        s3.open(region_uri, mode="rb") as region_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        lineitem = pl.read_parquet(lineitem_ipt).lazy()
        customer = pl.read_parquet(customer_ipt).lazy()
        orders = pl.read_parquet(orders_ipt).lazy()
        supplier = pl.read_parquet(supplier_ipt).lazy()
        nation = pl.read_parquet(nation_ipt).lazy()
        region = pl.read_parquet(region_ipt).lazy()

        output_df = (
            customer.lazy()
            .join(orders.lazy(), left_on="C_CUSTKEY", right_on="O_CUSTKEY")
            .join(lineitem.lazy(), left_on="O_ORDERKEY", right_on="L_ORDERKEY")
            .join(supplier.lazy(), left_on="L_SUPPKEY", right_on="S_SUPPKEY")
            .join(nation.lazy(), left_on="S_NATIONKEY", right_on="N_NATIONKEY")
            .join(region.lazy(), left_on="N_REGIONKEY", right_on="R_REGIONKEY")
            .filter(pl.col("R_NAME") == "ASIA")
            .filter(pl.col("O_ORDERDATE") >= datetime.datetime(1994, 1, 1))
            .filter(
                pl.col("O_ORDERDATE")
                < datetime.datetime(1994, 1, 1) + datetime.timedelta(days=365)
            )
            .group_by(["N_NAME"])
            .agg(
                [
                    (pl.col("L_EXTENDEDPRICE") * (1 - pl.col("L_DISCOUNT")))
                    .sum()
                    .alias("REVENUE")
                ]
            )
            .sort(["REVENUE"], descending=[True])
            .collect()
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
