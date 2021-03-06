from traits.api import HasTraits, Instance, Str, Bool, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view

import argparse, sys

from instruments.InstrumentManager import InstrumentLibrary
import Sweeps
import MeasFilters
import QGL.Channels
import json
import os
import config

class ExpSettings(HasTraits):

    sweeps = Instance(Sweeps.SweepLibrary)
    instruments = Instance(InstrumentLibrary)
    measurements = Instance(MeasFilters.MeasFilterLibrary)
    channels = Instance(QGL.Channels.ChannelLibrary, transient=True)
    CWMode = Bool(False)
    curFileName = Str('DefaultExpSettings.json', transient=True)

    def __init__(self, **kwargs):
        super(ExpSettings, self).__init__(**kwargs)
        self.update_instr_list()

    @on_trait_change('instruments.instrDict_items')
    def update_instr_list(self):
        if self.sweeps:
            del self.sweeps.possibleInstrs[:]
            for key in self.instruments.instrDict.keys():
                self.sweeps.possibleInstrs.append(key)

    def load_from_file(self, fileName):
        import JSONHelpers
        pass

    def write_to_file(self):
        import JSONHelpers
        with open(self.curFileName,'w') as FID:
            json.dump(self, FID, cls=JSONHelpers.ScripterEncoder, indent=2, sort_keys=True, CWMode=self.CWMode)

    def apply_quickpick(self, name):
        try:
            with open(config.quickpickFile, 'r') as FID:
                quickPicks = json.load(FID)
        except IOError:
            print('No quick pick file found.')
            return
        
        quickPick = quickPicks[name]

        #Apply sequence name
        if 'seqFile' in quickPick and 'seqDir' in quickPick:
            for awg in self.instruments.AWGs:
                awg.seqFile = os.path.normpath(os.path.join(config.AWGDir, quickPick['seqDir'],
                                 '{}-{}{}'.format(quickPick['seqFile'], awg.name, awg.seqFileExt)))

        #Apply sweep info
        if 'sweeps' in quickPick:
            for sweep in quickPick['sweeps']:
                if sweep in self.sweeps.sweepDict:
                    for k,v in quickPick['sweeps'][sweep].items():
                        setattr(self.sweeps.sweepDict[sweep], k, v)
        if 'sweepOrder' in quickPick:
            self.sweeps.sweepOrder = quickPick['sweepOrder']

        #Setup the digitizer number of segments
        if 'nbrSegments' in quickPick:
            self.instruments['scope'].nbrSegments = quickPick['nbrSegments']


if __name__ == '__main__':
    import Libraries

    from ExpSettingsGUI import ExpSettings
    expSettings= ExpSettings(sweeps=Libraries.sweepLib, instruments=Libraries.instrumentLib,
                     measurements=Libraries.measLib,  channels = Libraries.channelLib)

    #If we were passed a scripter file to write to the use it
    parser = argparse.ArgumentParser()
    parser.add_argument('--scripterFile', action='store', dest='scripterFile', default=None)    
    options =  parser.parse_args(sys.argv[1:])
    if options.scripterFile:
        expSettings.curFileName = options.scripterFile

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    show_simple_view(ExpSettingsView(expSettings=expSettings))





