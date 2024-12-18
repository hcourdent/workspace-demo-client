#requirements:
#polars==0.19.19
#wmill>=0.218.1
#s3fs==2023.12.0
import wmill
import polars as pl
import s3fs

s3object = dict


def main(scale_factor: str):
    s3_resource_path = "f/examples_etl/windmill-cloud-demo"
    s3 = s3fs.S3FileSystem(
        **wmill.polars_connection_settings(s3_resource_path)["s3fs_args"]
    )
    bucket = wmill.get_resource(s3_resource_path)["bucket"]

    part_uri = "s3://{}/tpc-h/{}/raw/{}".format(bucket, scale_factor, "part.parquet")
    supplier_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "supplier.parquet"
    )
    partsupp_uri = "s3://{}/tpc-h/{}/raw/{}".format(
        bucket, scale_factor, "partsupp.parquet"
    )

    output_filename = "tpc-h/{}/output-polars-mem/{}".format(
        scale_factor, "query_8.out.parquet"
    )
    output_uri = "s3://{}/{}".format(bucket, output_filename)

    with (
        s3.open(supplier_uri, mode="rb") as supplier_ipt,
        s3.open(part_uri, mode="rb") as part_ipt,
        s3.open(partsupp_uri, mode="rb") as partsupp_ipt,
        # s3.open(output_uri, mode="wb") as output_file,
    ):
        supplier = pl.read_parquet(supplier_ipt)
        partsupp = pl.read_parquet(partsupp_ipt)
        part = pl.read_parquet(part_ipt)

        output_df = (
            partsupp.join(part, left_on="PS_PARTKEY", right_on="P_PARTKEY")
            .filter(pl.col("P_BRAND") != "Brand#45")
            .filter(pl.col("P_TYPE").str.starts_with("MEDIUM POLISHED").not_())
            .filter(pl.col("P_SIZE").is_in([49, 14, 23, 45, 19, 3, 36, 9]))
            .join(
                supplier.filter(pl.col("S_COMMENT").str.contains("Customer")),
                left_on="PS_SUPPKEY",
                right_on="S_SUPPKEY",
                how="anti",
            )
            .group_by(["P_BRAND", "P_TYPE", "P_SIZE"])
            .agg([pl.col("PS_SUPPKEY").n_unique().alias("SUPPLIER_CNT")])
            .sort(
                ["SUPPLIER_CNT", "P_BRAND", "P_TYPE", "P_SIZE"],
                descending=[True, False, False, False],
            )
        )
        # in the real life, we would write the ouput back to s3.
        # output_df.write_parquet(output_file)
        # here since we have read-only access to the bucket, we just print it
        print(output_df)

    return s3object({"s3": output_filename})
