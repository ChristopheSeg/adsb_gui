 #!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os,time
import threading 
import math
if sys.version_info[0] < 3:
	import Tkinter
	from Tkconstants import *

else: # Pythimport mathon 3
	import tkinter as Tkinter
	# from tkconstants import *








class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.grid()
		self.entryVariable = Tkinter.StringVar()
		self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
		
		def thread_data(): 
			
			# create temp_files dir if it does not exits
			os.system('mkdir temp_files -p')
			# chemin du répertoire contenant les fichiers .dat
			Chemin_home=os.path.dirname(os.path.realpath('__file__'))
			# chemin du répertoire dans lequel on déplace les  fichiers .dat (pour traitement)
			Chemin_dossier_adsb=os.path.join(Chemin_home, 'temp_files')
			
			self.ICAO=['ICAO (HEX):   ']
			self.Vol=['Vol:          ']
			self.Vitesse_we=['Vit WE (km/h):']
			self.Vitesse_ns=['Vit NS (km/h):']
			self.Vitesse=['Vit (km/h):   ']
			self.Vertical=['Vrate (m/min):']
			self.Sens=['Sens:         ']
			self.Altitude=['ALTitude (m): ']
			self.Latitude=['Latitude (°): ']
			self.Longitude=['Longitude (°):']
			self.CPR_LAT_odd=['CPRLATodd']
			self.CPR_LON_odd=['CPRLONodd']
			self.CPR_LAT_even=['CPRLATeven']
			self.CPR_LON_even=['CPRLONeven']

			for i in range(0,20):
				#self.ICAO.append('-')
				self.Vol.append('-')
				self.Vitesse_we.append('-')
				self.Vitesse_ns.append('-')
				self.Vitesse.append('-')
				self.Vertical.append('-')
				self.Sens.append('-')
				self.Altitude.append('-')	
				self.Latitude.append('-')	
				self.Longitude.append('-')	
				self.CPR_LAT_odd.append('-')
				self.CPR_LON_odd.append('-')
				self.CPR_LAT_even.append('-')
				self.CPR_LON_even.append('-')
				
			
			while(True):
				
				time.sleep(2)
				fileCounter = 0
				for root, dirs, files in os.walk(Chemin_home+"/"):
					for file in files:    
						if file.startswith('file')  and file != 'files':
							fileCounter += 1
				if fileCounter==0:
					sys.stdout.write("*")
					sys.stdout.flush()
				else:
					os.system('mv {0}/file* {1}/'.format(Chemin_home,Chemin_dossier_adsb))
					print("") # print an EOL
				
				fichier=[]  
				for files in os.listdir(Chemin_dossier_adsb):  
					fichier.append(files)  
				if len(fichier)>0: 
					print(fichier)
				
				
				
				for k in range(0,len(fichier)):
					
					# Ouvrir le fichier binaire et afficher la trame
					with open('{0}/{1}'.format(Chemin_dossier_adsb,fichier[k]), "rb") as binary_file:
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
							''' D'aprÃ¨s pyModeS/util.py'''
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
							print ("TRAME INCOMPLÃˆTE ----- BAD PARITY", crc_msg)
							os.system('rm {0}/{1}'.format(Chemin_dossier_adsb,fichier[k]))
						else:
							print ('CRC check OK --- DonnÃ©es valides')
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
							print ("ICAO HEX:", hex(icao_decimal)[2:])
							
							
							for i in range(0,len(self.ICAO)+1):
								if hex(icao_decimal)[2:] in self.ICAO:
									pass
								else:
									self.ICAO.append(hex(icao_decimal)[2:])
									
							
						# Les 5 bits suivants ICAO constituent le Type Code TC qui dÃ©finit le type de donnÃ©es dans les DATA:
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
								self.Vol[self.ICAO.index(hex(icao_decimal)[2:])]=vol
								
						
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
									
								print ("Alt=",int(round((Alt_decimal*25-1000)*0.3046)),'m')
								
								self.Altitude[self.ICAO.index(hex(icao_decimal)[2:])]=int(round((Alt_decimal*25-1000)*0.3046))
								
						
				#CoordonnÃ©es CPR
								if msg[53] == '1':
									print ('Odd frame')
									CPR_LATodd=bin2dec(msg[54:71])
									print ("CPR_LATodd=", CPR_LATodd)
									self.CPR_LAT_odd[self.ICAO.index(hex(icao_decimal)[2:])]=CPR_LATodd/131072.0
									
									CPR_LONodd=bin2dec(msg[72:88])
									print ("CPR_LONodd=", CPR_LONodd)
									self.CPR_LON_odd[self.ICAO.index(hex(icao_decimal)[2:])]=CPR_LONodd/131072.0
									
								else:
									print ('even frame')
									CPR_LATeven=bin2dec(msg[54:71])
									print ("CPR_LATeven=", CPR_LATeven)
									self.CPR_LAT_even[self.ICAO.index(hex(icao_decimal)[2:])]=CPR_LATeven/131072.0
									
									CPR_LONeven=bin2dec(msg[72:88])
									print ("CPR_LONeven=", CPR_LONeven)
									self.CPR_LON_even[self.ICAO.index(hex(icao_decimal)[2:])]=CPR_LONeven/131072.0
						
							#Lat et Lon 
							for i in range(1,12):
								try:
									j=math.floor(59*self.CPR_LAT_even[i] - 60*self.CPR_LAT_odd[i] + 0.5)
									print ('j=',j)
									dLateven=6.0
									dLatodd=360/59.0
									Lateven = dLateven*((j-60*math.floor(j/60))+self.CPR_LAT_even[i])
									self.Latitude[i]=round(Lateven,3)
									
									D=(math.cos(math.pi*Lateven/180)*math.cos(math.pi*Lateven/180))
									C= 1- math.cos(math.pi/30)
									E=1-C/D
									NLlat=math.floor(2*math.pi/math.acos(E))
									print ('NLlat=',NLlat)
									dLon=360.0/NLlat
									m=math.floor(self.CPR_LON_even[i]*(NLlat-1) - self.CPR_LON_odd[i]*NLlat + 0.5)
									print ('m=',m)
									Lon = dLon*((m-math.floor(m/NLlat)) + self.CPR_LON_odd[i] )
									print ('Lon=',Lon)
									self.Longitude[i]=round(Lon,3)
								except:
									pass
							
							
						
							
						########################################################  VITESSE ###############################################################################################################################
							
							if TC_decimal == 19:
								print ("Airborne velocities")
								Sew=trame[40]
								Sns=trame[51]
								print ("Sew=",Sew)
								print ("Sns=",Sns)
								if Sew == 1:
									print ("Flying East -----> West")
								else:
									print ("Flying West -----> East")
								if Sns == 1:
									print ("Flying North -----> South")
								else:
									print ("Flying South -----> North")
								
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
								if Sew==1:
									print ("Vwe=", int(round(-Vew_decimal*1.852)) ,"km/h")
									self.Vitesse_we[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(-Vew_decimal*1.852))
							
								else:
									print ("Vwe=", int(round(Vew_decimal*1.852)) ,"km/h")
									self.Vitesse_we[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(Vew_decimal*1.852))
								
								
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
									self.Vitesse_ns[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(-Vns_decimal*1.852))
								else:
									print ("Vsn=", int(round(Vns_decimal*1.852)) ,"km/h")
									self.Vitesse_ns[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(Vns_decimal*1.852))
									
								print ("V=", int(round(math.sqrt(Vns_decimal*1.852*Vns_decimal*1.852+Vew_decimal*1.852*Vew_decimal*1.852))), "km/h")
								self.Vitesse[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(math.sqrt(Vns_decimal*1.852*Vns_decimal*1.852+Vew_decimal*1.852*Vew_decimal*1.852)))
								
								#Vertical Rate
								Svr=trame[63]
								if Svr==1:
									print ("Svr=", Svr, "DOWN, descending...")
									self.Sens[self.ICAO.index(hex(icao_decimal)[2:])]='DOWN'
								else:
									print ("Svr=", Svr, "UP, ascending...")
									self.Sens[self.ICAO.index(hex(icao_decimal)[2:])]='UP        '
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
								self.Vertical[self.ICAO.index(hex(icao_decimal)[2:])]=int(round(Vr_decimal*64*0.3048))
								
								
								
						########################################################  AIRBORNE POSITION (w/ GNSS Height) ######################################################################################################
							
								
							if 20 <= TC_decimal <= 22:
								print ("Les donnÃ©es indiquent: Airborne position (w/ GNSS Height")
								
						
						########################################################  OTHER USES ######################################################################################################
							
							if 23 <= TC_decimal <= 31:
								print ("Les donnÃ©es indiquent: Reserved for other uses")
						
						
						##########################################################################################################################################################################
							
							#print self.ICAO
							#print self.Vol
							#print self.Vitesse_we
							#print self.Vitesse_ns
							#print self.Vitesse
							#print self.Vertical
							#print self.Sens
							#print self.Altitude
							#print self.CPR_LAT_odd
							#print self.CPR_LON_odd
							#print self.CPR_LAT_even
							#print self.CPR_LON_even
							
						
							# remove decoded file 
                             os.system('rm {0}/{1}'.format(Chemin_dossier_adsb,fichier[k]))
						    
		t = threading.Thread(target=thread_data)
		t.start()
		
		
		
