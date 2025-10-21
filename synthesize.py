__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2025"

from synthesize_metadata import generate_roster

FOLDER_DATA_ORIGINAL = "data_original"

if __name__ == "__main__":
    generate_roster("ser222_00sc_ground_roster_synthetic.csv", 30)
