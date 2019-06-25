import pytest
import csv
import os

test_dir = os.path.join(os.path.realpath(__file__).replace(os.path.basename(__file__), ''), "data")
example_file = test_dir + "/example.csv"


def pytest_generate_tests(metafunc):
    csv_file = open(example_file)
    csv_content = csv.reader(csv_file, delimiter=',')
    rows = []
    for row in csv_content:
        rows.append(row)

    metafunc.parametrize('examples', rows)


def test_examples(examples):
    assert examples[0].isnumeric()
    #assert "" == examples[1], "Error with test case {}".format(examples[0])