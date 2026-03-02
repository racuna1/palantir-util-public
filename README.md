## palantir-util-public
This is a collection of scripts that perform data preprocessing on student data for later analysis. 

All scripts are written in terms of CSV files but some methods produced pickled DataFrames that are more easy to work with downstream.

Data:
* Roster (CSV): The raw roster data available from the university.
* Consent Form (CSV): The raw student analysis report for a Canvas quiz containing a consent form.
* Gradebook (CSV): The raw gradebook data exported from Canvas.
* Gradescope, Programming (YAML): The Gradescope provided YAML file containing code submission assessments.

Contents:
* anonymize.py: This file removes identifying information from a roster, gradebook, and Gradescope programming submissions. Also filters data based on a consent form.

## Authors
* Ruben Acuña