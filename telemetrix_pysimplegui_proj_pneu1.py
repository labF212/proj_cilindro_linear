import PySimpleGUI as sg
import time
from telemetrix import telemetrix
import sys

CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'

def LED(color, key):
    """
    A "user defined element".  In this case our LED is based on a Text element. This gives up 1 location to change how they look, size, etc.
    :param color: (str) The color of the LED
    :param key: (Any) The key used to look up the element
    :return: (sg.Text) Returns a Text element that displays the circle
    """
    return sg.Text(CIRCLE_OUTLINE, font="Any 36",text_color=color, key=key)

# Format of the current time
TIME_FORMAT = "%H:%M:%S"
 
# Format of the current date
DATE_FORMAT = "%d/%m/%Y"

# Some globals
# Make sure to select the analog pin numbers (A1 and A5)
ANALOG_PIN1 = 1 #sensor de distância analógico1
ANALOG_PIN5 = 5 #sensor de distância analógico2

DIGITAL_PIN2 = 4 #mudar para 9   Relé liga/desliga válvula esq
DIGITAL_PIN3 = 13 #mudar para 10 Relé liga/desliga válvula dir

DIGITAL_READ3 = 2 #sensor limite esquerdo
DIGITAL_READ5 = 3 #sensor limite direito

DIGITAL_PIN9 = 5  #Regular tensão para ITV1 (-SLIDER1-) esquerda (avanço)
DIGITAL_PIN10 = 6 #Regular tensão para ITV2 (-SLIDER2-) direita (recuo)


# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# Dictionary to store the analog values
analog_values = {ANALOG_PIN1: 0, ANALOG_PIN5: 0}
digital_values = {DIGITAL_PIN9: 0, DIGITAL_PIN10: 0}

sg.theme('DarkAmber')

layout = [
    [sg.Text((''), key='-DATE-'), sg.Push(), sg.Text((''), key='-TIME-')],
    [sg.Text('Direcção:'),sg.Radio("Esquerda","direcao",key='-ESQ-',enable_events=True),sg.Radio("Parado", "direcao",key='-PAR-', default=True),sg.Radio("Direita","direcao",key='-DIR-'),sg.Push()],
    [sg.Text('Controlo de velocidade - ITV0010-2L (Esquerda para direita)'),
     sg.Text('None', expand_x=True, key='-TRANS1-', justification='right', auto_size_text=True)],
    [sg.Slider((0,100), orientation='h', s=(50,15),disable_number_display=True,key='-SLIDER1-', expand_x=True)],
    [sg.Text('Controlo de velocidade - ITV0010-2L (Direita para esquerda)'),
    sg.Text('None', expand_x=True, key='-TRANS2-', justification='right', auto_size_text=True)],
    [sg.Slider((0,100), orientation='h', s=(50,15),disable_number_display=True,key='-SLIDER2-', expand_x=True)],
    [sg.Text('Distância ao sensor:'),
    sg.Text('None', expand_x=True, key='-TEMP1-', justification='right', auto_size_text=True)],
    
    [sg.Text('Analog Reading in Pin A1:'),
     sg.ProgressBar(1024, orientation='h', size=(20, 20), key='-VALUE1-'),
     sg.Text('None', expand_x=True, key='-VALUEA1-', justification='right',
             auto_size_text=True)],
    [sg.Text('Analog Reading in Pin A5:'),
     sg.ProgressBar(1024, orientation='h', size=(20, 20), key='-VALUE5-'),
     sg.Text('None', expand_x=True, key='-VALUEA5-', justification='right',
             auto_size_text=True)],
    [sg.Push(), sg.Text('Sensor Recuado '), LED('RED', '-LED0-'),sg.Text('Sensor Avançado '), LED('RED', '-LED1-') , sg.Push() ],
    [sg.Push(), sg.Button('Exit'), sg.Push()]
]


def the_callback(data):
    analog_values[data[CB_PIN]] = data[CB_VALUE]
    digital_values[data[CB_PIN]] = data[CB_VALUE]
    
    global date
    global current_time
    date = time.strftime('%Y-%m-%d', time.localtime(data[CB_TIME]))
    current_time = time.strftime('%H:%M:%S', time.localtime(data[CB_TIME]))

# Create a Telemetrix instance
board = telemetrix.Telemetrix()
board.set_pin_mode_analog_input(ANALOG_PIN1, callback=the_callback)
board.set_pin_mode_analog_input(ANALOG_PIN5, callback=the_callback)

board.set_pin_mode_digital_output(DIGITAL_PIN2)
board.set_pin_mode_digital_output(DIGITAL_PIN3)

board.set_pin_mode_analog_output(DIGITAL_PIN9)
board.set_pin_mode_analog_output(DIGITAL_PIN10)


# creates a window Title
window = sg.Window('Arduino LED Light Manual Control)', layout, resizable=True,
                   finalize=True)
while True:
    event, values = window.read(1000)  # window refresh time

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        board.digital_write(DIGITAL_PIN9, 0)
        board.digital_write(DIGITAL_PIN10, 0)
        board.shutdown()
        sys.exit(0)

    if values["-ESQ-"] == True:
        #board.analog_write(ANALOG_WRITE3,1)
        #board.analog_write(ANALOG_WRITE5,0)
        
        #value_slider1= (values['-SLIDER1-'])/100
        #digital_write3.write(value_slider1)
        board.digital_write(DIGITAL_PIN9, 1)
        board.digital_write(DIGITAL_PIN10, 0)
        
        window["-LED1-"].update(CIRCLE)
        print("esquerda")
        
    if values["-DIR-"] == True:
        print("direita")
        board.digital_write(DIGITAL_PIN9, 0)
        board.digital_write(DIGITAL_PIN10, 200)
        
    if values["-PAR-"] == True:
        board.digital_write(DIGITAL_PIN9, 0)
        board.digital_write(DIGITAL_PIN10, 0)
        print("parado") 
        
        window["-LED1-"].update(CIRCLE_OUTLINE)   

    voltage1 = analog_values[ANALOG_PIN1]
    window['-VALUE1-'].update(voltage1)
    voltage1a = voltage1 / (1023 / 5)
    window['-VALUEA1-'].update(f'{voltage1a:.2f} V')

    voltage5 = analog_values[ANALOG_PIN5]
    window['-VALUE5-'].update(voltage5)
    voltage5a = voltage5 / (1023 / 5)
    window['-VALUEA5-'].update(f'{voltage5a:.2f} V')
    
    #Capture the values of the slider (0 to 100)
    value_slider1= int ((values['-SLIDER1-'])*2.55)
    value_slider2= int ((values['-SLIDER2-'])*2.55)
    
    #Write the converted values to arduino PWD pins
    board.analog_write(DIGITAL_PIN9, value_slider1)
    board.analog_write(DIGITAL_PIN10, value_slider2)
    
    #Update the PWD values of the slider in the screen 
    window['-TRANS1-'].update(str(value_slider1)+" PWD")
    window['-TRANS2-'].update(str(value_slider2)+" PWD")
    
    
    window['-TIME-'].update(current_time)
    window['-DATE-'].update(date)

window.close()