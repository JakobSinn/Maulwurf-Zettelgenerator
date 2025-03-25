from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe

class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(value) if value is not None else 'N/A'

class NameForm(forms.Form):
    firstname = forms.CharField(max_length=50, required=False, label="Vorname")
    lastname = forms.CharField(max_length=50, required=False, label="Nachname", help_text="Optional")
    extratext = forms.CharField(max_length=100, label="Anmerkungen", help_text="Wird kleiner gedruckt", required=False)
    lesung = forms.CharField(max_length=400, widget=PlainTextWidget, required=False, disabled=True, label="Lesung: ")

NameFormSet = formset_factory(NameForm, extra=5)

class DataForm(forms.Form):
    gremiumname = forms.CharField(max_length=200, help_text="Name des zu besetzenden Gremiums oder Postens", label="Zetteltitel")
    stimmenzahl = forms.IntegerField(max_value=50, min_value=1, help_text="Stimmen, die auf diesem Zettel erwartet werden", initial=1)





