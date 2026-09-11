"""Gera arquivo .rem de teste com dados REAIS da Silva & Silva Advogados.

Falta apenas o convenio de pagamento, que sera fornecido pelo Bradesco
quando o servico Multipag for contratado. Enquanto isso, mantemos o
placeholder de 20 noves.
"""

from datetime import datetime
from gerador_cnab240_bradesco import gerar_cnab240

# ========== EMPRESA (dados REAIS) ==========
empresa = {
    "cnpj": "09177564000179",
    "nome_reduzido": "SILVA E SILVA ADVOGADOS ASSOCIADOS",
    # PLACEHOLDER - Bradesco entrega quando o servico Multipag for contratado
    # Ver Bradesco Net Empresa > Servicos > Multipag, ou perguntar ao gerente
    "convenio": "99999999999999999999",
    "agencia": "02149",
    "agencia_dv": "",
    "conta": "000000014339",
    "conta_dv": "1",
    "ag_conta_dv": "",
    "endereco": {
        "logradouro": "RUA 428",
        "numero": 15,
        "complemento": "",
        "bairro": "MORRETES",
        "cidade": "ITAPEMA",
        "cep": 88220,        # CEP aproximado, confirmar
        "cep_sufixo": "000",
        "uf": "SC",
    },
}

# ========== BOLETO REAL (fornecido pela Ana) ==========
# Digitavel original: 23790.13101 96254.000308 03021.197607 5 15710000010605
# Decodificado:
#   Banco: 237 (Bradesco)
#   Valor: R$ 106,05
#   Vencimento (fator 1571 base 07/10/1997): 25/01/2002 (data antiga, OK pra teste)
#   Codigo de barras 44 dig: 23795157100000106050131096254000300302119760
boleto_real = {
    "forma": "boleto",
    "favorecido": "BENEFICIARIO DO BOLETO",
    "cnpj_favorecido": "00000000000000",
    "codigo_barras": "23795157100000106050131096254000300302119760",
    "data_vencimento": "2002-01-25",  # extraido do fator de vencimento
    "data_pagamento": "2026-09-11",   # data de hoje
    "valor_titulo": 106.05,
    "valor_pagamento": 106.05,
    "seu_numero": "DESP-BOLETO-REAL-01",
    "cedente": {
        "tipo_inscricao": 2,
        "cnpj_cpf": "00000000000000",
        "nome": "BENEFICIARIO DO BOLETO",
    },
}

# ========== BOLETO 2 (mesmo do real, valor diferente pra somatoria variada) ==========
boleto_extra = {
    "forma": "boleto",
    "favorecido": "FORNECEDOR EXEMPLO LTDA",
    "cnpj_favorecido": "12345678000199",
    "codigo_barras": "23795157100000050000131096254000300302119760",
    "data_vencimento": "2002-01-25",
    "data_pagamento": "2026-09-11",
    "valor_titulo": 500.00,
    "valor_pagamento": 500.00,
    "seu_numero": "DESP-BOLETO-02",
    "cedente": {
        "tipo_inscricao": 2,
        "cnpj_cpf": "12345678000199",
        "nome": "FORNECEDOR EXEMPLO LTDA",
    },
}

# ========== PIX ==========
pix_chave_cnpj = {
    "forma": "pix",
    "favorecido": "PRESTADOR SERVICOS LTDA",
    "cnpj_favorecido": "11222333000144",
    "tipo_inscricao_favorecido": 2,
    "tipo_chave_pix": "cpf_cnpj",
    "chave_pix": "11222333000144",
    "ispb_favorecido": "60746948",   # ISPB do Bradesco (exemplo)
    "tipo_conta_favorecido": "01",
    "data_pagamento": "2026-09-11",
    "valor_pagamento": 800.00,
    "seu_numero": "DESP-PIX-01",
    "identificacao_pagamento": "Pagamento servicos setembro",
}

# ========== TED ==========
ted = {
    "forma": "ted",
    "favorecido": "JOAO DA SILVA CONSULTORIA",
    "cpf_favorecido": "12345678909",
    "tipo_inscricao_favorecido": 1,
    "banco_favorecido": "341",       # Itau
    "agencia_favorecido": "01234",
    "agencia_dv_favorecido": "",
    "conta_favorecido": "000000567890",
    "conta_dv_favorecido": "1",
    "data_pagamento": "2026-09-11",
    "valor_pagamento": 1500.00,
    "seu_numero": "DESP-TED-01",
    "finalidade_ted": "00003",       # pagamento a fornecedor
    "endereco_favorecido": {
        "logradouro": "AV BRASIL",
        "numero": 200,
        "complemento": "SALA 10",
        "bairro": "CENTRO",
        "cidade": "SAO PAULO",
        "cep": 1000,
        "cep_sufixo": "000",
        "uf": "SP",
    },
    "mensagem": "Honorarios setembro",
}

# ========== GERAR ==========
despesas = [boleto_real, boleto_extra, pix_chave_cnpj, ted]

arquivo = gerar_cnab240(
    despesas=despesas,
    empresa=empresa,
    nsa=1,
    data_geracao=datetime(2026, 9, 11, 18, 0, 0),
)

nome = "REMESSA_TESTE_BRADESCO_11-09-2026_v5.rem"
with open(nome, "w", encoding="latin-1", newline="") as f:
    f.write(arquivo)

print(f"Arquivo gerado: {nome}")
print(f"Total linhas: {arquivo.count(chr(10))}")
print(f"Total bytes: {len(arquivo.encode('latin-1'))}")
print()
print("=== Resumo do conteudo ===")
total = sum(float(d['valor_pagamento']) for d in despesas)
print(f"  Boletos: 2 (R$ {sum(float(d['valor_pagamento']) for d in despesas if d['forma']=='boleto'):.2f})")
print(f"  PIX: 1 (R$ {sum(float(d['valor_pagamento']) for d in despesas if d['forma']=='pix'):.2f})")
print(f"  TED: 1 (R$ {sum(float(d['valor_pagamento']) for d in despesas if d['forma']=='ted'):.2f})")
print(f"  TOTAL: R$ {total:.2f}")
print()
print("=== Preview das linhas ===")
linhas = arquivo.splitlines()
for i, linha in enumerate(linhas, 1):
    tipo = linha[7]
    seg = linha[13] if len(linha) > 13 else ""
    label = {
        "0": "Header Arquivo",
        "1": "Header Lote",
        "3": f"Detalhe ({seg})",
        "5": "Trailer Lote",
        "9": "Trailer Arquivo",
    }.get(tipo, "???")
    print(f"L{i:02d} [{label:20s}] len={len(linha)}")
