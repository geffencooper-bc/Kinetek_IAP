import argparse

#def verify_hex(file_name):

def assert_hex(expected_file, actual_file):
    expected = open(expected_file, "r")
    actual = open(actual_file, "r")

    # extract raw from expected
    data = expected.read()
    data_list = data.splitlines()
    print(data_list)


if __name__ == "__main__":

    # pass in the file to parse as a command line arg
    parser = argparse.ArgumentParser()
    parser.add_argument("--original_hex", required=True) # .hex file
    parser.add_argument("--raw_hex", required=True)      # .txt file
    args = parser.parse_args()
    expected_name = args.original_hex
    actual_name = args.raw_hex

    assert_hex(expected_name, actual_file)
