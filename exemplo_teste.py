"""Gera os arquivos .txt de homologacao pro Bradesco Multipag.

Dados reais do convenio enviados pela implantacao do Bradesco:
  Convenio 666228, agencia 2149-0, conta 14339-1, layout 240, Webta.
  Fornecedores, salarios e tributos: producao. Pix: ambiente de teste.

Regras aplicadas (e-mail do banco + manual Multipag Pix v5):
  - Pix vai em arquivo separado (header com 'PIX' nas posicoes 172-174).
  - Numero do documento (Seg A 74-93) nao pode repetir: os testes usam um
    prefixo com data e hora pra nao colidir com testes anteriores.
  - Colunas 16-17 = '09': pagamento entra bloqueado ate o master autorizar.

Os arquivos de teste NAO sao processados financeiramente pelo banco.
"""

from datetime import datetime
from gerador_cnab240_bradesco import gerar_remessas, INSTRUCAO_BLOQUEADO

agora = datetime.now()
data_pgto = agora.strftime("%Y-%m-%d")
prefixo = "T" + agora.strftime("%d%m%H%M")   # ex.: T28091530, unico por teste

empresa = {
    "cnpj": "09177564000179",
    "nome_reduzido": "SILVA E SILVA ADVOGADOS ASSOCIADOS",
    "convenio": "666228",          # enviado pelo Bradesco (posicoes 33-38)
    "agencia": "02149",
    "agencia_dv": "0",             # 2149-0
    "conta": "000000014339",
    "conta_dv": "1",               # 14339-1
    "ag_conta_dv": "",
    "endereco": {
        "logradouro": "RUA 428",
        "numero": 15,
        "complemento": "",
        "bairro": "MORRETES",
        "cidade": "ITAPEMA",
        "cep": 88220,
        "cep_sufixo": "000",
        "uf": "SC",
    },
}

# Boleto real que a Ana passou. Vencimento antigo (2002): o validador pode
# recusar por data; trocar por um boleto recente quando houver.
boleto = {
    "forma": "boleto",
    "favorecido": "BANCO BRADESCO",
    "cnpj_favorecido": "60746948000112",
    "codigo_barras": "23795157100000106050131096254000300302119760",
    "data_vencimento": "2002-01-25",
    "data_pagamento": data_pgto,
    "valor_titulo": 106.05,
    "valor_pagamento": 106.05,
    "seu_numero": f"{prefixo}-BOL01",
    "cedente": {"tipo_inscricao": 2, "cnpj_cpf": "60746948000112", "nome": "BANCO BRADESCO"},
}

ted = {
    "forma": "ted",
    "favorecido": "JOAO DA SILVA CONSULTORIA",
    "cpf_favorecido": "12345678909",
    "tipo_inscricao_favorecido": 1,
    "banco_favorecido": "341",
    "agencia_favorecido": "01234",
    "conta_favorecido": "000000567890",
    "conta_dv_favorecido": "1",
    "data_pagamento": data_pgto,
    "valor_pagamento": 1500.00,
    "seu_numero": f"{prefixo}-TED01",
    "finalidade_ted": "00003",
    "endereco_favorecido": {
        "logradouro": "AV BRASIL", "numero": 200, "complemento": "SALA 10",
        "bairro": "CENTRO", "cidade": "SAO PAULO", "cep": 1000,
        "cep_sufixo": "000", "uf": "SP",
    },
}

pix_cnpj = {
    "forma": "pix",
    "favorecido": "PRESTADOR SERVICOS LTDA",
    "cnpj_favorecido": "11222333000181",
    "tipo_inscricao_favorecido": 2,
    "tipo_chave_pix": "cpf_cnpj",
    "chave_pix": "11222333000181",
    "data_pagamento": data_pgto,
    "valor_pagamento": 800.00,
    "seu_numero": f"{prefixo}-PIX01",
    "identificacao_pagamento": "Servicos setembro",
}

pix_email = {
    "forma": "pix",
    "favorecido": "MARIA SILVA",
    "cpf_favorecido": "12345678909",
    "tipo_inscricao_favorecido": 1,
    "tipo_chave_pix": "email",
    "chave_pix": "maria.silva@example.com",
    "data_pagamento": data_pgto,
    "valor_pagamento": 450.00,
    "seu_numero": f"{prefixo}-PIX02",
    "identificacao_pagamento": "Salario setembro",
}

pix_aleatoria = {
    "forma": "pix",
    "favorecido": "CARLOS PEREIRA",
    "cpf_favorecido": "98765432100",
    "tipo_inscricao_favorecido": 1,
    "tipo_chave_pix": "aleatoria",
    "chave_pix": "123e4567-e89b-12d3-a456-426614174000",
    "data_pagamento": data_pgto,
    "valor_pagamento": 300.00,
    "seu_numero": f"{prefixo}-PIX03",
}

arquivos = gerar_remessas(
    despesas=[boleto, ted, pix_cnpj, pix_email, pix_aleatoria],
    empresa=empresa,
    nsa_inicial=1,
    data_geracao=agora,
    instrucao_movimento=INSTRUCAO_BLOQUEADO,
)

data_nome = agora.strftime("%d-%m-%Y")
for tipo, conteudo in arquivos.items():
    if not conteudo:
        continue
    nome = f"REMESSA_TESTE_{tipo}_{data_nome}.txt"
    with open(nome, "w", encoding="latin-1", newline="") as f:
        f.write(conteudo)
    linhas = conteudo.splitlines()
    print(f"{nome}: {len(linhas)} linhas, {len(conteudo.encode('latin-1'))} bytes")
    for i, linha in enumerate(linhas, 1):
        tipo_reg = {"0": "Header arquivo", "1": "Header lote", "3": f"Detalhe {linha[13]}",
                    "5": "Trailer lote", "9": "Trailer arquivo"}[linha[7]]
        print(f"  L{i:02d} {tipo_reg:16s} len={len(linha)}")
