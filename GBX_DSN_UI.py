##############################################################################################################
#  Programmer: Jacob Serena                                                                                  #
#  Company: Culligan International                                                                           #
#  Title: GBX DSN Scruber                                                                                    #
#  Date: 11/23/2020                                                                                          #
#                                                                                                            #
##############################################################################################################
# Purpose: A program that will scrub and XML file for a DSN and then Program a decvice. GBX, Twin, and SRO   #
#                                                                                                            #
##############################################################################################################

from tkinter import *
import tkinter as tk 
from tkinter import filedialog
import os, tkinter, serial, time, io, shutil, sys
from serial.tools.list_ports import comports   

# Setup the Tkinter window
root = Tk()                                             # Now I will use the name root when adding to frame
root.title("Culligan DSN Programer")                    # Set program name
root.configure(bg='#ffffff')                            # Color of the window


def RenameSRO():
    global name
    name= 'SRO.xml'
    btnSRO= Button(root, bg='#add8e6', text= "SRO", width = 20, command=RenameSRO)
    btnSRO.grid(row=3, column=3)
    btnGBX= Button(root, text= "GBX Single", width = 20, command=RenameGBX)
    btnGBX.grid(row=3, column=1)
    btnGBXTwin= Button(root, text= "GBX Twin", width = 20, command=RenameGBXTwin)
    btnGBXTwin.grid(row=3, column=2) # Change File name after selected. Shift button color after slected.


def RenameGBX():
    global name
    name= 'GBX_Single.xml'
    btnGBX= Button(root, bg='#add8e6', text= "GBX Single", width = 20, command=RenameGBX)
    btnGBX.grid(row=3, column=1)
    btnSRO= Button(root, text= "SRO", width = 20, command=RenameSRO)
    btnSRO.grid(row=3, column=3)
    btnGBXTwin= Button(root, text= "GBX Twin", width = 20, command=RenameGBXTwin)
    btnGBXTwin.grid(row=3, column=2) # Change File name after selected. Shift button color after slected.


def RenameGBXTwin():
    global name
    name= 'GBX_TWIN.xml'
    btnGBXTwin= Button(root, bg='#add8e6' ,text= "GBX Twin", width = 20, command=RenameGBXTwin)
    btnGBXTwin.grid(row=3, column=2)
    btnSRO= Button(root, text= "SRO", width = 20, command=RenameSRO)
    btnSRO.grid(row=3, column=3)
    btnGBX= Button(root, text= "GBX Single", width = 20, command=RenameGBX)
    btnGBX.grid(row=3, column=1) # Change File name after selected. Shift button color after slected.


def getFile():
    filename= filedialog.askopenfilename()  #search for file
    fileRead= open(filename, 'r')
    DSNfile = fileRead.readlines()          # Read the key file in lines
    key = open('Key.txt', 'w')              # Store key in this file
    key.write('nvs-set "ada.f.id/key" ')
    for x in range(4,9):                    # print lines 4-9     
        key1 = DSNfile[x].rstrip('\n')      # Remove Paragraph
        key.write(key1)                     # Write lines 4-9 to Temp file                
    key.close()                             # Close file
    fileRead.close()
    
    
    # Get the file name and store it in a global
    DSNfilename= str(DSNfile[2])
    DSNfilename= DSNfilename.strip(" <dsn>")
    DSNfilename= DSNfilename.strip("</dsn>\n")

    Dev_ID = open('DSN.txt', 'w')
    Dev_ID.write('nvs-set "ada.f.id/dev_id" ')
    Dev_ID.write(DSNfilename)
    Dev_ID.close()
    

    # Perpare to change the name of the file.
    print(filename)
    Newfilename = filename.strip(name)          # Just incase you run the same file twice
    Newfilename = Newfilename.strip('_Taken_')
    Newfilename = Newfilename.strip('.xml')
    # Change the name of the file.
    shutil.move(filename, Newfilename + '_Taken_' + name) # Scrub the file and print the key to a txt file.
    SelectedDSN_number = Label(root, bg='#ffffff', text="DSN Selected: ").grid(row=5, column=1,) 
    SelectedDSN_number1 = Label(root, bg='#ffffff', text=""+ DSNfilename).grid(row=5, column=2,) # Find the DSN file. Display it after it has been selected.


def ListCOMports():   
    port = list(comports())
    
    available_port = []

    for p in port:
        available_port.append(p.device)

    return available_port # List availbe COM ports


