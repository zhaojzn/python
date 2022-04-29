
import aubio
import numpy as num
import pyaudio
import sys
import PySimpleGUI as sg
import math
import pyfirmata

# Some constants for setting the PyAudio and the
# Aubio.
BUFFER_SIZE             = 2048
CHANNELS                = 1
FORMAT                  = pyaudio.paFloat32
METHOD                  = "default"
SAMPLE_RATE             = 44100
HOP_SIZE                = BUFFER_SIZE//2
PERIOD_SIZE_IN_FRAME    = HOP_SIZE


#constant
GRAPH_SIZE = (500, 500)
DATA_SIZE = (2500,2500)
# 
PLOTS_NUMBER = 30
RAND_MAX = 400
#Animation
GRAPH_STEP_SIZE = 5
DELAY = 15  #Time interval
#Layout
#Setting the drawing area of the graph
graph = sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE,
                 key='-GRAPH-', background_color='white',)

layout = [[sg.Text('data')],
          [graph],
          [sg.Button('animation') ]]

window = sg.Window('mic volume graph', layout)

before_value = 0  #Initialize line graph
delay = x = lastx = lasty = 0  #Animation initialization

pA = pyaudio.PyAudio()
# Open the microphone stream.
mic = pA.open(format=FORMAT, channels=CHANNELS,
    rate=SAMPLE_RATE, input=True,
    frames_per_buffer=PERIOD_SIZE_IN_FRAME)
# Initiating Aubio's pitch detection object.
pDetection = aubio.pitch(METHOD, BUFFER_SIZE,
    HOP_SIZE, SAMPLE_RATE)
# Set unit.
pDetection.set_unit("Hz")
# Frequency under -40 dB will considered
# as a silence.
pDetection.set_silence(-40)
# Infinite loop!
process = True

board = pyfirmata.Arduino('COM3')
board.digital[13].write(0)

while process:
    # Always listening to the microphone.
    data = mic.read(PERIOD_SIZE_IN_FRAME)
    # Convert into number that Aubio understand.
    samples = num.frombuffer(data,
        dtype=aubio.float_type)
    # Finally get the pitch.
    pitch = pDetection(samples)[0]
    # Compute the energy (volume)
    # of the current frame.
    volume = num.sum(samples**2)/len(samples)
    # Format the volume output so it only
    # displays at most six numbers behind 0.
    volume = "{:6f}".format(volume)
    
    if(pitch > 1):
        print("Voice trigger volume activated")
        board.digital[13].write(1)
        print(pitch)
        #process = False
    event = 'animation'
    is_animated = True
    if is_animated:
        #Regularly'__TIMEOUT__'Event is issued
        event, values = window.Read(timeout=DELAY)
    else:
        event, values = window.Read()
    if event == 'animation' or is_animated:
        if not is_animated:
            graph.Erase()  #Delete the graph once
        #Display a graph that moves in chronological order
        step_size, delay = GRAPH_STEP_SIZE, DELAY
        y = pitch
        if x < GRAPH_SIZE[0]:  #First time
            # window['-GRAPH-'].DrawLine((lastx, lasty), (x, y), width=1)
            graph.DrawLine((lastx, lasty), (x, y), width=1)
        else:
            # window['-GRAPH-'].Move(-step_size, 0)  #Shift the entire graph to the left
            # window['-GRAPH-'].DrawLine((lastx, lasty), (x, y), width=1)
            graph.Move(-step_size, 0)  #Shift the entire graph to the left
            graph.DrawLine((lastx, lasty), (x, y), width=1)
            x -= step_size
            lastx, lasty = x, y
        lastx, lasty = x, y
        x += step_size
    board.digital[13].write(0)
window.Close()
