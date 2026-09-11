"""
Gerador de arquivo CNAB 240 Bradesco (remessa de pagamento).

Baseado no Manual de Procedimentos Multipag Bradesco - Layout CNAB 240
Posicoes Bradesco, Versao 08, revisado em julho/2025.

Ver LAYOUT.md nesse repositorio para detalhes tecnicos de cada campo.

Suporta 3 tipos de pagamento (na ordem de prioridade do BPO):
  1. Boleto (Segmento J + J-52)
  2. PIX (Segmento A + B com formatacao PIX)
  3. TED (Segmento A + B)

Uso:
  from gerador_cnab240_bradesco import gerar_cnab240
  arquivo = gerar_cnab240(despesas=[...], empresa={...}, nsa=1)
  with open('remessa.rem', 'w', encoding='latin-1', newline='\\n') as f:
      f.write(arquivo)

Depois testar no Multipag Bradesco antes de subir ao banco.
"""

import unicodedata
from datetime import datetime
from typing import Iterable

# =====================================================================
# CONSTANTES
# =====================================================================

BANCO_BRADESCO = "237"
LINE_LEN = 240

# Tipo de Servico (G025)
SERV_PAG_FORNECEDOR = "20"

# Forma de Lancamento (G029)
FORMA_CREDITO_CONTA = "01"
FORMA_TITULO_MESMO_BANCO = "30"
FORMA_TITULO_OUTROS_BANCOS = "31"
FORMA_TED_OUTRA_TITULARIDADE = "41"
FORMA_TED_MESMA_TITULARIDADE = "43"
FORMA_PIX_TRANSFERENCIA = "45"
FORMA_PIX_QRCODE = "47"

# Layout do Lote (G030)
LAYOUT_LOTE_BOLETO = "040"
LAYOUT_LOTE_PAGAMENTO = "045"

# Camara Centralizadora (P001)
CAMARA_TED = "018"
CAMARA_CREDITO_CONTA = "000"

# Finalidade TED (P011)
FINALIDADE_PAG_FORNECEDOR = "00003"
FINALIDADE_CREDITO_CONTA = "00001"


# =====================================================================
# HELPERS DE FORMATACAO
# =====================================================================

