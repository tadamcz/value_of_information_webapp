import math

from boltons.dictutils import FrozenDict


def freeze(obj):
	"""
	Source (MIT license): https://github.com/zelaznik/frozen_dict/blob/master/freeze_recursive.py

	Recursive function which turns dictionaries into
	FrozenDict objects, lists into tuples, and sets
	into frozensets.

	Can also be used to turn JSON data into a hasahable value.
	"""

	try:
		# See if the object is hashable
		hash(obj)
		return obj
	except TypeError:
		pass

	try:
		# Try to see if this is a mapping
		try:
			obj[tuple(obj)]
		except KeyError:
			is_mapping = True
		else:
			is_mapping = False
	except (TypeError, IndexError):
		is_mapping = False

	if is_mapping:
		frz = {k: freeze(obj[k]) for k in obj}
		return FrozenDict(frz)

	# See if the object is a set like
	# or sequence like object
	try:
		obj[0]
		cls = tuple
	except TypeError:
		cls = frozenset
	except IndexError:
		cls = tuple

	try:
		itr = iter(obj)
		is_iterable = True
	except TypeError:
		is_iterable = False

	if is_iterable:
		return cls(freeze(i) for i in obj)

	msg = 'Unsupported type: %r' % type(obj).__name__
	raise TypeError(msg)


def lognormal_mu_sigma(mean, sd):
	"""
	todo: add tests!

	exp(mu + sigma^2/2) = mean
	(exp(sigma^2) -1)*exp(2*mu + sigma^2) = var

	Take logs:

	mu+sigma^2/2 = ln(mean)
	ln(exp(sigma^2) -1) + 2*mu + sigma^2 = ln(var)

	Substitute the first into the second:
	ln(exp(sigma^2) -1) + 2*ln(mean) = ln(var)
	ln(exp(sigma^2) -1) = ln(var) - 2*ln(mean)
	exp(sigma^2) = exp(ln(var) - 2*ln(mean)) + 1
	exp(sigma^2) = var/(mean^2) + 1
	sigma^2 = ln(var/(mean^2) + 1)
	sigma = sqrt(ln(var/(mean^2) + 1))


	Hence:
	mu = ln(mean) - sigma^2/2
	mu = ln(mean) - (1/2) * ln(var/(mean^2) + 1)


	Summary:
	sigma = sqrt(ln(var/(mean^2) + 1))
	mu = ln(mean) - (1/2) * ln(var/(mean^2) + 1)
	"""

	var = sd ** 2
	sigma = math.sqrt(math.log(var / (mean ** 2) + 1))

	mu = math.log(mean) - (1 / 2) * math.log(var / (mean ** 2) + 1)

	return mu, sigma
