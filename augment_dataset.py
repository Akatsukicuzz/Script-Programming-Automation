# Dataset Augmentation Script Program
# Authors: Abdirahman Gaal, Esther Kreutzfeldt, Steven Bonilla

import sys
import os

def is_eligible(path):
    name = os.path.basename(path)
    if name.startswith("."):          #hidden file
        return False
    if not os.path.isfile(path):      #not a regular file
        return False
    return True

def list_eligible_files(root, output_dir):
    eligible_files = []
    output_abs = os.path.abspath(output_dir)
    
    for folder, subfolders, filenames in os.walk(root):

        subfolders[:] = [
           s for s in subfolders 
           if not s.startswith(".")
           and os.path.abspath(os.path.join(folder, s)) != output_abs
            ]

       
        for filename in filenames:
            full_path = os.path.join(folder, filename)
            if is_eligible(full_path):
                eligible_files.append(full_path)

    return sorted(eligible_files)


def build_selection(sources, needed):
    """Shuffled cycles, no repeats within a cycle. TODO"""
    pass


def generate_names(count, sources):
    """Unique random numeric IDs, sorted ascending, extension kept. TODO"""
    pass


def copy_files(selection, names, output_dir):
    """Copy without overwriting. TODO"""
    pass


def set_dates(files):
    """10th of previous month, mtime/atime. TODO"""
    pass


def verify_and_report():
    """Counts, order, dates, originals unchanged, final summary. TODO"""
    pass

def main():

    #make sure user put in path arg
    if len(sys.argv) < 2:
        print("Error: Missing dataset path argument.")
        print("Usage: python augment_dataset.py <path_to_dataset>")
        sys.exit(1)

    #extract dataset path
    dataset_path = sys.argv[1]

    #make sure directory exists
    if not os.path.isdir(dataset_path):
        print(f"Error: The file '{dataset_path}' is not an existing directory.")
        sys.exit(1)

    #using full path
    output_dir = os.path.join(dataset_path, "augmented")

    print(f"Loading dataset from: {dataset_path}")

    eligible_files = list_eligible_files(dataset_path, output_dir)

    print("Original file count: N = ", len(eligible_files))

    

if __name__ == "__main__":
    main()
