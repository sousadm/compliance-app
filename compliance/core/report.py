# -*- coding: utf-8 -*-
import json
import os
from platform import python_version
import pyreportjasper
from django.http import FileResponse, Http404
from pyreportjasper import PyReportJasper

from compliance.core.models import Tarefa, Cliente, Evento


# def ImprimirPDF():
#     REPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'reports')
#     input_file = os.path.join(REPORTS_DIR, 'teste.jrxml')
#     output_file = os.path.join(REPORTS_DIR, 'teste')
#     pyreportjasper = PyReportJasper()
#     pyreportjasper.config(
#         input_file,
#         output_file,
#         output_formats=["pdf"]
#     )
#     pyreportjasper.process_report()


def json_to_pdf():
    # input_file = os.path.dirname(os.path.abspath(__file__)) + '/reports/tarefa.jrxml'
    # output_file = 'c:/tmp/tarefa.pdf'
    # json_query = 'tarefa'
    data_file = os.path.dirname(os.path.abspath(__file__)) + '/tarefa.json'
    tarefa = Tarefa.objects.get(pk=92)
    with open(data_file, 'w') as f:
        json.dump(tarefa.json(), f)

    # conn = {
    #     'driver': 'json',
    #     'data_file': data_file,
    #     'json_query': json_query
    # }
    # pyreportjasper = PyReportJasper()
    # pyreportjasper.config(
    #     input_file,
    #     output_file,
    #     output_formats=["pdf"],
    #     db_connection=conn,
    #     resource=data_file,
    #     parameters={
    #         'data': 'data_file'
    #     },
    # )
    # pyreportjasper.process_report()
    # print('Result is the file below.')
    # print(output_file + '.pdf')


def pdf_view(request):
    try:
        arquivo = 'C:/Tmp/tarefa_20210318042304.pdf'
        return FileResponse(open(arquivo, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()