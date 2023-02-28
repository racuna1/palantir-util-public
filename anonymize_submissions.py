__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2023"
"""
This file removes identifying information from a Canvas roster export and associated Gradescope metadata.

The following Canvas gradebook columns will be masked: Student, ID, SIS User ID, SIS Login ID. The SIS Login ID will be
populated with a random six digit number, and the order  of the rows randomized. In the Gradescope export, the following
fields will be masked: name, sid, email. The sid will be replaced with the same random numbers used to mask the Canvas
gradebook.
"""

import os

FOLDER_DATA_ORIGINAL = "data_original"
FOLDER_DATA_PROCESSED = "data_processed"


def process():
    canvas_gradebook = FOLDER_DATA_ORIGINAL + os.sep + "ser222_22sc_gradebook.csv"
    gradescope_metadata = FOLDER_DATA_ORIGINAL + os.sep + "ser222_22sc_m1_submission_metadata.yml"

    # TODO: mask Student, ID, IS Login ID.

    # TODO: find number of students

    # TODO: generate lookup table of original to masked IDs

    # TODO: update SIS User ID

    if os.path.exists(gradescope_metadata):
        # TODO: process Gradescope file
        pass

    pass


if __name__ == "__main__":
    process()
    