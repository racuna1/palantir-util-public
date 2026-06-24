__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2025-26"

import csv

import pandas as pd


def anonymize_roster(path_roster: str, path_roster_clean: str, map_ids: dict[int, int], consented: list[int]) -> pd.DataFrame:
    with open(path_roster) as input_csv:
        reader = csv.DictReader(input_csv)

        path_roster_clean_pkl = path_roster_clean[:-4] + "_anonymized.pkl"

        rows = []

        # create anonymized file
        with (open(path_roster_clean, "w", newline="")) as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for row in reader:
                # process only rows for students who consented
                real_id = int(row["ID"])
                if real_id not in consented:
                    continue

                # by default, all data is removed and all columns have an empty string
                row_anon = dict.fromkeys(row.keys(), "")

                # explicitly maintain some columns
                row_anon["Units"] = row["Units"]
                row_anon["Grade Basis"] = row["Grade Basis"]
                row_anon["Program and Plan"] = row["Program and Plan"]
                row_anon["Academic Level"] = row["Academic Level"]

                # anonymize identity information
                id_str = map_ids[int(row["ID"])]
                row_anon["ID"] = id_str
                row_anon["Posting ID"] = str(id_str) + "-000"
                row_anon["First Name"] = "Anon"
                row_anon["Last Name"] = "Anon" + str(id_str)
                row_anon["ASURITE"] = "aanon" + str(id_str)
                row_anon["Zoom Email"] = row_anon["ASURITE"] + "@anon.com"

                rows.append(row_anon)

            # randomize rows (works since last name includes a random number)
            rows = sorted(rows, key=lambda row: row['Last Name'])

            for row in rows:
                writer.writerow(row)

        # save DataFrame
        df = pd.DataFrame(rows)
        df.to_pickle(path_roster_clean_pkl)

    return df

def anonymize_gradebook(path_gradebook:str, path_gradebook_clean: str, map_ids: dict[int, int], consented: list[int],
                        df_roster: pd.DataFrame):
    with open(path_gradebook) as input_csv:
        reader = csv.DictReader(input_csv)

        path_gradebook_clean_pkl = path_gradebook_clean[:-4] + ".pkl"

        # create anonymized file
        with open(path_gradebook_clean, 'w', newline="") as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames)
            writer.writeheader()

            for i in range(2):
                line = next(reader)
                writer.writerow(line)

            rows = []
            for row in reader:
                if "Student, Test" in row["Student"]:
                    continue

                # process only rows for students who consented
                real_id = int(row["SIS User ID"])
                if real_id not in consented:
                    continue

                # mask Student, ID, IS Login ID. align with anonymized roster.
                anonymized_id = map_ids[real_id]
                df_row = df_roster[df_roster['ID'] == anonymized_id].iloc[0]
                row["Student"] = f"{df_row['Last Name']}, {df_row['First Name']}"
                row["ID"] = str(123456)
                row["SIS Login ID"] = df_row["ASURITE"]
                row["SIS User ID"] = anonymized_id

                rows += [row]

            # randomize rows (works since last name includes a random number)
            rows = sorted(rows, key=lambda row: row["Student"].split(",")[0])

            for row in rows:
                writer.writerow(row)

            # save DataFrame
            df = pd.DataFrame(rows)
            df.to_pickle(path_gradebook_clean_pkl)


def sanitize_quiz(path_quiz:str, path_quiz_clean:str, map_ids: dict[int, int], consented: list[int],
                  df_roster: pd.DataFrame):

    with open(path_quiz, encoding='utf-8') as input_csv:
        reader = csv.reader(input_csv)

        headers = next(reader)

        # create anonymized and consented file
        with open(path_quiz_clean, 'w', encoding='utf-8', newline="") as output_csv:
            writer = csv.writer(output_csv)
            writer.writerow(headers)

            #verify default columns. Based on Canvas Standard Quizzes (6/12/26).
            expected_columns = ["name", "id", "sis_id", "root_account", "section", "section_id", "section_sis_id",
                                "submitted", "attempt"]
            for i, item in enumerate(expected_columns):
                if headers[i] != item:
                    raise Exception(f"sanitize_quiz: Could not find column {item} at expected position {i}.")

            # process rows
            rows = []
            for row in reader:
                name = row[0]
                id = row[1]
                sis_id = row[2]
                root_account = row[3]
                section = row[4]
                section_id = row[5]
                section_sis_id = row[6]
                submitted = row[7]
                attempt = row[8]

                # process only rows for students who consented
                real_id = int(sis_id)
                if real_id not in consented:
                    continue

                # by default, all data is removed.
                row_anon = []

                # anonymize identity information
                anonymized_id = map_ids[int(sis_id)]
                df_row = df_roster[df_roster['ID'] == anonymized_id].iloc[0]
                row_anon.append(f"{df_row['First Name']} {df_row['Last Name']}")
                row_anon.append("000000") #ID
                row_anon.append(anonymized_id)

                # explicitly maintain some columns
                row_anon.append(root_account)
                row_anon.append(section)
                row_anon.append(section_id)
                row_anon.append(section_sis_id)
                row_anon.append(submitted)
                row_anon.append(attempt)

                # data rows
                remaining = row[9:]
                row_anon.extend(remaining)

                rows.append(row_anon)

            # randomize rows (works since last name includes a random number)
            rows = sorted(rows, key=lambda row: row[0])

            for row in rows:
                writer.writerow(row)
