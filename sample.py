import os
import pandas as pd
from argparse import ArgumentParser


def main(args):
    df = pd.read_csv(args.filename, compression='gzip')
    print(f'{len(df)} rows loaded from {args.filename}')

    return os.EX_OK


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()
    exit(main(args))
