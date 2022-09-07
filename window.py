from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkmacosx import Button as MacBtn
from simple_rpc import Interface
from glob import glob
import cgitb
from time import sleep
import time
from threading import Thread
import random

portSet = False
mainsOn = None
canvas = None
tree = None
startStatus = None
mainsStatus = None
portName = None
p = None
loopAnimationState = False
portsString = None
treeValues = [False,False,False,False,False,False,False]

def setPort():
    global portsString, interface, portSet

    if portsString.get() != "Choose Port":
        interface = Interface(portsString.get())
        portSet = True

def start():
    global startStatus, portName, p

    if portSet:
        if messagebox.askokcancel("Animation", "Start Animation?"):
            print("START")
            startStatus.config(text="Animation On,")
            p = Thread(target=animate)
            p.start()
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def loopAnimationUpdate():
    global loopAnimationState, loopAnimation
    
    loopAnimationState = loopAnimation.get()

def mains():
    global mainsOn, mainsStatus

    if portSet:
        if mainsOn:
            print("MAINS OFF")
            mainsOn = False
            mainsStatus.config(text="Mains Off")
            mainsRelay(False)
        else:
            if messagebox.askokcancel("120VAC On/Off", "Turn On 120VAC?"):
                print("MAINS ON")
                mainsOn = True
                mainsStatus.config(text="Mains On")
                mainsRelay(True)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def callback(event):
    if event.y >= 5 and event.y <= 35:
        if event.x < 35:
            toggleTree(0)
        elif event.x >= 35 and event.x < 65:
            toggleTree(1)
        elif event.x >= 65 and event.x < 95:
            toggleTree(2)
        elif event.x >= 95 and event.x < 125:
            toggleTree(3)
        elif event.x >= 125 and event.x < 155:
            toggleTree(4)
        elif event.x >= 155 and event.x < 185:
            toggleTree(5)
        elif event.x >= 185:
            toggleTree(6)

def animate():
    global loopAnimationState, portset, startStatus
    
    going = True
    if portSet:
        while going:
            allOff()
            for i in range(0, 7):
                setTree(i, True)
                sleep(1 / 7)
            for i in range(0, 7):
                setTree(i, False)
                sleep(1 / 7)
            sleep(1)
            allOn()
            sleep(1)
            trees = [False,False,False,False,False,False,False]
            for i in range(0, 7):
                validTree = True
                while validTree:
                    treeNum = random.randint(0, 6) ## 6 IS included
                    if trees[treeNum] == False:
                        validTree = False
                        trees[treeNum] = True
                        break;
                setTree(treeNum, False)
                sleep(1 / 7)
            allOff()
            sleep(0.5)
            trees = [True,True,True,True,True,True,True]
            for i in range(0, 7):
                validTree = True
                while validTree:
                    treeNum = random.randint(0, 6) ## 6 IS included
                    if trees[treeNum]:
                        validTree = False
                        trees[treeNum] = False
                        break;
                setTree(treeNum, True)
                sleep(0.75 / 7)
            allOn()
            sleep(1)
            allOff()
            
            going = loopAnimationState
        startStatus.config(text="Animation Off,")
    else:
        messagebox.showinfo("Set Port!","Set Port!")
        

def allOff():
    global portSet

    if portSet:
        for i in range(0, 7):
            setTree(i, False)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def allOn():
    global portSet

    if portSet:
        for i in range(0, 7):
            setTree(i, True)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def statusLed(value):
    global interface
    
    setPin(13, value)

def mainsRelay(value):
    global interface
    
    setPin(12, value)

def setTree(treeNum, value):
    global interface, treeValues

    treeValues[treeNum] = value
    treeIndicator(treeNum, value)
    setPin(treeNum + 2, value)

