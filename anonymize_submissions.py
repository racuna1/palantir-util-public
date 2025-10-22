__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2023-25"

import yaml

def anonymize_gs_yaml(filename_input: str, filename_output: str, mapping: dict[int, int]):
    with open(filename_input) as file_input:
        submissions = yaml.load(file_input, Loader=yaml.FullLoader)
        submissions_updated = dict()

        for key in submissions.keys():
            current = submissions[key]

            # partial validation
            if len(current[":submitters"]) != 1:
                raise Exception(f"Unexpected number of submitters in {key}.")

            for result in current[":history"]:
                if len(result[":submitters"]) != 0:
                    raise Exception(f"Unexpected number of submitters in {key}'s :history ({result}).")

            sid = int(current[":submitters"][0][":sid"])

            # anonymize in place
            current[":submitters"][0][":name"] = "anon" + str(sid)
            current[":submitters"][0][":email"] = f"anon{str(sid)}@anon.com"

            # build new dict with masked keys
            new_key = "submission_" + mapping[sid]
            submissions_updated[new_key] = current

        with open(filename_output, 'w') as file_submissions_updated:
            yaml.dump(submissions_updated, file_submissions_updated)