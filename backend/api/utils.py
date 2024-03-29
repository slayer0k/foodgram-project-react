from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


def get_pdf(results):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposiotion'] = (
        'attachment; filename="shoplist.pdf"'
    )
    file = Canvas(response, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', './FreeSans.ttf'))
    file.setFont('FreeSans', 30)
    file.drawString(200, 750, 'Список покупок')
    file.setFont('FreeSans', 18)
    file.drawString(
        0, 730, '---------------------------------------------------'
        '-----------------------------------------------------------'
    )
    y = 700
    x = 1
    for obj in results:
        file.drawString(
            50, y,
            f"{x}. {obj['recipe__recipeingredients__ingredient__name']}: "
            f"{obj['count']} "
            f"{obj['recipe__recipeingredients__ingredient__measuring_unit']}"
        )
        y -= 20
        x += 1
    file.showPage()
    file.save()
    return response
