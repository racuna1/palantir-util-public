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
import yaml

FOLDER_DATA_ORIGINAL = "data_original"
FOLDER_DATA_PROCESSED = "data_processed"


def process(filename_gradebook, filename_gradescope_metadata):
    path_gradebook = FOLDER_DATA_ORIGINAL + os.sep + filename_gradebook
    gradescope_metadata = FOLDER_DATA_ORIGINAL + os.sep + filename_gradescope_metadata

    path_gradebook_clean = FOLDER_DATA_PROCESSED + os.sep + filename_gradebook[:-4] + "_anonymized.csv"
    gradescope_metadata_clean = FOLDER_DATA_PROCESSED + os.sep + filename_gradescope_metadata[:-4] + "_anonymized.yml"

    output_paths = [path_gradebook_clean]

    if not os.path.exists(FOLDER_DATA_PROCESSED):
        os.makedirs(FOLDER_DATA_PROCESSED)

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

            all_rows = []
            for row in reader:
                # mask Student, ID, IS Login ID
                row["Student"] = "anon"
                row["ID"] = str(1234)
                row["SIS Login ID"] = "anon"

                # update SIS User ID
                row["SIS User ID"] = mapping[row["SIS User ID"]]

                all_rows += [row]

            # randomize rows
            random.shuffle(all_rows)

            for row in all_rows:
                writer.writerow(row)

        # process Gradescope file (if exists)
        withdrawn_students = 0

        if os.path.exists(gradescope_metadata):

            with open(gradescope_metadata) as file_input_gradescope:
                submissions = yaml.load(file_input_gradescope, Loader=yaml.FullLoader)
                submissions_updated = dict()

                for key in submissions.keys():
                    current = submissions[key]
                    if len(current[":submitters"]) != 1:
                        raise Exception(f"Unexpected number of submitters in {key}.")

                    for result in current[":history"]:
                        if len(result[":submitters"]) != 0:
                            raise Exception(f"Unexpected number of submitters in {key}'s :history ({result}).")

                    sid = current[":submitters"][0][":sid"]  # will be str

                    # mask in place
                    current[":submitters"][0][":name"] = "anon"
                    current[":submitters"][0][":email"] = "anon@anon.com"

                    #  is student still in gradebook? if so,there is a mapping. otherwise, we need to add a one.
                    if sid not in mapping:
                        mapping[sid] = str(10000 + withdrawn_students)  # all five digit students withdrew.
                        withdrawn_students += 1

                        current[":submitters"][0][":sid"] = mapping[sid]

                    # build new dict with masked keys
                    new_key = "submission_" + mapping[sid]
                    submissions_updated[new_key] = current

                with open(gradescope_metadata_clean, 'w') as file_submissions_updated:
                    yaml.dump(submissions_updated, file_submissions_updated)
                    output_paths += [gradescope_metadata_clean]

        return output_paths


if __name__ == "__main__":

    # inputs must be in a sub-folder called data_original. updated files will be saved to data_original.
    process("ser222_22sc_gradebook.csv", "ser222_22sc_m1_submission_metadata.yml")
