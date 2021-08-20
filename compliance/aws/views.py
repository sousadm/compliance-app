import urllib

import boto3
from boto.s3.connection import S3Connection

import compliance.settings as conf
from compliance import settings


def get_nome(arquivo):
    nome = arquivo[::-1]
    x = nome.find('/')
    nome = nome[:x][::-1]
    return nome


def getKeyRetorno(folder, key):
    tipo = 'folder' if key.name[-1:] == '/' else 'file'
    if tipo == 'folder':
        classe = 'fas fa-folder-open'
    elif '.pdf' in key.name:
        classe = 'fas fa-file-pdf'
    elif '.doc' in key.name:
        classe = 'fas fa-file-word'
    elif ('.xls' in key.name) or ('.ods' in key.name):
        classe = 'fas fa-file-excel'
    else:
        classe = 'fas fa-cloud-download-alt'
    if '.zip' in key.name:
        tipo = 'zip'
    return {
        "name": key.name,
        "folder": folder,
        "arquivo": get_nome(key.name),
        "url": urllib.parse.quote_plus(key.name),
        "tipo": tipo,
        "classe": classe
    }


def get_s3_filename_list(directory):
    conn = S3Connection(conf.AWS_ACCESS_KEY_ID, conf.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(conf.AWS_STORAGE_BUCKET_NAME)
    retorno = []
    lista = bucket.list(prefix=directory, delimiter="/")
    for key in lista:
        if key.name[-1:] == '/':
            retorno.append(getKeyRetorno(directory, key))
    for key in lista:
        if key.name[-1:] != '/':
            retorno.append(getKeyRetorno(directory, key))
    return retorno


def handle_uploaded_file(nome, f):
    with open(nome, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def s3_client():
    # "region_name": getenv("AWS_REGION"),
    boto_kwargs = {
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    }
    return boto3.session.Session(**boto_kwargs).client('s3')


def s3_upload_small_files(inp_file_name, s3_bucket_name, inp_file_key, content_type):
    client = s3_client()
    upload_file_response = client.put_object(Body=inp_file_name,
                                             Bucket=s3_bucket_name,
                                             Key=inp_file_key,
                                             ContentType=content_type)
    return upload_file_response


def s3_delete_file(s3_bucket_name, inp_file_key):
    client = s3_client()
    delete_file_response = client.delete_object(Bucket=s3_bucket_name, Key=inp_file_key)
    return delete_file_response
