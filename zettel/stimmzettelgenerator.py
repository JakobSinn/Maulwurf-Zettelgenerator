import os
from datetime import datetime
from django.templatetags.static import static
from django.conf import settings
from fpdf import FPDF

# strings, die später noch gebraucht werden
def heutestr():
    return datetime.today().strftime('%d.%m.%y')


def belehrstr(stimmen: int, multipage=False):
    s = "Du hast "
    if multipage: s += "auf dem **gesamten Zettel** "
    if stimmen == 1:
        s += "eine Stimme."
    else:
        s += (str(stimmen) + ' Stimmen.')
    return s


# funktionen, die in pdf gewisse elemente einfuegen
def jnestr(pdf, y, abstand=12, x=120):
    # Ja/Nein/Enthaltung drucken
    pdf.set_font("helvetica", "", 10)
    pdf.text((x + 2 - (2 * abstand)), y, text="Ja")
    pdf.text((x + 1 - abstand), y, text="Nein")
    pdf.text(x + 1, y, text="Enth.")


def linkeinfuegen(pdf):
    # Fügt, wenn platz ist, den qr code unten in den zettel ein
    pdf.set_font("helvetica", "I", 12)
    if pdf.get_y() < 175:  # Frage: haben wir noch einen Platz für den Hinweis zum QR-Code?
        pdf.set_y(185)
        pdf.set_x(25)
        pdf.multi_cell(w=70, text='Bewerbungsschreiben sind aus dem Uninetz heraus abrufbar unter:')
        qr_path = static("qrcode.svg")
        pdf.image(qr_path, x=100, y=pdf.get_y() - 20, w=30)


def header(pdf, datum, stimmgegenstand):
    # Kopfzeile des Zettels mit Logo, Datum, und zu Abstimmungsgegenstand
    pdf.set_font("helvetica", "B", 14)
    pdf.text(20, 20, "Stimmzettel")
    pdf.set_font("helvetica", "", 12)
    pdf.text(20, 26, "erstellt am " + datum)
    if len(stimmgegenstand) < 28:  # Kurze Bezeichnungen werden größer gesetzt
        pdf.set_font("helvetica", "B", 26)
    else:
        pdf.set_font("helvetica", "B", 18)
    pdf.set_y(33)
    pdf.multi_cell(w=0, text=stimmgegenstand)
    logo_path = static("StuRa_Logo_sw_RGB.svg")
    pdf.image(logo_path, x=70, y=12, h=15)
    pdf.ln(3)


def stimmbelehrung(pdf, jne=False):
    pdf.set_font("helvetica", "I", 12)
    if jne:
        pdf.multi_cell(new_y="LAST", markdown=True, w=0,
                       text="Nur ordentlich stimmberechtigte Mitglieder (grüne Stimmkarte) und korrekt angemeldete Stellvertreter:innen dürfen abstimmen. In jeder Zeile ist entweder **Ja**, **Nein**, oder **Enthaltung** anzukreuzen.")
        pdf.ln(20)
    else:
        pdf.multi_cell(w=0,
                       text="Nur ordentlich stimmberechtigte Mitglieder (grüne Stimmkarte) und korrekt angemeldete Stellvertreter:innen dürfen abstimmen.")
        pdf.ln(15)


def namendrucken(pdf, namen: list[str], breite, extra=[], start=1):
    assert len(namen) > 0, "Stimmzettel ohne Namen soll gedruckt werden"
    extradrucken = (len(namen) == len(extra))
    ymiddle = []
    for nr in range(len(namen)):
        pdf.set_x(20)
        obery = pdf.get_y() - 5
        pdf.line(x1=20, x2=130, y1=obery, y2=obery)
        pdf.set_font("helvetica", "B", 14)
        pdf.multi_cell(w=breite, text=str(nr + start) + " " + namen[nr], align="L")
        if extradrucken and extra[nr]:
            pdf.ln(0.1)
            pdf.set_x(30)
            pdf.set_font("helvetica", "", 12)
            pdf.multi_cell(w=breite - 10, text=extra[nr], align="L")
        pdf.ln(9)
        untery = pdf.get_y() - 5
        ymiddle.append(obery + (untery - obery) / 2)
    pdf.line(x1=20, x2=130, y1=pdf.get_y() - 5, y2=pdf.get_y() - 5)
    return ymiddle


