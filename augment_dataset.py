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
    cycle_number = 0 

    while len(selection) < needed:
        cycle_number +=1
        cycle = sources.copy()
        random.shuffle(cycle)

        remaining_needed  = needed - len(selection)
        for source in cycle[:remaining_needed]:
            selection.append(source, cycle_number)

    return selection


def generate_names(selection, output_dir):
    name = [] #creating an empyt list that will store the random numeric names.
    countNumber = len(selection)

    for i in range (countNumber):
        numericID = random.randint(10,1000) #creates a random numeric ID that will become the copied files name.     
        path = os.path.join(output_dir, str(numericID)+"_"+selection[i])
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

    return timestamp

def verify_and_report(originals, generated, output_dir, snapshot, target_ts):
    n = len(originals)
    new = len(generated)

    counts_ok = (new == n) and (len(os.listdir(output_dir)) == n)

    dates_ok = all(int(os.path.getmtime(f)) == int(target_ts) for f in generated)

    originals_ok = all(
        (os.path.getsize(path), os.path.getmtime(path)) == snapshot[path] for path in snapshot)

    numbers = [int(os.path.basename(f).split(".")[0]) for f in generated]
    names_ok = (len(set(numbers)) == len(numbers)) and (numbers == sorted(numbers))

    # summary
    all_ok = counts_ok and dates_ok and originals_ok and names_ok

    print("=" * 50)
    print("Summary")
    print(f"Original file count: N = {n}")
    print(f"Generated files:     {new}")
    print(f"Final dataset size:  {n + new}  (2N)")
    print(f"Output path:         {output_dir}")
    print(f"Target date:         {datetime.fromtimestamp(target_ts)}")
    print(f"Counts OK:           {'PASS' if counts_ok else 'FAIL'}")
    print(f"Dates OK:            {'PASS' if dates_ok else 'FAIL'}")
    print(f"Originals unchanged: {'PASS' if originals_ok else 'FAIL'}")
    print(f"Names OK:            {'PASS' if names_ok else 'FAIL'}")
    print("=" * 50)

    return all_ok

def take_snapshot(files):
    snapshot = {}
    for path in files:
        snapshot[path] = (os.path.getsize(path), os.path.getmtime(path))

    return snapshot


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

    snapshot = take_snapshot(eligible_files)

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

    target_ts = set_dates(generated) 
    verify_and_report(eligible_files, generated, output_dir, snapshot, target_ts)

if __name__ == "__main__":
    main()
