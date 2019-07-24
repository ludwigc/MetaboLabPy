'''
NMR spectrum display parameters
'''

from nmr import nmrConfig

class DispPars:
    
    def __init__(self):
        self.cf         = nmrConfig.NmrConfig()
        self.cf.readConfig()
        self.posCol     = "RGB"     #(r,g,b) or colour string (e.g. 'b')
        self.posColRGB  = (0,0,1)   
        self.negCol     = "RGB"     #(r,g,b) or colour string (e.g. 'r')
        self.phRefCol   = self.cf.phaseReferenceColour
        self.phRefDS    = 1
        self.phRefExp   = 1
        self.negColRGB  = (1,0,0)   
        self.nLevels    = 8         # integer1
        self.minLevel   = 0.01      # percentage of max
        self.maxLevel   = 0.1       # percentage of max
        self.axisType1  = 'ppm'     # 'ppm' / 'Hz'
        self.axisType2  = 'ppm'     # 'ppm' / 'Hz'
        self.displaySpc = False     # True / False (current spectrum is always plotted)
        self.spcOffset  = 0.0       # percentage of max (1D only)
        self.spcScale   = 1.0       # fold change (1D only)
        self.xLabel     = '1H'      # [axisType] added during plot
        self.yLabel     = '13C'     # [axisType] added during plot
        self.spcLabel   = ""        # spectrum title if not empty
        self.colours = {
            0             : "RGB",
            1             : "Red",
            2             : "Green",
            3             : "Blue",
            4             : "Black",
            5             : "Cyan",
            6             : "Magenta",
            7             : "Yellow",
            8             : "Gray",
            9             : "darkRed",
            10            : "darkGreen",
            11            : "darkBlue",
            12            : "darkCyan",
            13            : "darkMagenta",
            "RGB"         : 0,
            "Red"         : 1,
            "Green"       : 2,
            "Blue"        : 3,
            "Black"       : 4,
            "Cyan"        : 5,
            "Magenta"     : 6,
            "Yellow"      : 7,
            "Gray"        : 8,
            "darkRed"     : 9,
            "darkGreen"   : 10,
            "darkBlue"    : 11,
            "darkCyan"    : 12,
            "darkMagenta" : 13
        }
        self.colours2 = {
            0             : "Red",
            1             : "Green",
            2             : "Blue",
            3             : "Black",
            4             : "Cyan",
            5             : "Magenta",
            6             : "Yellow",
            7             : "Gray",
            8             : "darkRed",
            9             : "darkGreen",
            10            : "darkBlue",
            11            : "darkCyan",
            12            : "darkMagenta",
            "Red"         : 0,
            "Green"       : 1,
            "Blue"        : 2,
            "Black"       : 3,
            "Cyan"        : 4,
            "Magenta"     : 5,
            "Yellow"      : 6,
            "Gray"        : 7,
            "darkRed"     : 8,
            "darkGreen"   : 9,
            "darkBlue"    : 10,
            "darkCyan"    : 11,
            "darkMagenta" : 12
        }
        self.axes = {
            0      : "ppm",
            1      : "Hz",
            "ppm"  : 0,
            "Hz"   : 1
        }
        self.falseTrue = {
            0      : False,
            1      : True,
            False  : 0,
            True   : 1
        }
        # end __init__
        
    def __str__(self):
        return "Display parameters"
        # end __str__
