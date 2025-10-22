"""
anonymize.py: removes identifying information from a roster, Canvas gradebook, and associated submission
                          Gradescope metadata.

The anonymized data is intended to be in a format as close to the original as possible.

The following Canvas gradebook columns will be masked: Student, ID, SIS User ID, SIS Login ID. The SIS Login ID will be
populated with a random four-digit number, and the order of the rows randomized. In the Gradescope export, the following
fields will be masked: name, sid, email. The sid will be replaced with the same random numbers used to mask the Canvas
gradebook.

Removes "Student, Test" if present in the data.
"""
__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2023-25"

import csv
import os
import random

from anonymize_metadata import anonymize_roster, anonymize_gradebook
from constants import FOLDER_DATA_PROCESSED, FOLDER_DATA_ORIGINAL


def process(filename_gradebook: str, filename_roster: str, filenames_submissions_gs: list[str], local_anonymization: bool):
    if not os.path.exists(FOLDER_DATA_PROCESSED):
        os.makedirs(FOLDER_DATA_PROCESSED)

    # generate global anonymized IDs (protocol dependent) for students from gradebook (assumed to exist)
    path_gradebook = FOLDER_DATA_ORIGINAL + os.sep + filename_gradebook
    map_ids = generate_id_map(path_gradebook)

    # process roster
    path_roster = FOLDER_DATA_ORIGINAL + os.sep + filename_roster
    path_roster_clean = FOLDER_DATA_PROCESSED + os.sep + filename_roster[:-4] + "_anonymized.csv"
    anonymize_roster(path_roster, path_roster_clean, map_ids)

    # process gradebook
    path_gradebook_clean = FOLDER_DATA_PROCESSED + os.sep + filename_gradebook[:-4] + "_anonymized.csv"
    output_paths = [path_gradebook_clean]
    if local_anonymization:
        map_ids = generate_id_map(path_gradebook)
    anonymize_gradebook(path_gradebook, path_gradebook_clean, map_ids)

    # process gradescope files
    for filename_gs_data in filenames_submissions_gs:
        path_gs_data = FOLDER_DATA_ORIGINAL + os.sep + filename_gs_data

        if os.path.exists(path_gs_data):
            filepath_gs_processed = FOLDER_DATA_PROCESSED + os.sep + filename_gs_data[:-4] + "_anonymized.yml"
            anonymize_submission_gs(path_gs_data, filepath_gs_processed, map_ids)
            output_paths += [filepath_gs_processed]

    return output_paths


def generate_id_map(path_gradebook: str) -> dict[int, int]:
    """
    Generates an int to int map from original gradebook IDs to randomly generated four-digit IDs. Used for protocols
    performing global (rather than local) anonymization that preserve the same anonymized ID across multiple items.
    Mapping is stored only in memory and never saved to storage.
    :param path_gradebook: input gradebook.
    :return: dictionary that maps original to anonymized IDs.
    """
    # find number of students
    student_count = 0
    student_ids = []

    with open(path_gradebook) as input_csv:
        reader = csv.DictReader(input_csv)

        # skip header lines (removing two lines due to Canvas export format).
        header = list(next(reader).keys())
        next(reader)  # dummy line

        for row in reader:
            if "Student, Test" in row["Student"]:
                continue

            student_ids.append(row["SIS User ID"])
            student_count += 1

    # generate lookup table of original to anonymized IDs
    masked_ids = [x for x in random.sample(range(1000, 10000), student_count)] # .sample returns unique values
    map_ids = dict()
    for i, id in enumerate(student_ids):
        map_ids[int(id)] = masked_ids[i]

    return map_ids


if __name__ == "__main__":

    # inputs must be in a sub-folder called data_original. updated files will be saved to data_original.
    #process("ser222_22sc_gradebook.csv", ["ser222_22sc_m1_submission_metadata.yml"])

    #input: TODO consent results, gradebook, roster, protocol, gradescope data, TODO submissions (?)
    #TODO: staff filter
    process("ser222_25sc_ground_gradebook.csv", "ser222_25sc_ground_roster.csv", [], False)
