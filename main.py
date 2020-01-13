#################
###Import
#################

#region Frontend
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
#endregion Frontend

#region Backend
import numpy as np
from pmxutils.mathtools import advConstruct, construct, isInbetween
#endregion Backend

#################
###Initialization
#################

#region GUI Initialization
root = tk.Tk()
root.wm_title("Koi")
root.state("zoomed")
#endregion GUI Initialization

#region Settings
s = tk.Frame(root)

YEAR = 12
av = tk.IntVar(s, 0)                    #Start of intervall
bv = tk.IntVar(s, 10)                   #End of intervall
isYear = tk.StringVar(s, "Months")      #Wether time intrvall is in Years or Months
y0v = tk.IntVar(s, 100)                 #Startvalue for koi mass in kg


#Bv = tk.IntVar(s, 1e5)                  #Carrying Capacity
lv = tk.DoubleVar(s, 50)               #Length of tank
wv = tk.DoubleVar(s, 25)               #Width of tank
dv = tk.DoubleVar(s, 5)               #Depth of tank

lengthToWeight = 0.0885                 #Weight/Length of average koi
lengthGrowthMonth = 2                   #cm grown each month
gv = tk.DoubleVar(s, lengthToWeight*lengthGrowthMonth) #Growth Rate


Resv = tk.IntVar(s, 100)                    #Resolution
growthv = tk.IntVar(s, 12)                  #Months with no harvest
Safetyv = tk.IntVar(s, 50)                  #Safety limit to avoid population collapse
ConsAmountv = tk.IntVar(s, 0)               #Constant amount to harvest each month
VarAmountv = tk.IntVar(s, 0)                #Harvest each month proportional to population
RocketGrowthv = tk.DoubleVar(s, 5)          #Growth Rate for Rocket
HarvestSizev = tk.IntVar(s, 10)             #Minimum Rocket biomass before harvesting everything
KoiPricev = tk.DoubleVar(s, 38.33)          #Prcie for 1 kg Koi
RocketPricev = tk.DoubleVar(s, 189.82)      #Price for 1 kg Rocket salad

'''
ElectricityCostv = tk.DoubleVar(s, 0.4635)  #Price for 1 kwh
Heatingv = tk.IntVar(s, 0)                  #Maximum degrees to heat
HeatingModev = tk.StringVar(s, "Max")
'''

KoiHarvestSizev = tk.IntVar(s, 50)         #Minimum size of koi pop before harvest
KoiHarvestIntervallv = tk.IntVar(s, 1)       #How often, in months, koi should be harvested
cal = 1.162e-6                              #Calories per kwh, heats 1g of water by 1C
spaceReq = 0.14                             #Qubic meters of water per kg koi        
#endregion Settings