def _remover_acentos(texto: str) -> str:
    """Remove acentos, cedilhas e similares."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def num(valor, tamanho: int) -> str:
    """Formata campo numerico: zeros a esquerda, tamanho exato."""
    if valor is None:
        s = "0"
    elif isinstance(valor, (int, float)):
        s = str(int(valor))
    else:
        s = "".join(c for c in str(valor) if c.isdigit())
        if not s:
            s = "0"
    s = s.zfill(tamanho)
    if len(s) > tamanho:
        raise ValueError(f"num overflow: valor {valor!r} > tamanho {tamanho}")
    return s


def alfa(texto, tamanho: int) -> str:
    """Formata campo alfanumerico: espacos a direita, sem acento, upper."""
    if texto is None:
        texto = ""
    t = _remover_acentos(str(texto)).upper()
    # substituir caracteres nao ascii por espaco
    t = "".join(c if 32 <= ord(c) < 127 else " " for c in t)
    t = t.ljust(tamanho)[:tamanho]
    return t


def brancos(tamanho: int) -> str:
    return " " * tamanho


def zeros(tamanho: int) -> str:
    return "0" * tamanho


def valor_centavos(valor_reais, tamanho: int = 15) -> str:
    """Converte R$ 1234.56 em '000000000123456' com tamanho especificado."""
    if valor_reais is None:
        cent = 0
    else:
        cent = int(round(float(valor_reais) * 100))
    return num(cent, tamanho)


def data_ddmmaaaa(dt) -> str:
    """Converte date/datetime/string em DDMMAAAA."""
    if dt is None:
        return "00000000"
    if isinstance(dt, str):
        # aceitar "AAAA-MM-DD" ou "DD/MM/AAAA"
        if "-" in dt:
            dt = datetime.strptime(dt[:10], "%Y-%m-%d")
        elif "/" in dt:
            dt = datetime.strptime(dt[:10], "%d/%m/%Y")
        else:
            raise ValueError(f"Formato de data desconhecido: {dt!r}")
    return dt.strftime("%d%m%Y")


def hora_hhmmss(dt) -> str:
    if dt is None:
        return "000000"
    return dt.strftime("%H%M%S")


def _assert_line(line: str, contexto: str = "linha") -> str:
    if len(line) != LINE_LEN:
        raise ValueError(
            f"{contexto} com tamanho invalido: {len(line)} (esperado {LINE_LEN})"
        )
    return line


# =====================================================================
# REGISTROS
# =====================================================================

def monta_header_arquivo(empresa: dict, nsa: int, data_geracao: datetime) -> str:
    """Header do Arquivo (Tipo 0). Uma linha, 240 caracteres."""
    partes = [
        BANCO_BRADESCO,                                       # 1-3
        "0000",                                               # 4-7 lote
        "0",                                                  # 8 tipo registro
        brancos(9),                                           # 9-17 uso febraban
        "2",                                                  # 18 tipo inscricao (CNPJ)
        num(empresa["cnpj"], 14),                             # 19-32 CNPJ
        alfa(empresa["convenio"], 20),                        # 33-52 convenio
        num(empresa["agencia"], 5),                           # 53-57 agencia
        alfa(empresa.get("agencia_dv", ""), 1),               # 58 DV agencia
        num(empresa["conta"], 12),                            # 59-70 conta
        alfa(empresa["conta_dv"], 1),                         # 71 DV conta
        alfa(empresa.get("ag_conta_dv", ""), 1),              # 72 DV ag/conta
        alfa(empresa["nome_reduzido"], 30),                   # 73-102 nome empresa
        alfa("BANCO BRADESCO", 30),                           # 103-132 nome banco
        brancos(10),                                          # 133-142 uso febraban
        "1",                                                  # 143 remessa
        data_ddmmaaaa(data_geracao),                          # 144-151 data
        hora_hhmmss(data_geracao),                            # 152-157 hora
        num(nsa, 6),                                          # 158-163 NSA
        "089",                                                # 164-166 versao layout
        "01600",                                              # 167-171 densidade
        brancos(20),                                          # 172-191 reservado banco
        brancos(20),                                          # 192-211 reservado empresa
        brancos(29),                                          # 212-240 uso febraban
    ]
    linha = "".join(partes)
    return _assert_line(linha, "header arquivo")


def monta_header_lote(
    empresa: dict,
    lote: int,
    forma_lancamento: str,
    layout_lote: str,
    mensagem: str = "",
) -> str:
    """Header do Lote (Tipo 1). Uma linha, 240 caracteres.

    forma_lancamento: '30' boleto mesmo banco, '31' boleto outros,
                      '41'/'43' TED, '45' PIX transferencia, '47' PIX QRCode
    layout_lote: '040' para boleto, '045' para outros
    """
    endereco = empresa.get("endereco", {})

    # Header de lote pra boleto tem 8 posicoes de uso febraban no fim (223-230)
    # pra outros tem 6 posicoes + 2 posicoes de "Indicativo de Forma de Pagamento"
    is_boleto = layout_lote == LAYOUT_LOTE_BOLETO

    partes = [
        BANCO_BRADESCO,                                       # 1-3
        num(lote, 4),                                         # 4-7
        "1",                                                  # 8 tipo registro
        "C",                                                  # 9 operacao credito
        SERV_PAG_FORNECEDOR,                                  # 10-11 tipo servico
        forma_lancamento,                                     # 12-13 forma lancamento
        layout_lote,                                          # 14-16 versao layout lote
        brancos(1),                                           # 17 uso febraban
        "2",                                                  # 18 tipo inscricao CNPJ
        num(empresa["cnpj"], 14),                             # 19-32
        alfa(empresa["convenio"], 20),                        # 33-52
        num(empresa["agencia"], 5),                           # 53-57
        alfa(empresa.get("agencia_dv", ""), 1),               # 58
        num(empresa["conta"], 12),                            # 59-70
        alfa(empresa["conta_dv"], 1),                         # 71
        alfa(empresa.get("ag_conta_dv", ""), 1),              # 72
        alfa(empresa["nome_reduzido"], 30),                   # 73-102
        alfa(mensagem, 40),                                   # 103-142 mensagem
        alfa(endereco.get("logradouro", ""), 30),             # 143-172
        num(endereco.get("numero", 0), 5),                    # 173-177
        alfa(endereco.get("complemento", ""), 15),            # 178-192
        alfa(endereco.get("cidade", ""), 20),                 # 193-212
        num(endereco.get("cep", 0), 5),                       # 213-217
        alfa(endereco.get("cep_sufixo", ""), 3),              # 218-220
        alfa(endereco.get("uf", "SC"), 2),                    # 221-222
    ]
    # 223-240 varia:
    if is_boleto:
        partes.extend([
            brancos(8),                                       # 223-230
            brancos(10),                                      # 231-240 ocorrencias
        ])
    else:
        partes.extend([
            "01",                                             # 223-224 indicativo
            brancos(6),                                       # 225-230
            brancos(10),                                      # 231-240 ocorrencias
        ])

    linha = "".join(partes)
    return _assert_line(linha, f"header lote {lote}")


def monta_segmento_j(
    lote: int,
    seq: int,
    despesa: dict,
) -> str:
    """Segmento J (Detalhe de pagamento de boleto)."""
    partes = [
        BANCO_BRADESCO,                                       # 1-3
        num(lote, 4),                                         # 4-7
        "3",                                                  # 8 tipo registro
        num(seq, 5),                                          # 9-13
        "J",                                                  # 14 segmento
        "0",                                                  # 15 tipo movimento (inclusao)
        "00",                                                 # 16-17 codigo instrucao
        num(despesa["codigo_barras"], 44),                    # 18-61 codigo de barras
        alfa(despesa["favorecido"], 30),                      # 62-91 nome cedente
        data_ddmmaaaa(despesa.get("data_vencimento")),        # 92-99 vencimento
        valor_centavos(despesa["valor_titulo"], 15),          # 100-114 valor titulo
        valor_centavos(despesa.get("desconto_abatimento", 0), 15),  # 115-129
        valor_centavos(despesa.get("mora_multa", 0), 15),     # 130-144
        data_ddmmaaaa(despesa["data_pagamento"]),             # 145-152
        valor_centavos(despesa["valor_pagamento"], 15),       # 153-167
        zeros(15),                                            # 168-182 quantidade moeda
        alfa(despesa.get("seu_numero", ""), 20),              # 183-202 referencia
        brancos(20),                                          # 203-222 nosso numero (retorno)
        "09",                                                 # 223-224 moeda BRL
        brancos(6),                                           # 225-230
        brancos(10),                                          # 231-240 ocorrencias
    ]
    linha = "".join(partes)
    return _assert_line(linha, f"segmento J lote {lote} seq {seq}")


def monta_segmento_j52(
    lote: int,
    seq: int,
    despesa: dict,
    empresa: dict,
) -> str:
    """Segmento J-52 (complemento obrigatorio ao J com dados de sacado/cedente/sacador)."""
    cedente = despesa.get("cedente", {})

    partes = [
        BANCO_BRADESCO,                                       # 1-3
        num(lote, 4),                                         # 4-7
        "3",                                                  # 8 tipo registro
        num(seq, 5),                                          # 9-13
        "J",                                                  # 14 segmento
        brancos(1),                                           # 15 uso febraban
        "00",                                                 # 16-17 codigo movimento
        "52",                                                 # 18-19 identificacao registro
        "2",                                                  # 20 tipo inscricao sacado (CNPJ)
        num(empresa["cnpj"], 15),                             # 21-35
        alfa(empresa["nome_reduzido"], 40),                   # 36-75
        num(cedente.get("tipo_inscricao", 2), 1),             # 76 tipo inscricao cedente
        num(cedente.get("cnpj_cpf", 0), 15),                  # 77-91
        alfa(cedente.get("nome", despesa["favorecido"]), 40), # 92-131
        num(cedente.get("tipo_inscricao_sacador", cedente.get("tipo_inscricao", 2)), 1),  # 132
        num(cedente.get("cnpj_cpf_sacador", cedente.get("cnpj_cpf", 0)), 15),  # 133-147
        alfa(cedente.get("nome_sacador", cedente.get("nome", despesa["favorecido"])), 40),  # 148-187
        brancos(53),                                          # 188-240
    ]
    linha = "".join(partes)
    return _assert_line(linha, f"segmento J-52 lote {lote} seq {seq}")


def monta_trailer_lote(
    lote: int,
    qtd_registros: int,
    soma_valores_reais,
) -> str:
    """Trailer do Lote (Tipo 5). Uma linha, 240 caracteres.

    qtd_registros = 1 (header lote) + N (detalhes) + 1 (trailer lote)
    soma_valores_reais = soma dos valores de pagamento do lote, em reais
    """
    partes = [
        BANCO_BRADESCO,                                       # 1-3
        num(lote, 4),                                         # 4-7
        "5",                                                  # 8 tipo registro
        brancos(9),                                           # 9-17
        num(qtd_registros, 6),                                # 18-23
        valor_centavos(soma_valores_reais, 18),               # 24-41 somatoria valor
        zeros(18),                                            # 42-59 somatoria moeda
        zeros(6),                                             # 60-65 aviso debito
        brancos(165),                                         # 66-230
        brancos(10),                                          # 231-240
    ]
    linha = "".join(partes)
    return _assert_line(linha, f"trailer lote {lote}")


def monta_trailer_arquivo(qtd_lotes: int, qtd_registros_total: int) -> str:
    """Trailer do Arquivo (Tipo 9). Uma linha, 240 caracteres."""
    partes = [
        BANCO_BRADESCO,                                       # 1-3
        "9999",                                               # 4-7
        "9",                                                  # 8
        brancos(9),                                           # 9-17
        num(qtd_lotes, 6),                                    # 18-23
        num(qtd_registros_total, 6),                          # 24-29
        zeros(6),                                             # 30-35 contas concil
        brancos(205),                                         # 36-240
    ]
    linha = "".join(partes)
    return _assert_line(linha, "trailer arquivo")


# =====================================================================
# ORQUESTRADOR
# =====================================================================

def gerar_lote_boletos(empresa: dict, lote: int, despesas: list) -> tuple:
    """Gera todas as linhas de um lote de boletos.
    Retorna (linhas, qtd_registros_lote, soma_valores).
    """
    linhas = []
    linhas.append(monta_header_lote(
        empresa=empresa,
        lote=lote,
        forma_lancamento=FORMA_TITULO_OUTROS_BANCOS,
        layout_lote=LAYOUT_LOTE_BOLETO,
    ))

    seq = 0
    soma = 0.0
    for d in despesas:
        seq += 1
        linhas.append(monta_segmento_j(lote, seq, d))
        seq += 1
        linhas.append(monta_segmento_j52(lote, seq, d, empresa))
        soma += float(d["valor_pagamento"])

    # trailer do lote: qtd = 1 header + N detalhes + 1 trailer
    qtd_registros = 2 + (2 * len(despesas))
    linhas.append(monta_trailer_lote(lote, qtd_registros, soma))
    return linhas, qtd_registros, soma


def gerar_cnab240(
    despesas: list,
    empresa: dict,
    nsa: int,
    data_geracao: datetime = None,
) -> str:
    """
    despesas: lista de dicts. Cada dict deve ter:
      forma: 'boleto' | 'pix' | 'ted'
      favorecido: nome (str)
      cnpj_favorecido ou cpf_favorecido: str
      valor_pagamento: float (em reais)
      data_pagamento: datetime ou 'AAAA-MM-DD'
      seu_numero: str (id da despesa no EasyJur)
      # para BOLETO:
      codigo_barras: str (44 dig)
      data_vencimento: datetime ou str
      valor_titulo: float
      desconto_abatimento: float (opcional)
      mora_multa: float (opcional)
      cedente: dict com tipo_inscricao, cnpj_cpf, nome

    empresa: dict com:
      cnpj, nome_reduzido, convenio, agencia, agencia_dv,
      conta, conta_dv, ag_conta_dv, endereco (dict com logradouro,
      numero, complemento, cidade, cep, cep_sufixo, uf)

    nsa: numero sequencial do arquivo (int, incremental)
    data_geracao: datetime (default: agora)

    Retorna string com o arquivo inteiro (linhas separadas por \\n).
    """
    if data_geracao is None:
        data_geracao = datetime.now()

    linhas = []
    linhas.append(monta_header_arquivo(empresa, nsa, data_geracao))

    # separar despesas por tipo
    boletos = [d for d in despesas if d.get("forma") == "boleto"]
    pix = [d for d in despesas if d.get("forma") == "pix"]
    ted = [d for d in despesas if d.get("forma") == "ted"]

    qtd_lotes = 0
    lote = 0

    if boletos:
        lote += 1
        qtd_lotes += 1
        lote_linhas, _, _ = gerar_lote_boletos(empresa, lote, boletos)
        linhas.extend(lote_linhas)

    # PIX e TED: implementar nas proximas iteracoes
    if pix:
        raise NotImplementedError("Lote de PIX ainda nao implementado (proxima iteracao).")
    if ted:
        raise NotImplementedError("Lote de TED ainda nao implementado (proxima iteracao).")

    # trailer do arquivo
    # qtd_registros = header arquivo (1) + todas linhas de lotes + trailer arquivo (1)
    # linhas ate agora = 1 (header) + linhas dos lotes
    qtd_registros_total = len(linhas) + 1  # +1 do trailer que vamos adicionar
    linhas.append(monta_trailer_arquivo(qtd_lotes, qtd_registros_total))

    # Bradesco exige CRLF ao final de cada linha (Windows line endings).
    # Sem isso o Multipag reclama "delimitador (finalizador) de linhas nao localizado".
    return "\r\n".join(linhas) + "\r\n"


# =====================================================================
# TESTE RAPIDO
# =====================================================================

if __name__ == "__main__":
    # exemplo minimo pra testar visualmente
    empresa_teste = {
        "cnpj": "09177564000179",
        "nome_reduzido": "SILVA E SILVA ADVOGADOS ASSOCIADOS",
        "convenio": "99999999999999999999",
        "agencia": "02149",
        "agencia_dv": "",
        "conta": "000000014339",
        "conta_dv": "1",
        "ag_conta_dv": "",
        "endereco": {
            "logradouro": "RUA JOAO PESSOA",
            "numero": 100,
            "complemento": "SALA 1",
            "cidade": "FLORIANOPOLIS",
            "cep": 88010,
            "cep_sufixo": "000",
            "uf": "SC",
        },
    }

    despesa_teste = {
        "forma": "boleto",
        "favorecido": "FORNECEDOR TESTE LTDA",
        "cnpj_favorecido": "12345678000199",
        "codigo_barras": "23791234500000123456789012345678901234567890",  # 44 digitos
        "data_vencimento": "2026-09-15",
        "data_pagamento": "2026-09-15",
        "valor_titulo": 500.00,
        "valor_pagamento": 500.00,
        "desconto_abatimento": 0,
        "mora_multa": 0,
        "seu_numero": "DESP-3936629",
        "cedente": {
            "tipo_inscricao": 2,
            "cnpj_cpf": "12345678000199",
            "nome": "FORNECEDOR TESTE LTDA",
        },
    }

    arquivo = gerar_cnab240(
        despesas=[despesa_teste],
        empresa=empresa_teste,
        nsa=1,
        data_geracao=datetime(2026, 9, 11, 14, 30, 0),
    )
    print(arquivo)
    print("---")
    for i, linha in enumerate(arquivo.strip().split("\n"), 1):
        print(f"Linha {i}: {len(linha)} chars, tipo pos8={linha[7]}, segmento pos14={linha[13]}")
