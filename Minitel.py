from time import sleep
import serial, serial.tools.list_ports
import random

long = 39
haut = 24

#Commandes de contrôle utilisateur :
x_buzzer = b'\x07'                       #Lance un buzzer dans le terminal
x_desactiver = b'\x1B\x3B\x60\x58\x52'   # désactiver écho local
x_masquer_curseur = b'\x14'              # masquer curseur (curseur déjà invisible pour ma part)
x_afficher_curseur = b'\x11'             # afficher le curseur
x_mode_pixel = b'\x0E'                   #Change la saisie de texte pour transformer les carractères en "pixels"
x_mode_texte = b'\x0F'                   #Remet la saisie de texte habituelle
x_mode_ASCII_etendu = b'\x16'            #Permet la saisie de certains caractères spéciaux

#Nettoyage :
x_vider_ecran = b'\x0C'                  # effacer écran (sauf la ligne max)
x_vider_ligne_actuelle = b'\x18\x18'     #Effacer tout ce qu'il y a après le curseur dans la même ligne

#Contrôle de la position du curseur
x_ligne_max = b'\x1F\x40\x41'            # Met le curseur une ligne au dessus du point d'origine normal
x_ligne_min = b'\x0B'                    # Met le curseur à la dernière ligne
x_home = b'\x1E'                         # Met le curseur au point d'origine normal (pas ligne max)
x_reculer_curseur  = b'\x08'             # Déplace le curseur une caractére à gauche
x_avancer_curseur  = b'\x09'             # Déplace le curseur une caractére à gauche
x_monter_curseur  = b'\x0B'              # Déplace le curseur une ligne au dessus
x_descendre_curseur = b'\x0A'            # Déplace le curseur une ligne en dessous
x_debut_ligne = b'\x0D'                  #Met le curseur au début de la ligne actuelle

x_o = b'\x7f' #Carré blanc

class Minitel(serial.Serial):
    def __init__(self, baud_rate=4800, parity=serial.PARITY_EVEN, byte_size=7, force_COM=False):
        #Si un port de COM est déjà saisi, on essaie de s'y connecter directement
        if force_COM:
            try:
                super().__init__(force_COM, baud_rate, parity=parity, bytesize=byte_size, rtscts=1)
                print("Port " + force_COM + " connecté (choisi de force)")
            except serial.SerialException as e:
                print("Port " + force_COM + " non compatible (choisi de force)")
        else :
            #Sans port séléctionné à l'avance, on liste tous les ports disponible et on se connecte au premier qui fonctionne
            liste_ports = serial.tools.list_ports.comports()
            for port in liste_ports:
                try:
                    super().__init__(port.name, baud_rate, parity=parity, bytesize=byte_size, rtscts=1)
                    print("Port " + port.name + " connecté")
                except serial.SerialException as e:
                    print("Port " + port.name + " non compatible")


    def test_neige(self, taille=haut, rand=3):
        for i in range (taille):
            random_string = b''
            while len(random_string) < long+1:
                random_string += b' '*random.randint(1,rand)+b'o'
            random_string = random_string[:long+1]
            self.write(b'\r' + random_string)


    def test_boing(self):
        self.write(x_debut_ligne+b' ')
        #Vers le bas
        for i in range(haut-1):
            self.write(x_reculer_curseur+b' '+x_descendre_curseur+x_reculer_curseur+b'o')
            sleep(0.05)
        # Vers la droite
        for i in range(long):
            self.write(x_reculer_curseur + b' ' + b'o')
            sleep(0.05)
        #Vers le haut
        for i in range(haut-1):
            self.write(x_reculer_curseur + b' ' + x_monter_curseur + x_reculer_curseur + b'o')
            sleep(0.05)
        # Vers la gauche
        for i in range(long):
            self.write(x_reculer_curseur + x_reculer_curseur)
            self.write(x_vider_ligne_actuelle)
            self.write(b'o')
            sleep(0.04)


    def vider_ecran(self):
        self.write(x_vider_ecran)

    def mode_expo(self):
        self.write(x_masquer_curseur+x_desactiver)

if __name__ == '__main__':
    howitzer = Minitel(force_COM='COM4')
    howitzer.vider_ecran()
    howitzer.mode_expo()
    while 1:
        howitzer.test_boing()
    howitzer.close()