def toggleTree(treeNum):
    global treeValues
    if portSet:
        if treeValues[treeNum]:
            setTree(treeNum, False)
        else:
            setTree(treeNum, True)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def setPin(pinNum, value):
    if portSet:
        interface.digital_write(pinNum, value)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def getPin(pinNum):
    if portSet:
        return interface.digital_read(pinNum)
    else:
        messagebox.showinfo("Set Port!","Set Port!")

def treeIndicator(treeNum, value):
    global canvas, tree

    if value:
        canvas.itemconfig(tree[treeNum], fill='red')
    else:
        canvas.itemconfig(tree[treeNum], fill='grey')

def detectDoorbell():
    global portSet

    while not portSet:
        nothing = "This does nothing, but I must obey the compiler"
    while True:
        if getPin(11) == False:
            while not getPin(11):
                nothing = "This does nothing, but I must obey the compiler"
            messagebox.showinfo("Doorbell!","Someone has Pressed the Doorbell!\nPausing Animation...\nHit OK to resume")
        sleep(0.1)

def main():
    global portSet, going, mainsOn, canvas, tree, startStatus, mainsStatus, loopAnimation, portsString
    
    cgitb.enable()

    p2 = Thread(target=detectDoorbell)
    p2.start()

    portSet = False

    mainsOn = False

    ports = glob('/dev/tty.*')

    root = Tk()
    root.title("X-Mas Lights Controller")
    root.configure(width=1000, height=600, bg="lightgray")

    padded = Frame(root, bg="lightgray")

    closeBtn = MacBtn(root, text="Close", command=root.destroy, bg="black", fg="white")
    closeBtn.pack(side=TOP, anchor=NW, padx=5, pady=5)

    portSelect = Frame(padded)

    portsString = StringVar(portSelect)
    portsString.set("Choose Port")
    port = OptionMenu(portSelect, portsString, *ports)
    port.pack(side=LEFT)

    portBtn = MacBtn(portSelect, text="Select", command=setPort)
    portBtn.pack(side=LEFT)

    portSelect.pack(side=TOP)

    buttons = Frame(padded, bg="lightgray")

    animationFrame = Frame(buttons)
    startBtn = MacBtn(animationFrame, text="Start Animation", command=start, bg="green", fg="white").pack(side=LEFT)
    loopAnimation = IntVar()
    loopBox = Checkbutton(animationFrame, text='Loop Animation', variable=loopAnimation, onvalue=1, offvalue=0, command=loopAnimationUpdate).pack(side=LEFT)
    animationFrame.pack(side=TOP)

    mainsBtn = MacBtn(buttons, text="Turn 120VAC On/Off", command=mains, bg="#2d8cff", fg="white").pack(side=TOP)

    buttons.pack(side=TOP)

    status = Frame(padded)

    startStatus = Label(status, text="Animation Off,", bg="lightgray")
    startStatus.pack(side=LEFT)

    mainsStatus = Label(status, text="Mains Off", bg="lightgray")
    mainsStatus.pack(side=LEFT)

    status.pack(side=TOP)

    canvas = Canvas(padded, width=220, height=40, bg="lightgray")
    canvas.bind("<Button-1>", callback)
    canvas.pack(side=TOP)

    offOnBtns = Frame(padded, bg="lightgray")
    
    allOnBtn = MacBtn(offOnBtns, text="All On", command=allOn, bg="red", fg="white").pack(side=LEFT)
    allOffBtn = MacBtn(offOnBtns, text="All Off", command=allOff, bg="gray", fg="white").pack(side=LEFT)

    offOnBtns.pack(side=TOP)

    tree = [None, None, None, None, None, None, None]
    for i in range(0, 7):
        tree[i] = canvas.create_rectangle((i * 30) + 5, 35, (i * 30) + 35, 5, outline='black', fill="grey")

    padded.pack(padx=50, pady=50)

    root.mainloop()
    if portSet:
        mainsRelay(False)
        allOff()
    print("Window Closed")

if __name__ == "__main__":
    main()
