def run(self, cxn, context):
        p = self.parameters.Dephasing_Pulses
        self.data_vault_new_trace()
        self.setup_sequence_parameters()
        for i,interaction_duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop:
                return False
            second_pulse_dur = min(self.max_second_pulse, interaction_duration)
            ramsey_time = max(WithUnit(0,'us'), interaction_duration - self.max_second_pulse)
            #ramsey_time = WithUnit(0,'us')
            p.evolution_ramsey_time = ramsey_time
            p.evolution_pulses_duration = second_pulse_dur
            self.excite.set_parameters(self.parameters)
            excitation, readout = self.excite.run(cxn, context)
            submission = [interaction_duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.update_progress(i)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)
        ####### FROM DYLAN -- PULSE SEQUENCE PLOTTING #########
        #ttl = self.cxn.pulser.human_readable_ttl()
        #dds = self.cxn.pulser.human_readable_dds()
        #channels = self.cxn.pulser.get_channels().asarray
        #sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
        #sp.makePlot()
        ############################################3
        return True
     
