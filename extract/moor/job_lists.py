"""
Module to create dicts for multiple (or single) mooring extractions.
"""

def get_sta_dict(job_name):
    
    # specific job definitions
    
    if job_name == 'willapa_bc': # Willapa Bay Center PCSGA Mooring
        sta_dict = {
            'wbc': (-123.9516, 46.6290)
            }
            
    elif job_name == 'QuadraBoL': # SOG mooring by QuadraBoL island
        sta_dict = {
            'QuadraBoL': (-125.222, 50.116)
            }
            
    elif job_name == 'OCNMS': # Olympic Coast National Marine Sanctary
        sta_dict = {
        
#            'CA015': (-124.7568, 48.1663),
#            'CA042': (-124.8234, 48.1660),
#            'CA065': (-124.8949, 48.1659),
#            'CA100': (-124.9319, 48.1658), # too short
#            'CE015': (-124.3481, 47.3568),
            'CE042': (-124.4887, 47.3531), # not untill 2012
#            'CE065': (-124.5669, 47.3528),
#            'KL015': (-124.4284, 47.6008), #no bottom DO
#            'KL027': (-124.4971, 47.5946),
#            'KL050': (-124.6112, 47.5933), # too short
#            'MB015': (-124.6768, 48.3254), #no bottom DO
#            'MB042': (-124.7354, 48.3240),
#            'TH015': (-124.6195, 47.8761),  # too short
#            'TH042': (-124.7334, 47.8762),
#            'TH065': (-124.7967, 47.8767) # too short
        }
    elif job_name == 'PMEL': # NOAA PMEL moor
        sta_dict = {

            #'CapeElizabeth': (-124.731, 47.353),
            #'Chaba':         (-125.958, 47.936),
# discard   #'NH10':          (-124.778, 44.904), # not accurate based on https://www.pmel.noaa.gov/co2/timeseries/NH10.txt
            'NH10':          (-124.301, 44.642), # from https://www.pmel.noaa.gov/co2/story/NH-10
            #'CapeArago':     (-124.530, 43.300), # https://www.pmel.noaa.gov/co2/story/CB-06
            #'Dabob':         (-122.803, 47.803),
           # 'Twanoh':        (-123.008, 47.375)
        }

    elif job_name == 'OOI': # Ocean Observation Initiative on the west coast
        sta_dict = {

            'CE01ISSM': (-124.09583, 44.65978), # MFN btm 25m
            #'CE02SHSM': (-124.3032, 44.63532), # RID surf 7m
            'CE02SHBP': (-124.30572, 44.63721), # cabled benthic package at OR shelf btm 80m
            #'CE04OSBP': (-124.95351, 44.36926), # cabled benthic package at OR offshore btm 581m
            #'CE04OSSM': (-124.9398, 44.36518), # RID surf 7m
            #'CE06ISSM': (-124.26973, 47.13365), # MFN btm 29m
            #'CE07SHSM': (-124.55202, 46.98472), # MFN btm 87m 
            #'CE09OSSM': (-124.9509, 46.85343) # MFN btm 540m

        }
        
    elif job_name == 'LineP':  # Line P program
        sta_dict = {

            'P01': (-125.5000, 48.5750),  # 120 m
            'P02': (-126.0000, 48.6000),  # 114 m
            'P03': (-126.3333, 48.6250),  # 750 m
#            'P04': (-126.6667, 48.6500),  # 1300 m
            'P05': (-127.1667, 48.6917),  # 2100 m
            'P06': (-127.6667, 48.7433),  # 2500 m
            'P07': (-128.1667, 48.7767),  # 2450 m
            'P08': (-128.6667, 48.8167),  # 2440 m
            'P09': (-129.1667, 48.8567),  # 2340 m
            'P10': (-129.6667, 48.8933),  # 2660 m
            #'P11': (-130.1667, 48.9333),  # 2700 m
            #'P12': (-130.6667, 48.9700)  # 3300 m
#            'P12': (-130.0, 48.9700) # manipulated
        }
        
    elif job_name == 'NHL':  # Newport Hydrography Line
        sta_dict = {
#            'NH00': (-124.050, 44.652),  # virtual_made up
#            'NH01': (-124.100, 44.652),  # 30 m
#            'NH03': (-124.130, 44.652),  # 48 m
#            'NH05': (-124.177, 44.652),  # 60 m
            'NH10': (-124.295, 44.652),  # 81 m
#            'NH15': (-124.412, 44.652),  # 90 m
#            'NH20': (-124.528, 44.652),  # 140 m
#            'NH25': (-124.650, 44.652),  # 296 m
#            'NH26': (-124.700, 44.652)  # virtual_made up
        } 
               
    elif job_name == 'mickett_1':
        sta_dict = {
        'ORCA_Hansville': (-122.6270, 47.9073),
        'ORCA_Hoodsport': (-123.1126, 47.4218),
        'ORCA_Point_Wells': (-122.3972, 47.7612),
        'Central_Main_Stem_Hood_Canal': (-122.989507, 47.574352),
        'North_Central_Main_Basin': (-122.440755, 47.825099)
        }
            
    elif job_name == 'mickett_2':
        sta_dict = {
        'Carr_Inlet_ORCA': (-122 - 43.8/60, 47 + 16.8/60),
        'East_of_Fox_Island': (-122 - 35.158/60, 47 + 13.185/60)
        }
        
    elif job_name == 'stoll_corals':
        sta_dict = {
        'Carson_D01_Lopez': (-122.8728, 48.36816),
        'Carson_D02_Admiralty': (-122.7883, 48.19252),
        'Carson_D04_Admiralty': (-122.8166, 48.19764),
        'Carson_D05_Keystone': (-122.6576, 48.12828),
        'Carson_D07_NorthAdmiralty': (-122.8898, 48.22245),
        'Carson_D08_Canada': (-123.149, 48.36136),
        'USNM_19270_Canada': (-123.233, 48.35),
        'USNM_92626_Admiralty': (-122.80, 48.1917),
        'USNM_19228_Dungeness': (-123.189, 48.225),
        'USNM_19272_Admiralty': (-122.817, 48.20),
        'USNM_92620_Lopez': (-122.85, 48.3667),
        }
            
    elif job_name == 'stoll_obs':
        sta_dict = {
        'DOE_SJF002': (-123.025, 48.25),
        'DOE_ADM002': ( -122.8417151, 48.1875056),
        'DOE_ADM001': ( -122.616715, 48.0300056),
        'WOAC_STN21': (-122.8504, 48.1883),
        'WOAC_STN20': (-122.6848, 48.142),
        'WOAC_STN19': (-122.6318, 48.0915),
        }
            
    elif job_name == 'Kelly':
        # note I pushed two of the locations a bit West to get off the landmask
        sta_dict = {
        'Seal_Rock': (-122.87004, 47.70557),
        'Little_Dewatto': (-123.08612-.005, 47.44489),
        'Red_Bluff': (-123.10438-.007, 47.41625)
        }
            
    elif job_name == 'jazzy':
        sta_dict = {
        'Middle_Bank': (-123.09651, 48.40935),
        'East_Bank': (-122.97376, 48.30042),
        'Upright_Channel': (-122.923005, 48.55410),
        'Blakely_Orcas': (-122.82880, 48.58790),
        'Rosario_Strait': (-122.74001, 48.64631),
        'North_Station': (-123.04166, 48.58330),
        'South_Station': (-122.94330, 48.42000),
        'Hein_Bank': (-123.03940, 48.35825)
        }
        
    elif job_name == 'ooi':
        sta_dict = {
            'CE01':(-124.095, 44.6598), # Oregon Inshore (25 m)
            'CE02':(-124.304, 44.6393), # Oregon Shelf (80 m)
            'CE04':(-124.956, 44.3811), # Oregon Offshore (588 m)
            'PN01A':(-125.3983, 44.5096), # Slope Base (2905 m)
        }
        
    elif job_name == 'erika_esci491w2022':
        sta_dict = {
        'Olympia': (-122.9165, 47.0823),
        'Tacoma': (-122.4758, 47.3015),
        'Seattle_West_Point': (-122.4435, 47.6813),
        'Bellingham': (-122.5519, 48.7348),
        'Central_Hood_Canal': (-122.9895, 47.5744),
        'Skokomish': (-123.1272, 47.3639),
        'Hein_Bank': (-123.0394, 48.35825),
        'Admiralty': (-122.6949, 48.1370),
        'Everett': (-122.2806, 47.9855)
        }
        
    elif job_name == 'scoot':
        sta_dict= {
        'F_090_WEH': (-126.92523957836097, 50.86003686529567),
        'F_087_SIM': (-126.88867577473951, 50.8779837900623),
        'F_083_CEC': (-126.71014703214891, 50.86003686529567),
        'M_083_087': (-126.79852585292794, 50.89607323113631),
        'F_084_CYP': (-126.65795536471262, 50.84223133403236),
        'M_083_084': (-126.69268072600828, 50.86003686529567),
        'F_088_SIR': (-126.60638135698926, 50.84223133403236),
        'M_084_089': (-126.6235045170437, 50.86003686529567),
        'F_082_BRE': (-125.34911668789157, 50.28660059365715),
        'F_089_VEN': (-125.33704071737607, 50.300007509695305),
        'F_086_RAZ': (-125.01765650844104, 50.327117635547935),
        'E_079_TOF': (-126.04793822349058, 49.21393673803513),
        'E_129_STG': (-125.12767093555838, 50.0962109697609),
        'E_004_NOO': (-126.60638135698926, 49.57825722433716),
        'E_002_ESP': (-126.9806322902372, 49.829746612851736),
        'E_016_RIV': (-126.13824776832129, 49.66598688018571),
        'F_004_CON': (-126.47181502357597, 49.65693905574285),
        'F_022_GOR': (-126.43883566700802, 49.64795343794384),
        'F_016_MUC': (-126.3414536354723, 49.63902959909838),
        'M_023_014': (-126.3414536354723, 50.607192072687155),
        'F_008_BAR': (-125.2773744875855, 50.31351066854337),
        'F_005_AHL': (-124.15671501359827, 49.77957267482829),
        'F_013_VAN': (-123.85335983884296, 49.675097341923546),
        'F_011_SAL': (-123.83316138272168, 49.62136556218934),
        'F_006_NEW': (-123.65810809633727, 49.64795343794384),
        'E_006_RIV': (-123.5436501783167, 49.693507914816124)}
        
    elif job_name == 'kastner':
        sta_dict = {
        'Canal_Mouth': (-122.637493, 47.928439),
        'Bridge': (-122.621784, 47.858911),
        'Joint': (-122.819507, 47.669810),
        'Dabob_Bay_Entrance': (-122.860989, 47.693196),
        'Dabob_Bay_Head': (-122.805422, 47.808231),
        'Duckabush_River': (-122.908291, 47.633095),
        'Hama_Hama': (-123.026320, 47.534954),
        'Lilliwaup': (-123.088399, 47.456583),
        'ORCA_Hoodsport': (-123.1126, 47.4218),
        'Skokomish': (-123.127835, 47.363217),
        'Sisters_Point': (-123.022404, 47.358448),
        'ORCA_Twanoh': (-123.0083, 47.375),
        'Head': (-122.893559, 47.411036)
        }
        
    elif job_name == 'ROMS_update':
        sta_dict = {
        'ORCA_Hoodsport': (-123.1126, 47.4218),
        'CE02':(-124.304, 44.6393), # Oregon Shelf (80 m)
        'JdF_west':(-124.675, 48.481),
        'Willapa':(-123.97,46.55),
        'dabob':(-122.8098,47.7948)
        }
        
    elif job_name == 'fatland1':
        sta_dict = {
        'Oregon_Offshore': (-124.95648, 44.37415),
        'Oregon_Slope_Base': (-125.38966, 44.52897)
        }
        
    elif job_name == 'nina_long':
        sta_dict = {
            'nb1': (-122.303428, 48.016441),
            'nb2': (-122.396982, 48.131897),
            'nb3': (-122.489881, 48.107576),
            'nb4': (-122.554192, 48.241760),
            'nb5': (-122.369498, 47.882541),
            'nb6': (-122.466784, 47.923468),
            'nb7': (-122.620341, 47.983403),
            'nb8': (-122.605158, 47.896722),
            'nb9': (-122.666187, 47.833808),
            'nb10': (-122.719706, 47.800428),
            'nb11': (-123.132905, 47.371157),
            'nb12': (-123.107573, 47.425875),
            'nb13': (-123.007577, 47.546858),
            'nb14': (-122.940392, 47.606550),
            'nb15': (-122.860076, 47.661459),
            'nb16': (-122.763730, 47.691309),
            'nb17': (-122.761501, 47.735374),
            'nb18': (-122.617107, 48.033422),
            'nb19': (-122.630732, 48.092559),
            'nb20': (-122.684716, 48.142632),
            'nb21': (-122.857502, 48.192594),
            'nb22': (-123.020134, 48.271261),
            'nb23': (-123.225046, 48.240944),
            'nb24': (-123.127674, 48.338261),
            'nb25': (-123.009646, 48.399957),
            'nb26': (-122.718451, 48.373715),
            'nb27': (-122.454556, 47.813703),
            'nb28': (-122.453217, 47.704475),
            'nb29': (-122.443363, 47.555799),
            'nb30': (-122.407443, 47.456332),
            'nb31': (-122.359581, 47.392952),
            'nb32': (-122.441613, 47.332982),
            'nb33': (-122.501045, 47.319672),
            'nb34': (-122.538671, 47.287076),
            'nb35': (-122.631933, 47.182935),
            'nb36': (-122.784580, 47.167546),
            'nb37': (-122.852711, 47.257702),
            'nb38': (-122.706422, 47.276766),
            'nb39': (-122.525976, 47.414724),
            'nb51': (-122.866800, 47.699300),
            'nb52': (-123.016200, 47.133620),
            'nb105': (-125.015600, 48.268900),
            'nb111': (-124.893900, 48.366700),
            'nb119': (-124.819992, 48.432808),
            'nb120': (-124.784668, 48.471330),
            'nb122': (-124.688200, 48.473400),
            'nb123': (-124.432894, 48.394849),
            'nb128': (-124.269032, 48.349003),
            'nb131': (-124.101707, 48.295260),
            'nb132': (-123.980702, 48.262285),
            'nb133': (-123.731108, 48.238315),
            'nb136': (-123.491922, 48.224020),
            'nb381': (-124.950117, 47.966728),
            'nb382': (-124.949600, 47.964765),
            'nb401': (-123.056612, 47.489942),
            'nb402': (-123.022725, 47.357173),
            'nb403': (-122.866800, 47.699300),
            'nb404': (-123.016300, 47.133700),
            'nb500': (-122.364835, 47.596734)
        }
        
    elif job_name == 'nina_short':
        sta_dict = {
            'nb4': (-122.554192, 48.241760),
            'nb7': (-122.620341, 47.983403),
            'nb8': (-122.605158, 47.896722),
            'nb12': (-123.107573, 47.425875),
            'nb22': (-123.020134, 48.271261),
            'nb28': (-122.453217, 47.704475),
            'nb38': (-122.706422, 47.276766),
            'nb123': (-124.432894, 48.394849),
            'nb132': (-123.980702, 48.262285),
            'nb136': (-123.491922, 48.224020),
            'nb381': (-124.950117, 47.966728),
            'nb402': (-123.022725, 47.357173),
        }
        
    elif job_name == 'nina_more':
        sta_dict = {
            'ANA': (-122.604745, 48.510059),
            'APS': (-122.581108, 47.701860),
            'COR': (-122.625143, 48.400322),
            'LOF': (-122.655995, 47.815366),
            'MCR': (-122.545308, 47.573770),
            'PTW': (-122.760792, 48.135760),
            'ROS': (-122.663325, 48.416618),
            'SQR': (-123.019722, 48.037076),
            'ZIT': (-122.808021, 47.165366),
        }
        
    elif job_name == 'orca_eb':
        # ORCA mooring locations, from Erin Broatch 2023.06.16
        sta_dict = {
        'CI': (-122.7300, 47.2800),
        'PW': (-122.3972, 47.7612),
        'NB': (-122.6270, 47.9073),
        'DB': (-122.8029, 47.8034),
        'HP': (-123.1126, 47.4218),
        'TW': (-123.0083, 47.3750)
        }
        
    else:
        print('Unsupported job name!')
        a = dict()
        return a
        
    return sta_dict