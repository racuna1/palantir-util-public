"""
anonymize_submissions.py: removes identifying information from a Canvas gradebook and associated Gradescope metadata.

The following Canvas gradebook columns will be masked: Student, ID, SIS User ID, SIS Login ID. The SIS Login ID will be
populated with a random four-digit number, and the order of the rows randomized. In the Gradescope export, the following
fields will be masked: name, sid, email. The sid will be replaced with the same random numbers used to mask the Canvas
gradebook.
"""
__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2023"

import csv
import os
import random

FOLDER_DATA_ORIGINAL = "data_original"
FOLDER_DATA_PROCESSED = "data_processed"


def process(path_gradebook, gradescope_metadata):
    path_gradebook_clean = FOLDER_DATA_PROCESSED + os.sep + "ser222_22sc_gradebook_clean.csv"

    # find number of students
    student_count = 0
    student_ids = []

    with open(path_gradebook) as input_csv:
        reader = csv.DictReader(input_csv)

        # skip header lines (removing two lines due to Canvas export format).
        header = list(next(reader).keys())
        next(reader)  # dummy line

        for row in reader:
            student_ids.append(row["SIS User ID"])
            student_count += 1

    # generate lookup table of original to masked IDs
    masked_ids = [str(x) for x in random.sample(range(1000, 10000), student_count)]
    mapping = dict()
    for i, id in enumerate(student_ids):
        mapping[id] = masked_ids[i]

    with open(path_gradebook) as input_csv:
        reader = csv.DictReader(input_csv)

        # create modified file
        with open(path_gradebook_clean, 'w', newline="") as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames)
            writer.writeheader()

            for i in range(2):
                line = next(reader)
                writer.writerow(line)

            for row in reader:
                # mask Student, ID, IS Login ID
                row["Student"] = "anon"
                row["ID"] = str(1234)
                row["SIS Login ID"] = "anon"

                # update SIS User ID
                row["SIS User ID"] = mapping[row["SIS User ID"]]

                writer.writerow(row)

        if os.path.exists(gradescope_metadata):
            # TODO: process Gradescope file
            pass

        pass


if __name__ == "__main__":

    path_gradebook = FOLDER_DATA_ORIGINAL + os.sep + "ser222_22sc_gradebook.csv"
    gradescope_metadata = FOLDER_DATA_ORIGINAL + os.sep + "ser222_22sc_m1_submission_metadata.yml"

    process(path_gradebook, gradescope_metadata)
