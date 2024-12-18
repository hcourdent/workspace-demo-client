
def main(scale_factor: str, dataset_name: str):
    return {
        "s3": "tpc-h/{}/input/{}.csv".format(scale_factor, dataset_name)
    }