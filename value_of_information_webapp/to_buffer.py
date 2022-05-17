import contextlib
import io
from typing import Callable


def to_buffer(_callable: Callable, callable_args=None, callable_kwargs=None):
	if callable_args is None:
		callable_args = tuple()
	if callable_kwargs is None:
		callable_kwargs = {}

	with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
		return_value = _callable(*callable_args, **callable_kwargs)
		return {"text_buffer": buffer.getvalue(), "return_value": return_value}
