from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import time
import numpy as np


class vaet(pulse_sequence):

    scannable_params = {"VAET.vaet_duration": [(0., 50., 1., "us"), "vaet_time"],
                        "VAET.rabi_duration": [(0., 50., 1., "us"), "vaet_time"],
                        "SZX.nu_effective": [(-10.0, 10, 0.5, "kHz"),"vaet_delta"],
                        "SZX.carrier_detuning": [(-1, 1, .1, "MHz"), "vaet_time"],
                        "RamseyScanGap.ramsey_duration": [(0, 1.0, 0.5, "ms") ,"parity"]}

    show_params = ["VAET.duration",
                   "VAET.calibrate_szx",
                   "VAET.rotate_out",
                   "VAET.rotate_in",
                   "VAET.calibrate_detuning",
                   "VAET.scan_nu_effective",
                   # "VAET.analysis_pulse_enable",
                   "SZX.line_selection",
                   "SZX.sideband_selection",
                   "SZX.bichro_enable",
                   "SZX.amplitude",
                   "SZX.amp_blue",
                   "SZX.amp_red",
                   "SZX.nu_effective",
                   "SZX.carrier_detuning",
                   "SZX.post_local_rotation",
                   "SZX.calibration_offset",
                   "SZX.local_rabi_amp",
                   "MolmerSorensen.line_selection",
                   "MolmerSorensen.line_selection_ion2",
                   "MolmerSorensen.due_carrier_enable",
                   "MolmerSorensen.sideband_selection",
                   "MolmerSorensen.detuning",
                   "MolmerSorensen.amp_red",
                   "MolmerSorensen.amp_blue",
                   "MolmerSorensen.amplitude",
                   "MolmerSorensen.amplitude_ion2",
                   "MolmerSorensen.analysis_pulse_enable",
                   "MolmerSorensen.SDDS_enable",
                   "MolmerSorensen.SDDS_rotate_out",
                   "MolmerSorensen.bichro_enable",
                   "MolmerSorensen.carrier_1",
                   "MolmerSorensen.carrier_2",
                   "MolmerSorensen.analysis_duration",
                   "MolmerSorensen.analysis_amplitude",
                   "MolmerSorensen.analysis_amplitude_ion2",
                   "MolmerSorensen.detuning_carrier_1",
                   "MolmerSorensen.detuning_carrier_2",
                   "MolmerSorensen.asymetric_ac_stark_shift",
                   "RamseyScanGap.ramsey_duration"]


    @classmethod
    def run_initial(cls, cxn, parameters_dict):

        cxn.pulser.switch_auto("866DP")

        szx = parameters_dict.SZX
        ms = parameters_dict.MolmerSorensen

        # Calc freq shift of the local SP
        szx_mode = szx.sideband_selection
        szx_trap_frequency = parameters_dict["TrapFrequencies." + szx_mode]
        ms_mode = ms.sideband_selection
        ms_trap_frequency = parameters_dict["TrapFrequencies." + ms_mode]

        f_local = U(80 - .2, "MHz")
        f_global = U(80 + .15, "MHz")
        szx_freq_blue = f_local - (szx_trap_frequency / 2) + szx.calibration_offset + szx.nu_effective
        szx_freq_red = f_local +  (szx_trap_frequency / 2) + szx.calibration_offset
        ms_freq_blue = f_global - ms_trap_frequency - ms.detuning - ms.asymetric_ac_stark_shift
        ms_freq_red = f_global + ms_trap_frequency + ms.detuning

        szx_amp_blue = szx.amp_blue
        szx_amp_red = szx.amp_red
        ms_amp_blue = ms.amp_blue
        ms_amp_red = ms.amp_red

        cxn.dds_cw.frequency("0", ms_freq_blue)
        cxn.dds_cw.frequency("1", ms_freq_red)
        cxn.dds_cw.frequency("2", f_global)
        cxn.dds_cw.frequency("3", szx_freq_blue)
        cxn.dds_cw.frequency("4", szx_freq_red)
        cxn.dds_cw.amplitude("0", ms_amp_blue)
        cxn.dds_cw.amplitude("1", ms_amp_red)
        cxn.dds_cw.amplitude("3", szx_amp_blue)
        cxn.dds_cw.amplitude("4", szx_amp_red)

        cxn.dds_cw.output("0", True)
        cxn.dds_cw.output("1", True)
        cxn.dds_cw.output("2", True)
        cxn.dds_cw.output("3", True)
        cxn.dds_cw.output("4", True)
        cxn.dds_cw.output("5", True)

        # Time for the single pass to thermalize/ make sure everything is programmed
        time.sleep(1.5)


    @classmethod
    def run_finally(cls, cxn, parameters_dict, data, x):

        cxn.pulser.switch_manual("866DP", True)


    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.SZX import SZX
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.VAET import VAET
        from subsequences.LocalRotation import LocalRotation
        from subsequences.EmptySequence import EmptySequence

        szx = self.parameters.SZX
        v = self.parameters.VAET
        ms = self.parameters.MolmerSorensen

        # Calc DP freq
        bare_freq_729_szx = self.calc_freq(szx.line_selection)
        freq_729_szx = bare_freq_729_szx + szx.carrier_detuning
        bare_freq_729_ms = self.calc_freq(ms.line_selection)
        freq_729_ms = bare_freq_729_ms + ms.detuning_carrier_1
        bare_freq_729_ms_ion2 = self.calc_freq(ms.line_selection_ion2)
        freq_729_ms_ion2 = bare_freq_729_ms_ion2 + ms.detuning_carrier_2
        ramsey_gap = self.parameters.RamseyScanGap.ramsey_duration

        self.end = U(10., "us")
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        

        if v.scan_nu_effective:
            import labrad
            cxn = labrad.connect()
            szx_mode = szx.sideband_selection
            # szx_trap_frequency = self.parameters_dict["TrapFrequencies." + szx_mode]
            szx_trap_frequency = self.parameters.TrapFrequencies[szx_mode]
            f_local = U(80 - .2, "MHz")
            szx_freq_blue = f_local - (szx_trap_frequency / 2) + szx.calibration_offset + szx.nu_effective
            # szx_freq_red = f_local +  (szx_trap_frequency / 2) + szx.calibration_offset
            # szx_amp_blue = szx.amp_blue
            # szx_amp_red = szx.amp_red
            cxn.dds_cw.frequency("3", szx_freq_blue)
            # cxn.dds_cw.frequency("4", szx_freq_red)
            # cxn.dds_cw.amplitude("3", szx_amp_blue)
            # cxn.dds_cw.amplitude("4", szx_amp_red)
            cxn.dds_cw.output("3", True)
            # cxn.dds_cw.output("4", True)
            # Time for the single pass to thermalize/ make sure everything is programmed
            time.sleep(1.)



        if v.calibrate_szx:
            self.addSequence(SZX, {"SZX.frequency": freq_729_szx,
                                   "SZX.duration": v.vaet_duration})

            # Using this as a quick check to see if bichro interaction is working
            if szx.post_local_rotation:
                self.addSequence(RabiExcitation, {"Excitation_729.rabi_excitation_frequency": bare_freq_729_szx,
                                                  "Excitation_729.rabi_excitation_amplitude": szx.local_rabi_amp,
                                                  "Excitation_729.channel_729": "729local",
                                                  "Excitation_729.rabi_excitation_duration": v.rabi_duration})
            self.addSequence(StateReadout)
            return


        if ms.due_carrier_enable:
            if v.rotate_in:
                self.addSequence(LocalRotation, {"LocalRotation.frequency": bare_freq_729_ms_ion2,
                                                 "LocalRotation.angle": U(180, "deg")})
            self.addSequence(VAET, {"SZX.frequency": freq_729_szx,
                                    "MolmerSorensen.frequency": freq_729_ms,
                                    "MolmerSorensen.frequency_ion2": freq_729_ms_ion2})
            self.addSequence(EmptySequence, {"EmptySequence.empty_sequence_duration": ramsey_gap})
            if v.rotate_out:
                self.addSequence(LocalRotation, {"LocalRotation.frequency": freq_729_ms_ion2,
                                                 "LocalRotation.angle": U(180, "deg"),
                                                 "LocalRotation.phase": U(180, "deg")
                                                 })
        else:
            if v.rotate_in:
                self.addSequence(LocalRotation, {"LocalRotation.frequency": bare_freq_729_ms,
                                                 "LocalRotation.angle": U(180, "deg")})
            if v.calibrate_detuning:
                self.addSequence(VAET, {"SZX.amplitude": U(-63, "dBm"),
                                        "SZX.carrier_detuning": U(-1, "MHz"),
                                        "SZX.bichro_enable": False,
                                        "MolmerSorensen.frequency": freq_729_ms,
                                        "MolmerSorensen.frequency_ion2": freq_729_ms})
                self.addSequence(SZX, {"SZX.frequency": freq_729_szx,
                                       "SZX.duration": ramsey_gap})
            else:
                if not v.ka:
                    self.addSequence(VAET, {"SZX.frequency": freq_729_szx,
                                            "MolmerSorensen.frequency": freq_729_ms,
                                            "MolmerSorensen.frequency_ion2": freq_729_ms})
                else:
                    self.addSequence(VAET, {"SZX.frequency": freq_729_szx,
                                        "MolmerSorensen.frequency": freq_729_ms,
                                        "MolmerSorensen.frequency_ion2": freq_729_ms,
                                        "MolmerSorensen.bichro_enable": False})


            if v.rotate_out:
                self.addSequence(LocalRotation, {"LocalRotation.frequency": freq_729_ms,
                                                 "LocalRotation.angle": U(180, "deg"),
                                                 "LocalRotation.phase": U(180, "deg")})

        if v.calibrate_detuning:
            mode = ms.sideband_selection
            trap_frequency = self.parameters.TrapFrequencies[mode]
            if not ms.due_carrier_enable:
                self.addSequence(MolmerSorensen, {"MolmerSorensen.frequency": freq_729_ms,
                                                  "MolmerSorensen.frequency_ion2": freq_729_ms,
                                                  "MolmerSorensen.phase": ms.ms_phase,
                                                  "MolmerSorensen.bichro_enable": False,
                                                  "MolmerSorensen.amplitude": ms.analysis_amplitude,
                                                  "MolmerSorensen.duration": ms.analysis_duration,
                                                  "MolmerSorensen.detuning": -trap_frequency})
            else:  
                self.addSequence(MolmerSorensen, {"MolmerSorensen.frequency": freq_729_ms,
                                                  "MolmerSorensen.frequency_ion2": freq_729_ms_ion2,
                                                  "MolmerSorensen.phase": ms.ms_phase,
                                                  "MolmerSorensen.bichro_enable": False,
                                                  "MolmerSorensen.amplitude": ms.analysis_amplitude,
                                                  "MolmerSorensen.amplitude_ion2": ms.analysis_amplitude_ion2,
                                                  "MolmerSorensen.duration": ms.analysis_duration,
                                                  "MolmerSorensen.detuning": -trap_frequency})
        self.addSequence(StateReadout)

