from traits.api import HasTraits, List, Instance, Float, Dict, Str, Property, on_trait_change, Any

import json

from Instrument import Instrument
import MicrowaveSources
import AWGs
import FileWatcher

class InstrumentLibrary(HasTraits):
    #All the instruments are stored as a dictionary keyed of the instrument name
    instrDict = Dict(Str, Instrument)
    libFile = Str(transient=True)

    #Some helpers to pull out certain types of instruments
    AWGs = Property(List, depends_on='instrDict[]')
    sources = Property(List, depends_on='instrDict[]')

    fileWatcher = Any(None, transient=True)

    def __init__(self, **kwargs):
        super(InstrumentLibrary, self).__init__(**kwargs)
        self.load_from_library()
        if self.libFile:
            self.fileWatcher = FileWatcher.LibraryFileWatcher(self.libFile, self.update_from_file)

    #Overload [] to allow direct pulling of channel info
    def __getitem__(self, instrName):
        return self.instrDict[instrName]

    @on_trait_change('instrDict.anytrait')
    def write_to_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            #Pause the file watcher to stop cicular updating insanity
            if self.fileWatcher:
                self.fileWatcher.pause()
            with open(self.libFile,'w') as FID:
                json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)
            if self.fileWatcher:
                self.fileWatcher.resume()

    def load_from_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=JSONHelpers.LibraryDecoder)
                    if isinstance(tmpLib, InstrumentLibrary):
                        self.instrDict.update(tmpLib.instrDict)
            except IOError:
                print('No instrument library found')
            except ValueError:
                print('Failed to load instrument library')

    def update_from_file(self):
        """
        Only update relevant parameters
        Helps avoid stale references by replacing whole channel objects as in load_from_library
        and the overhead of recreating everything.
        """
        if self.libFile:
            with open(self.libFile, 'r') as FID:
                try:
                    allParams = json.load(FID)['instrDict']
                except ValueError:
                    print('Failed to update instrument library from file.  Probably just half-written.')
                    return
                for instrName, instrParams in allParams.items():
                    if instrName in self.instrDict:
                        #Update AWG offsets'
                        if isinstance(self.instrDict[instrName], AWGs.AWG):
                            for ct in range(self.instrDict[instrName].numChannels):
                                self.instrDict[instrName].channels[ct].offset = instrParams['channels'][ct]['offset']


    #Getter for AWG list
    def _get_AWGs(self):
        return sorted([instr for instr in self.instrDict.values() if isinstance(instr, AWGs.AWG)], key = lambda instr : instr.name)

    #Getter for microwave source list
    def _get_sources(self):
        return sorted([instr for instr in self.instrDict.values() if isinstance(instr, MicrowaveSources.MicrowaveSource)], key = lambda instr : instr.name)

if __name__ == '__main__':
    import enaml
    from enaml.stdlib.sessions import show_simple_view

    from Libraries import instrumentLib
    with enaml.imports():
        from InstrumentManagerView import InstrumentManagerWindow
    show_simple_view(InstrumentManagerWindow(instrLib=instrumentLib))








    
    
