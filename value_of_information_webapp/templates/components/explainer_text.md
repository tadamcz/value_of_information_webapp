{% load static %}

### Introduction

When we gain information about a decision-relevant quantity, that information may improve the decision we ultimately
make. The value of the (expected) improvement in the decision is
the [value of information](https://en.wikipedia.org/wiki/Value_of_information) (VOI).

Sometimes, the information we gain tells us that one action is _certain_ to be better than another (for example, knowing
that tails came up in a coin toss implies we should bet on tails). But often the information is imperfect, and can only
pull our decision in the direction of optimality, in expectation.

Such imperfect information can be modelled as observing a random variable (or signal) `B` that is informative about the
true state of the world `T` but contains some noise. The expected value of information is the expected benefit from
observing this random variable.

The realised value of information is:

```
VOI(T,B) = U(decision(B), T) - U(decision_0, T) 
```

where `U` is the payoff function, `decision` is the decision function when we have access to the signal, and `decision_0` is the decision we make in the absence of the signal.

If a signal of `B` fails to change our decision, the value we realised is zero (regardless of `T`). This is intuitive.

When the signal does change our decision, the size of the benefit depends on the true state `T`, and on our decision
function `decision`, which in turn depends on how the distribution of `B` is related to `T`.

For each `T=t`, the expected value of information is

```
VOI(t) = E_B[VOI(T,B) | T=t] = E_B[U(decision(B), T) - U(decision_0, T) | T=t]
```

where `E_B` indicates that we're taking expectations with respect to (i.e. over the distribution of) `B`.

We can then find the entirely unconditional expected VOI `V` by taking expectations of the above with respect to `T`:

```
V = E_T[ E_B[VOI(t,b) | T=t]] 
```

Of course we might also, by the law of iterated expectations, write `V=E[VOI(t,b)]`, where the expectation sign without a subscript means the expectation is taken with respect to the joint distribution of `T` and `B`. 


### Model details

We make some simplifying assumptions:

* We model the decision problem as a binary choice between:
    * **the bar** (`d_1`): an option with an expected payoff of `bar` about which we cannot gain additional information. Expressed mathematically, the inability to gain additional information means that `U(d_1, T)` is independent of `T`. So we can write `E[U(d_1)]=bar`. (It's
      irrelevant whether or not there is uncertainty over the payoff `U(d_1)`, what matters here is that this uncertainty is independent of `T` so we cannot gain additional information).
    * **the object of study** (`d_2`): an uncertain option whose payoff is `T`, about which we can gain additional information.
* The decision-maker is rational, i.e. upon receiving a signal of `B=b` they update their prior `P(T)` to `P(T|B=b)`. They risk-neutrally maximise expected `U`, which means they choose the object of study if and only if `E[T|B=b]>bar` (or `E[T]>bar` in the absence of the signal).
* The problem is one-dimensional, i.e. `T` and `B` follow one-dimensional distributions.
* Currently, only one distribution family is supported for `B`: `B` has a normal distribution with unknown mean `T` and
  known standard deviation.
* On this website, the prior over `T` must be normal, log-normal, or [metalog](https://github.com/tadamcz/metalogistic). The underlying Python package supports any prior
  specified as a one-dimensional SciPy continuous distribution.

This tool uses a simulation to approximate the expectation mentioned in the previous section. Specifically, for each
iteration `i` of the simulation:

1. We draw a true value `t_i` from the decision-maker's prior `P(T)`.
2. We draw an estimate `b_i` from `Normal(t_i,sd(B))`.
3. We can then calculate the decision that would be made with and without access to the signal:
    * _With the signal._ The decision-maker's subjective posterior expected value is `E[T|b_i]`. If `E[T|b_i]>bar`, the
      decision-maker chooses the object of study, otherwise they choose the bar.
    * _Without the signal._ If `E[T]>bar`, the decision-maker chooses the object of study, otherwise they choose the
      bar.
5. We calculate the decision-maker's payoffs with and without access to the signal. If choosing the object of study,
   they get a payoff of `T_i`; the payoff for the bar is `bar`.

Drawing `t_i` corresponds to the outer expectation `E_T[]` discussed above, and drawing `b_i` (dependent on `t_i`) corresponds to the inner expectation `E_B[]`.

#### Remarks
Astute readers will have noticed another simplification. In calculating `V`, we take expectations over `T` according to the decision maker's prior `P(T)` (this is because `T_i`s
are drawn from `P(T)` in step 1). In a subjective bayesian sense, this means that we compute the expected VOI by the
lights of the decision-maker; a frequentist interpretation might be that the decision situation is drawn from a larger
reference class in which `T` follows `P(T)`, and we are computing the average VOI in that class.

These concepts need not coincide in general. We could without difficulty model the decision-maker as acting according
to `P(T)`, but nonetheless compute the value of information by the lights of another actor who believes `Q(T)` (or the
VOI in a reference class following `Q(T)`).

Analogously, `V` is calculated according to the same values as the decision-maker's values, i.e. it is modeled from a risk-neutral `U`-maximisation perspective, but this need not be so. (Technically this assumption is already present in the first section of this document).

### Computational shortcut: skipping the decision-maker's Bayesian update
We make use of the following fact: 

> When the signal `B` is normally distributed, with
mean `T`, then, for any prior distribution over `T`, `E[T|B=b]` is increasing in `b`.
 
This was shown by [Andrews et al. 1972]({% static 'pdf/andrews1972.pdf' %}) (Lemma 1).

In these cases, instead of explicitly computing the posterior for every `b`-value, we
1. First run a numerical equation solver to find the threshold value `b_*` ("b-star"), such that `E[T|B=b]>bar` if and only if `b>b_*`.
2. Then, simply compare subsequent `b`-values to `b_*`.

This is hundreds of times faster than explicitly computing the posterior probability distribution `P(T|B=b)` for each iteartion.

The shortcut can be disabled by selecting `explicit_bayes`.

### Cost-benefit analysis
The cost-benefit analysis assumes:

- "Choosing" the bar or the object of study means spending one's capital implementing that option. The amount of capital may vary.
- `T` and `bar` are expressed in terms of value realised _per unit of capital_. For example, "deaths averted per million dollars" or "new clients per dollar".
- The decision-maker can choose to spend `signal_cost` to acquire the signal. All other capital is spent implementing the option with the highest expected value.

This model is well-suited when choosing between different options that can absorb flexible amounts of capital (e.g. venture capital, ad spend, or philanthropy). However, it should be easy to model the costs and benefits differently yourself, while still using the VOI simulation, which is more generally applicable.