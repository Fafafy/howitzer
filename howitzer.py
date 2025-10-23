import sys
import time
import subprocess
from threading import Thread
#On essaie de récupérer le module PyMinitel. Comme il n'est pas sur pip, on vient le récupérer directment sur Git
try :
    from minitel.Minitel import Minitel
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/Fafafy/PyMinitel.git"])
    from minitel.Minitel import Minitel

from minitel.constantes import (SS2, SEP, ESC, CSI, PRO1, PRO2, PRO3, MIXTE1,
                                              MIXTE2, TELINFO, ENQROM, SOH, EOT, TYPE_MINITELS, STATUS_FONCTIONNEMENT,
                                              LONGUEUR_PRO2, STATUS_TERMINAL, PROG, START, STOP, LONGUEUR_PRO3,
                                              RCPT_CLAVIER, ETEN, C0, MINUSCULES, RS, US, VT, LF, BS, TAB, CON, COF,
                                             AIGUILLAGE_ON, AIGUILLAGE_OFF, RCPT_ECRAN, EMET_MODEM, FF, CAN, BEL, CR,
                                              SO, SI, B300, B1200, B4800, B9600, REP, COULEURS_MINITEL,
                                              CAPACITES_BASIQUES, CONSTRUCTEURS, ROULEAU)
def affichage_logo(minitel):
    minitel.envoyer('a')

if __name__ == '__main__':
    howitzer = Minitel(peripherique='COM4')
    howitzer.definir_vitesse(4800)
    howitzer.efface('tout')
    howitzer.curseur(False)
    affichage_logo(howitzer)


