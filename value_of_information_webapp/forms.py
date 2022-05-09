from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class SimulationForm(forms.Form):
	max_iterations = forms.IntegerField(required=False)
	normal_prior_ev = forms.FloatField(required=False, label='Normal prior expectation')
	normal_prior_sd = forms.FloatField(required=False, label='Normal prior s.d.')
	lognormal_prior_ev = forms.FloatField(required=False, label='Lognormal prior expectation')
	lognormal_prior_sd = forms.FloatField(required=False, label='Lognormal prior s.d.')
	signal_sd = forms.FloatField(label="Signal standard deviation")
	bar = forms.FloatField()
	force_explicit = forms.BooleanField(required=False, label_suffix="")

	normal_prior_ev.math_expr = "E[T]"
	normal_prior_sd.math_expr = "sd(T)"
	lognormal_prior_ev.math_expr = "E[T]"
	lognormal_prior_sd.math_expr = "sd(T)"
	signal_sd.math_expr = "sd(B)"

	signal_sd.explainer_text = "For example, if the signal is a regression coefficient from a sample, this is the standard " \
							 "deviation of the estimator for that coefficient. This is often called the standard error of " \
							 "the coefficient."

	lognormal_prior_ev.explainer_text = "Be careful, this is not the `mu` parameter. `mu` is the expected value of `T`'s " \
										"logarithm "
	lognormal_prior_sd.explainer_text = "Be careful, this is not the `sigma` parameter. `sigma` is the standard deviation " \
										"of `T`'s logarithm "

	@staticmethod
	def initial():
		return {
			'max_iterations': 10_000,
			'lognormal_prior_ev': 5,
			'lognormal_prior_sd': 4,
			'signal_sd': 2,
			'bar': 7,
			'force_explicit': False,
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = 'submit_parameters'
		self.helper.add_input(Submit('submit', 'Submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col'
		self.helper.field_class = 'col'

	def is_valid(self) -> bool:
		is_valid = True
		if not super(SimulationForm, self).is_valid():
			is_valid = False

		normal_prior_mu = self.cleaned_data['normal_prior_ev']
		normal_prior_sigma = self.cleaned_data['normal_prior_sd']
		lognormal_prior_ev = self.cleaned_data['lognormal_prior_ev']
		lognormal_prior_sd = self.cleaned_data['lognormal_prior_sd']
		force_explicit = self.cleaned_data['force_explicit']
		max_iterations = self.cleaned_data['max_iterations']

		normal = normal_prior_mu is not None and normal_prior_sigma is not None
		lognormal = lognormal_prior_ev is not None and lognormal_prior_sd is not None

		if normal and lognormal:
			self.add_error(None, "Cannot provide normal and lognormal")
			is_valid = False

		if not normal and not lognormal:
			self.add_error(None, "Must provide one of normal or lognormal")
			is_valid = False

		if max_iterations is not None:
			max_iterations_max_allowed = 1800
			if force_explicit and max_iterations > max_iterations_max_allowed:
				self.add_error(None, f"When 'force explicit' is enabled, "
									 f"you cannot set max iterations to more than {max_iterations_max_allowed}, "
									 f"because it could take hours to run.")
				is_valid = False

		return is_valid


class CostBenefitForm(forms.Form):
	value_units = forms.CharField(required=False,
								  widget=forms.TextInput(attrs={
									  'placeholder': "For example: 'utils', 'multiples of GiveDirectly', or 'lives saved'"}))
	money_units = forms.CharField(required=False,
								  widget=forms.TextInput(attrs={'placeholder': 'For example: "$" or "M$", or "£"'}))
	capital = forms.FloatField(required=False)
	signal_cost = forms.FloatField(required=False, label='Cost to acquire signal')

	@staticmethod
	def initial():
		return {
			'value_units': 'utils',
			'money_units': 'M$',
			'capital': 100,
			'signal_cost': 5,
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = 'submit_parameters'
		self.helper.add_input(Submit('submit', 'Submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col'
		self.helper.field_class = 'col'

	def is_valid(self) -> bool:
		is_valid = True
		if not super(CostBenefitForm, self).is_valid():
			is_valid = False

		if not (self.is_full() or self.is_empty()):
			is_valid = False
			self.add_error(None, "Must provide either all fields or no fields")

		return is_valid

	def is_empty(self):
		inputs = list(self.cleaned_data.values())
		none_or_empty_str = inputs.count(None) + inputs.count("")
		return none_or_empty_str == len(inputs)

	def is_full(self):
		inputs = list(self.cleaned_data.values())
		none_or_empty_str = inputs.count(None) + inputs.count("")
		return none_or_empty_str == 0
