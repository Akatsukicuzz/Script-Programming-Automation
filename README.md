Dataset Augmentation Script

Course / Exam: CSCI 310 - Midterm Practical (Option 1: Script Programming Automation) 

Authors: Abdirahman Gaal, Esther Kreutzfeldt, Steven Bonilla

Date: Oct 2026

Setup:
  1. Clone the repository:
     
         git clone  https://github.com/Akatsukicuzz/Script-Programming-Automation.git

         cd Script-Programming-Automation
  3. Download the full dataset from physionet

         https://physionet.org/files/eegmmidb/1.0.0

To Run:

      python augment_dataset.py <path_to_dataset>

Output:

    ==================================================
    Summary
    Original file count: N = 3052
    Generated files:     3052
    Final dataset size:  6104  (2N)
    Output path:         <dataset path>
    Target date:         2026-09-10
    Dates found on disk: <10th of prev month> to <10th of previous month>
    Files with correct date: 3052/3052
    Counts OK:           PASS
    No cycle repeats:    PASS
    Dates OK:            PASS
    Originals unchanged: PASS
    Names OK:            PASS
    OVERALL STATUS:      SUCCESS
    ==================================================

CSV should resemble this but a lot longer: 

    new_file,source_file,cycle
    0000169.edf.event,S062/S062R02.edf.event,1
    0000245.edf.event,S093/S093R14.edf.event,1
    0000615.edf,S099/S099R08.edf,1
    0000961.edf,S002/S002R04.edf,1
    0001341.edf.event,S057/S057R01.edf.event,1
    0001585.edf.event,S091/S091R07.edf.event,1
    0001686.edf,S062/S062R10.edf,1
    0002307.edf,S025/S025R14.edf,1
    0003878.edf,S052/S052R08.edf,1
    0004176.edf,S052/S052R02.edf,1