#Main math function
def compute():
    #region Initializing
    if isYear.get() == "Years":
        a = av.get()*YEAR
        b = bv.get()*YEAR
    else:
        a = av.get()
        b = bv.get()
    y0 = y0v.get()
    vol = (lv.get()*wv.get()*dv.get())
    B = vol/spaceReq
    g = gv.get()/YEAR
    Res = Resv.get()
    growth = growthv.get()
    Safety = Safetyv.get()
    ConsAmount = ConsAmountv.get()
    VarAmount = VarAmountv.get()/100
    RocketGrowth = RocketGrowthv.get()/100
    HarvestSize = HarvestSizev.get()
    KoiPrice = KoiPricev.get()
    RocketPrice = RocketPricev.get()
    '''
    ElectricityCost = ElectricityCostv.get()
    water = 1000*vol*1000 #1 Qubic meter of water is 1000L, 1L is 1000 grams
    heating = Heatingv.get()
    HeatingMode = HeatingModev.get()
    '''
    KoiHarvestSize = KoiHarvestSizev.get()
    KoiHarvestIntervall = KoiHarvestIntervallv.get()


    #Step and Step size
    N = int((b-a)*Res)
    h = (b-a)/(N-1)
    t = np.linspace(a, b, N)

    #Temperature
    temp = np.zeros(N)
    temp[0] = 11
    '''
    dT = np.zeros(N)
    dT[0] = 11
    '''

    #Koi
    K = np.zeros(N)
    #Ks = np.zeros(N)
    K[0] = y0

    #Harvest
    H = np.zeros(N)
    H[0] = 0

    #Rocket
    R = np.zeros(N)
    Rh = np.zeros(N)

    #Gains
    Kg = np.zeros(N)    #Gains from selling Koi
    Rg = np.zeros(N)    #Gains from selling Rocket
    G = np.zeros(N)

    #Losses
    '''
    E = np.zeros(N)     #Electricity
    El = np.zeros(N)    #Losses from buying Electricity
    '''
    NET = np.zeros(N)
    #endregion Initializing
    
    #region Math
    
    #Expressions
    Mf = advConstruct("1-(11/t)", "t")                                                          #Metabolism
    Kd = advConstruct("(g*k*(1-k/B)*M)-(M*k*0.1)", "k", "M", constants={"B":B, "g":g+1})    #Growth-Cannibalism
    Rd = advConstruct("k*g*(1-r/(k*0.05))", "r", "k", constants={"g":RocketGrowth})

    for i in range(int((N)-1)):
        ###Harvest
        noHarvest = range(0, Res*growth, Res)
        if ((i % (Res*KoiHarvestIntervall) == 0) and (i not in noHarvest) and (K[i] > Safety) and (K[i]/B)>=(KoiHarvestSize/100)): # 
            H[i] = H[i] + (K[i]*VarAmount) + (ConsAmount)
            K[i] = K[i] - (K[i]*VarAmount) - (ConsAmount)
            Kg[i+1] = Kg[i] + ((K[i]*VarAmount) + (ConsAmount))*KoiPrice
        else:
            Kg[i+1] = Kg[i]

        Rh[i+1] = Rh[i]
        R[i+1] = R[i] + Rd(R[i], K[i])*h

        if R[i] >= HarvestSize:
            Rh[i+1] = R[i]+Rh[i]
            Rg[i+1] = Rg[i] + R[i]*RocketPrice
            R[i+1] = 0
        else:
            Rg[i+1] = Rg[i]
        ###Growth

        #Temperature and Metabolism
        temp[i+1] = np.sin((i+1)*h/2+5)*5+16    #Natural temperature of pool

        #Heating
        '''
        if HeatingMode == "Max":
            dTemp = 21-temp[i]
            if dTemp > heating:
                dTemp = heating
            dT[i+1] = temp[i+1]+dTemp
        else:
            dTemp = 0
            if temp[i] < heating:
                dTemp = heating - temp[i]
                dT[i+1] = heating
            else:
                dT[i+1] = temp[i]
        '''
        #Koi Growth
        M = Mf(temp[i])
        K[i+1] = K[i] + Kd(K[i], M) * h
        

        #Ensure constant value inbetween harvest
        H[i+1] = H[i]
        
        #Gains and Losses
        '''
        E[i] = dTemp*cal*water
        El[i+1] = E[i]*ElectricityCost + El[i]
        '''
        G[i+1] = Rg[i] + Kg[i]
        NET[i+1] = G[i]# - El[i]
    #endregion Math

    #region plot
    ###Figure One
    #region Koi and Harvest
    fig =  Figure()
    axK = fig.add_subplot(111)
    dataK = axK.plot(t, K, "-b", label="Koi")
    axH = axK.twinx()
    dataH = axH.plot(t, H, "-g", label="Harvested")

    #Key
    data = dataK + dataH
    datatittel = [l.get_label() for l in data]
    axK.legend(data, datatittel, loc=0)

    #Layout
    axK.set_ylim(0, np.amax(K)+np.amax(K)*0.1)
    axH.set_ylim(0, np.amax(H)+np.amax(H)*0.1)
    axK.grid(True)

    #Info
    axK.set_xlabel("Tid i måneder")
    axK.set_ylabel("Mengde Koi i kg")
    axH.set_ylabel("Mengde Koi høstet")
    #endregion



    ###Figure Two
    #region Koi and Temperature
    fig2 = Figure()
    axK2 = fig2.add_subplot(111)
    dataK2 = axK2.plot(t, K, "-b", label="Koi")
    axT = axK2.twinx()
    dataT = axT.plot(t, temp, "-r", label="Temperature")
    #axDT = axK2.twinx()
    #dataDT = axDT.plot(t, dT, "#ffbf00", label="Temperature (Water)")

    #Key
    data2 = dataK2 + dataT# + dataDT
    datatittel = [l.get_label() for l in data2]
    axK2.legend(data2, datatittel, loc=0)

    #Layout
    axK2.set_ylim(0, np.amax(K)+np.amax(K)*0.1)
    axT.set_ylim(0, 25)
    #axDT.set_ylim(0, 25)
    axK2.grid(True)

    #Info
    axK2.set_xlabel("Tid i måneder")
    axK2.set_ylabel("Mengde Koi i kg")
    axT.set_ylabel("Temperatur i C")
    #endregion



    ###Figure Three
    #region Koi and Rocket
    fig3 =  Figure()
    axK3 = fig3.add_subplot(111)
    dataK3 = axK3.plot(t, K, "-b", label="Koi")
    axRH = axK3.twinx()
    dataRH = axRH.plot(t, Rh, "-m", label="Ruccola Høstet")

    #Key
    data = dataK3 + dataRH
    datatittel = [l.get_label() for l in data]
    axK3.legend(data, datatittel, loc=0)

    #Layout
    axK3.set_ylim(0, np.amax(K)+np.amax(K)*0.1)
    axRH.set_ylim(0, np.amax(Rh)+np.amax(Rh)*0.1)
    axK3.grid(True)

    #Info
    axK3.set_xlabel("Tid i måneder")
    axK3.set_ylabel("Mengde Koi i kg")
    axRH.set_ylabel("Mengde Ruccola Høstet")
    #endregion



    ###Figure Four
    #region Temperature and Rocket Harvest
    fig4 =  Figure()
    axT3 = fig4.add_subplot(111)
    dataT3 = axT3.plot(t, temp, "-r", label="Temperature")
    axRH = axT3.twinx()
    dataRH = axRH.plot(t, Rh, "-m", label="Rocket Harvested")

    #Key
    data = dataT3 + dataRH
    datatittel = [l.get_label() for l in data]
    axT3.legend(data, datatittel, loc=0)

    #Layout
    axT3.set_ylim(0, np.amax(temp)+np.amax(temp)*0.1)
    axRH.set_ylim(0, np.amax(Rh)+np.amax(Rh)*0.1)
    axT3.grid(True)

    #Info
    axT3.set_xlabel("Tid i måneder")
    axT3.set_ylabel("Mengde Koi høstet")
    axRH.set_ylabel("Mengde Ruccola høstet")
    #endregion
    
    
    
    ###Figure Five
    #region Gains
    fig5 =  Figure()
    axKG = fig5.add_subplot(111)
    dataKG = axKG.plot(t, Kg, "-c", label="Koi Gains")
    axRG = axKG.twinx()
    dataRG = axRG.plot(t, Rg, "#ffa500", label="Rocket Gains")

    #Key
    data = dataKG + dataRG
    datatittel = [l.get_label() for l in data]
    axKG.legend(data, datatittel, loc=0)

    #Layout
    axKG.set_ylim(0, np.amax(Kg)+np.amax(Kg)*0.1)
    axRG.set_ylim(0, np.amax(Rg)+np.amax(Rg)*0.1)
    axKG.grid(True)

    #Info
    axKG.set_xlabel("Tid i måneder")
    axKG.set_ylabel("Kroner")
    axRG.set_ylabel("Kroner")
    #endregion

    '''
    ###Figure Six
    #region Losses and Gains
    fig6 =  Figure()
    axG = fig6.add_subplot(111)
    dataG = axG.plot(t, G, "#5e73d1", label="Gains")
    axEL = axG.twinx()
    dataEL = axEL.plot(t, El, "#e52761", label="Losses")

    #Key
    data = dataG + dataEL
    datatittel = [l.get_label() for l in data]
    axG.legend(data, datatittel, loc=0)

    #Layout
    axG.set_ylim(0, np.amax(G)+np.amax(G)*0.1)
    axEL.set_ylim(0, np.amax(El)+np.amax(El)*0.1)
    axG.grid(True)

    #Info
    axG.set_xlabel("Tid i måneder")
    axG.set_ylabel("Kroner Gained")
    axEL.set_ylabel("Kroner Lost")
    #endregion  
    '''     
     

    ###Figure Seven
    #region Net Gain
    fig7 =  Figure()
    axN = fig7.add_subplot(111)
    dataN = axN.plot(t, NET, "#5e73d1", label="Net Gain")

    #Key
    data = dataN
    datatittel = [l.get_label() for l in data]
    axN.legend(data, datatittel, loc=0)

    #Layout
    #axN.set_ylim(np.amin(NET)+np.amin(NET)*0.1, np.amax(NET)+np.amax(NET)*0.1)
    axN.grid(True)

    #Info
    axN.set_xlabel("Tid i måneder")
    axN.set_ylabel("Net Gain")
    #regionend  
      
    #endregion plot
    #endregion plot
    return [fig, fig2, fig3, fig4] #fig6, fig5, fig7

