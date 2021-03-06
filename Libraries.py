"""
Holds all the library instances as the one singleton copy.
"""

import config
from instruments.InstrumentManager import InstrumentLibrary
from QGL.Channels import ChannelLibrary
from Sweeps import SweepLibrary
from MeasFilters import MeasFilterLibrary

instrumentLib = InstrumentLibrary(libFile=config.instrumentLibFile)
channelLib = ChannelLibrary(libFile=config.channelLibFile)
sweepLib = SweepLibrary(libFile=config.sweepLibFile)
measLib = MeasFilterLibrary(libFile=config.measurementLibFile)

