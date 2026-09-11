"""
Leitor de arquivo CNAB 240 Bradesco (retorno de pagamento).

Baseado no Manual Multipag Bradesco - Layout CNAB 240 Posicoes Bradesco,
Versao 08, revisado em julho/2025.

Uso:
  from leitor_retorno_cnab240_bradesco import ler_retorno
  resultado = ler_retorno("RETORNO_15-09-2026.ret")
  for pag in resultado["pagamentos"]:
      print(pag["id_despesa"], pag["status"], pag["valor_efetivado"])

Estrutura do retorno:
  {
    "arquivo": {
      "banco": "237",
      "data_geracao": "AAAA-MM-DD",
      "cnpj_empresa": "09177564000179",
      "nsa": 42,
    },
    "lotes": [
      {
        "numero": 1,
        "tipo_servico": "20",
        "forma_lancamento": "31",  # boleto outros bancos
        "qtd_registros": 5,
        "soma_valores": 2500.00,
      },
      ...
    ],
    "pagamentos": [
      {
        "lote": 1,
        "seq": 1,
        "segmento": "J" | "A",
        "id_despesa": "DESP-3936629",     # do "seu numero"
        "nosso_numero": "12345678901234",  # atribuido pelo banco
        "favorecido": "FORNECEDOR X",
        "valor_previsto": 500.00,
        "valor_efetivado": 500.00,
        "data_pagamento": "AAAA-MM-DD",
        "data_efetivacao": "AAAA-MM-DD",
        "ocorrencias": ["00"],             # codigos G059
        "status": "pago" | "rejeitado" | "cancelado",
        "descricao_ocorrencias": ["Credito ou Debito Efetivado"],
      },
      ...
    ],
    "resumo": {
      "total_pagamentos": 10,
      "pagos": 8,
      "rejeitados": 2,
      "soma_efetivada": 4500.00,
      "soma_rejeitada": 300.00,
    },
  }
"""

from datetime import datetime

# =====================================================================
# TABELA DE OCORRENCIAS G059
# Extraida do manual Bradesco pag 106-114
# =====================================================================

OCORRENCIAS = {
    "00": "Credito ou Debito Efetivado",
    "01": "Insuficiencia de Fundos - Debito Nao Efetuado",
    "02": "Credito ou Debito Cancelado pelo Pagador/Credor",
    "03": "Debito Autorizado pela Agencia - Efetuado",
    "AA": "Controle Invalido",
    "AB": "Tipo de Operacao Invalido",
    "AC": "Tipo de Servico Invalido",
    "AD": "Forma de Lancamento Invalida",
    "AE": "Tipo/Numero de Inscricao Invalido",
    "AF": "Codigo de Convenio Invalido",
    "AG": "Agencia/Conta Corrente/DV Invalido",
    "AH": "N Sequencial do Registro no Lote Invalido",
    "AI": "Codigo de Segmento de Detalhe Invalido",
    "AJ": "Tipo de Movimento Invalido",
    "AK": "Codigo da Camara de Compensacao do Banco Favorecido/Depositario Invalido",
    "AL": "Codigo do Banco Favorecido Inoperante nesta data ou Depositario Invalido",
    "AM": "Agencia Mantenedora da Conta Corrente do Favorecido Invalida",
    "AN": "Conta Corrente/DV do Favorecido Invalido",
    "AO": "Nome do Favorecido Nao Informado",
    "AP": "Data Lancamento Invalido",
    "AQ": "Tipo/Quantidade da Moeda Invalido",
    "AR": "Valor do Lancamento Invalido",
    "AT": "Tipo/Numero de Inscricao do Favorecido Invalido",
    "AU": "Logradouro do Favorecido Nao Informado",
    "AV": "Numero do Local do Favorecido Nao Informado",
    "AX": "CEP/Complemento do Favorecido Invalido",
    "AY": "Sigla do Estado do Favorecido Invalida",
    "AZ": "Codigo/Nome do Banco Depositario Invalido",
    "BA": "Codigo/Nome da Agencia Depositaria Nao Informado",
    "BB": "Seu Numero Invalido",
    "BC": "Nosso Numero Invalido",
    "BD": "Inclusao Efetuada com Sucesso",
    "BE": "Alteracao Efetuada com Sucesso",
    "BF": "Exclusao Efetuada com Sucesso",
    "BG": "Agencia/Conta Impedida Legalmente",
    "CA": "Codigo de Barras - Codigo do Banco Invalido",
    "CB": "Codigo de Barras - Codigo da Moeda Invalido",
    "CC": "Codigo de Barras - Digito Verificador Geral Invalido",
    "CD": "Codigo de Barras - Valor do Titulo Divergente/Invalido",
    "CE": "Codigo de Barras - Fator de Vencimento Invalido",
    "CF": "Valor do Documento Invalido",
    "CG": "Valor do Abatimento Invalido",
    "CH": "Valor do Desconto Invalido",
    "CI": "Valor do Acrescimo Invalido",
    "CK": "Valor do IR Invalido",
    "CL": "Valor do ISS Invalido",
    "CM": "Valor do IOF Invalido",
    "CN": "Valor de Outras Deducoes Invalido",
    "CO": "Valor de Outros Acrescimos Invalido",
    "CP": "Valor do INSS Invalido",
    "HA": "Lote Nao Aceito",
    "HB": "Inscricao da Empresa Invalida para o Contrato",
    "HC": "Convenio com a Empresa Inexistente/Invalido para o Contrato",
    "HD": "Agencia/Conta Corrente da Empresa Inexistente/Invalido para o Contrato",
    "HE": "Tipo de Servico Invalido para o Contrato",
    "HF": "Conta Corrente da Empresa com Saldo Insuficiente",
    "HG": "Lote de Servico Fora de Sequencia",
    "HH": "Lote de Servico Invalido",
    "TA": "Lote Nao Aceito - Totais do Lote com Diferenca",
    "YA": "Titulo Nao Encontrado",
    "YB": "Identificador Registro Opcional Invalido",
    "YC": "Codigo Padrao Invalido",
    "YD": "Codigo de Ocorrencia Invalido",
    "YE": "Complemento de Ocorrencia Invalido",
    "YF": "Alegacao ja Informada",
    "ZA": "Agencia/Conta do Favorecido Substituida",
}