########################################################" INTERFACE GRAPHIQUE "##################################################################################################"""



		nbr=21
		entry_label=Tkinter.Label(self,text=self.ICAO[0], fg='blue',anchor ='c')
		entry_label.place(x=10,y=20)
		def refresh_icao():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.ICAO[i], fg='black', anchor ='c')
						entry_label.place(x=10,y=20+20*i)
					except:
						pass
		tr = threading.Thread(target=refresh_icao)
		tr.start()


		entry_label=Tkinter.Label(self,text=self.Vol[0], fg='blue',anchor ='c')
		entry_label.place(x=100,y=20)
		def refresh_vol():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Vol[i], fg='black', anchor ='c')
						entry_label.place(x=100,y=20+20*i)
					except:
						pass
		tv = threading.Thread(target=refresh_vol)
		tv.start()			
		
		entry_label=Tkinter.Label(self,text=self.Vitesse_we[0], fg='blue',anchor ='c')
		entry_label.place(x=200,y=20)
		def refresh_vitwe():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						
						entry_label=Tkinter.Label(self,text=self.Vitesse_we[i], fg='black', anchor ='c')
						entry_label.place(x=200,y=20+20*i)
					except:
						pass
		twe = threading.Thread(target=refresh_vitwe)
		twe.start()
		
		entry_label=Tkinter.Label(self,text=self.Vitesse_ns[0], fg='blue',anchor ='c')
		entry_label.place(x=300,y=20)
		def refresh_vitns():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
					
						entry_label=Tkinter.Label(self,text=self.Vitesse_ns[i], fg='black', anchor ='c')
						entry_label.place(x=300,y=20+20*i)
					except:
						pass
		tns = threading.Thread(target=refresh_vitns)
		tns.start()
		
		entry_label=Tkinter.Label(self,text=self.Vitesse[0], fg='blue',anchor ='c')
		entry_label.place(x=400,y=20)
		def refresh_vit():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
					
						entry_label=Tkinter.Label(self,text=self.Vitesse[i], fg='black', anchor ='c')
						entry_label.place(x=400,y=20+20*i)
					except:
						pass
		tv = threading.Thread(target=refresh_vit)
		tv.start()
				
		
		
		entry_label=Tkinter.Label(self,text=self.Vertical[0], fg='blue',anchor ='c')
		entry_label.place(x=500,y=20)
		def refresh_vert():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Vertical[i], fg='black', anchor ='c')
						entry_label.place(x=500,y=20+20*i)
					except:
						pass
		tvert = threading.Thread(target=refresh_vert)
		tvert.start()
				
		
		entry_label=Tkinter.Label(self,text=self.Sens[0], fg='blue',anchor ='c')
		entry_label.place(x=600,y=20)
		def refresh_Sens():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Sens[i], fg='black', anchor ='c')
						entry_label.place(x=600,y=20+20*i)
					except:
						pass
		tsens = threading.Thread(target=refresh_Sens)
		tsens.start()
				
		
		entry_label=Tkinter.Label(self,text=self.Altitude[0], fg='blue',anchor ='c')
		entry_label.place(x=700,y=20)
		def refresh_alt():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Altitude[i], fg='black', anchor ='c')
						entry_label.place(x=700,y=20+20*i)
					except:
						pass
		talt = threading.Thread(target=refresh_alt)
		talt.start()
					
		
		
		entry_label=Tkinter.Label(self,text=self.Latitude[0], fg='blue',anchor ='c')
		entry_label.place(x=800,y=20)
		def refresh_lat():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Latitude[i], fg='black', anchor ='c')
						entry_label.place(x=800,y=20+20*i)
					except:
						pass
		tlat = threading.Thread(target=refresh_lat)
		tlat.start()		
		
		
		
		
		
		entry_label=Tkinter.Label(self,text=self.Longitude[0], fg='blue',anchor ='c')
		entry_label.place(x=900,y=20)
		def refresh_lon():
			while(True):
				time.sleep(2)
				for i in range(1,nbr):
					try:
						entry_label=Tkinter.Label(self,text=self.Longitude[i], fg='black', anchor ='c')
						entry_label.place(x=900,y=20+20*i)
					except:
						pass
		tlon = threading.Thread(target=refresh_lon)
		tlon.start()
		
		
			
		
		
		
	
if __name__ == "__main__": 
    app = simpleapp_tk(None)
    app.geometry('1000x500')
    app.title('Surveillance du trafic aérien')
    app.mainloop()				
				
