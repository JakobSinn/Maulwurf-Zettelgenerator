from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.generic import ListView

from .forms import StimmzettelEigenschaftenForm, NameFormSet, ExtraFormSet
from .models import Kandidatur
from .stimmzettelgenerator import zetteldrucken, heutestr, bericht


class UniqueGremiumListView(ListView):
    model = Kandidatur
    template_name = 'zettel/index.html'  # Replace with your template
    context_object_name = 'gremium_list'

    def get_queryset(self):
        return Kandidatur.objects.filter(bestaetigt='ja').filter(gewaehlt='noch nicht').values('gremium').distinct()


def KandiView(request, gremiumwanted=''):
    if request.method == 'POST':
        stimmzettel_eigenschaften_form = StimmzettelEigenschaftenForm(request.POST)
        kandidaten_form = NameFormSet(request.POST)

        if not (stimmzettel_eigenschaften_form.is_valid() and kandidaten_form.is_valid()):
            return HttpResponseServerError('Die Eingaben gefallen dem Server nicht.')

        stimmzettel_eigenschaften = stimmzettel_eigenschaften_form.cleaned_data
        kandidaten = [nd.cleaned_data for nd in kandidaten_form if nd.cleaned_data]

        kandidaten_namen = list(map(
            lambda kandidat: kandidat['first_name'] + ' ' + kandidat['last_name'], kandidaten))

        kandidaten_kommentare = list(map(
            lambda kandidat: kandidat['candidate_comment'], kandidaten))

        # Wenn keine Kampfkandidatur vorliegt, wird bei allen Kandidaten mit ja / nein / enth. abgestimmt.
        is_jnewahl = not (len(kandidaten_namen) > stimmzettel_eigenschaften['anzahl_stimmen'])

        if 'willstimmzettel' in request.POST:
            # Stimmzettel generieren" wurde gedrückt
            try:
                response = (HttpResponse(zetteldrucken(kandidaten_namen, stimmzettel_eigenschaften['gremien_name'],
                                                       extras=kandidaten_kommentare,
                                                       stimmen=stimmzettel_eigenschaften['anzahl_stimmen'],
                                                       jne=is_jnewahl),
                                         content_type='application/pdf'))
                response['Content-Disposition'] = "attachment; filename=" + stimmzettel_eigenschaften[
                    'gremien_name'] + heutestr() + 'Stimmzettel.pdf'
                return response
            except:
                return HttpResponseServerError("Leider ist beim Erstellen des Zettels etwas schiefgelaufen, sorry!")
        if 'willbericht' in request.POST:
            # Wakobericht wurde gedrückt
            try:
                response = HttpResponse(
                    bericht(kandidaten=kandidaten_namen, posten=stimmzettel_eigenschaften['gremien_name'],
                            jne=is_jnewahl),
                    content_type='application/pdf')
                response['Content-Disposition'] = "attachment; filename=" + stimmzettel_eigenschaften[
                    'gremien_name'] + heutestr() + 'Berichtvorlage.pdf'
                return response
            except Exception as e: 
                print(e)
                return HttpResponseServerError("Leider ist beim Erstellen des Berichts etwas schiefgelaufen, sorry! " + repr(e))
    else:
        namelist = Kandidatur.objects.filter(bestaetigt='ja').filter(gewaehlt='noch nicht').filter(
            gremium=gremiumwanted)
        initialname = []
        for n in namelist:
            initialname.append(
                {'first_name': n.first_name,
                 'last_name': n.last_name,
                 'candidate_comment': n.fakultaetFachschaft,
                 'lesung': n.lesung or " ACHTUNG: Keine Daten in DB!"
                 }
            )
        initialdata = {'gremien_name': gremiumwanted, 'stimmenzahl': len(initialname)}
        stimmzettel_eigenschaften_form = StimmzettelEigenschaftenForm(initial=initialdata)
        if gremiumwanted:
            kandidaten_form = NameFormSet(initial=initialname)
        else:
            kandidaten_form = ExtraFormSet()
    return render(request, "zettel/form.html",
                  {'DataForm': stimmzettel_eigenschaften_form, 'NameForm': kandidaten_form})