def programCOM():

    # Scrubbed DSN key file open and formate
    DSN = open('Key.txt', 'r+')
    Key = DSN.readlines()
    Key = str(Key)
    Key = Key.strip('[]')
    Key = Key.strip('\'\'')
    DSN.close()
    
    # Scrubbed Dev DSN file open and formate
    Dev_ID = open('DSN.txt', 'r+')
    dev_id = Dev_ID.readlines()
    dev_id = str(dev_id)
    dev_id = dev_id.strip('[]')
    dev_id = dev_id.strip('\'\'')
    Dev_ID.close()


    # DSN COM
    ser = serial.Serial(port = optionVar.get(), baudrate = 115200, timeout = 0, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)
    #ser.timeout = None        #block read
    #ser.timeout = 1           #non-block read
    #ser.timeout = 2           #timeout block read
    ser.xonxoff = True         #disable software flow control
    ser.rtscts = True          #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = True          #disable hardware (DSR/DTR) flow control
    #ser.writeTimeout = 2      #timeout for write
    
    # DSN
    print('1%')
    ser.write(bytes(dev_id + '\r\n', encoding= 'utf-8'))

    # Key
    print('10%')
    ser.write(bytes(Key + '\r\n', encoding= 'utf-8'))

    # Save
    print('20%')
    ser.write(bytes(b'save \r\n'))

    # Reboot
    print('30%')
    ser.write(bytes(b'esp-reboot \r\n'))
    time.sleep(8)
    
    # Oem key
    print('50%')
    ser.write(bytes(b'oem key 74042fa9f33fc93bda0482b0ed78c57f \r\n'))

    # Save
    print('60%')
    ser.write(bytes(b'save \r\n'))

    # Reboot
    print('80%')
    ser.write(bytes(b'esp-reboot \r\n'))
    time.sleep(8)
    
    # Disable setup
    print('90%')
    ser.write(bytes(b'setup_mode disable \r\n'))

    # Save
    print('100%')
    ser.write(bytes(b'save \r\n'))
    
    # Clear the buffer before reading from serial port to prevent garbage read.
    for i in range (0,10):
        time.sleep(0.1)
        ser.flushInput()
        ser.flushOutput()
        time.sleep(0.1)
    
    # WIFI
    ser.write(bytes('show wifi' + '\r\n', encoding= 'utf-8'))

    # OEM
    ser.write(bytes('oem' + '\r\n', encoding= 'utf-8'))

    # Setup Mode
    ser.write(ser.write(bytes('setup_mode show' + '\r\n', encoding= 'utf-8')))

    numOfLines = 0
    while True:
          time.sleep(0.1)
          response = ser.readline()
          response = str(response)
          
          if response != "b''":                      # Removes empty lines from the program read.
               response = response.strip("b'")       # Removes the b' from the begining of each line.
               response = response.rstrip("r\*\*n'")
               print(response)                       # Output

          numOfLines = numOfLines + 1                # Increase the loop count. 

          if (numOfLines >= 80):                     # I only need to see about 80 lines. Break when condition met.
            break
    print('===============================================================================') # Open the COM port and Program device.
    
    # Pulls the last Programmed DSN from file and displays
    lastProgrammedDSN = open('DSN.txt', 'r')
    LPDSN = lastProgrammedDSN.readlines()
    LPDSN = LPDSN[0].strip('nvs-set "ada.f.id/dev_id" ')
    LastDSN_number = Label(root, bg='#ffffff', text="Last Programmed DSN: ").grid(row=6, column=1,) 
    LastDSN_number1 = Label(root, bg='#ffffff', text="" + str(LPDSN)).grid(row=6, column=2,) # Program the device! Should display the percent left and the DSN after programming.



# Select a COM port.
optionVar = StringVar()                                                         # Specify that optionVar is a string
optionVar.set("Select COM Port")                                                # Label the comport menu
COMport = OptionMenu(root, optionVar, *ListCOMports()).grid(row= 0, column= 0)  # This shows the drop down menu.


#Blank Spaces
Space = Label(root, bg='#ffffff' ,text="").grid(row= 2)
Space = Label(root, bg='#ffffff' ,text="").grid(row= 4)
Space = Label(root, bg='#ffffff' ,text="").grid(row= 6)
Space = Label(root, bg='#ffffff' ,text="").grid(row= 8)

# Button to find DSN xml file.
btnFind_DSN1= Button(root, text= "Select DSN File", width = 20, command=getFile).grid(row= 5, column= 0,)

# Name the used file according to the name given.
COMport1 = Label(root, bg='#ffffff', text="Board type").grid(row= 3)
btnSRO= Button(root, text= "SRO", width = 20, command=RenameSRO).grid(row=3, column=3)
btnGBX= Button(root, text= "GBX Single", width = 20, command=RenameGBX).grid(row=3, column=1)
btnGBXTwin= Button(root, text= "GBX Twin", width = 20, command=RenameGBXTwin).grid(row=3, column=2)


# Button that calls def programCOM. Opens a COM port and starts the progrogram.
ProgramDSN= Button(root, activebackground='#ffff99' ,text="Program", width = 20,command=programCOM).grid(row=9, column=0)

root.mainloop() # No code executes after the program close. This will allow the user to run the program multiple time in a row.