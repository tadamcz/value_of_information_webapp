import contextlib
import io
from typing import Callable

from value_of_information.utils import print_wrapped


def to_buffer(_callable: Callable, callable_args=None, callable_kwargs=None):
	if callable_args is None:
		callable_args = tuple()
	if callable_kwargs is None:
		callable_kwargs = {}

	with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
		try:
			return_value = _callable(*callable_args, **callable_kwargs)
			success = True
		except Exception as e:
			# Any uncaught errors that reach this point simply get printed. Because we're not re-raising the
			# exceptions (which would cause the buffer to get lost) we need to explicitly return a 'success' key.
			print_wrapped(f"{type(e).__name__}: {e}")
			return_value = None
			success = False
		return {"success": success, "text_buffer": buffer.getvalue(), "return_value": return_value}
