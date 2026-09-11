"""Gera arquivo .rem de teste pra rodar no Multipag."""

from datetime import datetime
from gerador_cnab240_bradesco import gerar_cnab240

empresa_teste = {
    "cnpj": "09177564000179",
    "nome_reduzido": "SILVA E SILVA ADVOGADOS ASSOCIADOS",
    "convenio": "99999999999999999999",  # PLACEHOLDER — trocar pelo convenio real do Bradesco
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

# 3 boletos de teste
despesas_teste = [
    {
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
    },
    {
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
    },
    {
        "forma": "boleto",
        "favorecido": "JOSE DA SILVA CONSULTORIA",
        "cpf_favorecido": "12345678909",
        "codigo_barras": "23791234500000330001234567890987654321012345",
        "data_vencimento": "2026-09-17",
        "data_pagamento": "2026-09-17",
        "valor_titulo": 330.00,
        "valor_pagamento": 330.00,
        "seu_numero": "DESP-1003",
        "cedente": {
            "tipo_inscricao": 1,  # CPF
            "cnpj_cpf": "12345678909",
            "nome": "JOSE DA SILVA",
        },
    },
]

arquivo = gerar_cnab240(
    despesas=despesas_teste,
    empresa=empresa_teste,
    nsa=1,
    data_geracao=datetime(2026, 9, 11, 14, 30, 0),
)

nome = "REMESSA_TESTE_BRADESCO_11-09-2026.rem"
with open(nome, "w", encoding="latin-1", newline="") as f:
    # CNAB tradicionalmente usa \r\n mas o Bradesco aceita \n
    f.write(arquivo)

print(f"Arquivo gerado: {nome}")
print(f"Total linhas: {arquivo.count(chr(10))}")
print(f"Total bytes: {len(arquivo.encode('latin-1'))}")
print()
print("=== Preview das linhas ===")
linhas = [l for l in arquivo.split("\n") if l]  # ignora linha vazia final
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
