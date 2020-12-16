# import modules
import os
import re
import csv, operator
import pandas as pd
import scipy as sio
import numpy as np
from decimal import *
from enum import Enum

# First identify directories
# files_dir ='/imaging/su01/RED/GNG Task Data'
# output_dir = '/imaging/su01/RED/bids'
files_dir = os.getcwd()
output_dir = os.getcwd()

# Identify subject list (red_files correspond to bids_ids order)
red_events = ["99013_events.txt"]
red_files = ["99013_trials.txt"]
bids_ids = ["sub-005"]


# Define condition names
# Identify whether the block string variable includes the conditions ('s_n', 's_g', etc.)
# Then return the condition name only (excluding 'block onset 0..etc'
def findCondStr(blockStr):
    if re.search('s_n', blockStr):
        return 's_n'
    elif re.search('s_g', blockStr):
        return 's_g'
    elif re.search('n_n', blockStr):
        return 'n_n'
    elif re.search('n_g', blockStr):
        return 'n_g'
    elif re.search('h_n', blockStr):
        return 'h_n'
    elif re.search('h_g', blockStr):
        return 'h_g'
    elif re.search('c_n', blockStr):
        return 'c_n'
    elif re.search('c_g', blockStr):
        return 'c_g'
    else:
        return 'Invalid:' + blockStr


# Define the rest of the columns and have function to combine all of these
# The input variables will be resolved in the main code below
def addSummaryRecord(summary, condition, onset):
    # for the trial_type: go vs nogo
    if condition[-1] == 'n':  # if the condition str ends with 'n' this will record 'nogo' in variable g_or_ng
        g_or_ng = 'nogo'
    else:
        g_or_ng = 'go'

    # for the emotion type
    if condition[0] == 's':  # if the condition str begins with certain letter, that will determine emotion
        emotion = 'sad'
    elif condition[0] == 'n':
        emotion = 'neutral'
    elif condition[0] == 'h':
        emotion = 'happy'
    elif condition[0] == 'c':
        emotion = 'control'
    else:
        emotion = 'invalid'

    # put together this list (duration is set for 60s)
    summary.append([condition, onset, 60, g_or_ng, emotion])
    return


if __name__ == '__main__':
    os.chdir(files_dir)

    # for event in red_events:
    for i in range(0, len(red_events)):
        event = red_events[i]
        data = pd.read_table(event)
        block_start = mri_start = False
        summary = list()

        for index, row in data.iterrows():
            if not block_start:
                if not re.search('block', row['event']):
                    continue
                else:
                    mystr = findCondStr(row['event'])
                    block_start = True
            else:
                if not mri_start:
                    # look for MRI pulse
                    if not re.search("MRI pulse", row['event']):
                        continue
                    else:
                        mri_start = True
                        mri_pulse = float(row['time'])
                else:
                    # look for stim onset
                    if not re.search("stim onset", row['event']):
                        continue
                    else:
                        stim_onset = float(row['time'])
                        block_start = False
                        elapsedTime = (stim_onset - mri_pulse) / 1000
                        addSummaryRecord(summary, mystr, elapsedTime)

        # now create dataframe of all the variables
        df = pd.DataFrame(summary, columns=['conditions', 'onset', 'duration', 'trial_type', 'emotion'])
        print(df)
        # save dataframe as tsv into respective output directory folder
        # set name of file

        #tsvname = (output_dir + '/' + bids_ids[i] + '/' + 'func/' + bids_ids[i] + '_events.tsv')
        with open(bids_ids[i] + '/' + 'func/' + bids_ids[i] + '_events.tsv', 'w') as tsvfile:
            tsvfile.write(df.to_csv(sep="\t", index=False))  # without row index