#################
###GUI
#################

#region Settings
tk.Label(master=s, text="Start").grid(row=0, column=0)
tk.Entry(master=s, textvariable=av).grid(row=0, column=1)

tk.Label(master=s, text="Stop").grid(row=0, column=2)
tk.Entry(master=s, textvariable=bv).grid(row=0, column=3)

monthMenu = tk.OptionMenu(s, isYear, *{"Months", "Years"})
monthMenu.grid(row=0, column=4)

tk.Label(master=s, text="y(0)").grid(row=1, column=0)
tk.Entry(master=s, textvariable=y0v).grid(row=1, column=1)

#tk.Label(master=s, text="Heating").grid(row=1, column=2)
#tk.Entry(master=s, textvariable=Heatingv).grid(row=1, column=3)

#monthMenu = tk.OptionMenu(s, HeatingModev, *{"Max", "Min"})
#monthMenu.grid(row=1, column=4)

tk.Label(master=s, text="Tank Size(l, meters)").grid(row=1, column=2)
tk.Entry(master=s, textvariable=lv).grid(row=1, column=3)

tk.Label(master=s, text="Tank Size(w, meters)").grid(row=2, column=0)
tk.Entry(master=s, textvariable=wv).grid(row=2, column=1)

tk.Label(master=s, text="Tank Size(d, meters)").grid(row=2, column=2)
tk.Entry(master=s, textvariable=dv).grid(row=2, column=3)

