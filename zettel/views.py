from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.generic import ListView

from .forms import *
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
        einzelform = DataForm(request.POST)
        namenform = NameFormSet(request.POST)

        if not (einzelform.is_valid() and namenform.is_valid()):
            return

        einzeldaten = einzelform.cleaned_data
        namensdaten = [nd.cleaned_data for nd in namenform if nd.cleaned_data]

        namestrs = []
        extrastrs = []

        extrasdrucken = False
        for name in namensdaten:
            if name['firstname']:
                namestrs.append(name['firstname'] + ' ' + name['lastname'])
                extrastrs.append(name['extratext'])
                if name['extratext']:
                    extrasdrucken = True

        jnemachen = not (len(namestrs) > einzeldaten['stimmenzahl'])

        if 'willstimmzettel' in request.POST:
            # Stimmzettel generieren" wurde gedrückt
            try:
                response = HttpResponse(zetteldrucken(namestrs, einzeldaten['gremiumname'], extras=extrastrs,
                                                      stimmen=einzeldaten['stimmenzahl'], jne=jnemachen),
                                        content_type='application/pdf')
                response['Content-Disposition'] = "attachment; filename=" + einzeldaten[
                    'gremiumname'] + heutestr() + 'Stimmzettel.pdf'
                return response
            except:
                return HttpResponseServerError("Leider ist beim Erstellen des Zettels etwas schiefgelaufen, sorry!")
        if 'willbericht' in request.POST:
            # Wakobericht wurde gedrückt
            try:
                response = HttpResponse(
                    bericht(kandidaten=namestrs, posten=einzeldaten['gremiumname'], jne=jnemachen),
                    content_type='application/pdf')
                response['Content-Disposition'] = "attachment; filename=" + einzeldaten[
                    'gremiumname'] + heutestr() + 'Berichtvorlage.pdf'
                return response
            except:
                return HttpResponseServerError(
                    "Leider ist beim Erstellen des Berichts etwas schiefgelaufen, sorry!")
    else:
        namelist = Kandidatur.objects.filter(bestaetigt='ja').filter(gewaehlt='noch nicht').filter(
            gremium=gremiumwanted)
        initialname = []
        for n in namelist:
            initialname.append(
                {'firstname': n.first_name,
                 'lastname': n.last_name,
                 'extratext': n.fakultaetFachschaft,
                 'lesung': n.lesung or " ACHTUNG: Keine Daten in DB!"
                 }
            )
        initialdata = {'gremiumname': gremiumwanted, 'stimmenzahl': len(initialname)}
        einzelform = DataForm(initial=initialdata)
        if gremiumwanted:
            namenform = NameFormSet(initial=initialname)
        else:
            namenform = ExtraFormSet()
    return render(request, "zettel/form.html", {'DataForm': einzelform, 'NameForm': namenform})
