import data_saving as datSave
import datetime
import numpy as np
from selectStream_Avertus import connectLSL


# formatSelect = input('\nChoose file format: \n'
#                         '  0: CSV \n'
#                         '  1: MAT (for RAW data only) \n'
#                         '  2: BDF+ (for RAW data only - experimental) \n'
#                         'File format #? : ')
#
# if not (formatSelect == 0 or formatSelect == 1 or formatSelect == 2):
#     formatSelect = 0
#     print("Invalid format selection, defaulting to CSV.")

formatSelect = 0  # Defaulting to CSV for integration with marker

if formatSelect == 0:  # CSV
    inlet, inf = connectLSL('all')
elif formatSelect == 1:  # MAT
    inlet, inf = connectLSL('raw')
elif formatSelect == 2:  # BDF+
    inlet, inf = connectLSL('raw')

# Connect to Marker LSL
inletMark, infMark = connectLSL('mark')

if formatSelect == 0:  # CSV
    # File Naming
    csvName = raw_input('Input the filename for your recording: ')

    print("Recording data into "+csvName+".csv...")

    # Initialize the CSV file with headings
    if inf.type() == 'EEG':
        montageDesc = 'RAW'
        montageHeader = ['Fp1', 'Fp2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'O1', 'O2', 'TIME(s)', 'MARKER']
        datSave.csvSaveInit(csvName, ['Name:', inf.name(), 'SN:', inf.source_id(), 'Type:', inf.type(),
                                      '# of Ch:', inf.channel_count(), 'SampRate (SPS):', inf.nominal_srate(),
                                      'Montage:', montageDesc, '+MARKERS'])
        datSave.csvSave1D(csvName, [' '])
        datSave.csvSave1D(csvName, montageHeader)
        columnNum = inf.channel_count() + 2
    elif inf.type() == 'ProcessedEEG':
        montageDesc = inf.desc().child_value("montageDesc")
        headerList = inf.desc().child("channels").child("channel")
        montageHeader = []
        for k in range(inf.channel_count()):
            montageListK = headerList.child_value("name")
            montageHeader.append(str(montageListK))
            headerList = headerList.next_sibling()
        montageHeader.append('TIME(s)')
        montageHeader.append('MARKER')
        datSave.csvSaveInit(csvName, ['Name:', inf.name(), 'SN:', inf.source_id(), 'Type:', inf.type(),
                                      '# of Ch:', inf.channel_count(), 'SampRate (SPS):', inf.nominal_srate(),
                                      'Montage:', montageDesc, '+MARKERS'])
        datSave.csvSave1D(csvName, [' '])
        datSave.csvSave1D(csvName, montageHeader)
        columnNum = inf.channel_count() + 2
    elif inf.type() == 'PSD':
        header = ['CHANNEL', 'TIME(s)', 'MARKER']
        for i in range(0, 263):
            header.append(str(i) + ' Hz')
        datSave.csvSaveInit(csvName, ['Name:', inf.name(), 'SN:', inf.source_id(), 'Type:', inf.type(),
                                      '# of Ch:', inf.channel_count()/263,
                                      'SampRate (SPS):', inf.nominal_srate(),
                                      'Channels:', inf.desc().child_value("chanListStr"), '+MARKERS'])
        datSave.csvSave1D(csvName, [' '])
        datSave.csvSave1D(csvName, header)
        chanList = inf.desc().child_value("chanListStr")
        chanList = chanList.split(',')
        columnNum = 263+3

    savRefresh = 1000  # ms
    samples = np.zeros((savRefresh, columnNum))
    count = 0

elif formatSelect == 1:  # MAT
    # File Naming
    fileName = raw_input('Input the filename for your recording: ')

    print("Recording data into " + fileName + ".mat...")

    # Initialize samples and timestamps buffer
    savRefresh = 1000  # ms
    samples = np.zeros((savRefresh, 10))
    timestamps = np.zeros((savRefresh, 1))

    date = datetime.datetime.now().date()
    date = str(date)
    date = map(float, date.split('-'))

    time = datetime.datetime.now().time()
    time = str(time)
    time = map(float, time.split(':'))

    cStart = np.array([date,time])
    cStart = np.ndarray.flatten(cStart)

    datSave.matSaveInit(fileName, cStart, inf.nominal_srate())

    count = 0

elif formatSelect == 2:  # BDF+
    bdfPort = datSave.bdfSaveInit(inf)
    savRefresh = 1000  # ms
    samples = np.zeros((savRefresh, 10))
    count = 0

# Log data from LSL stream into CSV file
try:
    timestamp = 0  # Initialize sample timestamp value for comparison with marker timestamp
    marker, timestampMark = inletMark.pull_sample()
    marker = [0]  # First input error
    while True:
        sample, timestamp = inlet.pull_sample()
        if timestamp < timestampMark:
            onsetMark = 0
        # elif timestamp == timestampMark:
        #     onsetMark = marker
        #     marker, timestampMark = inletMark.pull_sample()
        else:
            # onsetMark = 0
            # print("Marker at time = "+str(timestampMark)+" missed!")
            onsetMark = marker[0]
            print onsetMark
            marker, timestampMark = inletMark.pull_sample()
        if formatSelect == 0:  # CSV
            if inf.type() == 'PSD':
                for j in range(0, inf.channel_count()/263):
                    sampleRearranged = sample[j*263:(j+1)*263]
                    sampleRearranged.insert(0,timestamp)
                    sampleRearranged.insert(0,onsetMark)
                    sampleRearranged.insert(0,chanList[j])
                    samples[count] = sampleRearranged
                    #datSave.csvSave1D(csvName, sampleRearranged)
            else:
                sample.extend([timestamp, onsetMark])
                samples[count] = sample
                #datSave.csvSave1D(csvName, sample)
            count = count + 1
            if count == savRefresh:
                datSave.csvSave2D(csvName, samples)
                count = 0
        elif formatSelect == 1:  # MAT
            samples[count] = sample
            timestamps[count] = [timestamp]
            count = count + 1
            if count == savRefresh:
                datSave.matSave(fileName, 'data', samples, 'time', timestamps)
                #print timestamp
                count = 0
        elif formatSelect == 2:  # BDF+
            samples[count] = sample
            count = count + 1
            if count == savRefresh:
                bdfPort.writeSamples(np.transpose(samples))
                # print timestamp
                count = 0
except:
    if formatSelect == 1:  # CSV - saves remaining data
        if count > 2:
            samples = samples[0:count-1]
            datSave.csvSave2D(csvName, samples)
    elif formatSelect == 1:  # MAT - cStop input
        date = datetime.datetime.now().date()
        date = str(date)
        date = map(float, date.split('-'))

        time = datetime.datetime.now().time()
        time = str(time)
        time = map(float, time.split(':'))

        cStop = np.array([date, time])
        cStop = np.ndarray.flatten(cStop)
        datSave.matSave(fileName, 'cStop', cStop)

        if count > 2:
            samples = samples[0:count-1]
            timestamps = timestamps[0:count-1]
            datSave.matSave(fileName, 'data', samples, 'time', timestamps)
    elif formatSelect == 2:  # EDF+ - close port
        if count > 2:
            samples = samples[0:count-1]
            bdfPort.writeSamples(np.transpose(samples))
        bdfPort.close()

    print "Recording interrupted and stopped!"