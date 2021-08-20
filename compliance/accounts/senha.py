import secrets
import string
import uuid
from datetime import datetime

from compliance.core.models import Cliente


def gerar_senha_letras(comprimento):
    """Gerar uma senha com letras, com o comprimento informado
    :param comprimento: Comprimento da senha
    :return: Senha gerada
    """
    password_characters = string.ascii_letters
    password = ''.join(secrets.choice(password_characters) for i in range(comprimento))
    return password


def gerar_senha_letras_numeros(comprimento):
    """Gerar uma senha com letras e números, com o comprimento informado
    :param comprimento: Comprimento da senha
    :return: Senha gerada
    """
    password_characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(password_characters) for i in range(comprimento))
    return password


def gerar_senha_letras_numeros_simbolos(comprimento):
    """Gerar uma senha com letras, números e símbolos, com o comprimento informado
    :param comprimento: Comprimento da senha
    :return: Senha gerada
    """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(password_characters) for i in range(comprimento))
    return password


def gerar_senha_hexadecimal(metade_comprimento):
    """Gerar uma senha hexadecimal, sendo o comprimento igual o dobro
    :param metade_comprimento: Comprimento da senha
    :return: Senha gerada
    """
    password = secrets.token_hex(metade_comprimento)
    return password


def gerar_senha_uuid():
    """Gerar uma senha com UUID com 36 caracteres
    :return:
    """
    password = uuid.uuid4()
    return password


# if __name__ == '__main__':
#     """Função principal do script que gera senhas em Python"""
#     senha = gerar_senha_letras(16)
#     print(senha)
#
#     senha = gerar_senha_letras_numeros(16)
#     print(senha)
#
#     senha = gerar_senha_letras_numeros_simbolos(16)
#     print(senha)
#
#     senha = gerar_senha_hexadecimal(12)
#     print(senha)
#
#     senha = gerar_senha_uuid()
#     print(senha)


def gerarNumeroSerie(cliente, vencimento):
    # StartDate = "27/06/2021"
    # vencimento = datetime.strptime(StartDate, "%d/%m/%Y")
    # cnpj = '03654469000132'
    # cliente = Cliente.objects.get(pk=pk)

    cnpj = cliente.cnpj
    strdireta = '0123456789'
    strinversa = '7931582406'
    p0 = 0

    i = 0
    while i < len(cnpj):
        c1 = cnpj[i:i + 1]
        pos1 = strdireta.index(c1)
        c2 = strinversa[pos1:pos1 + 1]
        p0 += int(c2)
        i += 1

    p2 = vencimento.strftime("%d")
    p3 = vencimento.strftime("%m")
    p4 = str(vencimento.strftime("%Y"))[:2]
    p5 = vencimento.strftime("%y")

    p1 = p4 + p2 + p5 + p3
    p11 = p5 + p4 + p3 + p2

    xx = 0
    m = 1
    while m <= len(p11):
        if m / 2 - int(m / 2) > 0:
            xx += int(p11[m - 1:m]) * int(p3)
        else:
            xx += int(p11[m - 1:m]) * int(p2)
        if xx < 0:
            xx = 0
        m += 1

    p0x = p0 + xx

    px = ''
    i = 0
    while i < len(p1):
        c1 = p1[i:i + 1]
        pos1 = strdireta.index(c1)
        px = px + strinversa[pos1:pos1 + 1]
        i += 1

    i = 1
    soma = 0
    inverso = px[::-1]
    while i <= len(inverso):
        soma += int(inverso[i - 1:i]) * (i + 1)
        i += 1

    if (11 - (soma % 11)) >= 10:
        dig = 0
    else:
        dig = 11 - (soma % 11)

    if cliente.nivel == 'C':
        digito = int(datetime.now().strftime("%d")) % 10
        cod_venc = str(px) + str(dig) + '-' + str(p0x) + str(digito)
    else:
        cod_venc = str(px) + str(dig) + '-' + str(p0x)
    # cliente.serie = cod_venc
    # cliente.serie_dt = vencimento
    # cliente.save()

    return cod_venc