__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2023-26"

import pandas as pd
import random
import yaml
import zipfile

GS_METADATA_YAML = "submission_metadata.yml"


def anonymize_gs_prog_yaml(filename_input_zip: str, filename_output: str, map_ids: dict[int, int], consented: list[int], df_roster: pd.DataFrame):
    with zipfile.ZipFile(filename_input_zip, 'r') as gs_export:
        all_files = gs_export.namelist()
        macless_files = [f for f in all_files if "_MACOSX" not in f] # remove mac metadata. helps perf and anonymity.
        candidates = [x for x in macless_files if GS_METADATA_YAML in x]
        if len(candidates) != 1:
            raise Exception(f"Unexpected issue finding YAML metadata. Found: {candidates}")
        filename_input = candidates[0]

        #format: assignment_XXXXXXX_export/submission_XXXXXXXXX/
        #submission_roots = [x for x in all_files if len(x) == 47 and x[-1] == "/"]

        with gs_export.open(filename_input) as file_input, zipfile.ZipFile(filename_output + ".zip", 'w', compression=zipfile.ZIP_DEFLATED) as zip_output:
            submissions = yaml.load(file_input, Loader=yaml.CLoader)
            anonymized = dict()

            for key in submissions.keys():
                current = submissions[key]

                # validation: only one submitter.
                if len(current[":submitters"]) != 1:
                    raise Exception(f"Unexpected number of submitters in {key}.")

                for result in current[":history"]:
                    if len(result[":submitters"]) != 0:
                        raise Exception(f"Unexpected number of submitters in {key}'s :history ({result}).")

                # process only rows for students who consented
                sid = int(current[":submitters"][0][":sid"])
                if sid not in consented:
                    continue

                # anonymize existing record. align with anonymized roster.
                anonymized_id = map_ids[sid]
                df_row = df_roster[df_roster['ID'] == anonymized_id].iloc[0]
                current[":submitters"][0][":sid"] = map_ids[sid]
                current[":submitters"][0][":name"] = f"{df_row['First Name']} {df_row['Last Name']}"
                current[":submitters"][0][":email"] = df_row["Zoom Email"]

                # mask out ID in each attempt (they are unique parts of the gradescope URL)
                for i, attempt in enumerate(current[":history"]):
                    new_id = "submission_30" + str(i+1).zfill(3) + str(map_ids[sid])  # see note about key below
                    attempt[":id"] = new_id

                # build new dict with masked keys
                new_key = "submission_30000" + str(map_ids[sid]) # normally "9 random" digits. using fake sid for distinctness.
                anonymized[new_key] = current

                # find original files associated with the final submission for this student.
                submission_files = [f for f in macless_files if key in f and f[-1] != "/"]

                # map each file into the new ZIP
                for submission_file in submission_files:
                    with gs_export.open(submission_file) as file_submission:
                        base_name = submission_file[47:]
                        submission_renamed = f"assignment_0000000_export/{new_key}/{base_name}"

                        # if a submission file is Java, mask out the author field.
                        if submission_file.endswith(".java"):
                            file_text = file_submission.read().decode("utf‑8")

                            processed_lines = []
                            for line in file_text.splitlines(keepends=True):
                                if "@author" in line:
                                    start_idx = line.find("@author")
                                    eol = line[len(line.rstrip("\r\n")):] # find the line ending for preservation
                                    processed_lines.append(f"{line[:start_idx]}@author MASKED{eol}")
                                else:
                                    processed_lines.append(line)

                            zip_output.writestr(submission_renamed, "".join(processed_lines))
                        else:
                            print("anonymize_gs_prog_yaml: WARNING encountered unknown file type when copying contents of GS ZIP.")
                            file_data = file_submission.read()
                            zip_output.writestr(submission_renamed, file_data)

            # modern versions of python preserve insert order. need to shuffle
            anonymized_keys = list(anonymized.keys())
            random.shuffle(anonymized_keys)
            anonymized_shuffled = {key: anonymized[key] for key in anonymized_keys}

            # save dictionary as YAML into ZIP
            yaml_text = yaml.dump(anonymized_shuffled, Dumper=yaml.CDumper)
            zip_output.writestr(f"assignment_0000000_export/{GS_METADATA_YAML}", yaml_text)

            #with open(filename_output + ".yml", 'w') as file_submissions_updated:
            #    yaml.dump(anonymized_shuffled, file_submissions_updated, Dumper=yaml.CDumper)
