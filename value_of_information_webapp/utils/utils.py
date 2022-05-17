import math


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