def stimmbereichdrucken(pdf, kandidaten, jne: bool, extra=[], start=1):
    if jne:
        stimmy = namendrucken(pdf, kandidaten, breite=65, extra=extra, start=start)
        for i in stimmy:
            dreistimmfelder(pdf, i)
    else:
        stimmy = namendrucken(pdf, kandidaten, breite=90, extra=extra, start=start)
        for i in stimmy:
            stimmfeld(pdf, i)


def textueberfelder(pdf, jne, stimmen=1, felderabstand=12):
    if jne:
        jnestr(pdf, y=pdf.get_y() - 7, abstand=felderabstand, x=115)
    else:
        pdf.set_font("helvetica", "I", 12)
        pdf.text(95, pdf.get_y() - 8, text=belehrstr(stimmen))


def stimmfeld(pdf, y, x=120):
    pdf.circle(x=x, y=y, radius=5)


def dreistimmfelder(pdf, y, abstand=12, x=120):
    for i in range(3):
        xhier = x - (i * abstand)
        stimmfeld(pdf, y, x=xhier)


def stimmzettel(pdf, kandidaten: list[str], posten: str, jne: bool, stimmen=1, datum=heutestr(), extras=[],
                printbel=True):
    felderabstand = 12
    zahlkandi = len(kandidaten)
    assert stimmen > 0, "Mitglieder sollten mindestens eine Stimme haben"
    assert zahlkandi > 0, "Mindesten eine Option sollte auf dem Zettel stehen"
    pdf.set_auto_page_break(False, margin=0)
    pdf.add_page()
    header(pdf, datum, posten)
    if printbel:
        stimmbelehrung(pdf, jne=jne)
    else:
        pdf.ln(15)  # Damit wenn keine belehrung gedruckt wird die texte nicht ineinander rutschen
    # Text über den Kästchen
    textueberfelder(pdf, jne, stimmen, felderabstand)
    # teil mit den namen drucken
    stimmbereichdrucken(pdf, kandidaten, jne=jne, extra=extras)
    if (pdf.get_y() > 205):
        return False
    else:
        linkeinfuegen(pdf)
        return pdf


def stimmzettelzwei(pdf, kandidaten: list[str], jne: bool, count, extras=[]):
    print("Stimmzettelzwei hat als extras bekommen: " + str(extras))
    felderabstand = 12
    zahlkandi = len(kandidaten)
    assert zahlkandi > 0, "Mindesten eine Option sollte auf dem Zettel stehen"
    pdf.set_auto_page_break(False, margin=0)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.set_y(15)
    pdf.multi_cell(w=0,
                   border=1,
                   align='C',
                   text="Nicht Abtrennen! Dieser Stimmzettel ist A4!")
    # Text über den Kästchen
    pdf.ln()
    if jne:
        pdf.ln(8)
        textueberfelder(pdf, jne, 1, felderabstand)
    else:
        pdf.ln(-2)
        pdf.set_font("helvetica", "I", 14)
        pdf.cell(w=0, align='C', text='Die Stimmenzahl gilt für beide Spalten zusammen.')
        pdf.ln(14)
    # teil mit den namen drucken
    stimmbereichdrucken(pdf, kandidaten, jne=jne, extra=extras, start=count)
    if (pdf.get_y() > 205):
        return False
    else:
        try:
            linkeinfuegen(pdf)
        except:
            pass
        return pdf


