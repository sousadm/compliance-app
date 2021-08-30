# -*- coding: utf-8 -*-
import json
import os
from django.http import FileResponse, Http404
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from compliance.core.models import Tarefa, Cliente, Evento


def json_to_pdf():
    data_file = os.path.dirname(os.path.abspath(__file__)) + '/tarefa.json'
    tarefa = Tarefa.objects.get(pk=92)
    with open(data_file, 'w') as f:
        json.dump(tarefa.json(), f)


def pdf_view(request):
    try:
        arquivo = 'C:/Tmp/tarefa_20210318042304.pdf'
        return FileResponse(open(arquivo, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
