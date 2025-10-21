__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2025"

import csv
import random

def anonymize_roster(path_roster: str, path_roster_clean: str, map_ids: dict[int, int]):
    with open(path_roster) as input_csv:
        reader = csv.DictReader(input_csv)

        # create anonymized file
        with (open(path_roster_clean, "w", newline="")) as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            all_rows = []
            for row in reader:
                # by default, all data is removed and all columns have an empty string
                row_anon = dict.fromkeys(row.keys(), "")

                # explicitly maintain some columns
                row_anon["Units"] = row["Units"]
                row_anon["Grade Basis"] = row["Grade Basis"]
                row_anon["Program and Plan"] = row["Program and Plan"]
                row_anon["Academic Level"] = row["Academic Level"]

                # anonymize identity information
                id_str = str(map_ids[int(row["ID"])])
                row_anon["ID"] = id_str
                row_anon["Posting ID"] = id_str + "-000"
                row_anon["First Name"] = "Anon"
                row_anon["Last Name"] = "Anon" + id_str

                all_rows.append(row_anon)

            # randomize rows
            random.shuffle(all_rows)

            for row in all_rows:
                writer.writerow(row)