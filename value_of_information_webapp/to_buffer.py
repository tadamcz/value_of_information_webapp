import contextlib
import io

from value_of_information.simulation import SimulationExecutor
from value_of_information.study_cost_benefit import CostBenefitsExecutor


def to_buffer(sim_executor: SimulationExecutor, c_b_executor: CostBenefitsExecutor, **kwargs):
    with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
        if kwargs['max_iterations'] is None:
            kwargs.pop('max_iterations')
        sim_run = sim_executor.execute(**kwargs)
        if c_b_executor is not None:
            c_b_executor.sim_run = sim_run
            c_b_executor.execute()
        return buffer.getvalue()
