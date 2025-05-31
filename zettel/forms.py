from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe
from datetime import datetime


class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(value) if value is not None else 'N/A'


class NameForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False, label="Vorname")
    last_name = forms.CharField(max_length=50, required=False, label="Nachname", help_text="Optional")
    candidate_comment = forms.CharField(max_length=100, label="Anmerkungen", help_text="Wird kleiner gedruckt",
                                        required=False)

    lesung = forms.CharField(max_length=400, widget=PlainTextWidget, required=False, disabled=True, label="Lesung: ")


class StimmzettelEigenschaftenForm(forms.Form):
    gremien_name = forms.CharField(max_length=200, help_text="Name des zu besetzenden Gremiums oder Postens",
                                   label="Zetteltitel")
    anzahl_stimmen = forms.IntegerField(max_value=50, min_value=1,
                                        help_text="Stimmen, die auf diesem Zettel erwartet werden", initial=1)
    abstimmung_datum = forms.DateField(label="Abstimmungsdatum", initial=datetime.today())


NameFormSet = formset_factory(NameForm, extra=2)

ExtraFormSet = formset_factory(NameForm, extra=10)
