import contextlib
import io

from value_of_information import Simulation

def simulation_to_io(simulation: Simulation, **kwargs):
    with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
        simulation.run(**kwargs)
        return buffer.getvalue()
