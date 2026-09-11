"""Gera arquivo .rem de teste com Boleto + PIX + TED pra rodar no Multipag."""

from datetime import datetime
from gerador_cnab240_bradesco import gerar_cnab240

empresa_teste = {
    "cnpj": "09177564000179",
    "nome_reduzido": "SILVA E SILVA ADVOGADOS ASSOCIADOS",
    "convenio": "99999999999999999999",  # PLACEHOLDER - substituir pelo convenio real
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

# ========== BOLETOS ==========
boleto1 = {
    "forma": "boleto",
    "favorecido": "FORNECEDOR ALFA LTDA",
    "cnpj_favorecido": "12345678000199",
    "codigo_barras": "23791234500000500001234567890123456789012345",
    "data_vencimento": "2026-09-15",
    "data_pagamento": "2026-09-15",
    "valor_titulo": 500.00,
    "valor_pagamento": 500.00,
    "seu_numero": "DESP-1001",
    "cedente": {
        "tipo_inscricao": 2,
        "cnpj_cpf": "12345678000199",
        "nome": "FORNECEDOR ALFA LTDA",
    },
}

boleto2 = {
    "forma": "boleto",
    "favorecido": "SERVICOS BETA ME",
    "cnpj_favorecido": "98765432000188",
    "codigo_barras": "23791234500001250009876543210987654321098765",
    "data_vencimento": "2026-09-16",
    "data_pagamento": "2026-09-16",
    "valor_titulo": 1250.00,
    "valor_pagamento": 1250.00,
    "seu_numero": "DESP-1002",
    "cedente": {
        "tipo_inscricao": 2,
        "cnpj_cpf": "98765432000188",
        "nome": "SERVICOS BETA ME",
    },
}

# ========== PIX ==========
pix_chave_cnpj = {
    "forma": "pix",
    "favorecido": "PRESTADOR GAMA LTDA",
    "cnpj_favorecido": "11222333000144",
    "tipo_inscricao_favorecido": 2,
    "tipo_chave_pix": "cpf_cnpj",
    "chave_pix": "11222333000144",  # a chave neste caso e o proprio CNPJ
    "ispb_favorecido": "60746948",  # ISPB do Bradesco (ex.: usar o real do banco do favorecido)
    "tipo_conta_favorecido": "01",
    "data_pagamento": "2026-09-15",
    "valor_pagamento": 800.00,
    "seu_numero": "DESP-2001",
    "identificacao_pagamento": "Pagamento servicos setembro",
}

pix_chave_email = {
    "forma": "pix",
    "favorecido": "MARIA SILVA CONSULTORA",
    "cpf_favorecido": "12345678909",
    "tipo_inscricao_favorecido": 1,
    "tipo_chave_pix": "email",
    "chave_pix": "maria.silva@example.com",
    "ispb_favorecido": "00000000",
    "tipo_conta_favorecido": "01",
    "data_pagamento": "2026-09-15",
    "valor_pagamento": 450.00,
    "seu_numero": "DESP-2002",
    "identificacao_pagamento": "Consultoria RH",
}

# ========== TED ==========
ted1 = {
    "forma": "ted",
    "favorecido": "JOAO PEREIRA ADV",
    "cpf_favorecido": "98765432100",
    "tipo_inscricao_favorecido": 1,
    "banco_favorecido": "341",  # Itau
    "agencia_favorecido": "01234",
    "agencia_dv_favorecido": "",
    "conta_favorecido": "000000567890",
    "conta_dv_favorecido": "1",
    "data_pagamento": "2026-09-15",
    "valor_pagamento": 2000.00,
    "seu_numero": "DESP-3001",
    "finalidade_ted": "00003",  # Pagamento a fornecedor
    "endereco_favorecido": {
        "logradouro": "AV BRASIL",
        "numero": 200,
        "complemento": "ANDAR 5",
        "bairro": "CENTRO",
        "cidade": "SAO PAULO",
        "cep": 1000,
        "cep_sufixo": "000",
        "uf": "SP",
    },
    "mensagem": "Honorarios setembro",
}

despesas_teste = [boleto1, boleto2, pix_chave_cnpj, pix_chave_email, ted1]

arquivo = gerar_cnab240(
    despesas=despesas_teste,
    empresa=empresa_teste,
    nsa=1,
    data_geracao=datetime(2026, 9, 11, 17, 30, 0),
)

nome = "REMESSA_TESTE_BRADESCO_11-09-2026_v4.rem"
with open(nome, "w", encoding="latin-1", newline="") as f:
    f.write(arquivo)

print(f"Arquivo gerado: {nome}")
print(f"Total linhas: {arquivo.count(chr(10))}")
print(f"Total bytes: {len(arquivo.encode('latin-1'))}")
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
