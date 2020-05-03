#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licence GPLV3
# Authors : Thomas Lavarenne, Christophe Seguinot
# CRC decoding original code :  Junzi Sun et al https://pypi.org/project/pyModeS/

import os, sys,datetime, math, webbrowser, json
import subprocess

from os import path
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QLabel, QLineEdit, QTabWidget, QTableWidget, QTableWidgetItem, QGridLayout, QFormLayout, QVBoxLayout,QHBoxLayout,QPushButton,QComboBox, QSpacerItem, QSizePolicy,QMessageBox
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont, QTextCharFormat, QPalette
from PyQt5.QtCore import pyqtSlot

# maps, flight/aircraft web page
from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import *


class App(QWidget):

    def __init__(self):
        super(App, self).__init__()
        
        # set processes to None
        self.processMap=None
        self.processADSB_receiver=None
        self.processADSB_receiverGRC=None
        

        # set GUI
        screen = app.primaryScreen()
        rect = screen.availableGeometry()
        self.timeStart=datetime.datetime.now()
        self.readMyData()
        
        self.title = 'ADS-B decoded data'
        self.ICAO_viewtitle='ICAO view'
        self.left = 0
        self.top = 0
        self.width = (2*rect.width()) / 3
        self.height = (2*rect.height()) / 3 
        self.nb_decoded= 0
        self.nb_undecoded= 0
        
        self.linkStyle=QFont()
        self.linkStyle.setUnderline(True)

        self.boldFont = QFont()
        self.boldFont.setBold(True)

        

        # chemin du répertoire contenant les fichiers .dat
        self.ADSB_Dir=os.path.dirname(os.path.realpath('__file__'))
        # chemin du répertoire dans lequel on déplace les  fichiers .dat (pour traitement)
        self.ADSB_DirTempFiles=os.path.join(self.ADSB_Dir, 'temp_files')
        # create temp_files dir if it does not exits
        if not os.path.exists(self.ADSB_DirTempFiles):
            os.mkdir(self.ADSB_DirTempFiles)

        # remove older AdsbGuiPlanesData.json
        try:
            os.remove(os.path.join(self.ADSB_Dir,'AdsbGuiPlanesData.json'))
        except:
            pass

