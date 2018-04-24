# EEG Notebooks

A collection of classic EEG experiments implemented in Python and Jupyter notebooks. This repo is a work in progress with the goal of making it easy to perform classical EEG experiments and automatically analyze data.

Currently, all experiments are implemented for the Muse EEG device and based on work done by Alexandre Barachant and Hubert Banville for the [muse-lsl](https://github.com/alexandrebarachant/muse-lsl) library

## Getting Started

Run setup_mark.py in order to get the markers to be written into the EEG data capture file, navigate to /eeg-notebooks/H10C-lsl/ directory:
`~/eeg-notebooks/H10C-lsl>python setup_mark.py` 

To run an ERP experiment, use pre-existing PythonAPI driver code, navigate to the /pythonAPI directory: 
`~/pythonAPI>python connect_H10C.py` 
Follow configuration guide. 

To visualize streaming data, use the existing pythonAPI viewer, navigate to the /pythonAPI directory:

`~/pythonAPI>python view_H10C.py`

IMPORTANT: If you intend to collect data for an experiment, ensure that your signal quality is "excellent" and that there is very little noise before proceeding.

### Running an experiment

navigate to the /eeg-notebooks directory:
`cd /eeg-notebooks`

run the stimulus presentation: 
`~/eeg-notebooks>python /stimulus_presentation/generate_Visual_P300.py`

while this is still running, use another terminal and navigate to /H10C-lsl directory. 
`~/eeg-notebooks/H10C-lsl>python recMarker_H10C.py` 

Follow prompt, this will generate a CSV file output inside /output directory under /eeg-notebooks/H10C-lsl. 