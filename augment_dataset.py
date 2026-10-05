# Dataset Augmentation Script Program
# Authors: Abdirahman Gaal, Esther Kreutzfeldt, Steven Bonilla

import sys
import os
import random 
import shutil
from datetime import datetime

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
    """Shuffled cycles, no repeats within a cycle."""
    if needed <= 0:
        return []

    if not sources:
        raise ValueError("Cannot build selection: no eligible sources files.")
    
    selection = []

    while len(selection) < needed:
        cycle = sources.copy()
        random.shuffle(cycle)

        remaining_needed  = needed - len(selection)
        selection.extend(cycle[:remaining_needed])

    return selection


def generate_names(selection, output_dir):
    name = [] #creating an empyt list that will store the random numeric names.
    countNumber = len(selection)

    for i in range (countNumber):
        numericID = random.randint(10,1000) #creates a random numeric ID that will become the copied files name.     
        path = os.path.join(output_dir, str(numericID)+"_"+selection[i])
        print ("path:", path)

        if os.listdir(output_dir) == 0: 
            while numericID in name: #making sure the number has not been picked already. 
                 numericID = random.randint(10,1000)
        else:         
            for filename in os.listdir(output_dir):
                if str(numericID) in filename or numericID in name: 
                    numericID = random.randint(10,1000) #creates a random numeric ID that will become the copied files name.     
        
        name.append(numericID)

    name.sort() #sort the list is numeric order. 
    return name

def copy_files(selection, names, output_dir):
    eligibleFiles = len(selection)
    
    for i in range(eligibleFiles): 
        # traceableName = selection[i].split("R") #making the file traceable to the source file by including the numeric value from the source file. 
        traceableName = os.path.basename(selection[i]) #making the file traceable to the source file by including the numeric value from the source file. 
        destination = os.path.join(output_dir, str(names[i])+"_"+traceableName) 
        
        # print(destination)
        shutil.copy2(selection[i],destination)
    sorted(os.listdir(output_dir), key=lambda filename: int(filename.split("_")[0])) #sorting the directory into numerical order. 

def set_dates(files):
    """10th of previous month, mtime/atime."""
    now = datetime.now()

    if now.month == 1:
        year = now.year - 1
        month = 12
    else:
        year = now.year
        month = now.month - 1

    target_date = datetime(year, month, 10)
    timestamp = target_date.timestamp()

    for file in files:
        os.utime(file, (timestamp, timestamp))


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

    # temporary test for set_dates
    test_file = "date_test.txt"

    with open(test_file, "w") as f:
        f.write("Testing set_dates")


    os.makedirs(output_dir, exist_ok=True)
    sourceList = build_selection(eligible_files, len(eligible_files))
    generatedNames = generate_names(sourceList, output_dir)
    
    copy_files(sourceList, generatedNames, output_dir)

    set_dates([test_file])

    print("Test modified date", datetime.fromtimestamp(os.path.getmtime(test_file)))

    os.remove(test_file)

if __name__ == "__main__":
    main()
