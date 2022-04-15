from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class SimulationForm(forms.Form):
	max_iterations = forms.IntegerField(required=False)
	normal_prior_mu = forms.FloatField(required=False)
	normal_prior_sigma = forms.FloatField(required=False)
	lognormal_prior_ev = forms.FloatField(required=False, label='Lognormal prior expectation (not mu!)')
	lognormal_prior_sd = forms.FloatField(required=False, label='Lognormal prior std deviation (not sigma!)')
	study_sd_of_estimator = forms.FloatField(label="Study sd(estimator) (often 'standard error')")
	bar = forms.FloatField()
	force_explicit = forms.BooleanField(required=False)

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
		if not super(SimulationForm, self).is_valid():
			return False

		normal_prior_mu = self.cleaned_data['normal_prior_mu']
		normal_prior_sigma = self.cleaned_data['normal_prior_sigma']
		lognormal_prior_ev = self.cleaned_data['lognormal_prior_ev']
		lognormal_prior_sd = self.cleaned_data['lognormal_prior_sd']

		normal = normal_prior_mu is not None and normal_prior_sigma is not None
		lognormal = lognormal_prior_ev is not None and lognormal_prior_sd is not None

		if normal and lognormal:
			self.add_error(None, "Cannot provide normal and lognormal")
			return False

		if not normal and not lognormal:
			self.add_error(None, "Must provide one of normal or lognormal")
			return False

		return True
