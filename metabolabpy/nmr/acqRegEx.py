"""
acqus regular expression class
"""

import re


class AcqRegEx:

    def __init__(self):
        self.sfo1 = re.compile(r'##\$SFO1= (\d+\.\d+)')
        self.sfo2 = re.compile(r'##\$SFO2= (\d+\.\d+)')
        self.sfo3 = re.compile(r'##\$SFO3= (\d+\.\d+)')
        self.sfo4 = re.compile(r'##\$SFO4= (\d+\.\d+)')
        self.sfo5 = re.compile(r'##\$SFO5= (\d+\.\d+)')
        self.sfo6 = re.compile(r'##\$SFO6= (\d+\.\d+)')
        self.sfo7 = re.compile(r'##\$SFO7= (\d+\.\d+)')
        self.sfo8 = re.compile(r'##\$SFO8= (\d+\.\d+)')
        self.bf1 = re.compile(r'##\$BF1= (\d+\.\d+)')
        self.bf2 = re.compile(r'##\$BF2= (\d+\.\d+)')
        self.bf3 = re.compile(r'##\$BF3= (\d+\.\d+)')
        self.bf4 = re.compile(r'##\$BF4= (\d+\.\d+)')
        self.bf5 = re.compile(r'##\$BF5= (\d+\.\d+)')
        self.bf6 = re.compile(r'##\$BF6= (\d+\.\d+)')
        self.bf7 = re.compile(r'##\$BF7= (\d+\.\d+)')
        self.bf8 = re.compile(r'##\$BF8= (\d+\.\d+)')
        self.o1 = re.compile(r'##\$O1= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o2 = re.compile(r'##\$O2= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o3 = re.compile(r'##\$O3= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o4 = re.compile(r'##\$O4= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o5 = re.compile(r'##\$O5= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o6 = re.compile(r'##\$O6= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o7 = re.compile(r'##\$O7= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.o8 = re.compile(r'##\$O8= (-?\d+\.?\d?\d?\d?\d?\d?\d?)')
        self.sw = re.compile(r'##\$SW= (\d+\.\d+)')
        self.sw_h = re.compile(r'##\$SW_h= (\d+\.?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?\d?)')
        self.td = re.compile(r'##\$TD= (\d+)')
        self.decim = re.compile(r'##\$DECIM= (\d+)')
        self.dspfvs = re.compile(r'##\$DSPFVS= (\d+)')
        self.grpdly = re.compile(r'##\$GRPDLY= (-?\d+(\.\d+)?)')
        self.byte_order = re.compile(r'##\$BYTORDA= (\d+)')
        self.aq_mode = re.compile(r'##\$AQ_mod= (\d+)')
        self.dig_mod = re.compile(r'##\$DIGMOD= (\d+)')
        self.transients = re.compile(r'##\$NS= (\d+)')
        self.steady_state_scans = re.compile(r'##\$DS= (\d+)')
        self.relaxation_delay = re.compile(r'##\$RD= (\d+\.?\d?)')
        self.spin_rate = re.compile(r'##\$MASR= (\d+)')
        self.pul_prog = re.compile(r'##\$PULPROG= (.+)')
        self.aunm = re.compile(r'##\$AUNM= (.+)')
        self.autopos = re.compile(r'##\$AUTOPOS= (.+)')
        self.nucleus = re.compile(r'##\$NUC\d= (.+)')
        self.nucleus_index = re.compile(r'##\$NUC(\d)=.+')
        self.instrument = re.compile(r'##\$INSTRUM= (.+)')
        self.data_type = re.compile(r'##\$DTYPA= (\d+)')
        self.solvent = re.compile(r'##\$SOLVENT= (.+)')
        self.probe = re.compile(r'##\$PROBHD= (.+)')
        self.title = re.compile(r'##TITLE= (.+), (.+)(\t)?(.+)')
        self.origin = re.compile(r'##ORIGIN= (.+)')
        self.owner = re.compile(r'##OWNER= (.+)')
        self.meta_info = re.compile(r'\$\$ (.+)')
        self.temperature = re.compile(r'##\$TE= (\d+\.?\d?)')
        self.cnst = re.compile(r'##\$CNST= \(\d+..\d+\)')
        self.delay = re.compile(r'##\$D= \(\d+..\d+\)')
        self.cpd_prog = re.compile(r'##\$CPDPRG= \(\d+..\d+\)')
        self.cpd_prog0 = re.compile(r'##\$CPDPRG= \(\d+..\d+\)')
        self.cpd_prog1 = re.compile(r'##\$CPDPRG1= \(\d+..\d+\)')
        self.cpd_prog2 = re.compile(r'##\$CPDPRG2= \(\d+..\d+\)')
        self.cpd_prog3 = re.compile(r'##\$CPDPRG3= \(\d+..\d+\)')
        self.cpd_prog4 = re.compile(r'##\$CPDPRG4= \(\d+..\d+\)')
        self.cpd_prog5 = re.compile(r'##\$CPDPRG5= \(\d+..\d+\)')
        self.cpd_prog6 = re.compile(r'##\$CPDPRG6= \(\d+..\d+\)')
        self.cpd_prog7 = re.compile(r'##\$CPDPRG7= \(\d+..\d+\)')
        self.cpd_prog8 = re.compile(r'##\$CPDPRG8= \(\d+..\d+\)')
        self.gp_name = re.compile(r'##\$GPNAM= \(\d+..\d+\)')
        self.gp_name0 = re.compile(r'##\$GPNAM0= \(\d+..\d+\)')
        self.gp_name1 = re.compile(r'##\$GPNAM1= \(\d+..\d+\)')
        self.gp_name2 = re.compile(r'##\$GPNAM2= \(\d+..\d+\)')
        self.gp_name3 = re.compile(r'##\$GPNAM3= \(\d+..\d+\)')
        self.gp_name4 = re.compile(r'##\$GPNAM4= \(\d+..\d+\)')
        self.gp_name5 = re.compile(r'##\$GPNAM5= \(\d+..\d+\)')
        self.gp_name6 = re.compile(r'##\$GPNAM6= \(\d+..\d+\)')
        self.gp_name7 = re.compile(r'##\$GPNAM7= \(\d+..\d+\)')
        self.gp_name8 = re.compile(r'##\$GPNAM8= \(\d+..\d+\)')
        self.gp_name9 = re.compile(r'##\$GPNAM9= \(\d+..\d+\)')
        self.gp_name10 = re.compile(r'##\$GPNAM10= \(\d+..\d+\)')
        self.gp_name11 = re.compile(r'##\$GPNAM11= \(\d+..\d+\)')
        self.gp_name12 = re.compile(r'##\$GPNAM12= \(\d+..\d+\)')
        self.gp_name13 = re.compile(r'##\$GPNAM13= \(\d+..\d+\)')
        self.gp_name14 = re.compile(r'##\$GPNAM14= \(\d+..\d+\)')
        self.gp_name15 = re.compile(r'##\$GPNAM15= \(\d+..\d+\)')
        self.gp_name16 = re.compile(r'##\$GPNAM16= \(\d+..\d+\)')
        self.gp_name17 = re.compile(r'##\$GPNAM17= \(\d+..\d+\)')
        self.gp_name18 = re.compile(r'##\$GPNAM18= \(\d+..\d+\)')
        self.gp_name19 = re.compile(r'##\$GPNAM19= \(\d+..\d+\)')
        self.gp_name20 = re.compile(r'##\$GPNAM20= \(\d+..\d+\)')
        self.gp_name21 = re.compile(r'##\$GPNAM21= \(\d+..\d+\)')
        self.gp_name22 = re.compile(r'##\$GPNAM22= \(\d+..\d+\)')
        self.gp_name23 = re.compile(r'##\$GPNAM23= \(\d+..\d+\)')
        self.gp_name24 = re.compile(r'##\$GPNAM24= \(\d+..\d+\)')
        self.gp_name25 = re.compile(r'##\$GPNAM25= \(\d+..\d+\)')
        self.gp_name26 = re.compile(r'##\$GPNAM26= \(\d+..\d+\)')
        self.gp_name27 = re.compile(r'##\$GPNAM27= \(\d+..\d+\)')
        self.gp_name28 = re.compile(r'##\$GPNAM28= \(\d+..\d+\)')
        self.gp_name29 = re.compile(r'##\$GPNAM29= \(\d+..\d+\)')
        self.gp_name30 = re.compile(r'##\$GPNAM30= \(\d+..\d+\)')
        self.gp_name31 = re.compile(r'##\$GPNAM31= \(\d+..\d+\)')
        self.gpx = re.compile(r'##\$GPX= \(\d+..\d+\)')
        self.gpy = re.compile(r'##\$GPY= \(\d+..\d+\)')
        self.gpz = re.compile(r'##\$GPZ= \(\d+..\d+\)')
        self.increments = re.compile(r'##\$IN= \(\d+..\d+\)')
        self.pulse = re.compile(r'##\$P= \(\d+..\d+\)')
        self.pcpd = re.compile(r'##\$PCPD= \(\d+..\d+\)')
        self.power_level = re.compile(r'##\$PL= \(\d+..\d+\)')
        self.power_level_watt = re.compile(r'##\$PLW= \(\d+..\d+\)')
        self.power_level_max = re.compile(r'##\$PLWMAX= \(\d+..\d+\)')
        self.shaped_power = re.compile(r'##\$SP= \(\d+..\d+\)')
        self.shaped_power_watt = re.compile(r'##\$SPW= \(\d+..\d+\)')
        self.spoal = re.compile(r'##\$SPOAL= \(\d+..\d+\)')
        self.spoffs = re.compile(r'##\$SPOFFS= \(\d+..\d+\)')
        self.vc_list = re.compile(r'##\$VCLIST= (.+)')
        self.vd_list = re.compile(r'##\$VDLIST= (.+)')
        self.vp_list = re.compile(r'##\$VPLIST= (.+)')
        self.va_list = re.compile(r'##\$VALIST= (.+)')
        self.vt_list = re.compile(r'##\$VTLIST= (.+)')
        self.nuc1 = re.compile(r'##\$NUC1= (.+)')
        self.nuc2 = re.compile(r'##\$NUC2= (.+)')
        self.nuc3 = re.compile(r'##\$NUC3= (.+)')
        self.nuc4 = re.compile(r'##\$NUC4= (.+)')
        self.nuc5 = re.compile(r'##\$NUC5= (.+)')
        self.nuc6 = re.compile(r'##\$NUC6= (.+)')
        self.nuc7 = re.compile(r'##\$NUC7= (.+)')
        self.nuc8 = re.compile(r'##\$NUC8= (.+)')
        self.nus_list = re.compile(r'##\$NUSLIST= (.+)')
        self.nus_amount = re.compile(r'##\$NusAMOUNT= (\d+)')
        self.nus_seed = re.compile(r'##\$NusSEED= (\d+)')
        self.nus_jsp = re.compile(r'##\$NusJSP= (\d+)')
        self.nus_t2 = re.compile(r'##\$NusT2= (\d+(\.\d+)?)')
        self.nus_td = re.compile(r'##\$NusTD= (\d+)')
        self.over_flow = re.compile(r'##\$OVERFLW= (\d+)')
        self.pynm = re.compile(r'##\$PYNM= (.+)')
        self.acq_t0 = re.compile(r'##\$ACQT0= (\d+)')
        self.fn_mode = re.compile(r'##\$FnMODE= (\d+)')
        self.inf = re.compile(r'##\$INF= \(\d+..\d+\)')
        # end __init__
