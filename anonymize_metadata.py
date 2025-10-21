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


def anonymize_gradebook(path_gradebook:str, path_gradebook_clean: str, map_ids: dict[int, int]):
    with open(path_gradebook) as input_csv:
        reader = csv.DictReader(input_csv)

        # create anonymized file
        with open(path_gradebook_clean, 'w', newline="") as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames)
            writer.writeheader()

            for i in range(2):
                line = next(reader)
                writer.writerow(line)

            all_rows = []
            for row in reader:
                if "Student, Test" in row["Student"]:
                    continue

                # mask Student, ID, IS Login ID
                row["Student"] = "anon"
                row["ID"] = str(123456789)
                row["SIS Login ID"] = "anon"

                # update SIS User ID
                row["SIS User ID"] = map_ids[int(row["SIS User ID"])]

                all_rows += [row]

            # randomize rows
            random.shuffle(all_rows)

            for row in all_rows:
                writer.writerow(row)