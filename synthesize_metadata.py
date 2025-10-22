__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2025"

import csv
import pandas as pd
import random
import os
from datetime import date, timedelta
from faker import Faker
from typing import Any

from constants import FOLDER_DATA_ORIGINAL
from synthesize_util import sample_distribution


def generate_roster(path_roster, n):
    fake = Faker('ja_JP')

    ids = [x for x in random.sample(range(1200000000, 1299999999), n)]
    path_csv = FOLDER_DATA_ORIGINAL + os.sep + path_roster
    path_pkl = FOLDER_DATA_ORIGINAL + os.sep + path_roster[:-4] + "_anonymized.pkl"

    # hardcoded course characteristics: (TODO: would be nice to use distributions estimated from real course)
    units = 3
    str_dist_pp = [(.91, "Ira A Fulton Engineering - Software Engineering"),
                   (.03, "Ira A Fulton Engineering - Computer Science"),
                   (.03, "Ira A Fulton Engineering - Engineering"),
                   (.03, "Ira A Fulton Engineering - Information Technology")]
    str_dist_al = [(.11, "Graduate"), (.23, "Sophomore"), (.55, "Junior"), (.11, "Senior")]
    str_dist_r = [(.67, "Resident"), (.33, "Non-Resident")]

    # ASU Fall 2025 Format
    keys = ['ID', 'Posting ID', 'First Name', 'Last Name', 'Status', 'Units', 'Grade Basis', 'Program and Plan',
            'Academic Level', 'ASURITE', 'Residency', 'Zoom Email']
    rows = []

    # build and save CSV
    with (open(path_csv, "w", newline="")) as output_csv:
        writer = csv.DictWriter(output_csv, keys, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        used_asurites = []
        for i in range(n):
            row = dict.fromkeys(keys, "")

            #columns = ['ID', 'Posting ID', 'First Name', 'Last Name', 'Status', 'Units', 'Grade Basis', 'Program and Plan',
            #          'Academic Level', 'ASURITE', 'Residency', 'Zoom Email']
            row['ID'] = str(ids[i])
            row['Posting ID'] = str(ids[i] % 10000).zfill(4) + f"-{random.randint(100, 999)}"
            row['First Name'] = fake.first_romanized_name()
            row['Last Name'] = fake.last_romanized_name()

            # very simple method. use today as start date and randomly enroll up to a week out.
            offset = random.randint(0, 7)
            enrolled = date.today() + timedelta(days=offset)
            row['Status'] = f"ENRL ({enrolled.strftime("%Y-%m-%d")})"

            row['Units'] = units
            row['Grade Basis'] = "Standard"
            row['Program and Plan'] = sample_distribution(str_dist_pp)
            row['Academic Level'] = sample_distribution(str_dist_al)

            asurite = select_asurite(row, used_asurites)
            row['ASURITE'] = asurite
            used_asurites.append(asurite)

            row['Residency'] = sample_distribution(str_dist_r)
            row['Zoom Email'] = asurite + "@asu.edu"

            rows.append(row)

        # sort by last name
        rows = sorted(rows, key=lambda row: row['Last Name'])

        for row in rows:
            writer.writerow(row)

    # save DataFrame
    df = pd.DataFrame(rows)
    df.to_pickle(path_pkl)


def select_asurite(row: dict[str | Any, str], used_asurites: list[Any]) -> str:
    asurite = (row['First Name'][0].lower() + row['Last Name'].lower())[:8]
    if asurite in used_asurites:
        prefix = asurite[:7]
        tries = 0
        found_unused = False
        while not found_unused:
            tries += 1
            if prefix + str(tries) not in used_asurites:
                found_unused = True
        asurite = prefix + str(tries)
    return asurite