#        column index
        self.index_ICAO=0
        self.index_elapsed_time=1
        self.index_Distance=2
        self.index_Vol=3
        self.index_Vitesse_we=4
        self.index_Vitesse_ns=5
        self.index_Vitesse=6
        self.index_Vertical=7
        self.index_Sens=8
        self.index_Altitude=9
        self.index_Latitude=10
        self.index_Longitude=11
        self.index_CPR_LAT_odd=12
        self.index_CPR_LON_odd=13
        self.index_CPR_LAT_even=14
        self.index_CPR_LON_even=15
        self.nb_columns=16    
        
        self.createGUI()
        self.initDataTables();
        self.initICAO_view()
        # timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.adsb_decode)
        self.timer.start(2000)
        
    def closeEvent(self, event):


        # remove AdsbGuiPlanesData.json
        try:
            os.remove(os.path.join(self.ADSB_Dir,'AdsbGuiPlanesData.json'))
        except:
            pass
        # close Map and ADSB decoder windows
        self.openCloseMap(True)
        self.openADSB_Receiver(True)
        self.openADSB_ReceiverGRC(True)
       
    def readMyData(self):
        # read my_location.txt
        if path.exists("AdsbGuiPreferences.json"):
            with open('AdsbGuiPreferences.json') as json_file:
                data = json.load(json_file)

            try:
                self.browserLauncher=data['my_browserLauncher']
            except:
                self.browserLauncher= 'chromium-browser  --disable-web-security --allow-file-access-from-files --user-data-dir map/map.html'
                
            try:
                self.ADSB_LauncherGRC=data['my_ADSB_LauncherGRC']
            except:
                self.ADSB_LauncherGRC= 'gnuradio-companion adsb_receiver.grc'

            try:
                self.ADSB_Launcher=data['my_ADSB_Launcher']
            except:
                self.ADSB_Launcher= 'python3 adsb_receiver.py'

            try:
                self.myBrowser=data['myBrowser']
            except:
                self.myBrowser= 'PyQT built in browser'


            for p in data['my_location']:
                try:
                    self.myLatitude=float(p['Latitude'])
                except:
                    self.myLatitude=0
                try:
                    self.myLongitude=float(p['Longitude'])
                except:
                    self.myLongitude=0
                try:
                    self.myAltitude=p['Altitude']
                except:
                    self.myAltitude=0              

            for p in data['my_units']:
                try:
                    self.myDistanceUnit=p['DistanceUnit']
                except:
                    self.myDistanceUnit='km'               
                try:
                    self.myAltitudeUnit=p['AltitudeUnit']
                except:
                    self.myAltitudeUnit='m'               
                try:
                    self.myVerticalSpeedUnit=p['VerticalSpeedUnit']
                except:
                    self.myVerticalSpeedUnit='m/s'               
        else:
            self.myLatitude=0
            self.myLongitude=0
            self.myAltitude=0
            self.myDistanceUnit='km'
            self.myBrowser= 'PyQT built in browser'

            self.myAltitudeUnit='m'
            self.myVerticalSpeedUnit='m/s'
        if self.myDistanceUnit =='mi.':
            self.mySpeedUnit='mph'
        elif self.myDistanceUnit =='n.m.':
            self.mySpeedUnit='knots'
        else:
            self.mySpeedUnit='km/h'
                


    def saveMyData(self):
        
        # launchers 
        # 
        self.myBrowser= self.mybrowser.currentText()
        self.browserLauncher = self.myBrowserLauncher.text()
        self.ADSB_Launcher = self.myADSB_launcher.text()
        self.ADSB_LauncherGRC = self.myADSB_LauncherGRC.text()
        # read my_location from QlineEdit
        self.myLatitude=float(self.mylat.text())
        self.myLongitude=float(self.mylon.text())
        self.myAltitude=float(self.myalt.text())

        myDistanceUnit=self.myDistanceUnit
        self.myDistanceUnit =self.mydisu.currentText()
        myAltitudeUnit=self.myAltitudeUnit 
        self.myAltitudeUnit =self.myaltu.currentText()
        myVerticalSpeedUnit=self.myVerticalSpeedUnit
        self.myVerticalSpeedUnit =self.myvspu.currentText()

        # Refresh Altitude
        if myAltitudeUnit != self.myAltitudeUnit:
            self.refreshAltitude()
        
        # Refresh Vertical speed
        if myVerticalSpeedUnit != self.myVerticalSpeedUnit:
            self.refreshVerticalSpeed()
        
        # TODO refresh distance and speed when needed !
        if myDistanceUnit != self.myDistanceUnit:
            if self.myDistanceUnit =='mi.':
                self.mySpeedUnit='mph'
            elif self.myDistanceUnit =='n.m.':
                self.mySpeedUnit='knots'
            else:
                self.mySpeedUnit='km/h'

            self.refreshDistanceAndSpeed()
        
        # Always refresh table headers 
        self.setTableHeaders ()
        
        #Save my data in a json text file 
        data = {}
        data['my_browserLauncher'] = self.browserLauncher
        data['my_ADSB_Launcher'] = self.ADSB_Launcher
        data['myBrowser'] = self.myBrowser
        data['my_location'] = []
        data['my_location'].append({
            'Latitude': self.myLatitude,
            'Longitude': self.myLongitude,
            'Altitude': self.myAltitude,
        })
        data['my_units'] = []
        data['my_units'].append({
            'DistanceUnit':self.myDistanceUnit,
            'AltitudeUnit':self.myAltitudeUnit,
            'VerticalSpeedUnit':self.myVerticalSpeedUnit,
        })
        print(json.dumps(data))
        with open('AdsbGuiPreferences.json', 'w') as outfile:
            json.dump(data, outfile)        
    
    def setTableHeaders (self) :
        self.tableWidget.setHorizontalHeaderLabels(
                ['ICAO (HEX)','Last seen','Distance('+self.myDistanceUnit+')','Flight',
                 'Speed WE ('+self.mySpeedUnit+')','Speed NS ('+self.mySpeedUnit+')',
                 'Speed ('+self.mySpeedUnit+')',
                 'Vrate ('+self.myVerticalSpeedUnit+')','Sens','Altitude ('+self.myAltitudeUnit+')','Latitude (deg)',
                 'Longitude (deg)','CPRLATodd','CPRLONodd','CPRLATeven',
                 'CPRLONeven'])

    def calculDistance(self, Lat1, Lon1, Lat2, Lon2):
        lat1 = math.radians(Lat1)
        lon1 = math.radians(Lon1)
        lat2 = math.radians(Lat2)
        lon2 = math.radians(Lon2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        
        # Haversine formula
        distance = 6373.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # TODO estimate with altitude !=0 or not?
        
        return distance
    
    def initDataTables(self):
       # initialise table used for recording decoded data
        self.ICAO=[]
        self.elapsed_time=[]
        self.lastSeen=[]
        self.Distance=[]
        self.Vol=[]
        self.Vitesse_we=[]
        self.Vitesse_ns=[]
        self.Vitesse=[]
        self.VerticalSpeed=[]
        self.Sens=[]
        self.Altitude=[]
        self.Latitude=[]
        self.Longitude=[]
        self.CPR_LAT_odd=[]
        self.CPR_LON_odd=[]
        self.CPR_LAT_even=[]
        self.CPR_LON_even=[]
        self.TC_CPR_odd=[]
        self.TC_CPR_even=[]
        
        self.Direction=[] # not shown on table
        
        for i in range(0,self.tableWidget.rowCount()+1):
            self.ICAO.append('')
            self.elapsed_time.append(datetime.timedelta(0))
            self.lastSeen.append(0)
            self.Distance.append('-')
            self.Vol.append('-')
            self.Vitesse_we.append('-')
            self.Vitesse_ns.append('-')
            self.Vitesse.append('-')
            self.VerticalSpeed.append('-')
            self.Sens.append('-')
            self.Altitude.append('-')    
            self.Latitude.append('-')    
            self.Longitude.append('-')    
            self.CPR_LAT_odd.append('-')
            self.CPR_LON_odd.append('-')
            self.CPR_LAT_even.append('-')
            self.CPR_LON_even.append('-')
            self.Direction.append('')
            self.TC_CPR_odd.append('-')
            self.TC_CPR_even.append('-')
  
                
    def initICAO_view(self):
        self.ICAOview = QWebView()
        self.ICAOview.setWindowTitle(self.ICAO_viewtitle)
        self.ICAOview.resize(self.width, self.height)
        self.ICAOview.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.ICAOview.load(QtCore.QUrl('https://www.radarbox.com'))  
        
    def ICAOviewShow(self):
        #https://docs.python.org/3/library/subprocess.html#subprocess.Popen

        self.ICAOview.show()
    
    def openADSB_Receiver(self, close):            
        if self.processADSB_receiver is None:
            print ('NONE')
        if close==True:
            if self.processADSB_receiver is not None:
                # Close Map
                self.processADSB_receiver.terminate() 
            return
        
        if self.processADSB_receiver is None:
            # Open ADSB_Receiver.py
            if self.ADSB_Launcher:
                command=self.ADSB_Launcher.split()
                self.processADSB_receiver = subprocess.Popen(command)
        else:
            # Close ADSB_Receiver.py
            self.processADSB_receiver.terminate()
            self.processADSB_receiver=None
            
            
    def openADSB_ReceiverGRC(self, close):
        if close==True:
            if self.processADSB_receiverGRC is not None:
                # Close Map
                self.processADSB_receiverGRC.terminate() 
            return
        
        if self.processADSB_receiverGRC is None:
            # Open ADSB_Receiver.py
            if self.ADSB_LauncherGRC:
                command=self.ADSB_LauncherGRC.split()
                self.processADSB_receiverGRC = subprocess.Popen(command)
        else:
            # Close ADSB_Receiver.py
            self.processADSB_receiverGRC.terminate()
            self.processADSB_receiverGRC=None
    
    def openCloseMap(self, close):       
        if close==True:
            if self.processMap is not None:
                # Close Map
                self.processMap.terminate() 
            return
        
        if self.processMap is None:
            # Open Map
            if self.browserLauncher:
                command=self.browserLauncher.split()
                self.processMap = subprocess.Popen(command)
        else:
            # Close Map
            self.processMap.terminate()
            self.processMap=None

    
    def createGUI(self):

        label_width=250
         
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout) 

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabTable = QWidget()
        self.tabPreferences = QWidget()
        self.tabHelp = QWidget()
        self.tabs.resize(600,600)
        self.layout.addWidget(self.tabs)
 
       # Add tabs to  tab screen
        self.tabs.addTab(self.tabTable,"ADS-B decoded Data")
        self.tabs.addTab(self.tabPreferences,"Preferences")
        self.tabs.addTab(self.tabHelp,"Help, How-to")
        
        # Create tabTable
        tabTableLayout=QVBoxLayout()
        self.tabTable.setLayout(tabTableLayout)

        # add decoding messages to tabTable
        upperTabs = QHBoxLayout()
        self.text_nb_decoded= QLabel("Decoded : 0")     
        self.text_nb_decoded.setFont(self.boldFont)
        self.text_nb_decoded.setFixedWidth(label_width)
        upperTabs.addWidget(self.text_nb_decoded)
        self.text_nb_undecoded= QLabel("Bad CRC : 0")
        self.text_nb_undecoded.setFont(self.boldFont)
        self.text_nb_undecoded.setFixedWidth(label_width)
        upperTabs.addWidget(self.text_nb_decoded)
        upperTabs.addWidget(self.text_nb_undecoded)

        button = QPushButton('Open/Close Air Trafic Map', self)
        button.setFixedWidth(2*label_width)
        button.clicked.connect(self.openCloseMap)
        upperTabs.addWidget(button)
        
        button2 = QPushButton('Open/Close adsb_receiver.py', self)
        button2.setFixedWidth(2*label_width)
        button2.clicked.connect(self.openADSB_Receiver)
        upperTabs.addWidget(button2)

        button3 = QPushButton('Open/Close GRC adsb_Receiver.grc', self)
        button3.setFixedWidth(2*label_width)
        button3.clicked.connect(self.openADSB_ReceiverGRC)
        upperTabs.addWidget(button3)

        upperTabs.addStretch(1)
        
        tabTableLayout.addLayout(upperTabs)

        
        # Add tableWidget to tabTable
        table=QVBoxLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers( QTableWidget.NoEditTriggers)
        self.tableWidget.itemDoubleClicked.connect(self.Open_ICAO_Link)
        self.tableWidget.setRowCount(19)
        self.tableWidget.setColumnCount(self.nb_columns)
        
        self.setTableHeaders ()

        for i in range(0,self.tableWidget.rowCount()):
            self.tableWidget.setItem(i,0, QTableWidgetItem(''))
            for j in range(1,self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QTableWidgetItem('-'))
                
        table.addWidget(self.tableWidget) 
        tabTableLayout.addLayout(table)
        
        # Create tabPreferences
        tabPreferencesLayout = QVBoxLayout()
        self.tabPreferences.setLayout(tabPreferencesLayout)

        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        tabPreferencesLayout.addItem(verticalSpacer)
        label = QLabel("Local position (used for distance calculation)")
        label.setFont(self.boldFont)
        tabPreferencesLayout.addWidget(label)
        tabPreferencesLayout.addItem(verticalSpacer)
        
        tabPreferencesSubLayout1 = QFormLayout()
        tabPreferencesLayout.addLayout(tabPreferencesSubLayout1)
        
        self.mylat = QLineEdit(str(self.myLatitude))
        self.mylat.setFixedWidth(label_width)
        tabPreferencesSubLayout1.addRow("Local Latitude (deg.)", self.mylat);
        self.mylat.textChanged.connect(self.saveMyData)

        self.mylon = QLineEdit(str(self.myLongitude))
        self.mylon.setFixedWidth(label_width)
        tabPreferencesSubLayout1.addRow("Local Longitude (deg.)", self.mylon);
        self.mylon.textChanged.connect(self.saveMyData)

        self.myalt = QLineEdit(str(self.myAltitude))
        self.myalt.setFixedWidth(label_width)
        tabPreferencesSubLayout1.addRow("Altitude (m)", self.myalt);
        self.mylon.textChanged.connect(self.saveMyData)

        tabPreferencesLayout.addItem(verticalSpacer)
        label = QLabel("Prefered units")
        label.setFont(self.boldFont)
        tabPreferencesLayout.addWidget(label)
        tabPreferencesLayout.addItem(verticalSpacer)

        tabPreferencesSubLayout2 = QFormLayout()
        tabPreferencesLayout.addLayout(tabPreferencesSubLayout2)
        self.mydisu = QComboBox(self)
        self.mydisu.addItem("km")
        self.mydisu.addItem("Miles")
        self.mydisu.addItem("Nm")
        index = self.mydisu.findText(self.myDistanceUnit, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.mydisu.setCurrentIndex(index)
        self.mydisu.setFixedWidth(label_width)
        tabPreferencesSubLayout2.addRow("Distance unit", self.mydisu);
        self.mydisu.activated[str].connect(self.saveMyData)
        
        self.myaltu = QComboBox(self)
        self.myaltu.addItem("m")
        self.myaltu.addItem("ft")
        index = self.myaltu.findText(self.myAltitudeUnit, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.myaltu.setCurrentIndex(index)
        self.myaltu.setFixedWidth(label_width)
        tabPreferencesSubLayout2.addRow("Altitude unit", self.myaltu);
        self.myaltu.activated[str].connect(self.saveMyData)

        self.myvspu = QComboBox(self)
        self.myvspu.addItem("m/s")
        self.myvspu.addItem("ft/min")
        index = self.myvspu.findText(self.myVerticalSpeedUnit, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.myvspu.setCurrentIndex(index)
        self.myvspu.setFixedWidth(label_width)
        tabPreferencesSubLayout2.addRow("Vertical Speed unit", self.myvspu);
        self.myvspu.activated[str].connect(self.saveMyData)

        tabPreferencesLayout.addItem(verticalSpacer)
        label = QLabel("Command for opening Map in Browser and ADSB-decoder (GRC or Python)")
        label.setFont(self.boldFont)
        tabPreferencesLayout.addWidget(label)
        tabPreferencesLayout.addItem(verticalSpacer)

        tabPreferencesSubLayout3 = QFormLayout()
        tabPreferencesLayout.addLayout(tabPreferencesSubLayout3)
        tabPreferencesLayout.addItem(verticalSpacer)

        self.myBrowserLauncher = QLineEdit(str(self.browserLauncher))
        # self.myBrowserLauncher.setFixedWidth(4*label_width)
        tabPreferencesSubLayout3.addRow("Browser launcher", self.myBrowserLauncher);
        self.myBrowserLauncher.textChanged.connect(self.saveMyData)

        self.myADSB_launcher = QLineEdit(str(self.ADSB_Launcher))
        # self.myADSB_launcher.setFixedWidth(4*label_width)
        tabPreferencesSubLayout3.addRow("run ADSB_receiver.py", self.myADSB_launcher);
        self.myADSB_launcher.textChanged.connect(self.saveMyData)

        self.myADSB_LauncherGRC = QLineEdit(str(self.ADSB_LauncherGRC))
        # self.myADSB_launcher.setFixedWidth(4*label_width)
        tabPreferencesSubLayout3.addRow("run ADSB_receiver.grc", self.myADSB_LauncherGRC);
        self.myADSB_LauncherGRC.textChanged.connect(self.saveMyData)

        tabPreferencesLayout.addItem(verticalSpacer)
        label = QLabel("ICAO and Flight number Browsing")
        label.setFont(self.boldFont)
        tabPreferencesLayout.addWidget(label)
        label = QLabel("Using PyQT browser Widget only open one window but do not allow manually changing URL")
        tabPreferencesLayout.addWidget(label)
        label = QLabel("Using OS browser wil open one window for each ICAO or Flight and allow manually changing URL")
        tabPreferencesLayout.addWidget(label)
        tabPreferencesLayout.addItem(verticalSpacer)

        self.mybrowser = QComboBox(self)
        self.mybrowser.addItem("PyQT built in browser")
        self.mybrowser.addItem("OS default browser")
        index = self.mybrowser.findText(self.myBrowser, QtCore.Qt.MatchContains)
        if index >= 0:
            self.mybrowser.setCurrentIndex(index)
        self.mybrowser.setFixedWidth(label_width)
        tabPreferencesSubLayout3.addRow("Browser", self.mybrowser);
        self.mybrowser.activated[str].connect(self.saveMyData)

        tabPreferencesLayout.addStretch(1)

        # Create tabHelp
        tabHelpLayout = QVBoxLayout()
        helpText = "<br/><b>Authors :</b>"

        helpText+= "<br/><b>Original Authors :</b> Thomas Lavarenne (adsb_graphique.py)"
        helpText+= "<br/><b>This version :</b> Christophe Seguinot (py2 and PY3 compatibility, PyQT5 interface, 'Flight radar' map"
        helpText+= "<br/><br/>"
        helpText+= "<br/><b>Default Units :</b> All data saved in table have default units m (meter) km km/h  and m/s for vertical speed."
        helpText+= "<br/><b>User Units :</b> Select your prefered unit in the preference tab. All data displayed by the GUI use units defined byt the user. Speed unit is adjusted to correspond to distance unit."
        helpText+= "<br/><b>ICAO, Flight ID :</b> Double clicking one ICAO or flight ID open browser tab giving information retrieved from the internet."
        helpText+= "<br/><b>Distance :</b> Distance is evaluated from the defined local longitude and latitude. At present time, altitude is not taken into account (ground distance calculation) ."
        helpText+= "<br/><br/>"
        helpText+= "<br/><b>How does it works? :</b><br/><ul>"
        helpText+= "<li>-</li>"
        helpText+= "<li><b>adsb_receiver.py</b> (generated by compiling adsb_receiver.grc)</li>"
        helpText+= "<ul><li>select correct threshold for detecting received ADSB frame</li>"
        helpText+= "<li>If the 'Taggeg File Sink' is enabled in adsb_receiver.grc, detected frames are recorded on the local disk. Do not enable this 'Taggeg File Sink' if no code is run to process recorded frames (adsb_gui.py): you may rapidly end up with a full disk!</li>"
        helpText+= "<li>frames are saved in the adsb_receiver.py directory in files named filexxx.dat, where xxx is based on the time when the frame was seen.</li>"
        helpText+= "</ul>"
        helpText+= "<li><b>adsb_gui.py</b> (ADS-B Frames decoding)</li>"
        helpText+= "<ul><li>The adsb_gui.py try to decode recorded frames, it first moves recorded files to temp_files directory, process and delete them</li>"
        helpText+= "<li>adsb_receiver.py, adsb_receiver.grc and Map.html can be opended/closed whithin adsb_receiver.py (Adjust corresponding launchers in preferences tab)</li>"
        helpText+= "<li>every two seconds, new data collected in the decoded ADSB frames are send to AdsbGuiPlanesData.json file, displayed in the terminal, and on a table</li>"
        helpText+= "<li>double clicking on ICAO or Flight number you can browse plane or flight information</li>"
        helpText+= "</ul>"
        helpText+= "<li><b>map/map.html</b> (Planes location and tracks)</li>"
        helpText+= "<ul><li>every second, the map read (*) new data in AdsbGuiPlanesData.json file and refresh planes location and tracks</li>"
        helpText+= "<li></li></ul>"
        helpText+= "<li><b>Requirements</b></li>"
        helpText+= "<ul><li>This app may run on every computer running GNURadio >3.8 without any additionnal installation</li>"
        helpText+= "<li>it should run on Linux (tested on Ubuntu 18.04), Mac OS X (not tested) and Windows (not tested)</li><li>GNURadio, Pyqt5</li><li>Python 2 or 3 (already installed with GNURadio)</li>"
        helpText+= "<li>Browsing the map is done by reading data in AdsbGuiPlanesData.json local file: (*) this requires bypassing the 'Same-Origin-Policy' For Local Files. Browser like Chrome allows it</li>"
        helpText+= "<li>An alternative to bypassing the 'Same-Origin-Policy' is to open map.html with a local web server </li></ul>"
        helpText+= "<li><b>File structure</b></li>"
        helpText+= "<ul><li>Main folder (gnuradio and gnuradio-companion files</li>"
        helpText+= "<ul><li><b>temp_files</b> (temp folder where files filexxx.dat are move, processed, and then deleted)</li><li><b>map</b> (folder containing html png and js files for browsing the map)</li><li><b>__pycache__</b> (can be removed: cache folder created by python)</li>"
        helpText+= "<li>adsb_2000kSps2_1uint8_10Msamples.bin (1090 MHz record sampled at 2MHz)</li>"
        helpText+= "<li>adsb_2M.bin (1090 MHz record sampled at 2MHz)</li>"
        helpText+= "<li>adsb_receiver.grc (Gnuradio Companion ADS-B receiver)</li>"
        helpText+= "<li>adsb_receiver.py (Compiled python code for adsb_receiver.grc)</li>"
        helpText+= "<li>AdsbGuiPreferences.json (User saved preferences)</li>"
        helpText+= "<li>epy_module_0.py (required by adsb_receiver.grc)</li>"
        helpText+= "<li>gui_adsb.py (main GUI)</li>"
        helpText+= "<li>readme.txt (read me first)</li>"
        helpText+= "</ul></ul>"
        helpText+= "<br/></ul>"        
        label = QLabel(helpText)
        tabHelpLayout.addWidget(label)
        tabHelpLayout.addStretch(1)
        self.tabHelp.setLayout(tabHelpLayout)

        # Show widget
        self.show()


    def refreshLastSeen(self):
        # save last time of update for this ICAO (used to suppress oldest record)
        now=datetime.datetime.now()
        for i in range(0,len(self.ICAO)):
            if self.ICAO[i] != '':
                elapsed_time=now-self.lastSeen[i]
                seconds = int(elapsed_time.total_seconds())
                hours = int(seconds // 3600)
                minutes =  int(seconds / 60) % 60
                seconds = seconds % 60
                text='{}:{}:{}'.format(hours,minutes, seconds)
                self.tableWidget.setItem(i,self.index_elapsed_time, QTableWidgetItem(text))

    
    @pyqtSlot()
    def Open_ICAO_Link(self):
        self.ICAOviewShow() 
        item=self.tableWidget.currentItem()
        url =''
        if item.column() == 0 and item.text() !='' and item.text() !='-':
            url='https://www.radarbox.com/data/mode-s/'+str(item.text())
        if item.column() == 3 and item.text() !='..' and item.text() !='-':
            # It's not possible to always open the same window/tab
            url='https://www.radarbox.com/data/flights/'+str(item.text()) 
        if url !='':
            if "PyQT" in self.myBrowser:
                self.ICAOview.load((QtCore.QUrl(url)))  
                self.ICAOview.loadFinished.connect(self.ICAOviewShow)
                self.ICAOview.show()
            else:
                # It's not possible to always open the same window/tab
                webbrowser.open(url,new=0) 
                
    def textAltitude(self,altitude):
        if self.myAltitudeUnit=='ft': 
            return 'Alt: ' + str(int(altitude*0.3048)) + ' ft'
        return 'Alt: ' + str(altitude) + ' m'
    
    def convAltitude(self,altitude): 
        if self.myAltitudeUnit=='ft': 
            return int(altitude*0.3048)
        return altitude
   
    def refreshAltitude(self):
        for i in range(0, len(self.Altitude)):
            if self.Altitude[i] !='-':
                self.tableWidget.setItem(i,self.index_Altitude, QTableWidgetItem(str(self.convAltitude(self.Altitude[i])))) 
     
    def textVerticalSpeed(self,VerticalSpeed):
        if self.myVerticalSpeedUnit=='ft/min': 
            return 'Alt: ' + str(int(VerticalSpeed*196.85)) + ' ft/min'
        return 'Alt: ' + str(VerticalSpeed) + ' m/s'
    
    def convVerticalSpeed(self,VerticalSpeed): 
        if self.myVerticalSpeedUnit=='ft/min': 
            return int(VerticalSpeed*196.85)
        return VerticalSpeed
   
    def refreshVerticalSpeed(self):
        for i in range(0, len(self.VerticalSpeed)):
            if self.VerticalSpeed[i] !='-':
                self.tableWidget.setItem(i,self.index_VerticalSpeed, QTableWidgetItem(str(self.convAltitude(self.VerticalSpeed[i])))) 
     
    def convVitesse(self,Vitesse): 
        if self.myspeedUnit=='mph':
            return int(Speed*0.621371)
        elif self.mySpeedUnit=='knots':
            return int(Speed*1.852)
        else: # km/h
            return speed

    def convDistance(self,Distance): 
        if self.myDistanceUnit=='mi.':
            return int(Distance*0.621371)
        elif self.myDistanceUnit=='n.m.':
            return int(Distance*1.852)
        else: # m
            return Distance

    def refreshDistanceAndSpeed(self):
        for i in range(0, len(self.ICAO)):
            if self.Distance[i] !='-':
                self.tableWidget.setItem(i,self.index_Distance, QTableWidgetItem(str(self.convDistance(self.Distance[i])))) 
            if self.Vitesse_we[i] !='-':
                self.tableWidget.setItem(i,self.index_Vitesse_we, QTableWidgetItem(str(self.convVitesse(self.Vitesse_we[i])))) 
            if self.Vitesse_we[i] !='-':
                self.tableWidget.setItem(i,self.index_Vitesse_ns, QTableWidgetItem(str(self.convVitesse(self.Vitesse_ns[i])))) 
            if self.Vitesse_we[i] !='-':
                self.tableWidget.setItem(i,self.index_Vitesse, QTableWidgetItem(str(self.convVitesse(self.Vitesse[i])))) 

    def adsb_decode(self):
        self.refreshLastSeen()

        jsonData = {}
        jsonData['newLocation'] = []

        # Search for file* and move them to temp_files 
        fileCounter = 0
        for file in os.listdir(self.ADSB_Dir):  
            if file.startswith('file')  and file != 'files':
                os.rename(os.path.join(self.ADSB_Dir, file), os.path.join(self.ADSB_DirTempFiles, file))
                fileCounter += 1
        if fileCounter==0:
            sys.stdout.write("*")
            sys.stdout.flush()
        else:
            print("") # print an EOL
        
        fichier=[]  
        for files in os.listdir(self.ADSB_DirTempFiles):  
            fichier.append(files)  
        if len(fichier)>0: 
            print(fichier)

        
        # decode each file one by one 
        for k in range(0,len(fichier)):
            
            # Ouvrir le fichier binaire et afficher la trame
            with open('{0}/{1}'.format(self.ADSB_DirTempFiles,fichier[k]), "rb") as binary_file:
                data = binary_file.read()
                if sys.version_info[0] > 2:
                    byte=list(data[:107*2])
                else:
                    byte = map(ord,data[:107*2])
                trame=[]
                trame_dec=""
                try:
                    for i in range(0,107):
                        trame.append(byte[2*i])
                        trame_dec+=str(trame[i])
                except:
                    pass
                msg= "10001"+trame_dec
                print ("la trame binaire est:",msg)
                trame_compl=[1,0,0,0,1]
                trame_compl.extend(trame)            
                            
        ########################################"" CHECK PARITY ""############################################################################        
    
                GENERATOR = "1111111111111010000001001"
                
                def hex2bin(hexstr):
                    scale = 16
                    num_of_bits = len(hexstr) * math.log(scale, 2)
                    binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
                    return binstr
    
                def crc(msg):
                    # Original code for CRC decoding Junzi Sun et al https://pypi.org/project/pyModeS/
                    msgbin = list(hex2bin(msg))
                    # loop all bits, except last 24 piraty bits
                    for i in range(len(msgbin)-24):
                        # if 1, perform modulo 2 multiplication,
                        if msgbin[i] == '1':
                            for j in range(len(GENERATOR)):
                                # modulo 2 multiplication = XOR
                                msgbin[i+j] = str((int(msgbin[i+j]) ^ int(GENERATOR[j])))
                    # last 24 bits
                    reminder = ''.join(msgbin[-24:])
                    return reminder
                crc_msg=crc(msg)
                
    ########################################################################################################################################################
    
                if crc_msg != '000000000000000000000000':
                    self.nb_undecoded+=1
                    self.text_nb_undecoded.setText("Bad CRC : {}".format(self.nb_undecoded))
                    print ("TRAME INCOMPLèTE ....- BAD PARITY", crc_msg)
                    try:
                        os.remove(os.path.join(self.ADSB_DirTempFiles,fichier[k]))
                    except:
                        pass
                else:
                    self.nb_decoded+=1
                    self.text_nb_decoded.setText("Decoded : {}".format(self.nb_decoded))
                    print ('CRC check OK ..- Données valides')
                # Afficher les 24 bits suivants concernant l'addresse ICAO de l'appareil:
                    icao=[]
                    icao_dec=""
                    for i in range(0,24):
                        icao.append(trame[3+i])
                        icao_dec+=str(icao[i])
                    print ("ICAO BIN:", icao_dec)
                    icao_decimal=0
                    for i in range(0,24):
                        icao_decimal += icao[23-i]*2**i
                    current_ICAO= hex(icao_decimal)[2:]
                    print ("ICAO HEX:", hex(icao_decimal)[2:])
                    
                    #ICAO decoded 

                    # for i in range(0,len(self.ICAO)+1):
                    if current_ICAO in self.ICAO:
                        current_ICAO_index= self.ICAO.index(current_ICAO)
                    else:
                        #use first empty row
                        current_ICAO_index= self.ICAO.index('')
                        self.ICAO[current_ICAO_index]=current_ICAO
                        # initialize new table row  (normally not necessary)
                        self.tableWidget.setItem(current_ICAO_index, self.index_ICAO, QTableWidgetItem(str(current_ICAO)))
                        self.tableWidget.item(current_ICAO_index, self.index_ICAO).setForeground(QBrush(QColor(QtCore.Qt.blue)))
                        self.tableWidget.item(current_ICAO_index, self.index_ICAO).setFont(self.linkStyle)

                        for j in range(1,self.tableWidget.columnCount()):
                            self.tableWidget.setItem(current_ICAO_index,j, QTableWidgetItem('..'))
    
                            # initialise new row in each data table
                            self.ICAO[current_ICAO_index]=current_ICAO
                            self.Distance[current_ICAO_index]=''
                            self.Vol[current_ICAO_index]=''
                            self.Vitesse_we[current_ICAO_index]=''
                            self.Vitesse_ns[current_ICAO_index]=''
                            self.Vitesse[current_ICAO_index]=''
                            self.VerticalSpeed[current_ICAO_index]=''
                            self.Sens[current_ICAO_index]=''
                            self.Altitude[current_ICAO_index]=''
                            self.Latitude[current_ICAO_index]=''
                            self.Longitude[current_ICAO_index]=''
                            self.CPR_LAT_odd[current_ICAO_index]=''
                            self.CPR_LON_odd[current_ICAO_index]=''
                            self.CPR_LAT_even[current_ICAO_index]=''
                            self.CPR_LON_even[current_ICAO_index]=''

                    # save last time of update for this ICAO (used to suppress oldest record)
                    self.lastSeen[current_ICAO_index]=datetime.datetime.now()
                    print ("ICAOindex:", current_ICAO_index)
                    # Les 5 bits suivants ICAO constituent le Type Code TC qui définit le type de données dans les DATA:
                    TC=[]
                    for i in range(0,5):
                        TC.append(trame[27+i])
                    TC_decimal=0
                    TC_dec=""
                    for i in range(0,5):
                        TC_decimal += TC[4-i]*2**i
                        TC_dec+= str(TC[i])
                    print ("TC=", TC_dec)
                    print ("TC=", TC_decimal)
                
                
                    ########################################################  IDENTIFICATION VOL #################################################################################################################
                    def bin2dec(buf):
                        if 0 == len(buf):
                            return -1
                        return int(buf, 2)
                
                    if 1 <= TC_decimal <= 4:
                        print ("Aircraft identification")
                        CHARSET = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####################0123456789######'
                        volbin = msg[40:88]
                        
                        
                        
                            
                        vol = ''
                        for i in range(0,7):
                            vol += CHARSET[bin2dec(volbin[6*i:6*(i+1)])]
                
                        vol = vol.replace('#', '')
                        print ('Vol =', vol)
                        self.Vol[current_ICAO_index]=vol
                        self.tableWidget.setItem(current_ICAO_index,self.index_Vol, QTableWidgetItem(vol))
                       
                
                ########################################################  SURFACE POSITION ########################################################################################################################
                    
                    
                    
                    if 5 <= TC_decimal <= 8:
                        print ("Surface Position")
                        
                        
                
                ########################################################  AIRBORNE POSITION (w/ Baro Altitude) ######################################################################################################
                    
                    if 9 <= TC_decimal <= 18:
                        print ("Airborne position (w/ Baro Altitude) ")
        #ALtitude
                        Alt=[]
                        Alt2=[]
                        Alt_dec=""
                        Alt_decimal=0
                        for i in range(0,7):
                            Alt.append(trame[35+i])
                        for i in range(0,4):
                            Alt2.append(trame[43+i])
                        
                        Alt.extend(Alt2)
                        print ("Alt")    
                        for i in range(0,11):    
                            Alt_dec+=str(Alt[i])
                        for i in range(0,11):
                            Alt_decimal += Alt[10-i]*2**i
                            
                        self.Altitude[current_ICAO_index]=int(round((Alt_decimal*25-1000)*0.3046))
                        print (self.textAltitude(self.Altitude[current_ICAO_index]))
                        self.tableWidget.setItem(current_ICAO_index,self.index_Altitude, QTableWidgetItem(str(self.convAltitude(self.Altitude[current_ICAO_index]))))
                        
                
        #Coordonnées CPR
                        if msg[53] == '1':
                            print ('Odd frame')
                            self.TC_CPR_odd[current_ICAO_index]=TC_decimal
                            CPR_LATodd=bin2dec(msg[54:71])
                            print ("CPR_LATodd=", CPR_LATodd)
                            self.CPR_LAT_odd[current_ICAO_index]=CPR_LATodd/131072.0
                            self.tableWidget.setItem(current_ICAO_index,self.index_CPR_LAT_odd, QTableWidgetItem(str(self.CPR_LAT_odd[current_ICAO_index])))
                            CPR_LONodd=bin2dec(msg[72:88])
                            print ("CPR_LONodd=", CPR_LONodd)
                            self.CPR_LON_odd[current_ICAO_index]=CPR_LONodd/131072.0
                            self.tableWidget.setItem(current_ICAO_index,self.index_CPR_LON_odd, QTableWidgetItem(str(self.CPR_LON_odd[current_ICAO_index])))
                            
                        else:
                            print ('even frame')
                            self.TC_CPR_even[current_ICAO_index]=TC_decimal
                            CPR_LATeven=bin2dec(msg[54:71])
                            print ("CPR_LATeven=", CPR_LATeven)
                            self.CPR_LAT_even[current_ICAO_index]=CPR_LATeven/131072.0
                            self.tableWidget.setItem(current_ICAO_index,self.index_CPR_LAT_even, QTableWidgetItem(str(self.CPR_LAT_even[current_ICAO_index])))
                            
                            CPR_LONeven=bin2dec(msg[72:88])
                            print ("CPR_LONeven=", CPR_LONeven)
                            self.CPR_LON_even[current_ICAO_index]=CPR_LONeven/131072.0
                            self.tableWidget.setItem(current_ICAO_index,self.index_CPR_LON_even, QTableWidgetItem(str(self.CPR_LON_even[current_ICAO_index])))
                
                    # Latitude # longitude 
                    for i in range(1,12):      # Me rappelle plus pourquoi 1 à 12? ..?
                        if self.TC_CPR_odd[i] == self.TC_CPR_even[i]:                    
                            try:
                                j=math.floor(59*self.CPR_LAT_even[current_ICAO_index] - 60*self.CPR_LAT_odd[current_ICAO_index] + 0.5)
                                # print ('j=',j)
                                dLateven=6.0
                                dLatodd=360/59.0
                                Lateven = dLateven*((j-60*math.floor(j/60))+self.CPR_LAT_even[current_ICAO_index])
                                self.Latitude[current_ICAO_index]=round(Lateven,3)
                                self.tableWidget.setItem(current_ICAO_index,self.index_Latitude, QTableWidgetItem(str(self.Latitude[current_ICAO_index])))
                      
                                D=(math.cos(math.pi*Lateven/180)*math.cos(math.pi*Lateven/180))
                                C= 1- math.cos(math.pi/30)
                                E=1-C/D
                                NLlat=math.floor(2*math.pi/math.acos(E))
                                print ('NLlat=',NLlat)
                                dLon=360.0/NLlat
                                m=math.floor(self.CPR_LON_even[current_ICAO_index]*(NLlat-1) - self.CPR_LON_odd[current_ICAO_index]*NLlat + 0.5)
                                # print ('m=',m)
                                Lon = dLon*((m-math.floor(m/NLlat)) + self.CPR_LON_odd[current_ICAO_index] )
                                print ('Lon=',Lon)
                                self.Longitude[current_ICAO_index]=round(Lon,3)
                                self.tableWidget.setItem(current_ICAO_index,self.index_Longitude, QTableWidgetItem(str(self.Longitude[current_ICAO_index])))
                            except:
                                pass
                    
                    # // 0<=direction <360 : trigonometric angle 0 is East 90 is North
                    self.Direction[current_ICAO_index]=0;
                    # distance 
                    if self.myLatitude!=0 and self.myLongitude!=0 and self.Latitude[current_ICAO_index]!='' and self.Latitude[current_ICAO_index]!='':
                        self.Distance[current_ICAO_index]=int(self.calculDistance(self.myLatitude, self.myLongitude,self.Latitude[current_ICAO_index],self.Longitude[current_ICAO_index]))
                        self.tableWidget.setItem(current_ICAO_index,self.index_Distance, QTableWidgetItem(str(self.Distance[current_ICAO_index])))
                    
                
                    
                ########################################################  VITESSE ###############################################################################################################################
                    
                    if TC_decimal == 19:
                        print ("Airborne velocities")
                        Sew=trame[40]
                        Sns=trame[51]
                        print ("Sew=",Sew)
                        print ("Sns=",Sns)
                        if Sew == 1:
                            print ("Flying East ....-> West")
                        else:
                            print ("Flying West ....-> East")
                        if Sns == 1:
                            print ("Flying North ....-> South")
                        else:
                            print ("Flying South ....-> North")
                        
                        #Vitesse East-West
                        Vew=[]
                        Vew_dec=""
                        Vew_decimal=-1
                        for i in range(0,10):
                            Vew.append(trame[41+i])
                            Vew_dec+=str(Vew[i])
                        for i in range(0,10):
                            Vew_decimal += Vew[9-i]*2**i
                            
                        print ("Vew=",Vew_dec)
                        print ("vitesse we=",current_ICAO_index, len(self.Vitesse_we),len(self.ICAO))
                        print ("vitesse we=",len(self.Vitesse_we), self.Vitesse_we[current_ICAO_index])
                        if Sew==1:
                            print ("Vwe=", int(round(-Vew_decimal*1.852)) ,"km/h")
                            self.Vitesse_we[current_ICAO_index]=int(round(-Vew_decimal*1.852))
                        else:
                            print ("Vwe=", int(round(Vew_decimal*1.852)) ,"km/h")
                            self.Vitesse_we[current_ICAO_index]=int(round(Vew_decimal*1.852))
                        
                        self.tableWidget.setItem(current_ICAO_index,self.index_Vitesse_we, QTableWidgetItem(str(self.Vitesse_we[current_ICAO_index])))
                        
                        
                        #Vitesse North - South
                        Vns=[]
                        Vns_dec=""
                        Vns_decimal=-1
                        for i in range(0,10):
                            Vns.append(trame[52+i])
                            Vns_dec+=str(Vns[i])
                        for i in range(0,10):
                            Vns_decimal += Vns[9-i]*2**i
                            
                        print ("Vns=",Vns_dec)
                        if Sns==1:
                            print ("Vsn=", int(round(-Vns_decimal*1.852)) ,"km/h")
                            self.Vitesse_ns[current_ICAO_index]=int(round(-Vns_decimal*1.852))
                        else:
                            print ("Vsn=", int(round(Vns_decimal*1.852)) ,"km/h")
                            self.Vitesse_ns[current_ICAO_index]=int(round(Vns_decimal*1.852))
                        
                        self.tableWidget.setItem(current_ICAO_index,self.index_Vitesse_ns, QTableWidgetItem(str(self.Vitesse_ns[current_ICAO_index])))
                            
                        print ("V=", int(round(math.sqrt(Vns_decimal*1.852*Vns_decimal*1.852+Vew_decimal*1.852*Vew_decimal*1.852))), "km/h")
                        self.Vitesse[current_ICAO_index]=int(round(math.sqrt(Vns_decimal*1.852*Vns_decimal*1.852+Vew_decimal*1.852*Vew_decimal*1.852)))
                        self.tableWidget.setItem(current_ICAO_index,self.index_Vitesse, QTableWidgetItem(str(self.Vitesse[current_ICAO_index])))
                        #Vertical Rate
                        Svr=trame[63]
                        if Svr==1:
                            print ("Svr=", Svr, "DOWN, descending...")
                            self.Sens[current_ICAO_index]='DOWN'
                        else:
                            print ("Svr=", Svr, "UP, ascending...")
                            self.Sens[current_ICAO_index]='UP        '
                        self.tableWidget.setItem(current_ICAO_index,self.index_Sens, QTableWidgetItem(self.Sens[current_ICAO_index]))
                        Vr=[]
                        Vr_dec=""
                        Vr_decimal=-1
                        for i in range(0,9):
                            Vr.append(trame[64+i])
                            Vr_dec+=str(Vr[i])
                        for i in range(0,9):
                            Vr_decimal += Vr[8-i]*2**i
                            
                        print ("Vr=",Vr_dec)
                        print ("Vr=",int(round(Vr_decimal*64*0.3048)),"m/min")
                        self.VerticalSpeed[current_ICAO_index]=int(round(Vr_decimal*64*0.3048))
                        print (self.textVerticalSpeed(self.VerticalSpeed[current_ICAO_index]))
                        self.tableWidget.setItem(current_ICAO_index,self.index_Vertical, QTableWidgetItem(str(self.convVerticalSpeed(self.VerticalSpeed[current_ICAO_index]))))
                        
                        
                        
                ########################################################  AIRBORNE POSITION (w/ GNSS Height) ######################################################################################################
                    
                        
                    if 20 <= TC_decimal <= 22:
                        print ("Les données indiquent: Airborne position (w/ GNSS Height")
                        
                
                ########################################################  OTHER USES ######################################################################################################
                    
                    if 23 <= TC_decimal <= 31:
                        print ("Les données indiquent: Reserved for other uses")
                
                    # Contruct json data for map
                    # {"newLocation": [{"Index": 1, "Latitude": 50.67, "Longitude": 3.13, "ICAO":"12345", "Direction": 0, 
                    #                  "Label":"ICAO : 12345<br>Altitude :24 m<br> AIRBUS"}]}
                    if self.Latitude[current_ICAO_index]!='' and self.Latitude[current_ICAO_index]!='':
                        jsonLabel  = 'ICAO : '+ self.ICAO[current_ICAO_index] + '<br/>'
                        jsonLabel += 'Flight : '+ self.Vol[current_ICAO_index] + '<br/>'
                        jsonLabel += 'Speed : '+ str(self.Vitesse[current_ICAO_index]) + '<br/>'
                        jsonLabel += 'Vert. speed : '+ self.textVerticalSpeed(self.VerticalSpeed[current_ICAO_index]) + '<br/>'
                        jsonLabel += 'Altitude : '+ str(self.Altitude[current_ICAO_index]) + '<br/>'
                        jsonLabel += 'Latitude : '+ str(self.Latitude[current_ICAO_index]) + '°<br/>'
                        jsonLabel += 'Longitude : '+ str(self.Longitude[current_ICAO_index]) + '°<br/>'
                        jsonLabel += 'Distance : '+ str(self.Distance[current_ICAO_index])
                        jsonData['newLocation'].append({
                            'Index' : current_ICAO_index,
                            'Latitude' : self.Latitude[current_ICAO_index],
                            'Longitude' : self.Longitude[current_ICAO_index],
                            'ICAO' : self.ICAO[current_ICAO_index],
                            'Label' : jsonLabel, 
                            'Direction' : self.Direction[current_ICAO_index],
                            })

                    # remove decoded file 
                    try:
                        os.remove(os.path.join(self.ADSB_DirTempFiles,fichier[k]))
                    except:
                        pass
                    
        # END decode each file one by one 
        # Save non empty jsonData 
        if len(jsonData['newLocation']) >0 :
            now=datetime.datetime.now()-self.timeStart
            timeStamp = int(10*now.total_seconds()) /10
            jsonData['timeStamp']=timeStamp
            with open('AdsbGuiPlanesData.json', 'w') as outfile:
                json.dump(jsonData, outfile)        

    # end def adsb_decode(self):

if __name__ == '__main__':
    # when running from inside spyder - which itself is a QApplication, the main loop should read:
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    ex = App()
    sys.exit(app.exec_())