# stimmzettel managment
def zetteldrucken(kandidaten, posten, datum=heutestr(), jne=False, stimmen=1, printbel=True, extras=[]):
    druckbar = len(kandidaten)
    if druckbar > 11: druckbar = 11  # spart zu langes suchen nach noch druckbarem zettel
    while True:
        testpdf = FPDF(format="A5")
        resultbin = stimmzettel(testpdf, kandidaten[:druckbar], posten, jne=jne, stimmen=stimmen, printbel=printbel, extras=extras[:druckbar])
        if resultbin:
            break
        else:
            druckbar = druckbar - 1
    # druckbar enthält jetzt die zahl an Einträgen, die auf die erste seite passen
    print("Es sollen " + str(len(kandidaten)) + " Zeilen gedruckt werden, davon passen " + str(
        druckbar) + " auf die erste Seite.")
    outpdf = FPDF(format="A5")
    if druckbar == len(kandidaten):
        print("Doppeltes pdf ausgeben...")
        stimmzettel(outpdf, kandidaten, posten, jne=jne, stimmen=stimmen, printbel=printbel, extras=extras)
        stimmzettel(outpdf, kandidaten, posten, jne=jne, stimmen=stimmen, printbel=printbel, extras=extras)
    else:
        print("Großen Stimmzettel ausgeben...")
        stimmzettel(outpdf, kandidaten[:druckbar], posten, jne=jne, stimmen=stimmen, extras=extras[:druckbar], printbel=printbel)
        assert stimmzettelzwei(outpdf, kandidaten[druckbar:], jne=jne, extras=extras[druckbar:], 
                               count=druckbar + 1), "Stimmzettel passt nicht auf zwei seiten"
    return bytes(outpdf.output())


def bericht(kandidaten=[], posten="_________________", jne=False):
    # PDF generieren
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()
    # Kopfzeile des Zettels mit Logo, Datum, und zu Abstimmungsgegenstand
    logo_path = static("StuRa_Logo_sw_RGB.svg")
    pdf.image(logo_path, x=100, y=12, h=25)
    pdf.set_font("helvetica", "B", 22)
    pdf.set_y(12)
    pdf.multi_cell(w=80, text="Ergebnis einer Wahl im StuRa", align="C", border=1, padding=5)
    pdf.set_y(40)
    pdf.set_font("helvetica", "", size=16)
    pdf.write_html(
        text="<p style=\"line-height:1.5\"\\>In der Sitzung vom [  &#160&#160  ] <b>" + heutestr() + "</b> [ &#160&#160  ] ______________ wurde vom Studierendenrat in das Gremium / auf den Posten <b>" + posten + "</b> gewählt. Es wurden ______ Stimmzettel abegegeben, davon ______ ungültig. <br> <br>Ergebnis:</p>")
    # Hier wird die tabelle gedruckt
    if jne:
        with pdf.table(text_align="CENTER", col_widths=(3, 1, 1, 1.5, 1.2)) as table:
            row = table.row()
            row.cell("Name")
            row.cell("Ja")
            row.cell("Nein")
            row.cell("Enthaltung")
            row.cell("Gewählt")
            for name in kandidaten:
                row = table.row()
                row.cell(name)
                row.cell("")
                row.cell("")
                row.cell("")
                row.cell("")
    else:
        with pdf.table(text_align="CENTER", col_widths=(5, 1, 1)) as table:
            row = table.row()
            row.cell("Name")
            row.cell("Stimmen")
            row.cell("Gewählt")
            for name in kandidaten:
                row = table.row()
                row.cell(name)
                row.cell("")
                row.cell("")
    # Hier der text unter der Tabelle
    pdf.ln()
    pdf.write(text="Anwesende Mitglieder der Wahlkommission oder des Präsidiums:")
    pdf.ln(20)
    pdf.write_html(
        text="<p style=\"line-height:1.5\"\\><b>Unterschriften der Auzählenden</b> (mindestens ein Mitglied von WaKo oder Präsidium muss an der Auszählung beteiligt sein):</p>")
    pdf.ln(20)
    return bytes(pdf.output())
