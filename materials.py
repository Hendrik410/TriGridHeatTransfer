'''
Created on 03.08.2017

@author: muel_hd
'''


#===============================================================================
# skeleton = {
#     "lambda_x": Waermeleitefaehigkeit in x-Richtung,
#     "lambda_y": Waermeleitefaehigkeit in y-Richtung,
#     "dichte"  : Dichte,
#     "cp"      : Waermekapazitaet,
#     "k_x"     : Permeabilitaet in x-Richtung,
#     "k_y"     : Permeabilitaet in y-Richtung
# }
#===============================================================================


SiC = {
    "lambda_x": 17.0,
    "lambda_y": 8.0,
    "dichte"  : 1300.0,
    "cp"      : 1300.0,
    "k_x"     : 4.36 * 10 ** -13,
    "k_y"     : 5.3 * 10 ** -14
}

Aluminum = {
    "lambda_x": 236.0,
    "lambda_y": 236.0,
    "dichte"  : 2700.0,
    "cp"      : 896.0,
    "k_x"     : 0.0,
    "k_y"     : 0.0
}

Nitrogen =  {
    "lambda_x": 0.02583,
    "lambda_y": 0.02583,
    "dichte"  : 1.25,
    "cp"      : 1040.0,
    "k_x"     : 0.0,
    "k_y"     : 0.0
}