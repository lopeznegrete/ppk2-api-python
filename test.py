
"""
Basic usage of PPK2 Python API.
The basic ampere mode sequence is:
1. read modifiers
2. set ampere mode
3. read stream of data
"""
import time
import datetime
from ppk2_api.ppk2_api import PPK2_API

ppk2s_connected = PPK2_API.list_devices()
if(len(ppk2s_connected) == 1):
    ppk2_port = ppk2s_connected[0]
    print(f'Found PPK2 at {ppk2_port}')
else:
    print(f'Too many connected PPK2\'s: {ppk2s_connected}')
    exit()

ppk2_test = PPK2_API(ppk2_port)
ppk2_test.get_modifiers()
ppk2_test.use_ampere_meter()  # set ampere meter mode
ppk2_test.toggle_DUT_power("ON")  # enable DUT power
ppk2_test.set_source_voltage(4150)  # set source voltage in mV
time.sleep(1)
ppk2_test.start_measuring()  # start measuring



# measurements are a constant stream of bytes
# multiprocessing variant starts a process in the background which constantly
# polls the device in order to prevent losing samples. It will buffer the
# last 10s (by default) of data so get_data() can be called less frequently.
loops = 0
loop_start_time = time.time();
average_current_mA = 0;
average_consumption_mWh = 0;

while(1):
    read_data = ppk2_test.get_data()
    loops += 1;
    if read_data != b'':
        samples = ppk2_test.get_samples(read_data)
        average_current_mA += (sum(samples) / len(samples)) / 1000  # measurements are in microamperes, divide by 1000
        average_power_mW = (ppk2_test.current_vdd / 1000) * average_current_mA  # divide by 1000 as source voltage is in millivolts - this gives us milliwatts
        measurement_duration_h = 10 / 3600  # duration in seconds, divide by 3600 to get hours
        average_consumption_mWh += average_power_mW * measurement_duration_h
        if (time.time() - loop_start_time > 1):
            loop_start_time = time.time();
            print(f"[{datetime.datetime.now()}] Average is: {average_current_mA/loops}mA {average_consumption_mWh/loops}mWh")

    time.sleep(0.02441)  # lower time between sampling -> less samples read in one sampling period

ppk2_test.stop_measuring()