# Ocorrencias que indicam pagamento efetivado com sucesso
OCORRENCIAS_SUCESSO = {"00", "03", "BD"}


# =====================================================================
# HELPERS
# =====================================================================

def _parse_data(txt):
    """Converte DDMMAAAA em 'AAAA-MM-DD'. Zeros = None."""
    txt = txt.strip()
    if not txt or txt == "00000000" or len(txt) != 8:
        return None
    try:
        dt = datetime.strptime(txt, "%d%m%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def _parse_valor(txt, decimais=2):
    """Converte '000000000050000' em 500.00 (centavos ate 2 decimais)."""
    txt = txt.strip()
    if not txt:
        return 0.0
    try:
        return int(txt) / (10 ** decimais)
    except ValueError:
        return 0.0


def _parse_ocorrencias(txt):
    """Le 10 chars com ate 5 codigos de 2 chars cada."""
    txt = txt.strip()
    codigos = []
    for i in range(0, min(len(txt), 10), 2):
        cod = txt[i:i+2].strip()
        if cod and cod != "00" or (cod == "00" and not codigos):
            # o "00" so entra na lista se for o unico (indicando sucesso)
            codigos.append(cod)
    # remover trailing "00" quando ha outros codigos
    while len(codigos) > 1 and codigos[-1] == "00":
        codigos.pop()
    return codigos


def _classificar_status(ocorrencias):
    """Retorna 'pago', 'rejeitado' ou 'cancelado' com base nas ocorrencias."""
    if not ocorrencias:
        return "sem_ocorrencia"
    if any(o in OCORRENCIAS_SUCESSO for o in ocorrencias):
        return "pago"
    if "02" in ocorrencias:
        return "cancelado"
    return "rejeitado"


def _descricao_ocorrencias(ocorrencias):
    return [OCORRENCIAS.get(o, f"Codigo desconhecido: {o}") for o in ocorrencias]


# =====================================================================
# PARSERS DE LINHA
# =====================================================================

def parse_header_arquivo(linha):
    return {
        "banco": linha[0:3],
        "cnpj_empresa": linha[18:32],
        "convenio": linha[32:52].strip(),
        "agencia": linha[52:57],
        "conta": linha[58:70],
        "nome_empresa": linha[72:102].strip(),
        "data_geracao": _parse_data(linha[143:151]),
        "hora_geracao": linha[151:157],
        "nsa": int(linha[157:163]),
    }


def parse_header_lote(linha):
    return {
        "numero": int(linha[3:7]),
        "tipo_operacao": linha[8],
        "tipo_servico": linha[9:11],
        "forma_lancamento": linha[11:13],
    }


def parse_segmento_a(linha):
    """Segmento A: PIX, TED, Credito em conta."""
    return {
        "seq": int(linha[8:13]),
        "segmento": "A",
        "banco_favorecido": linha[20:23],
        "agencia_favorecido": linha[23:28],
        "conta_favorecido": linha[29:41],
        "favorecido": linha[43:73].strip(),
        "id_despesa": linha[73:93].strip(),   # "seu numero"
        "data_pagamento": _parse_data(linha[93:101]),
        "valor_previsto": _parse_valor(linha[119:134]),
        "nosso_numero": linha[134:154].strip(),
        "data_efetivacao": _parse_data(linha[154:162]),
        "valor_efetivado": _parse_valor(linha[162:177]),
        "ocorrencias": _parse_ocorrencias(linha[230:240]),
    }


def parse_segmento_j(linha):
    """Segmento J: pagamento de boleto."""
    return {
        "seq": int(linha[8:13]),
        "segmento": "J",
        "codigo_barras": linha[17:61],
        "favorecido": linha[61:91].strip(),  # cedente
        "data_vencimento": _parse_data(linha[91:99]),
        "valor_titulo": _parse_valor(linha[99:114]),
        "data_pagamento": _parse_data(linha[144:152]),
        "valor_previsto": _parse_valor(linha[152:167]),
        "valor_efetivado": _parse_valor(linha[152:167]),  # J nao tem valor real separado
        "id_despesa": linha[182:202].strip(),
        "nosso_numero": linha[202:222].strip(),
        "ocorrencias": _parse_ocorrencias(linha[230:240]),
    }


def parse_trailer_lote(linha):
    return {
        "numero": int(linha[3:7]),
        "qtd_registros": int(linha[17:23]),
        "soma_valores": _parse_valor(linha[23:41]),
    }


def parse_trailer_arquivo(linha):
    return {
        "qtd_lotes": int(linha[17:23]),
        "qtd_registros": int(linha[23:29]),
    }


# =====================================================================
# LEITOR PRINCIPAL
# =====================================================================

def ler_retorno(caminho_ou_string):
    """Le um arquivo .ret CNAB 240 Bradesco.

    caminho_ou_string: caminho pra o arquivo OU string com o conteudo.

    Retorna dict com arquivo, lotes, pagamentos e resumo (ver docstring do modulo).
    """
    # aceitar caminho ou conteudo direto
    if isinstance(caminho_ou_string, str) and len(caminho_ou_string) > 500 and "\n" in caminho_ou_string:
        conteudo = caminho_ou_string
    else:
        with open(caminho_ou_string, "r", encoding="latin-1", newline="") as f:
            conteudo = f.read()

    # normalizar quebras de linha
    conteudo = conteudo.replace("\r\n", "\n").replace("\r", "\n")
    linhas = [l for l in conteudo.split("\n") if l]

    resultado = {
        "arquivo": None,
        "lotes": [],
        "pagamentos": [],
    }

    lote_atual = None

    for linha in linhas:
        if len(linha) != 240:
            # linha invalida, pula mas registra
            continue

        tipo = linha[7]

        if tipo == "0":
            # header do arquivo
            resultado["arquivo"] = parse_header_arquivo(linha)

        elif tipo == "1":
            # header do lote
            lote_atual = parse_header_lote(linha)

        elif tipo == "3":
            # detalhe
            segmento = linha[13]
            if segmento == "A":
                pag = parse_segmento_a(linha)
            elif segmento == "J":
                pag = parse_segmento_j(linha)
            else:
                # B, J-52 nao trazem informacao de status/ocorrencia relevante
                # eles complementam A ou J; a ocorrencia principal fica no A/J
                continue

            pag["lote"] = lote_atual["numero"] if lote_atual else 0
            pag["forma_lancamento"] = lote_atual["forma_lancamento"] if lote_atual else "?"
            pag["status"] = _classificar_status(pag["ocorrencias"])
            pag["descricao_ocorrencias"] = _descricao_ocorrencias(pag["ocorrencias"])
            resultado["pagamentos"].append(pag)

        elif tipo == "5":
            # trailer do lote
            trailer = parse_trailer_lote(linha)
            if lote_atual:
                lote_atual.update(trailer)
                resultado["lotes"].append(lote_atual)
            lote_atual = None

        elif tipo == "9":
            # trailer do arquivo, ignorado (nao precisamos)
            pass

    # resumo
    pagos = [p for p in resultado["pagamentos"] if p["status"] == "pago"]
    rejeitados = [p for p in resultado["pagamentos"] if p["status"] == "rejeitado"]
    cancelados = [p for p in resultado["pagamentos"] if p["status"] == "cancelado"]

    resultado["resumo"] = {
        "total_pagamentos": len(resultado["pagamentos"]),
        "pagos": len(pagos),
        "rejeitados": len(rejeitados),
        "cancelados": len(cancelados),
        "soma_efetivada": sum(p["valor_efetivado"] for p in pagos),
        "soma_rejeitada": sum(p["valor_previsto"] for p in rejeitados),
    }

    return resultado


# =====================================================================
# TESTE / DEMO
# =====================================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python leitor_retorno_cnab240_bradesco.py <arquivo.ret>")
        sys.exit(1)

    r = ler_retorno(sys.argv[1])

    print("=== Arquivo ===")
    print(r["arquivo"])
    print()
    print(f"=== {len(r['lotes'])} Lote(s) ===")
    for lote in r["lotes"]:
        print(f"  Lote {lote['numero']}: servico={lote['tipo_servico']}, forma={lote['forma_lancamento']}, "
              f"{lote.get('qtd_registros', '?')} registros, soma R$ {lote.get('soma_valores', 0):.2f}")
    print()
    print(f"=== {len(r['pagamentos'])} Pagamento(s) ===")
    for p in r["pagamentos"]:
        print(f"  L{p['lote']} seq {p['seq']} [{p['segmento']}] "
              f"{p['id_despesa']:20s} R$ {p['valor_efetivado']:>10.2f} "
              f"{p['status']:10s} {'|'.join(p['ocorrencias'])} "
              f"({'; '.join(p['descricao_ocorrencias'])})")
    print()
    print("=== Resumo ===")
    for k, v in r["resumo"].items():
        print(f"  {k}: {v}")
