This is a collection of scripts that perform data preprocessing on student data or Gradescope exports for later use by palantir. 

Data:
* Roster (CSV): The raw roster data available from the university.
* Gradebook (CSV): The raw gradebook data exported from Canvas.
* Gradescope, Programming (YAML): The Gradescope provided YAML file containing code submission assessments.

Contents:
* anonymize.py: This file removes identifying information from a roster, gradebook, and Gradescope programming submissions. 
* synthesize.py: This file contains functionality to synthetically generate course data (roster). Data is intended to closely match the natural data export formats so that it can be used by any other tools.