import contextlib
import io

from value_of_information.simulation import SimulationExecutor

def executor_to_io(executor: SimulationExecutor, **kwargs):
    with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
        if kwargs['max_iterations'] is None:
            kwargs.pop('max_iterations')
        executor.execute(**kwargs)
        return buffer.getvalue()
