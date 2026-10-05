# Dataset Augmentation Script Program
# Authors: Abdirahman Gaal, Esther Kreutzfeldt, Steven Bonilla

import sys
import os
import random 
import shutil
from datetime import datetime
import csv

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
            selection.append((source, cycle_number))

    return selection


def generate_names(selection, output_dir):
    name = [] #creating an empyt list that will store the random numeric names.

    existing = os.listdir(output_dir)

    for i in range (len(selection)):
        numericID = random.randint(10,1000) #creates a random numeric ID that will become the copied files name.     
        while numericID in name or any(f.startswith(str(numericID) + "_") for f in existing): #making sure the number has not been picked already. 
                 numericID = random.randint(10,1000)
        
        name.append(numericID)

    name.sort() #sort the list is numeric order. 
    return name

def copy_files(selection, names, output_dir):
    generated = []

    eligibleFiles = len(selection)
    
    for i in range(eligibleFiles): 
        # traceableName = selection[i].split("R") #making the file traceable to the source file by including the numeric value from the source file. 
        traceableName = os.path.basename(selection[i]) #making the file traceable to the source file by including the numeric value from the source file. 
        destination = os.path.join(output_dir, str(names[i])+"_"+traceableName) 

        # never overwrite
        if os.path.exists(destination):          
            raise FileExistsError(f"Refusing to overwrite: {destination}")  
 
        shutil.copy2(selection[i],destination)
        generated.append(destination)           
 
    return generated                   

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

def verify_cycles(selection):
    seen = set()

    for source, cycle in selection:
        key = (cycle, source)

        if key in seen:
            return False

        seen.add(key)

    return True

def verify_and_report(originals, selection, generated, output_dir, snapshot, target_ts):
    n = len(originals)
    new = len(generated)

    counts_ok = (new == n) and (len(os.listdir(output_dir)) == n)

    dates_ok = all(int(os.path.getmtime(f)) == int(target_ts) for f in generated)

    originals_ok = all(
        (os.path.getsize(path), os.path.getmtime(path)) == snapshot[path] for path in snapshot)

    numbers = [int(os.path.basename(f).split("_")[0]) for f in generated]

    names_ok = (len(set(numbers)) == len(numbers)) and (numbers == sorted(numbers))
    
   
    cycles_ok = verify_cycles(selection)

    # summary
    all_ok = counts_ok and dates_ok and originals_ok and names_ok and cycles_ok 

    print("=" * 50)
    print("Summary")
    print(f"Original file count: N = {n}")
    print(f"Generated files:     {new}")
    print(f"Final dataset size:  {n + new}  (2N)")
    print(f"Output path:         {output_dir}")
    print(f"Target date:         {datetime.fromtimestamp(target_ts)}")
    print(f"Counts OK:           {'PASS' if counts_ok else 'FAIL'}")
    print(f"No cycle repeats:    {'PASS' if cycles_ok else 'FAIL'}") 
    print(f"Dates OK:            {'PASS' if dates_ok else 'FAIL'}")
    print(f"Originals unchanged: {'PASS' if originals_ok else 'FAIL'}")
    print(f"Names OK:            {'PASS' if names_ok else 'FAIL'}")
    print(f"OVERALL STATUS:      {'SUCCESS' if all_ok else 'FAILED'}")
    print("=" * 50)

    return all_ok

def take_snapshot(files):
    snapshot = {}
    for path in files:
        snapshot[path] = (os.path.getsize(path), os.path.getmtime(path))

    return snapshot

def write_manifest(selection, generated, dataset_path, manifest_path):
    # Saved record: new file -> source file -> cycle
    with open(manifest_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["new_file", "source_file", "cycle"])
        for (source, cycle), new_path in zip(selection, generated):
            writer.writerow([
                os.path.basename(new_path),
                os.path.relpath(source, dataset_path),
                cycle
            ])


 

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
    manifest_path = "augmentation_manifest.csv"


    print(f"Loading dataset from: {dataset_path}")

    eligible_files = list_eligible_files(dataset_path, output_dir)

    snapshot = take_snapshot(eligible_files)

    print("Original file count: N = ", len(eligible_files))

    if os.path.isdir(output_dir) and os.listdir(output_dir):
        print(f"Error: output folder '{output_dir}' is not empty.")
        print("Remove it or move its files before running again.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    selection = build_selection(eligible_files, len(eligible_files))

    sourceList = [source for source, cycle in selection] 

    generatedNames = generate_names(sourceList, output_dir)

    generated = copy_files(sourceList, generatedNames, output_dir)

    write_manifest(selection, generated, dataset_path, manifest_path)
    print(f"Manifest written to: {manifest_path}")

    target_ts = set_dates(generated) 

    ok = verify_and_report(eligible_files, selection, generated, output_dir, snapshot, target_ts)

    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
