import numpy as np
# from metabolabpy.nmr import wdwf
from metabolabpy.nmr import acqPars
from metabolabpy.nmr import procPars
from metabolabpy.nmr import dispPars
import os
from scipy.fftpack import fft, ifft, fftshift
import math
import matplotlib.pyplot as pl
from scipy import signal
import time
from metabolabpy.nmr import nmrpipeData
from scipy import optimize
import scipy as sp
from metabolabpy.nmr import apcbc
import metabolabpy.__init__ as ml_version
from metabolabpy.nmr import nmrHsqc
from sklearn.decomposition import FastICA, PCA
from metabolabpy.nmr import hsqcData
import sys
from numba import jit
#from numba import vectorize
import multiprocessing as mp

try:
    import pygamma as pg
except:
    pass


class NmrData:
    projected_j_res: bool

    def __init__(self):
        self.fid = np.array([[]], dtype='complex')
        self.spc = np.array([[]], dtype='complex')
        self.ppm1 = np.array([], dtype='float64')
        self.ppm2 = np.array([], dtype='float64')
        self.ppm3 = np.array([], dtype='float64')
        self.start_peak = np.array([], dtype='float64')
        self.end_peak = np.array([], dtype='float64')
        self.start_peak_points = np.array([], dtype='int')
        self.end_peak_points = np.array([], dtype='int')
        self.peak_int = np.array([], dtype='float64')
        self.peak_max = np.array([], dtype='float64')
        self.peak_max_ppm = np.array([], dtype='float64')
        self.peak_max_points = np.array([], dtype='int')
        self.peak_label = np.array([], dtype='str')
        self.dim = 0
        self.title = np.array([], dtype='str')
        self.orig_data_set = str('')
        self.ph_corr_mode = 0
        self.acq = acqPars.AcqPars()
        self.proc = procPars.ProcPars()
        self.display = dispPars.DispPars()
        self.fid_offset_corr = 0
        self.data_set_name = ''
        self.data_set_number = ''
        self.title = str('Empty NMR data set')
        self.pulse_program = str('')
        self.window_function = {'none': 0, 'exponential': 1, 'gaussian': 2, 'sine': 3, 'qsine': 4, 'sem': 5}
        self.ref_shift = np.array([0, 0, 0], dtype='float64')
        self.ref_point = np.array([0, 0, 0], dtype='int')
        self.refsw = np.array([0, 0, 0], dtype='float64')
        self.ref_tmsp_range = 0.3  # [ppm]
        self.apc = apcbc.Apcbc()
        self.projected_j_res = False
        self.orig_j_res_set = -1
        self.orig_j_res_exp = -1
        self.pj_res_mode = ''
        self.j_res = False
        self.acqu = str('')
        self.acqu2 = str('')
        self.acqu3 = str('')
        self.audita_txt = str('')
        self.format_temp = str('')
        self.fq1list = str('')
        self.scon2 = str('')
        self.shimvalues = str('')
        self.uxnmr_par = str('')
        self.proc1 = str('')
        self.proc2 = str('')
        self.proc3 = str('')
        self.outd = str('')
        self.ver = ml_version.__version__
        self.hsqc = nmrHsqc.NmrHsqc()
        self.xsa = []
        self.ysa = []
        self.xst = []
        self.yst = []
        self.xss = []
        self.yss = []
        self.offset = 300.0
        self.assigned_text = []
        self.library_text = []
        self.metabolite_text = []
        self.fit_hsqc_again = False
        self.exclude_water = False
        self.delta_sw = 0.5
        if 'pygamma' in sys.modules:
            self.has_pg = True
        else:
            self.has_pg = False

        # end __init__

    def __str__(self):  # pragma: no cover
        r_string = '______________________________________________________________________________________\n'
        r_string += '\nMetaboLabPy NMR Data (v. ' + self.ver + ')\n'
        r_string += '______________________________________________________________________________________\n\n'
        r_string += self.title
        return r_string
        # end __str__

    def acq_pars(self):
        a = self.acq
        acq_str = "originalDataset      " + self.orig_data_set + "\n"
        acq_str += "___________________________________________________________________________________________________\n"
        acq_str += "\n"
        acq_str += "metaInfo             "
        for k in range(len(a.title)):
            acq_str += a.title[k] + " "

        acq_str += "\n                    "
        acq_str += " Origin\t" + a.origin + "\n                    "
        acq_str += " Owner\t" + a.owner + "\n"
        acq_str += "___________________________________________________________________________________________________\n"
        acq_str += "\n"
        acq_str += "probe                          " + a.probe + "\n"
        pp = a.pul_prog_name
        pp = pp[1:]
        pp = pp[:len(pp) - 1]
        acq_str += "pulseProgram                   " + pp + "\n\n"
        acq_str += "sw                   [ppm]    " + "% 9.2f" % a.sw[0] + "        |    % 9.2f" % a.sw[
            1] + "        |    % 9.2f\n" % a.sw[2]
        acq_str += "sw_h                 [Hz]     " + "% 9.2f" % a.sw_h[0] + "        |    % 9.2f" % a.sw_h[
            1] + "        |    % 9.2f\n" % a.sw_h[2]
        acq_str += "bf1/2/3              [MHz]    " + "% 9.2f" % a.bf1 + "        |    % 9.2f" % a.bf2 + "        |    % 9.2f\n" % a.bf3
        acq_str += "sfo1/2/3             [MHz]    " + "% 9.2f" % a.sfo1 + "        |    % 9.2f" % a.sfo2 + "        |    % 9.2f\n" % a.sfo3
        acq_str += "o1/2/3               [Hz]     " + "% 9.2f" % a.o1 + "        |    % 9.2f" % a.o2 + "        |    % 9.2f\n" % a.o3
        acq_str += "nPoints                       " + "% 6d" % a.n_data_points[0] + "           |    % 6d" % \
                   a.n_data_points[1] + "           |    % 6d\n" % a.n_data_points[2]
        acq_str += "transients                    " + "% 6d\n" % a.transients
        acq_str += "steadyStateScans              " + "% 6d\n\n" % a.steady_state_scans
        acq_str += "groupDelay           [us]     " + "% 9.2f\n" % a.group_delay
        acq_str += "decim                         " + "% 6d\n" % a.decim
        acq_str += "dspfvs                        " + "% 6d\n" % a.dspfvs
        acq_str += "temperature          [K]      " + "% 9.2f\n" % a.temperature
        print(acq_str)
        # end set_acq_pars

    def add_hsqc_peak(self, xdata=[], ydata=[]):
        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_picked[self.hsqc.cur_peak - 1].append(xdata)
        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1].append(ydata)
        for k in range(len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts'])):
            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts'][k][0] = \
                np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])

    # end add_hsqc_peak

    def add_peak(self, start_end=np.array([], dtype='float64'), peak_label=''):
        if len(start_end) > 0:
            start_peak = int(1e4 * self.points2ppm(self.ppm2points(max(start_end), 0), 0)) / 1e4
            end_peak = int(1e4 * self.points2ppm(self.ppm2points(min(start_end), 0), 0)) / 1e4
            start_peak_points = self.ppm2points(start_peak, 0)
            end_peak_points = self.ppm2points(end_peak, 0)
            self.start_peak = np.append(self.start_peak, start_peak)
            self.end_peak = np.append(self.end_peak, end_peak)
            self.start_peak_points = np.append(self.start_peak_points, start_peak_points)
            self.end_peak_points = np.append(self.end_peak_points, end_peak_points)
            self.peak_label = np.append(self.peak_label, peak_label)
            npts = len(self.spc[0])
            spc = self.spc[0][npts - start_peak_points:npts - end_peak_points].real
            max_pos = np.where(spc == np.max(spc))[0][0] + 1
            self.peak_max = np.append(self.peak_max, np.max(spc))
            self.peak_max_points = np.append(self.peak_max_points, start_peak_points - max_pos)
            self.peak_max_ppm = np.append(self.peak_max_ppm, self.points2ppm(start_peak_points - max_pos))
            self.peak_int = np.append(self.peak_int, sum(spc))  # - np.mean([spc[0], spc[-1]])))
            sort_idx = np.argsort(self.start_peak)[::-1]
            self.start_peak = self.start_peak[sort_idx]
            self.end_peak = self.end_peak[sort_idx]
            self.start_peak_points = self.start_peak_points[sort_idx]
            self.end_peak_points = self.end_peak_points[sort_idx]
            self.peak_label = self.peak_label[sort_idx]
            self.peak_max = self.peak_max[sort_idx]
            self.peak_max_points = self.peak_max_points[sort_idx]
            self.peak_max_ppm = self.peak_max_ppm[sort_idx]
            self.peak_int = self.peak_int[sort_idx]

        # end add_peak

    def set_peak(self, start_peak, end_peak, peak_label):
        self.start_peak = np.array([], dtype='float64')
        self.end_peak = np.array([], dtype='float64')
        self.peak_label = np.array([], dtype='str')
        self.start_peak_points = np.array([], dtype='int')
        self.end_peak_points = np.array([], dtype='int')
        self.peak_max = np.array([], dtype='float64')
        self.peak_max_ppm = np.array([], dtype='float64')
        self.peak_max_points = np.array([], dtype='int')
        self.peak_int = np.array([], dtype='float64')
        for k in range(len(start_peak)):
            self.add_peak(np.array([start_peak[k], end_peak[k]]), peak_label[k])

        # end set_peak

    def clear_peak(self):
        self.start_peak = np.array([], dtype='float64')
        self.end_peak = np.array([], dtype='float64')
        self.start_peak_points = np.array([], dtype='int')
        self.end_peak_points = np.array([], dtype='int')
        self.peak_label = np.array([], dtype='str')

        # end add_peak

    def add_tmsp(self, m0=1, r2=1):
        npts = len(self.spc[0])
        tsp_frq = 2 * math.pi * self.ref_point[0] / npts - math.pi
        t = np.linspace(0, npts - 1, npts);
        tsp_fid = m0 * np.exp(t * (1j * tsp_frq - r2));
        spc = fftshift(fft(tsp_fid));
        self.spc[0] += spc.real
        # end add_tmsp

    def apodise(self, fid, dim, lb, gb, ssb, group_delay, sw_h):
        fid = np.copy(fid)
        wdwf = np.zeros(len(fid))
        if self.proc.window_type[dim] == 0:  # no window
            wdwf = np.ones(len(fid))

        if self.proc.window_type[dim] == 1:  # exponential window
            t = (np.linspace(0.0, len(fid) - 1, len(fid)) - group_delay) / sw_h
            wdwf = np.exp(-lb * t)

        if self.proc.window_type[dim] == 2:  # gaussian window
            t = (np.linspace(0.0, len(fid) - 1 - group_delay, len(fid))) / sw_h
            wdwf = np.exp(-lb * 2 * math.pi * t - 2 * math.pi * (t ** 2) / ((2 * math.pi * gb * len(fid) / sw_h)))

        if self.proc.window_type[dim] == 3:  # sine window
            if self.acq.fn_mode == 1 or self.acq.fn_mode == 2:
                npts = int(min(self.acq.n_data_points[dim], len(fid)))
            else:
                npts = int(min(self.acq.n_data_points[dim] / 2, len(fid)))

            t = (np.linspace(0.0, npts - 1, npts)) / (npts - 1)
            wdwf = np.zeros(len(fid))
            ssb2 = ssb * math.pi / 180.0
            wdwf[:npts] = np.sin(ssb2 + (math.pi - ssb2) * t)

        if self.proc.window_type[dim] == 4:  # qsine window
            if self.acq.fn_mode == 1 or self.acq.fn_mode == 2:
                npts = int(min(self.acq.n_data_points[dim], len(fid)))
            else:
                npts = int(min(self.acq.n_data_points[dim] / 2, len(fid)))

            t = (np.linspace(0.0, npts - 1, npts)) / (npts - 1)
            wdwf = np.zeros(len(fid))
            ssb2 = ssb * math.pi / 180.0
            wdwf[:npts] = np.sin(ssb2 + (math.pi - ssb2) * t) ** 2

        if self.proc.window_type[dim] == 5:  # sem window
            if self.acq.fn_mode == 1 or self.acq.fn_mode == 2:
                npts = int(min(self.acq.n_data_points[dim], len(fid)))
            else:
                npts = int(min(self.acq.n_data_points[dim] / 2, len(fid)))

            t1 = (np.linspace(0.0, npts - 1 - group_delay, npts)) / sw_h
            t2 = (np.linspace(0.0, npts - 1, npts)) / (npts - 1)
            wdwf = np.zeros(len(fid))
            ssb2 = ssb * math.pi / 180.0
            wdwf[:npts] = np.exp(-lb * t1) * np.sin(ssb2 + (math.pi - ssb2) * t2)

        fid = np.copy(wdwf * fid)
        return fid
        # end apodise

    def autobaseline1d(self):
        spc = self.spc[0]
        self.apc.npts = len(spc)
        scale_fact = np.max(np.abs(spc))
        spc /= scale_fact
        xaxis = np.linspace(-self.apc.n_max, self.apc.n_max, self.apc.npts)
        par_eval = self.apc.fit_baseline(spc, xaxis)
        print("n_max: {}, par_eval: {}, xaxis: {}".format(self.apc.n_max, par_eval, xaxis))
        spc2 = self.apc.baseline_fit_func_eval(par_eval, spc, xaxis)  # , False)
        self.apc.pars = par_eval
        self.apc.r_spc = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.apc.i_spc = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.apc.r_spc[:int(len(par_eval) / 2)] = par_eval[:int(len(par_eval) / 2)]
        self.apc.i_spc[:int(len(par_eval) / 2)] = par_eval[int(len(par_eval) / 2):]
        self.spc[0] = spc2 * scale_fact
        self.apc.correct_baseline = 1
        self.proc_spc1d()
        self.baseline1d()
        # end autobaseline1d

    def autobaseline2d(self, poly_order=[16, 16], threshold=0.05):
        mat = np.copy(self.spc.real)
        for k in range(len(mat)):
            spc = np.copy(mat[k])
            xaxis = np.linspace(-10, 10, len(spc))
            spc[np.where(np.abs(spc) > threshold*np.max(np.abs(spc)))] = 0
            poly_bas = np.polynomial.polynomial.Polynomial.fit(xaxis, spc, poly_order[0])
            mat[k] -= poly_bas(xaxis)

        mat = np.ndarray.transpose(mat)
        for k in range(len(mat)):
            spc = np.copy(mat[k])
            xaxis = np.linspace(-10, 10, len(spc))
            spc[np.where(np.abs(spc) > threshold*np.max(np.abs(spc)))] = 0
            poly_bas = np.polynomial.polynomial.Polynomial.fit(xaxis, spc, poly_order[1])
            mat[k] -= poly_bas(xaxis)

        mat = np.ndarray.transpose(mat)
        self.spc = np.copy(mat)
        return 1.0
        # end autobaseline2d

    def autophase1d(self, gamma_factor=1.0):
        self.proc.ph0[0] = 0
        self.proc.ph1[0] = 0
        self.proc_spc1d()
        fit_parameters = [0.0, 0.0]
        spc = np.copy(self.spc[0])
        eval_parameters = optimize.minimize(self.autophase1d_fct, fit_parameters, method='Powell')
        e_pars = np.array(eval_parameters.x).tolist()
        self.proc.ph0[0] = e_pars[0]
        self.proc.ph1[0] = e_pars[1]
        self.proc_spc1d()
        # end autophase1d

    def autophase1d_exclude_water(self, delta_sw=-1):
        self.exclude_water = True
        if delta_sw > 0.0:
            self.delta_sw = delta_sw
        # end autophase1d_exclude_water

    def autophase1d_fct(self, fit_parameters):
        # implementation based on entropy minimization developed by Chen et al. JMR, 158 (2002) 164-168
        spc = np.copy(self.spc[0])
        npts = len(spc)
        sw = self.acq.sw[0]
        start_pts = int(npts/2 - npts * self.delta_sw / sw)
        end_pts = int(npts/2 + npts * self.delta_sw / sw)
        x_axis = range(npts)
        ph0 = fit_parameters[0]
        ph1 = fit_parameters[1]
        spc = np.copy(self.phase3(spc, ph0, ph1))
        spc_1 = np.copy(np.gradient(spc.real))
        gamma = 1.0 / np.sum(np.abs(spc.real))
        h_i = np.abs(spc_1.real) / np.sum(np.abs(spc_1.real))
        if self.exclude_water == True:
            penalty = 0
            penalty += gamma * np.sum((1 - np.heaviside(spc.real[:start_pts], 1)) * spc.real[:start_pts] ** 2)
            penalty += gamma * np.sum((1 - np.heaviside(spc.real[end_pts:], 1)) * spc.real[end_pts:] ** 2)
            entropy = 0  # penalty
            entropy -= np.sum(h_i[:start_pts] * np.log(h_i[:start_pts]))
            entropy -= np.sum(h_i[end_pts:] * np.log(h_i[end_pts:]))
        else:
            penalty = gamma * np.sum((1 - np.heaviside(spc.real, 1)) * spc.real ** 2)
            entropy = -np.sum(h_i * np.log(h_i))

        return penalty - entropy
        # end autophase1d_fct

    def autophase1d_include_water(self):
        self.exclude_water = False
        # end autophase1d_exclude_water

    def autophase1d1(self):
        spc = self.spc[0]
        self.apc.npts = len(spc)
        scale_fact = np.max(np.abs(spc))
        spc /= scale_fact
        xaxis = np.linspace(-self.apc.n_max, self.apc.n_max, self.apc.npts)
        par_eval = self.apc.fit_phase(spc, xaxis)
        spc2 = self.apc.phase_fit_func_eval(par_eval, spc, xaxis)  # , False)
        if (np.min(spc2.real) == -np.max(np.abs(spc2.real))):
            par_eval[0] = ((par_eval[0] * self.apc.m_fact0 + 180.0) % 360) / self.apc.m_fact0

        par_eval[0] = (((par_eval[0] * self.apc.m_fact0 + 180.0) % 360) - 180.0) / self.apc.m_fact0
        spc2 = self.apc.phase_fit_func_eval(par_eval, spc, xaxis)  # , False)
        self.apc.pars = par_eval
        self.apc.r_spc = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.apc.i_spc = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.apc.r_spc[:int((len(par_eval) - 2) / 2)] = par_eval[2:2 + int((len(par_eval) - 2) / 2)]
        self.apc.i_spc[:int((len(par_eval) - 2) / 2)] = par_eval[2 + int((len(par_eval) - 2) / 2):]
        self.spc[0] = spc2 * scale_fact
        self.proc.ph0[0] += par_eval[0] * self.apc.m_fact0
        self.proc.ph1[0] += par_eval[1] * self.apc.m_fact1
        self.apc.correct_baseline = 1
        self.auto_ref()
        self.proc_spc1d()
        self.baseline1d()
        # end autophase1d1

    def autopick_hsqc(self, metabolite_list=[]):
        if len(metabolite_list) == 0:
            metabolite_list = [self.hsqc.cur_metabolite]

        # set basic variables
        range_h = self.hsqc.autopick_range_h
        range_c = self.hsqc.autopick_range_c
        for m in metabolite_list:
            cur_peak = 1
            metabolite_name = m
            self.hsqc.hsqc_data[metabolite_name] = hsqcData.HsqcData()  # empty hsqc_data for chosen metabolite
            self.hsqc.read_metabolite_information(metabolite_name)
            self.hsqc.hsqc_data[metabolite_name].init_data(self.hsqc.metabolite_information)
            self.hsqc.cur_metabolite = metabolite_name
            self.hsqc.read_metabolite_information(metabolite_name)
            self.hsqc.set_metabolite_information(metabolite_name, self.hsqc.metabolite_information)
            self.hsqc.cur_peak = cur_peak
            self.hsqc.set_peak_information()
            for kk in range(len(self.hsqc.hsqc_data[metabolite_name].h1_shifts)):
                cur_peak = kk + 1
                self.hsqc.cur_peak = cur_peak
                self.hsqc.set_metabolite_information(metabolite_name, self.hsqc.metabolite_information)
                self.hsqc.set_peak_information()
                self.hsqc.hsqc_data[metabolite_name].c13_picked[cur_peak - 1] = \
                    self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['c13_shifts'][0]
                # 24.24, 30.30, 30.30, 15.15% contribution for multiplet components
                cont = np.copy(self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['contribution'])
                if len(cont) > 2:
                    cnt = np.array([80, 100, 100, 50])  # [100, 50, 50, 25])
                else:
                    cnt = np.array([100, 100])

                cnt = np.copy(cnt[range(len(cont))])
                cnt = cnt / np.sum(cnt)
                cnt *= 100
                self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['contribution'] = cnt
                # sim 1d 13C spectrum in library shift position
                self.sim_hsqc_1d()
                # determine spectral area to be used
                hd = self.hsqc.hsqc_data[metabolite_name]
                h1_centre = hd.h1_shifts[cur_peak - 1]
                c13_centre = hd.c13_shifts[hd.h1_index[cur_peak - 1] - 1]
                h1_suffix = hd.h1_suffix[cur_peak - 1]
                scale = self.hsqc.j_scale
                hsqc_idx = np.where(hd.hsqc == 1)[0]
                h1_index = hd.h1_index[cur_peak - 1]
                c13_index = hd.c13_index[hd.h1_index[cur_peak - 1] - 1]
                h1_beg = h1_centre + range_h
                h1_end = h1_centre - range_h
                c13_beg = c13_centre + range_c * scale
                c13_end = c13_centre - range_c * scale
                h1_pts = len(self.spc[0])
                c13_pts = len(self.spc)
                h1_pts1 = h1_pts - self.ppm2points(h1_beg, 0) - 1
                h1_pts2 = h1_pts - self.ppm2points(h1_end, 0) - 1
                c13_pts1 = c13_pts - self.ppm2points(c13_beg, 1) - 1
                c13_pts2 = c13_pts - self.ppm2points(c13_end, 1) - 1
                spc = self.spc[c13_pts1:c13_pts2, h1_pts1:h1_pts2].real
                c13_centre_pts = round(np.median(np.linspace(c13_pts1, c13_pts2, c13_pts2 - c13_pts1 + 1, dtype=int)))
                h1_centre_pts = round(np.median(np.linspace(h1_pts1, h1_pts2, h1_pts2 - h1_pts1 + 1, dtype=int)))
                # set FastICA parameters, execute ICA and get estimated mixing matrix (A_)
                n_comp = 9
                ica = FastICA(n_components=n_comp, algorithm='deflation', whiten='arbitrary-variance',
                              fun=self.my_g)
                S_ = ica.fit_transform(np.transpose(spc / np.max(spc)))  # Reconstruct signals
                A_ = ica.mixing_
                ica = np.transpose(A_)
                data = np.transpose(spc / np.max(spc))
                spc2 = self.hsqc.hsqc_data[metabolite_name].sim_spc[cur_peak - 1][c13_pts1:c13_pts2]
                spc2 /= np.linalg.norm(spc2)
                ppp = len(self.spc) / self.acq.sw[1]
                max_shift = int(len(spc2) / 2) - 1
                #max_shift = min(int(ppp * self.hsqc.range_c), int(len(spc2) / 2) - 1)
                #print("max_shift[13C]: {}, {} | ppp: {}".format(max_shift,int(len(spc2) / 2) - 1, ppp))
                corr2 = np.zeros((len(ica), 2 * max_shift + 1))
                shift2 = np.zeros((len(ica), 2 * max_shift + 1), dtype=int)
                corr_max = np.zeros(len(ica))
                idx_max = np.zeros(len(ica), dtype=int)
                shift_max = np.zeros(len(ica), dtype=int)
                for l in range(len(ica)):
                    for k in range(2 * max_shift + 1):
                        corr2[l][k] = np.corrcoef(ica[l], np.roll(spc2, k - max_shift))[0][1] / np.std(spc2)
                        shift2[l][k] = int(k - max_shift)

                    idx_max[l] = int(np.where(corr2[l] == np.max(corr2[l]))[0][0])
                    corr_max[l] = np.max(corr2[l])
                    shift_max[l] = shift2[l][idx_max[l]]

                spc2_idx = np.where(corr_max == np.max(corr_max))[0][0]
                spc3 = np.roll(spc2, shift_max[spc2_idx])
                # correlate 13C shifted, simulated spectrum across different 1H shift area
                corr3 = np.zeros(len(data))
                mid_point = int(len(data) / 2)
                #ppp = len(self.spc[0]) / self.acq.sw[0]
                #max_shift = min(int(ppp * self.hsqc.range_h), int(len(data) / 2) - 1)
                #print("max_shift[ 1H]: {}, {}".format(max_shift,int(len(data) / 2) - 1))
                #for l in range(mid_point - max_shift, mid_point + max_shift + 1):  # range(len(data)):
                for l in range(len(data)):
                        corr3[l] = np.corrcoef(data[l], spc3)[0][1] * np.max(data[l])
                    #print("weight: {}, corr3[l]: {}, corr3[l] * np.max(data[l]) / np.max(data): {}".format(np.max(data[l]) / np.max(data), corr3[l], corr3[l] * np.max(data[l]) / np.max(data)))

                #max_idx3 = np.where(corr3 == np.max(corr3))[0][0]
                #for l in range(len(data)):
                #    corr3[l] *= data[l][max_idx3] / np.max(data)
                #
                max_idx3 = np.where(corr3 == np.max(corr3))[0][0]
                h1_pts_f = h1_pts1 + max_idx3 - 1
                c13_pts_f = c13_pts1 + max_shift + shift_max[spc2_idx] + 1
                h1_shift = self.points2ppm(len(self.spc[0]) - h1_pts_f, 0)
                c13_shift = self.points2ppm(len(self.spc) - c13_pts_f, 1)
                local_opt = self.pick_local_opt([h1_shift, c13_shift])
                self.hsqc.hsqc_data[metabolite_name].c13_picked[cur_peak - 1] = [local_opt[1]]
                self.hsqc.hsqc_data[metabolite_name].h1_picked[cur_peak - 1] = [local_opt[0]]
                cont = np.copy(self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['contribution'])
                self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['contribution'] = np.zeros(len(cont))
                self.hsqc.hsqc_data[metabolite_name].spin_systems[cur_peak - 1]['contribution'][0] = 100
                self.hsqc.hsqc_data[metabolite_name].sim_spc[cur_peak - 1] = []

        # end autopick_hsqc

    def auto_ref(self, tmsp=True):
        if self.acq.o1 == 0:
            self.ref_shift[0] = 4.76
        else:
            self.ref_shift[0] = self.acq.o1 / self.acq.bf1

        self.ref_point[0] = int(len(self.spc[0]) / 2)
        if (self.dim == 2):
            self.ref_shift[1] = (self.acq.spc_frequency[1] + self.acq.spc_offset[1]) / self.acq.spc_frequency[1] - 1.0
            self.ref_point[1] = int(len(self.spc) / 2)
            if (tmsp == True):
                self.ref_point[0] = self.ppm2points(0.0, 0)
                self.ref_shift[0] = 0.0
                pts = self.ppm2points(np.array([-self.ref_tmsp_range, self.ref_tmsp_range]), 0)
                npts = len(self.spc[0])
                r = np.arange(npts - max(pts), npts - min(pts))
                spc = np.sum(self.spc, 0)
                spc = spc[r].real
                ref_p = np.where(spc == np.amax(spc))
                self.ref_point[0] -= ref_p[0][0] - int((max(pts) - min(pts)) / 2) + 1

            self.proc.ref_point[0] = self.ref_point[0]
            self.proc.ref_point[1] = self.ref_point[1]

        if (self.dim == 1):
            if (tmsp == True):
                self.ref_point[0] = self.ppm2points(0.0, 0)
                self.ref_shift[0] = 0.0
                pts = self.ppm2points(np.array([-self.ref_tmsp_range, self.ref_tmsp_range]), 0)
                npts = len(self.spc[0])
                r = np.arange(npts - max(pts), npts - min(pts))
                r = np.copy(r[np.where(r < len(self.spc[0]))])
                spc = self.spc[0][r].real
                ref_p = np.where(spc == np.amax(spc))
                self.ref_point[0] -= ref_p[0][0] - int((max(pts) - min(pts)) / 2) + 1

        self.calc_ppm()

        # end auto_ref

    def baseline1d(self):
        spc = self.spc[0]
        self.apc.npts = len(spc)
        # scale_fact         = np.max(np.abs(spc))
        # spc              /= scale_fact
        xaxis = np.linspace(-self.apc.n_max, self.apc.n_max, self.apc.npts)
        par_eval = np.copy(self.apc.r_spc)
        par_eval = np.append(par_eval, self.apc.i_spc)
        # print(par_eval)
        spc2 = self.apc.baseline_fit_func_eval(par_eval, spc, xaxis)  # , False)
        self.spc[0] = spc2  # *scale_fact
        # end baseline1d

    def calc_ppm(self):
        if self.proc.strip_start == 0:
            stsr = 1
        else:
            stsr = self.proc.strip_start

        if self.proc.strip_end > stsr:
            stsi = self.proc.strip_end
        else:
            stsi = int(len(self.spc[0]))

        if (self.display.axis_type1 == 'ppm'):
            self.ppm1 = self.points2ppm(np.linspace(self.proc.n_points[0] - 1, 0, self.proc.n_points[0]), 0)
        else:
            self.ppm1 = self.points2hz(np.linspace(self.proc.n_points[0] - 1, 0, self.proc.n_points[0]), 0)

        self.ppm1 = self.ppm1[stsr - 1:stsi]

        if (self.dim > 1):
            npts = int(len(self.spc))
            if (self.display.axis_type2 == 'ppm'):
                self.ppm2 = self.points2ppm(np.linspace(npts - 1, 0, npts), 1)
            else:
                self.ppm2 = self.points2hz(np.linspace(npts - 1, 0, npts), 1)

        # end calc_ppm

    def conv(self, fid):
        f1 = np.copy(fid)
        x = np.linspace(0, len(fid) - 1, len(fid))
        f0 = np.copy(fid)
        filt_fid = fid[list(range(round(self.acq.group_delay)))]
        fid = fid[list(range(round(self.acq.group_delay), len(fid)))]
        ws2 = int(self.proc.conv_window_size[0] / 2)
        es = self.proc.conv_extrapolation_size[0]
        wt = int(self.proc.conv_window_type[0])
        win = np.zeros(int(ws2 * 2 + 1))
        s_win = 0
        for k in range(int(ws2 * 2 + 1)):
            if (wt == 0):  # Gaussian window
                win[k] = math.exp(-4.0 * ((k - ws2) ** 2) / (ws2 ** 2))
                s_win += win[k]
            else:  # sine bell window
                win[k] = math.cos((math.pi * (k - ws2)) / (2 * ws2 + 2))
                s_win += win[k]

        fid2 = np.convolve(win, fid) / s_win
        # Extrapolation of first sw2 data points
        idx = np.linspace(2 * ws2 - 1, 0, 2 * ws2, dtype='int')
        idx2 = np.linspace(0, 2 * ws2 - 1, 2 * ws2, dtype='int')
        fid2[idx2].real = fid2[int(2 * ws2)].real + np.mean(np.diff(fid2[idx + int(2 * ws2) - 1].real)) * idx
        fid2[idx2].imag = fid2[int(2 * ws2)].imag + np.mean(np.diff(fid2[idx + int(2 * ws2) - 1].imag)) * idx
        # Extrapolation of last sw2 data points
        idx = np.linspace(0, 2 * ws2 - 1, 2 * ws2, dtype='int')
        idx2 = np.linspace(len(fid) - int(2 * ws2) - 1, len(fid) - 1, int(2 * ws2), dtype='int')
        fid2[idx2].real = fid2[len(fid) - int(2 * ws2) - 1].real - np.mean(
            np.diff(fid2[len(fid) - int(2 * ws2) - 1 - idx].real)) * idx
        fid2[idx2].imag = fid2[len(fid) - int(2 * ws2) - 1].imag - np.mean(
            np.diff(fid2[len(fid) - int(2 * ws2) - 1 - idx].imag)) * idx
        fid2 = np.delete(fid2, np.linspace(0, 2 * ws2 - 1, 2 * ws2, dtype='int'))
        fid -= fid2  # (fidRe + 1j*fidIm)
        fid = np.concatenate([filt_fid, fid])
        return fid
        # end conv

    def export_bruker_1d(self, path_name, exp_name, scale_factor=-1):
        if self.acq.manufacturer != 'Bruker':
            return

        if os.path.isdir(path_name + os.sep + exp_name) is False:
            os.makedirs(path_name + os.sep + exp_name)

        if os.path.isdir(path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1') is False:
            os.makedirs(path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1')

        fid_file1 = path_name + os.sep + exp_name + os.sep + 'fid'
        spc_file1r = path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1' + os.sep + '1r'
        # write 1D FID file
        fid = np.zeros(2 * len(self.fid[0]))
        fid[0::2] = self.fid[0].real
        fid[1::2] = self.fid[0].imag
        if self.acq.byte_order == 1:
            fid.astype('>i4').tofile(fid_file1)
        else:
            if self.acq.data_type == 0:
                fid.astype('<i4').tofile(fid_file1)
            else:
                if self.acq.data_type == 1:
                    fid.astype(np.float64).tofile(fid_file1)
                else:
                    fid.astype(np.float32).tofile(fid_file1)

        # write 1r file
        spc = self.spc[0].real
        if scale_factor == -1:
            scale_factor = 2 * np.max(spc) / 2147483647

        spc /= scale_factor
        spc.real.astype(np.int32).tofile(spc_file1r)
        # write parameter files
        # acqu file
        f_name = path_name + os.sep + exp_name + os.sep + 'acqu'
        f = open(f_name, 'w')
        f.write(self.acq.acqus_text)
        f.close()
        # acqus file
        f_name = path_name + os.sep + exp_name + os.sep + 'acqus'
        f = open(f_name, 'w')
        f.write(self.acq.acqus_text)
        f.close()
        # pulse_program file
        f_name = path_name + os.sep + exp_name + os.sep + 'pulse_program'
        f = open(f_name, 'w')
        f.write(self.pulse_program)
        f.close()
        # audita.txt file
        f_name = path_name + os.sep + exp_name + os.sep + 'audita.txt'
        f = open(f_name, 'w')
        f.write(self.audita_txt)
        f.close()
        # format.temp file
        f_name = path_name + os.sep + exp_name + os.sep + 'format.temp'
        f = open(f_name, 'w')
        f.write(self.format_temp)
        f.close()
        # fq1list file
        f_name = path_name + os.sep + exp_name + os.sep + 'fq1list'
        f = open(f_name, 'w')
        f.write(self.fq1list)
        f.close()
        # scon2 file
        f_name = path_name + os.sep + exp_name + os.sep + 'scon2'
        f = open(f_name, 'w')
        f.write(self.scon2)
        f.close()
        # shimvalues file
        f_name = path_name + os.sep + exp_name + os.sep + 'shimvalues'
        f = open(f_name, 'w')
        f.write(self.shimvalues)
        f.close()
        # uxnmr.par file
        f_name = path_name + os.sep + exp_name + os.sep + 'uxnmr.par'
        f = open(f_name, 'w')
        f.write(self.uxnmr_par)
        f.close()
        # procs file
        orig_si = self.proc.reg_ex.si.findall(self.proc.procs_text)[0]
        ft_mod = int(self.proc.reg_ex.ft_mod.findall(self.proc.procs_text)[0])
        nc_proc = int(self.proc.reg_ex.nc_proc.findall(self.proc.procs_text)[0])
        procs_text = self.proc.procs_text.replace(orig_si, str(len(self.spc[0])))
        procs_text = procs_text.replace('FT_mod= ' + str(ft_mod), 'FT_mod= 6')
        procs_text = procs_text.replace('NC_proc= ' + str(nc_proc), 'NC_proc= 0')
        f_name = path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1' + os.sep + 'procs'
        f = open(f_name, 'w')
        f.write(procs_text)
        f.close()
        # proc file
        f_name = path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1' + os.sep + 'proc'
        f = open(f_name, 'w')
        f.write(procs_text)
        f.close()
        # outd file
        f_name = path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1' + os.sep + 'outd'
        f = open(f_name, 'w')
        f.write(self.outd)
        f.close()
        # title file
        f_name = path_name + os.sep + exp_name + os.sep + 'pdata' + os.sep + '1' + os.sep + 'title'
        f = open(f_name, 'w')
        f.write(self.title)
        f.close()
        # end export_bruker_1d

    def fid_offset_correction(self, fid):
        fid = np.copy(fid)
        if (self.fid_offset_corr > 0):
            m_mean = np.mean(fid[:self.fid_offset_corr])
            fid -= m_mean

        return fid
        # end fid_offset_correction

    def gibbs(self, fid):
        if (self.proc.gibbs[0] == True):
            fid[0] /= 2.0

        return fid
        # end gibbs

    def hilbert(self, mat, dim=0):
        if (dim == 1):
            mat = np.ndarray.transpose(mat)

        npts = len(mat[0])
        npts1 = len(mat)
        v1 = np.ones(npts1)
        mat1 = np.array([[]], dtype='complex')
        mat1 = np.resize(mat1, (npts1, npts))
        b_mat = np.zeros(int(2 * npts), dtype='complex')
        b_mat[:(npts + 1)] = np.ones(npts + 1)
        b_mat[1:npts] += b_mat[1:npts]
        z_mat = np.zeros(int(2 * npts), dtype='complex')
        b_mat = np.outer(v1, b_mat)
        z_mat = np.outer(v1, z_mat)
        z_mat[:, :npts] = mat
        z_mat = np.fft.ifft(b_mat * np.fft.fft(z_mat))
        mat = z_mat[:, :npts]
        if (dim == 1):
            mat = np.ndarray.transpose(mat)

        return mat
        # end hilbert

    def hilbert1(self, mat, dim):
        if (self.dim == 1):
            npts = len(mat)
            b_mat = np.zeros(int(2 * npts), dtype='complex')
            z_mat = np.zeros(int(2 * npts), dtype='complex')
            z_mat[:int(len(mat))] = mat
            b_mat[:(npts + 1)] = np.ones(npts + 1)
            b_mat[1:npts] += b_mat[1:npts]
            mat2 = np.zeros(2 * npts, dtype='complex')
            mat2[:len(mat)] = mat
            mat2 = ifft(b_mat * fft(mat2))
            mat1 = np.copy(mat2[:len(mat)])

        if (self.dim == 2):
            if (dim == 1):
                mat = np.ndarray.transpose(mat)

            npts = len(mat[0])
            npts1 = len(mat)
            mat1 = np.array([[]], dtype='complex')
            mat1 = np.resize(mat1, (npts1, npts))
            for k in range(len(mat)):
                b_mat = np.zeros(int(2 * npts), dtype='complex')
                z_mat = np.zeros(int(2 * npts), dtype='complex')
                z_mat[:int(len(mat[k]))] = mat[k]
                b_mat[:(npts + 1)] = np.ones(npts + 1)
                b_mat[1:npts] += b_mat[1:npts]
                mat2 = np.zeros(2 * npts, dtype='complex')
                mat2[:len(mat[k])] = mat[k]
                mat2 = ifft(b_mat * fft(mat2))
                mat1[k] = mat2[:len(mat[k])]

            if (dim == 1):
                mat1 = np.ndarray.transpose(mat1)

        return mat1
        # end hilbert1

    def make_hsqc_spin_sys(self, c13_offset, idx=0):
        c13_nc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_nc']
        c13_idx = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_idx']
        chem_shift = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts']
        if len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1]) > 0:
            for k in range(len(c13_idx)):
                chem_shift[k][0] = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak \
                                    - 1]) + c13_offset[k] / 1000.0

        j_cc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['j_cc']
        sys = pg.spin_system(sum(c13_nc[idx]))
        sys.Omega(self.acq.sfo2)
        for k in range(len(c13_nc[idx])):
            #print('chem_shift[idx][k]: {}'.format(chem_shift[idx][k]))
            sys.PPM(k, chem_shift[idx][k])

        for k in range(len(j_cc[idx])):
            sys.J(0, k + 1, j_cc[idx][k])

        return sys
        # end make_spin_sys

    def multiply(self, factor=1.0):
        self.spc = factor * self.spc

    def my_g(self, x):
        # define custom G function used in the approximation to neg entropy
        # used in independent component analysis
        return x ** 2, 2 * x
        # end my_g

    def phase(self, ph0, ph1, npts):
        ph0 = -ph0 * math.pi / 180.0
        ph1 = -ph1 * math.pi / 180.0
        t = complex()
        frac = np.linspace(0, 1, npts)
        ph = ph0 + frac * ph1
        self.spc[0] = np.cos(ph) * self.spc[0].real + np.sin(ph) * self.spc[0].imag + 1j * (
                -np.sin(ph) * self.spc[0].real + np.cos(ph) * self.spc[0].imag)
        # end phase

    def phase2(self, mat, ph0, ph1):
        npts = len(mat)
        ph0 = -ph0 * math.pi / 180.0
        ph1 = -ph1 * math.pi / 180.0
        t = complex()
        frac = np.linspace(0, 1, npts)
        ph = ph0 + frac * ph1
        mat = np.cos(ph) * mat.real + np.sin(ph) * mat.imag + 1j * (-np.sin(ph) * mat.real + np.cos(ph) * mat.imag)
        return mat
        # end phase2

    def phase2a(self, ph0, ph1, dim=0):
        mat = np.copy(self.spc.real)
        mat = self.hilbert(mat, dim)
        if dim == 1:
            mat = np.ndarray.transpose(mat)

        npts = len(mat[0])
        npts1 = len(mat)
        v1 = np.ones(npts1)
        ph0 = -ph0 * math.pi / 180.0
        ph1 = -ph1 * math.pi / 180.0
        frac = np.outer(v1, np.linspace(0, 1, npts))
        ph = ph0 + frac * ph1
        mat = np.cos(ph) * mat.real + np.sin(ph) * mat.imag + 1j * (-np.sin(ph) * mat.real + np.cos(ph) * mat.imag)
        if dim == 1:
            mat = np.ndarray.transpose(mat)

        self.spc = np.copy(mat.real)
        # end phase2a

    def phase2d(self, ph0, ph1, dim):
        mat = self.hilbert1(self.spc, dim)
        if dim == 1:
            mat = np.ndarray.transpose(mat)

        npts = len(mat)
        for k in range(npts):
            mat[k] = self.phase2(mat[k], ph0, ph1)

        if dim == 1:
            mat = np.ndarray.transpose(mat)

        self.spc = np.copy(mat.real)
        # end phase2d

    @jit
    def phase3(self, mat, ph0, ph1):
        npts = len(mat)
        ph0 = -ph0 * math.pi / 180.0
        ph1 = -ph1 * math.pi / 180.0
        t = complex()
        for k in range(int(npts)):
            frac = float(k) / float(npts)
            ph = ph0 + frac * ph1
            t = complex(math.cos(ph) * mat[k].real + math.sin(ph) * mat[k].imag,
                        -math.sin(ph) * mat[k].real + math.cos(ph) * mat[k].imag)
            mat[k] = t

        return mat
        # end phase3

    def pick_local_opt(self, start=[0, 0]):
        start_h1 = len(self.spc[0]) - self.ppm2points(start[0], 0) - 1
        start_c13 = len(self.spc) - self.ppm2points(start[1], 1) - 1
        check_matrix = np.array([[[1, 1], [0, 1], [-1, 1]], [[1, 0], [0, 0], [-1, 0]], [[1, -1], [0, -1], [-1, -1]]])
        local_spc = np.array([[]])
        local_spc.resize(3, 3)
        for k in range(3):
            for l in range(3):
                local_spc[k][l] = self.spc[start_c13 + check_matrix[k][l][0]][start_h1 + check_matrix[k][l][1]].real

        max_pos = np.where(local_spc == local_spc.max())
        while check_matrix[max_pos][0][0] != 0 or check_matrix[max_pos][0][1] != 0:
            start_h1 += check_matrix[max_pos][0][1]
            start_c13 += check_matrix[max_pos][0][0]
            for k in range(3):
                for l in range(3):
                    local_spc[k][l] = self.spc[start_c13 + check_matrix[k][l][0]][start_h1 + check_matrix[k][l][1]].real

            max_pos = np.where(local_spc == local_spc.max())

        start_h1 = self.points2ppm(len(self.spc[0]) - start_h1 - 1, 0)
        start_c13 = self.points2ppm(len(self.spc) - start_c13 - 1, 1)
        return [start_h1, start_c13]
        # end pick_local_opt

    def points2hz(self, points, dim=0):
        sw = self.acq.sw_h[dim]
        if dim == 0:
            npts = int(len(self.spc[0]))

        if dim == 1:
            npts = int(len(self.spc))

        hz = sw * (points - npts / 2) / npts
        return hz
        # end points2hz

    def points2ppm(self, points, dim=0):
        sw = self.acq.sw_h[dim]
        if dim == 0:
            sfo = self.acq.sfo1
            npts = self.proc.n_points[0]  # int(len(self.spc[0]))

        if dim == 1:
            if self.acq.manufacturer == 'Bruker':
                sfo = self.proc.sf[1]
                if sfo == 0.0:
                    sfo = self.acq.sfo2

            else:
                sfo = self.acq.sfo2

            npts = int(len(self.spc))

        ppm = (sw / sfo) * (points / (npts - 1) - self.ref_point[dim] / (npts - 1)) + self.ref_shift[dim]
        return ppm
        # end points2ppm

    def ppm2points(self, ppm, dim=0):
        sw = self.acq.sw_h[dim]
        if dim == 0:
            sfo = self.acq.sfo1
            npts = int(len(self.spc[0]))

        if dim == 1:
            if self.acq.manufacturer == 'Bruker':
                sfo = self.proc.sf[1]
            else:
                sfo = self.acq.sfo2

            npts = int(len(self.spc))

        # points = np.round(((ppm - self.ref_shift[dim]) * (sfo / sw) + self.ref_point[dim] / (npts - 1)) * (npts - 1))
        points = np.round(((ppm - self.ref_shift[dim]) * (sfo / sw) + self.ref_point[dim] / (npts - 1)) * (npts - 1))
        return points.astype(int)
        # end ppm2points

    def ppm2points2d(self, ppm):
        points = np.copy(ppm)
        for k in range(len(ppm)):
            points[k][0] = self.ppm2points(ppm[k][0], 0)
            points[k][1] = self.ppm2points(ppm[k][1], 1)

        return points
        # end ppm2points2d

    def proc_spc(self):
        if self.dim == 1:
            self.proc_spc1d()

        if self.dim == 2:
            self.proc_spc2d()

        # self.auto_ref()
        self.calc_ppm()
        # end proc_spc

    def proc_spc1d(self):
        fid = np.copy(self.fid[0])
        fid = self.water_supp(fid)
        fid = self.fid_offset_correction(fid)
        fid = self.gibbs(fid)
        fid = self.apodise(fid, 0, self.proc.lb[0], self.proc.gb[0], self.proc.ssb[0], self.acq.group_delay,
                           self.acq.sw_h[0])
        fid = self.zero_fill(fid)
        spc = fftshift(fft(fid))
        self.spc = np.resize(self.spc, (1, len(spc)))
        self.spc[0] = np.copy(spc)
        self.phase(0, 360.0 * self.acq.group_delay, self.proc.n_points[0])
        if self.proc.invert_matrix[0]:
            self.spc[0] = np.copy(np.flip(self.spc[0]))

        self.phase(self.proc.ph0[0], self.proc.ph1[0], self.proc.n_points[0])
        # end proc_spc1d

    def proc_spc2d(self, test_quad_2d=False, no_abs=False):
        fid = np.copy(self.fid)
        if self.proc.mult_factor[0] == 0:
            self.proc.mult_factor[0] = self.proc.n_points[0] / len(self.fid[0])

        if self.proc.mult_factor[1] == 0:
            self.proc.mult_factor[1] = self.proc.n_points[1] / len(self.fid)

        npts2 = len(self.spc)
        npts1 = len(self.spc[0])
        if npts1 > 0:
            if self.proc.strip_start < 1:
                stsr = 1
            else:
                stsr = self.proc.strip_start

            if self.proc.n_points[0] != npts1:
                self.ref_point[0] = int((self.proc.ref_point[0]) * self.proc.n_points[0] / (
                        self.proc.mult_factor[0] * len(self.fid[0])))  # - stsr + 1

        if npts2 > 1:
            if self.proc.n_points[1] != npts2:
                self.ref_point[1] = int(
                    self.proc.ref_point[1] * self.proc.n_points[1] / (self.proc.mult_factor[1] * len(self.fid)))

        self.spc = np.copy(np.array([[]], dtype='complex'))
        self.spc = np.copy(np.resize(self.spc, (self.proc.n_points[0], self.proc.n_points[1])))
        self.spc *= 0
        if self.proc.n_points[0] > len(fid[0]):
            fid = np.resize(fid, (self.proc.n_points[1], self.proc.n_points[0]))
            fid *= 0
            for k in range(len(self.fid)):
                fid[k][:len(self.fid[k])] = np.copy(self.fid[k][:])

        if self.proc.n_points[0] < len(fid[0]):
            fid = np.resize(fid, (len(fid), self.proc.n_points[0]))
            for k in range(len(fid)):
                fid[k] = np.copy(self.fid[k][:self.proc.n_points[0]])

        for k in range(len(self.fid)):
            fid2 = np.copy(fid[k])
            fid2 = self.water_supp(fid2)
            fid2 = self.fid_offset_correction(fid2)
            fid2 = self.gibbs(fid2)
            fid2 = self.apodise(fid2, 0, self.proc.lb[0], self.proc.gb[0], self.proc.ssb[0], self.acq.group_delay,
                                self.acq.sw_h[0])
            fid2 = self.zero_fill(fid2, 0)
            fid2 = fftshift(fft(fid2))
            if self.acq.fn_mode != 1:
                fid2 = self.phase2(fid2, 0, 360.0 * self.acq.group_delay)

            if self.proc.invert_matrix[0]:
                fid2 = np.flip(fid2)

            if self.acq.fn_mode != 1:
                fid2 = self.phase2(fid2, self.proc.ph0[0], self.proc.ph1[0])

            fid[k] = np.copy(fid2)

        fid = np.copy(np.ndarray.transpose(np.conj(fid)))
        if not test_quad_2d:
            fid = self.quad_2d(fid)
            for k in range(len(fid)):
                fid2 = np.copy(fid[k])
                fid2 = self.gibbs(fid2)
                fid2 = self.apodise(fid2, 1, self.proc.lb[1], self.proc.gb[1], self.proc.ssb[1], 0.0, self.acq.sw_h[1])
                fid2 = self.zero_fill(fid2, 1)
                fid2 = fftshift(fft(fid2))
                if self.proc.invert_matrix[1]:
                    fid2 = np.flip(fid2)

                if self.acq.fn_mode != 1:
                    fid2 = self.phase2(fid2, self.proc.ph0[1], self.proc.ph1[1])
                    self.spc[k] = fid2.real
                else:
                    self.spc[k] = np.copy(fid2)

            self.spc = np.copy(np.ndarray.transpose(self.spc))
            if (self.acq.fn_mode == 1) and (self.proc.tilt == True):
                # self.spc = np.copy(self.hilbert(self.spc, 0))
                self.tiltj_res()

            if self.acq.fn_mode == 1 and no_abs is False:
                for k in range(len(self.spc)):
                    self.spc[k] = np.copy(np.abs(self.spc[k]))

                if self.proc.symj == True:
                    self.symj_res()

        else:
            self.spc = np.copy(self.fid)

        if self.proc.strip_start == 0:
            stsr = 1
        else:
            stsr = self.proc.strip_start

        if self.proc.strip_end > stsr:
            stsi = self.proc.strip_end
            self.spc = np.ndarray.transpose(self.spc)
            self.spc = self.spc[stsr - 1:stsi]
            self.ppm1 = self.ppm1[stsr - 1:stsi]
            self.spc = np.ndarray.transpose(self.spc)

        self.spc = np.copy(self.spc.real)
        # end proc_spc2d

    def quad_2d(self, fid):
        fid = np.copy(fid)
        inc = self.acq.fn_mode
        # MetLab: 6,     0,    3,      2,            1,   4
        # FnMode: 1,     2,    3,      4,            5,   6
        #         j_res, QF, TPPI, States, States-TPPI , E/A
        rFid = np.copy(fid)
        rFid = np.resize(rFid, (len(fid), int(len(fid[0]) / 2)))
        iFid = np.copy(fid)
        iFid = np.resize(iFid, (len(fid), int(len(fid[0]) / 2)))
        if inc == 1 or inc == 2:
            fid = fid  # rFid + 1j * iFid

        if inc == 5:
            for k in range(len(fid)):
                npts = int(len(fid[k]) / 2)
                rFid[k] = fid[k][0::2].real * (-2 * (np.linspace(0, npts - 1, npts, dtype='int') % 2) + 1)
                iFid[k] = fid[k][1::2].real * (2 * (np.linspace(0, npts - 1, npts, dtype='int') % 2) - 1)

            fid = np.copy(rFid + 1j * iFid)

        if inc == 6:
            for k in range(len(fid)):
                rFid[k] = np.conj(fid[k][0::2] + fid[k][1::2])
                iFid[k] = np.conj(fid[k][0::2] - fid[k][1::2])
                iFid[k] = iFid[k].imag - 1j * iFid[k].real
                rFid[k] = rFid[k].imag + 1j * iFid[k].imag

            fid = np.copy(rFid)

        return fid
        # end quad_2d

    def read_pipe_2d(self, p_name, f_name):
        npd = nmrpipeData.NmrPipeData()
        npd.read_pipe(p_name, f_name)
        self.spc = npd.spc
        self.proc.sw_h[0] = npd.fdf2sw
        self.ref_shift[0] = npd.fdf2orig / self.acq.sfo1
        self.ref_point[0] = 0
        self.proc.sw_h[1] = npd.fdf1sw
        self.ref_shift[1] = npd.fdf1orig / self.acq.sfo2
        self.ref_point[1] = 0
        self.proc.phase_inversion = False
        self.proc.mult_factor = [1, 1]
        self.proc.n_points[0] = len(self.spc[0])
        self.proc.n_points[1] = len(self.spc)
        if self.acq.sw[1] == 0.0:
            self.acq.sw[1] = self.acq.sw_h[1] / self.acq.sfo2

        self.calc_ppm()
        # end read_pipe_2d

    def read_spc(self):
        self.acq.read(self.data_set_name + os.sep + self.data_set_number)
        self.proc.read(self.data_set_name + os.sep + self.data_set_number)
        # self.proc.sw_h = self.acq.sw_h
        self.orig_data_set = self.data_set_name + os.sep + self.data_set_number
        if self.acq.manufacturer == 'Bruker':
            title_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + 'title'
            if (os.path.isfile(title_file)):
                fid = open(title_file, "r")
                self.title = fid.read()
                fid.close()

            acqu_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'acqu'
            if (os.path.isfile(acqu_file)):
                fid = open(acqu_file, "r")
                self.acqu = fid.read()
                fid.close()

            acqu2_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'acqu2'
            if (os.path.isfile(acqu2_file)):
                fid = open(acqu2_file, "r")
                self.acqu2 = fid.read()
                fid.close()

            acqu3_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'acqu3'
            if (os.path.isfile(acqu3_file)):
                fid = open(acqu3_file, "r")
                self.acqu3 = fid.read()
                fid.close()

            audita_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'audita.txt'
            if (os.path.isfile(audita_file)):
                fid = open(audita_file, "r")
                self.audita_txt = fid.read()
                fid.close()

            format_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'format.temp'
            if (os.path.isfile(format_file)):
                fid = open(format_file, "r")
                self.format_temp = fid.read()
                fid.close()

            fq1list_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'fq1list'
            if (os.path.isfile(fq1list_file)):
                fid = open(fq1list_file, "r")
                self.fq1list = fid.read()
                fid.close()

            scon2_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'scon2'
            if (os.path.isfile(scon2_file)):
                fid = open(scon2_file, "r")
                self.scon2 = fid.read()
                fid.close()

            shimvalues_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'shimvalues'
            if (os.path.isfile(shimvalues_file)):
                fid = open(shimvalues_file, "r")
                self.shimvalues = fid.read()
                fid.close()

            uxnmrpar_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'uxnmr.par'
            if (os.path.isfile(uxnmrpar_file)):
                fid = open(uxnmrpar_file, "r")
                self.uxnmr_par = fid.read()
                fid.close()

            proc_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + 'proc'
            if (os.path.isfile(proc_file)):
                fid = open(proc_file, "r")
                self.proc1 = fid.read()
                fid.close()

            proc2_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + 'proc2'
            if (os.path.isfile(proc2_file)):
                fid = open(proc2_file, "r")
                self.proc2 = fid.read()
                fid.close()

            proc3_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + 'proc3'
            if (os.path.isfile(proc3_file)):
                fid = open(proc3_file, "r")
                self.proc3 = fid.read()
                fid.close()

            outd_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + 'outd'
            if (os.path.isfile(outd_file)):
                fid = open(outd_file, "r")
                self.outd = fid.read()
                fid.close()

            self.acq.sfo2 = self.acq.bf2 + self.acq.o2 / 1000000.0  # self.proc.sf[1]
            if self.proc.axis_nucleus[1] != 'off':
                self.display.y_label = self.proc.axis_nucleus[1]

        else:
            title_file1 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'text'
            title_file2 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'TEXT'
            if os.path.isfile(title_file1):
                fid = open(title_file1, "r")
                self.title = fid.read()
                fid.close()

            if os.path.isfile(title_file2):
                fid = open(title_file2, "r")
                self.title = fid.read()
                fid.close()

        if self.acq.manufacturer == 'Bruker':
            pul_prog_file = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pulseprogram'
        else:
            pul_prog_file = self.data_set_name + os.sep + self.data_set_number + os.sep + self.acq.pul_prog_name + ".c"

        if os.path.isfile(pul_prog_file):
            fid = open(pul_prog_file, "r")
            self.pulse_program = fid.read()
            fid.close()

        if self.acq.manufacturer == 'Bruker':
            fid_file1 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'fid'
            spc_file1r = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + '1r'
            spc_file1i = self.data_set_name + os.sep + self.data_set_number + os.sep + 'pdata' + os.sep + '1' + os.sep + '1i'
            fid_file2 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'ser'
            if os.path.isfile(fid_file1):
                # read 1D FID file
                self.fid = np.resize(self.fid, (1, int(self.acq.n_data_points[0] / 2)))
                f = open(fid_file1, 'rb')
                if self.acq.byte_order == 1:
                    fid = np.fromfile(f, dtype='>i4')
                else:
                    if self.acq.data_type == 0:
                        fid = np.fromfile(f, dtype='<i4')
                    else:
                        if self.acq.data_type == 1:
                            fid = np.fromfile(f, dtype=np.float64)
                        else:
                            if self.acq.data_type == 2:
                                fid = np.fromfile(f, dtype=np.double)
                            else:
                                fid = np.fromfile(f, dtype=np.float32)

                f.close()
                self.fid[0].real = fid[0::2]
                self.fid[0].imag = -fid[1::2]
                self.dim = 1

            if os.path.isfile(spc_file1r):
                # read 1D spectrum file (real part)
                f = open(spc_file1r, 'rb')
                fid = np.fromfile(f, dtype=np.int32)
                self.spc = np.resize(self.spc, (1, int(len(fid))))
                self.spc[0].real = fid
                f.close()
                if os.path.isfile(spc_file1i):
                    # read 1D spectrum file (imaginary part)
                    f = open(spc_file1i, 'rb')
                    fid = np.fromfile(f, dtype=np.int32)
                    f.close()
                    self.spc[0].imag = fid


            elif (os.path.isfile(fid_file2)):
                # read 2D spectrum
                np1 = int(self.acq.n_data_points[0])
                np2 = int(self.acq.n_data_points[1])
                self.fid = np.resize(self.fid, (int(np2), int(np1 / 2)))
                f = open(fid_file2, 'rb')
                fid = np.fromfile(f, dtype=np.int32)
                f.close()
                fid = fid.reshape(int(np2), int(np1))
                for x in range(np2):
                    self.fid[x].real = fid[x][0::2]
                    self.fid[x].imag = -fid[x][1::2]

                self.dim = 2
                if self.acq.pul_prog_name.find("j_res"):
                    self.j_res = True
                    self.proc.tilt = True
                    self.proc.symj = True

            self.proc.sw_h = np.copy(self.acq.sw_h)
        elif self.acq.manufacturer == 'Varian':
            fid_file1 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'fid'
            fid_file2 = self.data_set_name + os.sep + self.data_set_number + os.sep + 'FID'
            fid_file = ''
            if os.path.isfile(fid_file1):
                fid_file = fid_file1
            elif os.path.isfile(fid_file2):
                fid_file = fid_file2

            if len(fid_file) > 0:
                self.dim = self.acq.np + self.acq.np2 - 1
                if self.dim == 1 and self.acq.ni > 1:
                    self.dim = 2
                    self.j_res = True
                    self.proc.tilt = True
                    self.proc.symj = True
                    self.acq.fn_mode = 1

                f = open(fid_file, 'rb')
                dh1 = np.fromfile(f, dtype='>i4', count=6)
                dh2 = np.fromfile(f, dtype='>i2', count=2)
                dh3 = np.fromfile(f, dtype='>i4', count=1)
                status = np.binary_repr(dh2[1], 16)
                data_format = '>i2'
                if status[12] == '1':
                    data_format = '>f'
                elif status[13] == '1':
                    data_format = '>i4'

                n_blocks = dh1[0]
                n_traces = dh1[1]
                n_points = dh1[2]
                if self.dim == 1:
                    self.fid = np.resize(self.fid, (1, int(self.acq.n_data_points[0] / 2)))
                    fid = np.array([])
                    for k in range(n_blocks):
                        bh1 = np.fromfile(f, dtype='>i2', count=4)
                        bh2 = np.fromfile(f, dtype='>i4', count=1)
                        bh3 = np.fromfile(f, dtype='>f', count=4)
                        if status[10] == '1':
                            bh4 = np.fromfile(f, dtype='>i2', count=4)
                            bh5 = np.fromfile(f, dtype='>i4', count=1)
                            bh6 = np.fromfile(f, dtype='>f', count=4)

                        data = np.fromfile(f, dtype=data_format, count=n_traces * n_points)
                        fid = np.append(fid, data[0::2] + 1j * data[1::2])

                    self.fid[0] = fid

                else:
                    ni = int(self.acq.n_data_points[1] / 2)
                    td = int(self.acq.n_data_points[0] / 2)
                    self.fid = np.zeros((ni, td), dtype='complex')
                    for k in range(ni):
                        bh1 = np.fromfile(f, dtype='>i2', count=4)
                        bh2 = np.fromfile(f, dtype='>i4', count=1)
                        bh3 = np.fromfile(f, dtype='>f', count=4)
                        status = np.binary_repr(bh1[1], 8)
                        data_format = '>i2'
                        if status[4] == '1':
                            data_format = '>f'
                        elif status[5] == '1':
                            data_format = '>i4'

                        data = np.fromfile(f, dtype=data_format, count=n_traces * n_points)
                        self.fid[k] = data[0::2] + 1j * data[1::2]

                f.close()

        # end read_spc

    def set_ref(self, ref_shift, ref_point):
        for k in range(len(ref_shift)):
            self.ref_shift[k] = ref_shift[k]

        for k in range(len(ref_point)):
            self.ref_point[k] = ref_point[k]

        self.calc_ppm()
        # end set_ref    

    def set_window_function(self, dim, wdwf):
        try:
            self.proc.window_type[dim] = self.window_function[wdwf]

        except:
            self.proc.window_type[dim] = self.window_function['none']
            print('Unknown windowType, setting window_function to "none"')

        # end set_window_function

    def sim_hsqc_1d(self):
        sim_spc1 = np.array([], dtype=complex)
        sim_spc = np.array([], dtype=complex)
        n_points = self.proc.n_points[1]
        c13_nc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_nc']
        perc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['contribution']
        n_spin_sys = len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts'])
        intensity = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1]
        ref_shift2 = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])
        ref_point2 = n_points - self.ppm2points(ref_shift2, 1) - 1
        offset = (ref_point2 * (self.proc.sw_h[1] / self.acq.sfo2) / self.proc.n_points[1] + ref_shift2 - self.proc.sw_h[1] / self.acq.sfo2) * self.acq.sfo2
        #print('sim: ref_shift2: {}, ref_point2: {}, offset: {}'.format(ref_shift2, ref_point2, offset))
        sim_spc.resize(1, self.proc.n_points[1])
        c13_centre = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])
        if self.hsqc.autoscale_j == True:
            scale = self.hsqc.j_scale
        else:
            scale = 1.0

        c13_offset = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset']
        c13_beg = self.proc.n_points[1] - self.ppm2points(c13_centre + self.hsqc.range_c * scale) - 1
        c13_end = self.proc.n_points[1] - self.ppm2points(c13_centre - self.hsqc.range_c * scale) - 1
        n_points = 2 ** math.ceil(math.log2(abs(c13_beg - c13_end)) + 1)
        c13_centre_points = self.proc.n_points[1] - self.ppm2points(c13_centre, 1) - 1
        c13_beg = c13_centre_points - n_points - 1
        c13_end = c13_centre_points + n_points - 1
        c13_range = range(c13_centre_points - int(n_points / 2), c13_centre_points + int(n_points / 2))
        c13_beg_ppm = self.points2ppm(self.proc.n_points[1] - np.min([c13_range[0], c13_range[-1]]) - 1, 1)
        c13_end_ppm = self.points2ppm(self.proc.n_points[1] - np.max([c13_range[0], c13_range[-1]]) - 1, 1)
        # c13_midpoint = self.points2ppm(self.proc.n_points[1] - int(np.round(np.mean([c13_range[0], c13_range[-1]]))) - 1, 1)
        c13_nc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_nc']
        n_spin_sys = len(
            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts'])
        ref_shift2 = self.ppm2[
            c13_range[0]]  # np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])
        ref_point2 = 0  # n_points - self.ppm2points(ref_shift2, 1) - 1
        sw = abs(c13_beg_ppm - c13_end_ppm)
        offset = (ref_point2 * sw / (2 * n_points) + ref_shift2 - sw) * self.acq.sfo2
        sim_spc1.resize(1, n_points)
        for k in range(n_spin_sys):
            sys = self.make_hsqc_spin_sys(c13_offset, k)
            sys.offsetShifts(offset)
            sim_spc1[0] += intensity * self.c13spc1d(sys, perc[k], angle=90.0, dly_n=0.0,
                                                    c13_range=[c13_range[0], c13_range[-1]],
                                                    c13_sw=[c13_beg_ppm, c13_end_ppm]) / sum(c13_nc[k])

        #for k in range(n_spin_sys):
        #    sys = self.make_hsqc_spin_sys(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset'], k)
        #    sys.offsetShifts(offset)
        #    sim_spc[0] += intensity * self.c13spc1d(sys, perc[k]) / sum(c13_nc[k])
        sim_spc[0][c13_range] = sim_spc1[0]
        if intensity == 1.0:
            spc_max = np.array([], dtype=complex)
            spin_number = self.hsqc.cur_peak
            hd = self.hsqc.hsqc_data[self.hsqc.cur_metabolite]
            h1_shift = hd.h1_shifts[spin_number - 1]
            max_idx = np.where(sim_spc[0] == np.max(sim_spc[0]))[0][0]
            h1_picked = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_picked
            c13_picked = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked
            if len(h1_picked[spin_number - 1]) > 0:
                h1_pos = np.mean(h1_picked[spin_number - 1])
            else:
                h1_pos = h1_shift

            if len(c13_picked[spin_number - 1]) > 0:
                c13_pos = np.mean(c13_picked[spin_number - 1])
            else:
                c13_pos = c13_shift

            h1_pts = len(self.spc[0]) - self.ppm2points(h1_pos, 0) - 1
            c13_pts = len(self.spc) - self.ppm2points(c13_pos, 1) - 1
            #c13_ptsa = len(self.spc) - self.ppm2points(c13_pos + self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset'][0] / 1000.0, 1) - 1
            # spc_max.resize(len(sim_spc[0]))
            # for dd in range(len(sim_spc[0])):
            #    spc_max[dd] = self.spc[dd][h1_pts]
            #
            intensity = abs(self.spc[c13_pts][h1_pts].real / sim_spc[0][c13_pts].real)
            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1] = intensity

        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].sim_spc[self.hsqc.cur_peak - 1] = sim_spc[0].real
        self.sim_hsqc_1d_calc_cod()
        # end sim_hsqc_1d

    def sim_hsqc_1d_calc_cod(self):
        if len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].sim_spc[self.hsqc.cur_peak - 1]) == 0:
            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].cod[self.hsqc.cur_peak - 1] = - 1
            return

        gamma_adjust = 20.0*42.577 / 10.7084 # 20 times gamma_H / gamma_C
        h1_shift = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_shifts[self.hsqc.cur_peak - 1]
        c13_idx = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_index[self.hsqc.cur_peak - 1] - 1
        c13_shift = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_shifts[c13_idx]
        if len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_picked[self.hsqc.cur_peak - 1]) == 0:
            h1_exp = h1_shift
        else:
            h1_exp = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_picked[self.hsqc.cur_peak - 1])

        if len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1]) == 0:
            c13_exp = c13_shift
        else:
            c13_exp = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])

        h1_pts = len(self.spc[0]) - self.ppm2points(h1_exp, 0) - 1
        if self.hsqc.autoscale_j == True:
            scale = self.hsqc.j_scale
        else:
            scale = 1.0

        c13_beg = self.proc.n_points[1] - self.ppm2points(c13_exp + self.hsqc.range_c*scale) - 1
        c13_end = self.proc.n_points[1] - self.ppm2points(c13_exp - self.hsqc.range_c*scale) - 1
        n_points = 2 ** math.ceil(math.log2(abs(c13_beg - c13_end)) + 1)
        #print("c13_beg: {}, c13_end: {}, n_points: {}".format(c13_beg, c13_end, n_points))
        c13_centre_points = self.proc.n_points[1] - self.ppm2points(c13_exp, 1) - 1
        c13_beg = c13_centre_points - n_points - 1
        c13_end = c13_centre_points + n_points - 1
        c13_range = range(c13_centre_points - int(n_points/2), c13_centre_points + int(n_points/2))
        spc2 = np.array([])
        spc2.resize(2*n_points)
        spc2_sim = np.array([])
        spc2_sim.resize(2*n_points)
        #print(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].sim_spc)
        #print(c13_range)
        for k in range(len(c13_range)):
            spc2[k] = self.spc[c13_range[k]][h1_pts].real
            spc2_sim[k] = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].sim_spc[self.hsqc.cur_peak - 1][c13_range[k]]

        spc2 /= np.linalg.norm(spc2)
        spc2_sim /= np.linalg.norm(spc2_sim)
        #spc2_sim *= self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1]
        #print("max(spc2) = {}, max(spc2_sim) = {}, intensity = {}".format(np.max(spc2), np.max(spc2_sim), self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1]))
        #print("yAdjust: {}, 13c(idx): {}\n1h(lib): {}, 13c(lib): {}\n1h(exp): {}, 13c(exp): {}".format(gamma_adjust, c13_idx, h1_shift, c13_shift, h1_exp, c13_exp))
        #print("len(spc2): {}, len(spc2_sim): {}".format(len(spc2), len(spc2_sim)))
        max_dist = math.sqrt(self.hsqc.range_h**2 + (self.hsqc.range_c / gamma_adjust)**2)
        dist_2d = math.sqrt((h1_exp - h1_shift)**2 + ((c13_exp - c13_shift) / gamma_adjust)**2)
        if dist_2d > max_dist:
            weighted_distance = 1 - (dist_2d / max_dist - 1)
        else:
            weighted_distance = 1

        res = spc2 - spc2_sim
        cod1 = 1.0 - np.sum(res**2) / np.sum((spc2 - np.mean(spc2))**2)
        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].cod[self.hsqc.cur_peak - 1] = np.max([cod1 * weighted_distance * 100.0, 0.0])
        #print("max_dist: {}, dist_2d: {}, cod1: {}, cod: {}".format(max_dist, dist_2d, cod1, self.hsqc.hsqc_data[self.hsqc.cur_metabolite].cod[self.hsqc.cur_peak - 1]))
        # end sim_hsqc_1d_calc_cod

    def fit_hsqc_1d(self):
        autosim = self.hsqc.autosim
        self.hsqc.autosim = False
        intensity = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1]
        fit_parameters = []
        c13_offset = []
        contribution = []
        fit_parameters.append(intensity)
        for k in range(
                len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset'])):
            c13_offset.append(
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset'][k])

        for k in range(
                len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_offset'])):
            contribution.append(
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['contribution'][k])

        if self.hsqc.fit_zero_percentages == False:
            c13_offset = np.array(c13_offset)[np.where(np.array(contribution) != 0)]
            contribution = np.array(contribution)[np.where(np.array(contribution) != 0)]

        if self.hsqc.fit_chemical_shifts:
            for k in range(len(c13_offset)):
                fit_parameters.append(c13_offset[k])

        if self.hsqc.fit_percentages:
            for k in range(len(contribution)):
                fit_parameters.append(contribution[k])

        eval_parameters = optimize.minimize(self.fct_hsqc_1d, fit_parameters, method='Powell')
        # eval_parameters = optimize.leastsq(self.fct_hsqc_1d, fit_parameters, ftol=1e-12, xtol=1e-12, maxfev=1e10)
        e_pars = np.array(eval_parameters.x).tolist()
        intensity = e_pars.pop(0)
        n_fit_parameters = len(e_pars)
        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].intensities[self.hsqc.cur_peak - 1] = intensity
        if self.hsqc.fit_chemical_shifts and self.hsqc.fit_percentages:
            contribution = (np.array(e_pars[int(n_fit_parameters / 2):]) * 100.0 / np.array(
                e_pars[int(n_fit_parameters / 2):]).sum()).tolist()
            for k in range(len(contribution)):
                if contribution[k] < 0:
                    contribution[k] = 0

            contribution = (np.array(contribution) * 100.0 / np.array(contribution).sum()).tolist()
            for k in range(len(contribution)):
                contribution[k] = round(contribution[k], 3)

            c13_offset = e_pars[:int(n_fit_parameters / 2)]
            for k in range(len(c13_offset)):
                if c13_offset[k] > 50 or c13_offset[k] < -50:
                    c13_offset[k] = 0
                    contribution[k] = 0
                    self.fit_hsqc_again = True

                if contribution[k] == 0:
                    c13_offset[k] = 0

                c13_offset[k] = round(c13_offset[k], 2)

            contribution = (np.array(contribution) * 100.0 / np.array(contribution).sum()).tolist()
            for k in range(len(contribution)):
                contribution[k] = round(contribution[k], 3)

            if self.hsqc.fit_zero_percentages:
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset'] = c13_offset
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution'] = contribution
                for k in range(len(
                        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_idx'])):
                    idx = ' '.join(str(e) for e in
                                   self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                                       'c13_idx'][k])
                    self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_offset[idx] = c13_offset[k]

            else:
                c13_offset2 = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset']
                contribution2 = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution']
                contribution2 = np.array(contribution2)
                c13_offset2 = np.array(c13_offset2)
                c13_offset2[np.where(contribution2 != 0)] = np.array(c13_offset)
                contribution2[np.where(contribution2 != 0)] = np.array(contribution)
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset'] = c13_offset2.tolist()
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution'] = contribution2.tolist()
                for k in range(len(
                        self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_idx'])):
                    idx = ' '.join(str(e) for e in
                                   self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                                       'c13_idx'][k])
                    self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_offset[idx] = c13_offset2[k]


        elif self.hsqc.fit_chemical_shifts:
            if self.hsqc.fit_zero_percentages:
                c13_offset = e_pars

            else:
                c13_offset = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset']
                c13_offset = np.array(c13_offset)
                contribution = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution']
                contribution = np.array(contribution)
                c13_offset[np.where(contribution != 0)] = np.array(e_pars)
                c13_offset = c13_offset.tolist()

            for k in range(len(c13_offset)):
                if c13_offset[k] > 50 or c13_offset[k] < -50:
                    c13_offset[k] = 0

                if self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['contribution'][
                    k] < 0.8:
                    c13_offset[k] = 0

                c13_offset[k] = round(c13_offset[k], 2)

            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                'c13_offset'] = c13_offset
            for k in range(
                    len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_idx'])):
                idx = ' '.join(str(e) for e in
                               self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                                   'c13_idx'][k])
                self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_offset[idx] = c13_offset[k]

        else:
            if self.hsqc.fit_zero_percentages:
                contribution = (np.array(e_pars) * 100.0 / np.array(e_pars).sum()).tolist()
            else:
                contribution2 = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution']
                contribution2 = np.array(contribution2)
                contribution2[np.where(contribution2 != 0)] = np.array(e_pars)
                contribution = (contribution2 * 100.0 / contribution2.sum()).tolist()

            for k in range(len(contribution)):
                if contribution[k] < 0:
                    contribution[k] = 0

            contribution = (np.array(contribution) * 100.0 / np.array(contribution).sum()).tolist()
            for k in range(len(contribution)):
                contribution[k] = round(contribution[k], 3)

            self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                'contribution'] = contribution

        self.hsqc.autosim = autosim
        # end fit_hsqc_1d

    def fct_hsqc_1d(self, fit_parameters=[]):
        n_fit_pars = len(fit_parameters)
        if n_fit_pars == 0:
            return []

        intensity = fit_parameters[0]
        fit_parameters = fit_parameters[1:]
        n_fit_pars = len(fit_parameters)
        #print(fit_parameters)
        if self.hsqc.fit_chemical_shifts and self.hsqc.fit_percentages:
            if self.hsqc.fit_zero_percentages:
                c13_offset = fit_parameters[:int(n_fit_pars / 2)]
                perc = fit_parameters[int(n_fit_pars / 2):]
            else:
                perc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution']
                c13_offset = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset']
                c13_offset = np.array(c13_offset)
                c13_offset[np.where(np.array(perc) != 0)] = np.array(fit_parameters[:int(n_fit_pars / 2)])
                c13_offset = c13_offset.tolist()
                perc = np.array(perc)
                perc[np.where(perc != 0)] = np.array(fit_parameters[int(n_fit_pars / 2):])
                perc = perc.tolist()

        elif self.hsqc.fit_chemical_shifts:
            perc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['contribution']
            if self.hsqc.fit_zero_percentages:
                c13_offset = fit_parameters
            else:
                c13_offset = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'c13_offset']
                c13_offset = np.array(c13_offset)
                c13_offset[np.where(np.array(perc) != 0)] = np.array(fit_parameters)
                c13_offset = c13_offset.tolist()

        else:
            c13_offset = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                'c13_offset']
            if self.hsqc.fit_zero_percentages:
                perc = fit_parameters
            else:
                perc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1][
                    'contribution']
                perc = np.array(perc)
                perc[np.where(perc != 0)] = np.array(fit_parameters)
                perc = perc.tolist()

        perc = np.abs(np.array(perc)).tolist()
        sim_spc = np.array([], dtype=complex)
        c13_centre = np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])
        if self.hsqc.autoscale_j == True:
            scale = self.hsqc.j_scale
        else:
            scale = 1.0

        c13_beg = self.proc.n_points[1] - self.ppm2points(c13_centre + self.hsqc.range_c*scale) - 1
        c13_end = self.proc.n_points[1] - self.ppm2points(c13_centre - self.hsqc.range_c*scale) - 1
        n_points = 2 ** math.ceil(math.log2(abs(c13_beg - c13_end)) + 1)
        c13_centre_points = self.proc.n_points[1] - self.ppm2points(c13_centre, 1) - 1
        c13_beg = c13_centre_points - n_points - 1
        c13_end = c13_centre_points + n_points - 1
        c13_range = range(c13_centre_points - int(n_points/2), c13_centre_points + int(n_points/2))
        c13_beg_ppm = self.points2ppm(self.proc.n_points[1] - np.min([c13_range[0], c13_range[-1]]) - 1, 1)
        c13_end_ppm = self.points2ppm(self.proc.n_points[1] - np.max([c13_range[0], c13_range[-1]]) - 1, 1)
        #c13_midpoint = self.points2ppm(self.proc.n_points[1] - int(np.round(np.mean([c13_range[0], c13_range[-1]]))) - 1, 1)
        c13_nc = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_nc']
        n_spin_sys = len(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].spin_systems[self.hsqc.cur_peak - 1]['c13_shifts'])
        ref_shift2 = self.ppm2[c13_range[0]] #np.mean(self.hsqc.hsqc_data[self.hsqc.cur_metabolite].c13_picked[self.hsqc.cur_peak - 1])
        ref_point2 = 0 #n_points - self.ppm2points(ref_shift2, 1) - 1
        sw = abs(c13_beg_ppm - c13_end_ppm)
        offset = (ref_point2 * sw / (2*n_points) + ref_shift2 - sw) * self.acq.sfo2
        sim_spc.resize(1,n_points)
        for k in range(n_spin_sys):
            sys = self.make_hsqc_spin_sys(c13_offset, k)
            sys.offsetShifts(offset)
            sim_spc[0] += intensity * self.c13spc1d(sys, perc[k], angle=90.0, dly_n=0.0, c13_range=[c13_range[0], c13_range[-1]], c13_sw=[c13_beg_ppm, c13_end_ppm]) / sum(c13_nc[k])

        spin_number = self.hsqc.cur_peak
        h1_picked = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].h1_picked
        if len(h1_picked[spin_number - 1]) > 0:
            h1_pos = np.mean(h1_picked[spin_number - 1])
        else:
            h1_pos = h1_shift

        h1_pts = len(self.spc[0]) - self.ppm2points(h1_pos, 0) - 1
        spc2 = np.array([])
        spc2.resize(2*n_points)
        #print(c13_range)
        for k in range(len(c13_range)):
            spc2[k] = self.spc[c13_range[k]][h1_pts].real

        err = []
        for k in range(len(c13_range)):
            err.append((sim_spc[0][k].real * intensity - self.spc[c13_range[k]][h1_pts].real) ** 2)

        return np.array(err).sum()
        # end fct_hsqc_1d

    def c13spc1d(self, sys, perc=100.0, angle=90.0, dly_n=0.0, c13_range=[], c13_sw=[]):
        jres = self.acq.cnst[18]
        if len(c13_range) == 0:
            sw = self.acq.sw_h[1]
            td = int(self.acq.n_data_points[1] * 2)
            npts = self.proc.n_points[1]
        else:
            npts = np.max(c13_range) - np.min(c13_range) + 1
            sw = (np.max(c13_sw) - np.min(c13_sw))*self.acq.sfo2
            td = int(npts / (2 * jres))
            #print("npts: {}, sw: {}, td: {}".format(npts, sw, td))

        jres_n = 1.0
        for k in range(0, sys.spins() - 1):
            for l in range(k + 1, sys.spins()):
                if (sys.J(k, l) > 10000.0):
                    sys.J(k, l, sys.J(k, l) * jres_n / 100000.0)
                    sys.isotope(l, '15N')
                else:
                    sys.J(k, l, sys.J(k, l) * jres)

        r2 = self.hsqc.hsqc_data[self.hsqc.cur_metabolite].r2[self.hsqc.cur_peak - 1]
        echo_time = self.hsqc.echo_time / 1000.0
        dt = 1.0 / sw
        sigma0 = pg.sigma_eq(sys)
        H = pg.Hcs(sys) + pg.HJw(sys)
        D = pg.Fm(sys, "1H")
        fid = pg.row_vector(td)
        sigma1 = pg.Iypuls(sys, sigma0, 0, 90.0)
        sigma1 = pg.evolve(pg.gen_op(sigma1), pg.gen_op(H), dly_n / jres_n)
        sigma1 = pg.Ixpuls(sys, sigma1, "1H", 180.0)
        sigma1 = pg.Ixpuls(sys, sigma1, "15N", 180.0)
        sigma1 = pg.evolve(pg.gen_op(sigma1), pg.gen_op(H), dly_n / jres_n)
        sigma1 = pg.evolve(pg.gen_op(sigma1), pg.gen_op(H), echo_time / jres)
        sigma1 = pg.Ixpuls(sys, sigma1, "1H", 180.0)
        sigma1 = pg.evolve(pg.gen_op(sigma1), pg.gen_op(H), echo_time / jres)
        fid = fid + pg.FID(pg.gen_op(sigma1), pg.gen_op(D), pg.gen_op(H), dt, td)
        spc1 = np.array([], dtype=complex)
        spc1.resize(1, td)
        spc = np.array([], dtype=complex)
        spc.resize(1, npts)
        spc2 = np.array([], dtype=complex)
        spc2.resize(1, npts)
        for k in range(td):
            spc1[0][k] = fid.getRe(k) - 1j * fid.getIm(k)
            spc1[0][k] *= np.exp(-r2 * dt * k)

        # print("maxFID: {}".format(np.max(spc1[0])))
        spc1 = self.wdwf_qsin(spc1, angle)
        for k in range(td):
            spc[0][k] = spc1[0][k]

        spc = np.fft.fft(spc[0])
        # print("mmax: {}!".format(np.max(spc3.real)))
        for k in range(npts):
            spc2[0][k] = spc[k] - spc[0]

        spc2[0] = perc * spc2[0].real / 100.0
        # print("len(spc2): {}, len(spc2[0]): {}".format(len(spc2), len(spc2[0])))
        return spc2[0].real
        # end c13spc1d

    def wdwf_qsin(self, fid, angle=90.0):
        if (angle > -1.0):
            npts = len(fid[0])
            t = np.linspace(angle * np.pi / 180.0, np.pi, npts)
            for k in range(npts):
                fid[0][k] = fid[0][k].real * np.sin(t[k]) * np.sin(t[k]) + 1j * fid[0][k].imag * np.sin(t[k]) * np.sin(
                    t[k])

        return fid

    def smo(self, fid):
        x = np.linspace(0, len(fid) - 1, len(fid))
        f0 = np.copy(fid)
        fid = np.roll(fid, math.floor(-self.acq.group_delay))
        pp = np.polyfit(x, fid, self.proc.poly_order)
        fid = fid - np.polyval(pp, x)
        fid = np.roll(fid, math.ceil(self.acq.group_delay))
        return fid
        # end smo

    def symj_res(self):
        for k in range(int(len(self.spc) / 2)):
            tmp = np.minimum(self.spc[k], self.spc[len(self.spc) - k - 1])
            self.spc[k] = tmp
            self.spc[len(self.spc) - k - 1] = tmp

        # end symj

    def tiltj_res(self):
        hz_per_point = self.acq.sw_h[0] / len(self.spc[0])
        sw2 = self.acq.sw_h[1]
        npts2 = len(self.spc)
        hz_vect = np.linspace(sw2 / 2.0, -sw2 / 2.0, npts2)
        # hz_vect = hz_vect - (hz_vect[1] - hz_vect[0]) / 2.0
        for k in range(npts2):
            npts = hz_vect[k] / hz_per_point
            fid1 = np.copy(ifft(self.spc[k]))
            fid1 = self.phase2(fid1, 0, -npts * 360.0)

            self.spc[k] = np.copy(fft(fid1))

        # end tiltj_res

    def water_supp(self, fid):
        if (self.proc.water_suppression == 1):
            fid = self.conv(fid)

        if (self.proc.water_suppression == 2):
            fid = self.smo(fid)

        return fid
        # end water_supp

    def zero_fill(self, fid, dim=0):
        fid1 = np.zeros(self.proc.n_points[dim], dtype='complex')
        fid1[:int(len(fid))] = fid
        return fid1
        # end zero_fill