tk.Label(master=s, text="Growth Rate (+1)").grid(row=3, column=0)
tk.Entry(master=s, textvariable=gv).grid(row=3, column=1)

tk.Label(master=s, text="Resolution").grid(row=3, column=2)
tk.Entry(master=s, textvariable=Resv).grid(row=3, column=3)

tk.Label(master=s, text="Growth Period (Months)").grid(row=4, column=0)
tk.Entry(master=s, textvariable=growthv).grid(row=4, column=1)

tk.Label(master=s, text="Safety (Kg)").grid(row=4, column=2)
tk.Entry(master=s, textvariable=Safetyv).grid(row=4, column=3)

tk.Label(master=s, text="Constant Harvest (Kg)").grid(row=5, column=0)
tk.Entry(master=s, textvariable=ConsAmountv).grid(row=5, column=1)

tk.Label(master=s, text="Dynamic Harvest (%)").grid(row=5, column=2)
tk.Entry(master=s, textvariable=VarAmountv).grid(row=5, column=3)

tk.Label(master=s, text="Rocket Harvest (Kg)").grid(row=6, column=0)
tk.Entry(master=s, textvariable=HarvestSizev).grid(row=6, column=1)

tk.Label(master=s, text="Rocket Growth (%)").grid(row=6, column=2)
tk.Entry(master=s, textvariable=RocketGrowthv).grid(row=6, column=3)

#tk.Label(master=s, text="Koi Price").grid(row=7, column=0)
#tk.Entry(master=s, textvariable=KoiPricev).grid(row=7, column=1)

#tk.Label(master=s, text="Rocket Price").grid(row=7, column=2)
#tk.Entry(master=s, textvariable=RocketPricev).grid(row=7, column=3)

tk.Label(master=s, text="Harvest Size Koi (%)").grid(row=8, column=0)
tk.Entry(master=s, textvariable=KoiHarvestSizev).grid(row=8, column=1)

tk.Label(master=s, text="Harvest Intervall Koi (Months)").grid(row=8, column=2)
tk.Entry(master=s, textvariable=KoiHarvestIntervallv).grid(row=8, column=3)
#tk.Label(master=s, text="Electricity Price").grid(row=8, column=0)
#tk.Entry(master=s, textvariable=ElectricityCostv).grid(row=8, column=1)


s.pack()
#endregion Settings

#region Exit button
def _quit():
    root.quit()
    root.destroy()

button = tk.Button(master=s, text="Quit", command=_quit)
button.grid(row=9, column=1)
#endregion Exit button

###Backend x Frontend

#region Scrolling functionallity
container = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, command = container.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
container.configure(yscrollcommand = scrollbar.set)
def update():
    container.configure(scrollregion=container.bbox('all'))
#endregion Scrolling functionallity

#region Embedding graphs from matplotlig to tkinter
gridLayout = [(2, 0, 1), (2, 1, 1), (3, 0, 1), (3, 1, 1)]# (4, 1, 1), (4, 0, 1), (1, 0, 2)
def run():
    figs = compute()
    global graphs
    try:
        for child in container.winfo_children():
            child.destroy()
    except:
        pass 
    
    #Frame for housing graphs inside canvas container
    graphs = tk.Frame(container)
    container.create_window((0,0), window=graphs, anchor="e")

    #Plotting
    for fig, layout in zip(figs, gridLayout):
        canvas = FigureCanvasTkAgg(fig, master=graphs)
        canvas.draw()
        canvas.get_tk_widget().grid(row=layout[0], column=layout[1], columnspan=layout[2], padx=60, pady=20)
    
    #Update scrollbar
    update()

tk.Button(master=s, text="Graph", command=run).grid(row=9, column=3)
tk.Button(master=s, text="Scrollbar", command=update).grid(row=9, column=2)
container.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH,)
#endregion Embedding graphs from matplotlig to tkinter



#Start
tk.mainloop()