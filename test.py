import argparse

parser = argparse.ArgumentParser()
parser.add_argument("csvFile")
args = parser.parse_args()
print(args.csvFile)