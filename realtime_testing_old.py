from pathlib import Path
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
import mmwave as mm
import mmwave.dsp as dsp
import numpy as np
from mmwave.dataloader import DCA1000
from mmwave.dsp.utils import Window
from datetime import datetime



def remove_files(num_frames):
    """
    Removes test files
    """
    for i in range(250):
        Path(f'temp{i}.png').unlink()


numChirpsPerFrame = 192
numRxAntennas = 4
numADCSamples = 512
numTxAntennas = 3
# ----------CHANGE num_frames TO WHAT WE USE-------------
num_frames = 1
# -------------------------------------------------------



# adc_data_file = Path('./adc_data.txt')
# adc_data = np.fromfile(adc_data_file, sep = '\n')

# adc_data = adc_data.astype(complex).view(complex)

# print("Then length is: ")
# print(len(adc_data))
# print(adc_data[0::2])
dca = DCA1000()

times = []
figs = [70]
axs = [70] 
while True:
    
    
    adc_data = dca.read() # Read in ADC data from the DCA board

    # save_str = "{0}{1}.txt".format("adc_data",num_frames)
    # np.savetxt(save_str,adc_data)
    #frame = dca.organize(adc_data, numChirpsPerFrame, numRxAntennas, numADCSamples)

    # ------------What organize does-------START---------
    start = datetime.utcnow() # Start Timer
    ret = np.zeros(len(adc_data) // 2, dtype=complex)

    # Separate IQ data of all 4 receive antennas 
    #rx1 data
    ret[0::4] = adc_data[0::8] + 1j * adc_data[4::8]
    #rx1_data = ret[0::4]
    #rx2 data
    ret[1::4] = adc_data[1::8] + 1j * adc_data[5::8]
    #rx2_data = ret[1::4]
    #rx3 data
    ret[2::4] = adc_data[2::8] + 1j * adc_data[6::8]
    #rx3_data = ret[2::4]
    #rx4 data
    ret[3::4] = adc_data[3::8] + 1j * adc_data[7::8]
    #rx4_data = ret[3::4]

    #reshape ret into 3D array of 1 frame
    frame = ret.reshape((numChirpsPerFrame, numADCSamples, numRxAntennas))
    #swap axes to create a number of arrays equal to the number of chirps per frame
    #each array is numRx * numADCSamples
    frame = frame.swapaxes(1,2)

    # get radar cube data
    radar_cube = dsp.range_processing(frame, window_type_1d=Window.BLACKMAN)

    # Doppler processing
    det_matrix, aoa_input = dsp.doppler_processing(radar_cube, num_tx_antennas=3,clutter_removal_enabled=False)

    det_matrix_vis = np.fft.fftshift(det_matrix, axes=1)
    
    normalized = det_matrix_vis-det_matrix_vis.max()
    print(num_frames)
    num_frames = num_frames + 1



    # *************Start of Plotting**************
    plt.imshow(normalized, origin='lower', aspect='auto',vmin=-90)

    range_res = 0.05
    vel_res = 1
    range_step = 50
    vel_step = 8
    rangeAxis = np.arange(0,512,range_step)*range_res
    velocityAxis = np.arange(-64/2,64/2,vel_step)*vel_res
    plt.yticks(np.arange(0,512,range_step),rangeAxis)
    plt.xticks(np.arange(0,64,vel_step),velocityAxis)

    
    #plt.xlabel(labelpad='Velocity (m/s)')
    #plt.ylabel(labelpad='Distance (m)')
    plt.title(label=num_frames-1)
    plt.colorbar()
    #plt.show()
    plt.pause(0.00001)
    #plt.savefig(f'temp{num_frames-1}.png')
    plt.clf()

    # ************


    # range_res = 0.05
    # vel_res = 1
    # range_step = 50
    # vel_step = 8
    # rangeAxis = np.arange(0,512,range_step)*range_res
    # velocityAxis = np.arange(-64/2,64/2,vel_step)*vel_res


    # plt.imshow(normalized, origin = 'lower', aspect = 'auto')
    # plt.yticks(np.arange(0,512,range_step),rangeAxis)
    # plt.xticks(np.arange(0,64,vel_step),velocityAxis)
    # plt.title(label=num_frames)
    # #plt.colorbar()
    # plt.show()
    # plt.pause(0.0001)
    # plt.clf()
    
    # plt.pause(0.0001)
    # plt.clf()

    # plt.savefig(f'temp{i}.png')
    end = datetime.utcnow()
    times.append((end-start).microseconds)
    if num_frames == 100:
        print(np.mean(times)/1e6)        
    
print(np.mean(times)/1e6)
#remove_files(70)

