# Layout CNAB 240 Bradesco — Referência técnica

Fonte oficial: **Manual de Procedimentos Multipag Bradesco — Layout CNAB 240 Posições Bradesco, Versão 08, revisado em julho/2025** (arquivo em `layout/manual-cnab-240-bradesco-v08-jul2025.pdf`).

Este documento é a **destilação prática** do manual, extraindo apenas o que o BPO da Silva & Silva precisa: **Boleto, PIX e TED**. Ordem de prioridade: boleto → PIX → TED.

## Estrutura geral do arquivo

Todo arquivo CNAB 240 é uma sequência de linhas de 240 caracteres cada, terminadas por LF (line-feed). Estrutura fixa:

```
[Header do Arquivo]                      Tipo 0, uma linha
  [Header do Lote 1]                     Tipo 1
    [Detalhe 1]                          Tipo 3 (vários segmentos possíveis)
    [Detalhe 2]                          Tipo 3
    ...
  [Trailer do Lote 1]                    Tipo 5
  [Header do Lote 2] (se houver)         Tipo 1
    ...
  [Trailer do Lote 2]                    Tipo 5
[Trailer do Arquivo]                     Tipo 9
```

**Regras gerais:**
- Cada linha tem exatamente **240 caracteres + LF**
- **Campos numéricos:** alinhados à direita, preenchidos com **zeros à esquerda**
- **Campos alfanuméricos:** alinhados à esquerda, preenchidos com **espaços à direita**, sem acentos
- **Valores:** sempre em centavos (R$ 1.234,56 vira 000000000123456, 15 posições, 2 decimais)
- **Datas:** formato DDMMAAAA (dia, mês, ano com 4 dígitos)
- **Horas:** formato HHMMSS

Um único arquivo pode ter vários lotes, cada lote com um tipo de pagamento. **No nosso caso do BPO,** vamos manter um arquivo por dia com um lote por tipo:
- Lote 1: Boletos (Segmento J)
- Lote 2: PIX (Segmento A + B + J-52)
- Lote 3: TED (Segmento A + B)

---

## Header do Arquivo (Tipo 0)

Uma linha só, no início do arquivo.

| Pos | Tam | Tipo | Campo | Valor / Descrição |
|-----|-----|------|-------|-------------------|
| 1-3 | 3 | Num | Código do Banco | `237` (Bradesco) |
| 4-7 | 4 | Num | Lote de Serviço | `0000` (fixo pro header do arquivo) |
| 8-8 | 1 | Num | Tipo de Registro | `0` |
| 9-17 | 9 | Alfa | Uso FEBRABAN | brancos |
| 18-18 | 1 | Num | Tipo de Inscrição da Empresa | `2` (CNPJ) |
| 19-32 | 14 | Num | CNPJ da Empresa | 14 dígitos, sem formatação |
| 33-52 | 20 | Alfa | Código do Convênio no Banco | fornecido pelo Bradesco no cadastro |
| 53-57 | 5 | Num | Agência (sem DV) | `02149` |
| 58-58 | 1 | Alfa | DV da Agência | espaço se não houver |
| 59-70 | 12 | Num | Número da Conta | `000000014339` |
| 71-71 | 1 | Alfa | DV da Conta | `1` |
| 72-72 | 1 | Alfa | DV Ag/Conta | espaço |
| 73-102 | 30 | Alfa | Nome da Empresa | `SILVA E SILVA ADVOGADOS ASSOCIADOS` (sem acento, até 30) |
| 103-132 | 30 | Alfa | Nome do Banco | `BANCO BRADESCO` |
| 133-142 | 10 | Alfa | Uso FEBRABAN | brancos |
| 143-143 | 1 | Num | Código Remessa/Retorno | `1` (Remessa) |
| 144-151 | 8 | Num | Data de Geração | `DDMMAAAA` |
| 152-157 | 6 | Num | Hora de Geração | `HHMMSS` |
| 158-163 | 6 | Num | NSA — Nº Sequencial do Arquivo | incrementa a cada arquivo gerado |
| 164-166 | 3 | Num | Versão do Layout | `089` |
| 167-171 | 5 | Num | Densidade | `01600` |
| 172-191 | 20 | Alfa | Reservado Banco | brancos |
| 192-211 | 20 | Alfa | Reservado Empresa | brancos |
| 212-240 | 29 | Alfa | Uso FEBRABAN | brancos |

---

## Header do Lote (Tipo 1)

Uma linha por lote. **O lote define o tipo de pagamento** através de dois campos-chave: **Tipo de Serviço** (G025) e **Forma de Lançamento** (G029).

### Combinações que interessam pro BPO

| Tipo de pagamento | Tipo de Serviço (pos 10-11) | Forma de Lançamento (pos 12-13) | Layout do Lote (pos 14-16) |
|---|---|---|---|
| **Boleto (mesmo banco)** | `20` (Pagamento a Fornecedor) | `30` (Liquidação de Título do Próprio Banco) | `040` |
| **Boleto (outros bancos)** | `20` (Pagamento a Fornecedor) | `31` (Pagamento de Título de Outros Bancos) | `040` |
| **TED (outra titularidade)** | `20` (Pagamento a Fornecedor) | `41` (TED Outra Titularidade) | `045` |
| **TED (mesma titularidade)** | `20` (Pagamento a Fornecedor) | `43` (TED Mesma Titularidade) | `045` |
| **PIX Transferência** | `20` (Pagamento a Fornecedor) | `45` (PIX Transferência) | `045` |
| **PIX QRCode** | `20` (Pagamento a Fornecedor) | `47` (PIX QRCode) | `045` |
| **Crédito em conta Bradesco** | `20` (Pagamento a Fornecedor) | `01` (Crédito em Conta Corrente) | `045` |

### Campos do Header do Lote

| Pos | Tam | Tipo | Campo | Valor / Descrição |
|-----|-----|------|-------|-------------------|
| 1-3 | 3 | Num | Código do Banco | `237` |
| 4-7 | 4 | Num | Lote de Serviço | sequencial: `0001`, `0002`... |
| 8-8 | 1 | Num | Tipo de Registro | `1` |
| 9-9 | 1 | Alfa | Tipo da Operação | `C` (Crédito) |
| 10-11 | 2 | Num | Tipo do Serviço | ver tabela acima |
| 12-13 | 2 | Num | Forma de Lançamento | ver tabela acima |
| 14-16 | 3 | Num | Versão do Layout do Lote | ver tabela acima |
| 17-17 | 1 | Alfa | Uso FEBRABAN | branco |
| 18-18 | 1 | Num | Tipo Inscrição Empresa | `2` (CNPJ) |
| 19-32 | 14 | Num | CNPJ Empresa | idem header do arquivo |
| 33-52 | 20 | Alfa | Convênio | idem header do arquivo |
| 53-72 | 20 | Mix | Ag/Conta | idem header do arquivo |
| 73-102 | 30 | Alfa | Nome da Empresa | idem |
| 103-142 | 40 | Alfa | Mensagem (Informação 1) | opcional, brancos se vazio |
| 143-192 | 50 | Alfa | Endereço (logradouro+número+complemento) | brancos se não usar |
| 193-212 | 20 | Alfa | Cidade | idem |
| 213-217 | 5 | Num | CEP | 5 primeiros dígitos |
| 218-220 | 3 | Alfa | Sufixo CEP | 3 últimos dígitos ou brancos |
| 221-222 | 2 | Alfa | Estado (UF) | `SC` |
| 223-224 | 2 | Num | Indicativo de Forma de Pagamento | `01` (padrão) |
| 225-230 | 6 | Alfa | Uso FEBRABAN | brancos |
| 231-240 | 10 | Alfa | Ocorrências (retorno) | brancos na remessa |

**Nota importante:** para o layout `040` (boleto), a posição 223-230 é toda brancos (8 posições) e não tem o "Indicativo de Forma de Pagamento".

---

## Detalhe — Segmento A (Tipo 3, código 'A')

Usado para: **PIX, TED, Crédito em conta**. Contém dados bancários do favorecido e valor a pagar.

| Pos | Tam | Tipo | Campo | Valor / Descrição |
|-----|-----|------|-------|-------------------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem header do lote |
| 8-8 | 1 | Num | Tipo Registro | `3` |
| 9-13 | 5 | Num | Nº Sequencial no Lote | `00001`, `00002`... |
| 14-14 | 1 | Alfa | Segmento | `A` |
| 15-15 | 1 | Num | Tipo Movimento | `0` (inclusão) |
| 16-17 | 2 | Num | Código Instrução | `00` (nenhuma) |
| 18-20 | 3 | Num | Câmara Centralizadora | `018` (TED/CIP) ou `000` (PIX/crédito em conta) |
| 21-23 | 3 | Num | Banco do Favorecido | ex: `237`, `748`, `001` |
| 24-28 | 5 | Num | Agência do Favorecido | zeros à esquerda |
| 29-29 | 1 | Alfa | DV Agência | espaço se não houver |
| 30-41 | 12 | Num | Conta do Favorecido | zeros à esquerda |
| 42-42 | 1 | Alfa | DV Conta | 1 dígito |
| 43-43 | 1 | Alfa | DV Ag/Conta | espaço |
| 44-73 | 30 | Alfa | Nome do Favorecido | sem acento, até 30 caracteres |
| 74-93 | 20 | Alfa | Seu Número (documento da empresa) | id da despesa no EasyJur (ex: `DESP-3936629`) |
| 94-101 | 8 | Num | Data do Pagamento | DDMMAAAA |
| 102-104 | 3 | Alfa | Tipo Moeda | `BRL` |
| 105-119 | 15 | Num | Quantidade Moeda | `000000000000000` (para BRL, zeros) |
| 120-134 | 15 | Num | Valor do Pagamento | valor em centavos, ex: 500,00 → `000000000050000` |
| 135-154 | 20 | Alfa | Nosso Número (banco preenche) | brancos na remessa |
| 155-162 | 8 | Num | Data Real | zeros na remessa |
| 163-177 | 15 | Num | Valor Real | zeros na remessa |
| 178-217 | 40 | Alfa | Informação 2 (mensagem) | **usado pro PIX:** ver formatação abaixo |
| 218-219 | 2 | Alfa | Uso FEBRABAN | brancos |
| 220-224 | 5 | Alfa | Código Finalidade TED | ex: `00001` (Crédito em Conta), `00003` (Pagamento a Fornecedor) |
| 225-226 | 2 | Alfa | Código Finalidade Complementar | brancos |
| 227-229 | 3 | Alfa | Uso FEBRABAN | brancos |
| 230-230 | 1 | Num | Aviso ao Favorecido | `0` (não avisar) ou `2` (avisar) |
| 231-240 | 10 | Alfa | Ocorrências (retorno) | brancos na remessa |

**Formatação especial do PIX na "Informação 2" (pos 178-217):**
```
CCCCCCCCCCCCCC IIIIIIII RR
onde:
  C = CNPJ do favorecido (14 dígitos)
  I = Código ISPB do banco favorecido (8 dígitos)
  R = Tipo da conta:
    01 = Conta corrente
    02 = Conta pagamento
    03 = Conta poupança
```

---

## Detalhe — Segmento B (Tipo 3, código 'B')

Usado para: **complemento do Segmento A** (endereço do favorecido, ou dados PIX). Vem logo depois de cada Segmento A.

**Dois formatos diferentes:**

### Segmento B para TED/Crédito (não-PIX)

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem |
| 8-8 | 1 | Num | Tipo Registro | `3` |
| 9-13 | 5 | Num | Nº Sequencial | próximo (após o A) |
| 14-14 | 1 | Alfa | Segmento | `B` |
| 15-17 | 3 | Alfa | Uso FEBRABAN | brancos |
| 18-18 | 1 | Num | Tipo Inscrição Favorecido | `1` (CPF) ou `2` (CNPJ) |
| 19-32 | 14 | Num | CPF/CNPJ do Favorecido | 14 dígitos, zeros à esquerda se for CPF |
| 33-62 | 30 | Alfa | Logradouro | endereço do favorecido |
| 63-67 | 5 | Num | Número | número do endereço |
| 68-82 | 15 | Alfa | Complemento | ap, sala, etc |
| 83-97 | 15 | Alfa | Bairro | |
| 98-117 | 20 | Alfa | Cidade | |
| 118-122 | 5 | Num | CEP | 5 primeiros dígitos |
| 123-125 | 3 | Alfa | Sufixo CEP | |
| 126-127 | 2 | Alfa | Estado | UF |
| 128-135 | 8 | Num | Data Vencimento | DDMMAAAA (opcional) |
| 136-150 | 15 | Num | Valor Documento | valor em centavos (nominal) |
| 151-165 | 15 | Num | Abatimento | zeros se não houver |
| 166-180 | 15 | Num | Desconto | zeros se não houver |
| 181-195 | 15 | Num | Mora | zeros se não houver |
| 196-210 | 15 | Num | Multa | zeros se não houver |
| 211-225 | 15 | Alfa | Código do Favorecido | brancos ou id |
| 226-226 | 1 | Num | Aviso ao Favorecido | `0` |
| 227-232 | 6 | Num | Código UG (SIAPE) | zeros |
| 233-240 | 8 | Num | Código ISPB | zeros se não usar |

### Segmento B para PIX

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem |
| 8-8 | 1 | Num | Tipo Registro | `3` |
| 9-13 | 5 | Num | Nº Sequencial | próximo (após o A) |
| 14-14 | 1 | Alfa | Segmento | `B` |
| 15-17 | 3 | Alfa | Forma de Iniciação (G100) | ver tabela abaixo |
| 18-18 | 1 | Num | Tipo Inscrição Favorecido | `1` (CPF) ou `2` (CNPJ) |
| 19-32 | 14 | Num | CPF/CNPJ do Favorecido | 14 dígitos, zeros à esquerda |
| 33-67 | 35 | Alfa | Informação 10 | ver abaixo |
| 68-127 | 60 | Alfa | Informação 11 | ver abaixo |
| 128-226 | 99 | Alfa | Informação 12 | ver abaixo |
| 227-232 | 7 | Num | UG SIAPE | zeros |
| 233-240 | 8 | Num | Código ISPB | zeros |

**Forma de Iniciação (pos 15-17) para PIX:**
- `04 ` = PIX via chave CPF
- `05 ` = PIX via chave CNPJ
- `06 ` = PIX via chave e-mail
- `07 ` = PIX via chave telefone
- `08 ` = PIX via chave aleatória
- `09 ` = QRCode

**Informações 10, 11, 12 no PIX:**
Depende do tipo da chave. Regra geral: a chave PIX é colocada dividida entre os 3 campos, ou concentrada num só. Detalhes exatos ver seção específica do manual (pág 39-42 e 129-135).

---

## Detalhe — Segmento J (Tipo 3, código 'J')

Usado para: **Pagamento de Boleto**. Contém o código de barras e valor.

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem |
| 8-8 | 1 | Num | Tipo Registro | `3` |
| 9-13 | 5 | Num | Nº Sequencial | próximo |
| 14-14 | 1 | Alfa | Segmento | `J` |
| 15-15 | 1 | Num | Tipo Movimento | `0` (inclusão) |
| 16-17 | 2 | Num | Código Instrução | `00` |
| 18-61 | 44 | Num | Código de Barras | 44 dígitos do boleto (sem formatação, sem espaço, sem ponto) |
| 62-91 | 30 | Alfa | Nome do Cedente | quem vai receber (nome do boleto) |
| 92-99 | 8 | Num | Data Vencimento | DDMMAAAA do boleto |
| 100-114 | 15 | Num | Valor do Título | valor original em centavos |
| 115-129 | 15 | Num | Desconto+Abatimento | zeros se não houver |
| 130-144 | 15 | Num | Mora+Multa | zeros se não houver |
| 145-152 | 8 | Num | Data Pagamento | DDMMAAAA (data efetiva) |
| 153-167 | 15 | Num | Valor Pagamento | valor a pagar em centavos |
| 168-182 | 15 | Num | Quantidade Moeda | zeros |
| 183-202 | 20 | Alfa | Referência Sacado | id da despesa no EasyJur |
| 203-222 | 20 | Alfa | Nosso Número (banco preenche) | brancos |
| 223-224 | 2 | Num | Código Moeda | `09` (Real) |
| 225-230 | 6 | Alfa | Uso FEBRABAN | brancos |
| 231-240 | 10 | Alfa | Ocorrências | brancos |

---

## Segmento J-52 (Tipo 3, código 'J', identificador '52' na pos 18-19)

**Obrigatório** para pagamento de títulos de cobrança com transferência para o cedente (independente do valor). Vem depois do Segmento J.

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem |
| 8-8 | 1 | Num | Tipo Registro | `3` |
| 9-13 | 5 | Num | Nº Sequencial | próximo |
| 14-14 | 1 | Alfa | Segmento | `J` |
| 15-15 | 1 | Alfa | Uso FEBRABAN | branco |
| 16-17 | 2 | Num | Código de Movimento Remessa | `00` (inclusão) |
| 18-19 | 2 | Num | Identificação Registro Opcional | `52` |
| 20-20 | 1 | Num | Tipo Inscrição Sacado | `2` (CNPJ) |
| 21-35 | 15 | Num | CNPJ Sacado (nós) | zeros à esquerda pra completar 15 |
| 36-75 | 40 | Alfa | Nome Sacado (nós) | `SILVA E SILVA ADVOGADOS ASSOCIADOS` |
| 76-76 | 1 | Num | Tipo Inscrição Cedente | `1` (CPF) ou `2` (CNPJ) |
| 77-91 | 15 | Num | CPF/CNPJ do Cedente | zeros à esquerda |
| 92-131 | 40 | Alfa | Nome do Cedente | quem recebe o boleto |
| 132-132 | 1 | Num | Tipo Inscrição Sacador | igual ao cedente na maioria dos casos |
| 133-147 | 15 | Num | CPF/CNPJ Sacador | idem cedente |
| 148-187 | 40 | Alfa | Nome Sacador | idem cedente |
| 188-240 | 53 | Alfa | Uso FEBRABAN | brancos |

---

## J-52 para PIX (obrigatório para PIX QRCode)

Similar ao J-52 padrão, mas com chave PIX e TXID em vez de dados de sacado/cedente. Ver manual pág 42.

---

## Trailer do Lote (Tipo 5)

Uma linha ao final de cada lote. Contém somatórias.

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | idem header do lote |
| 8-8 | 1 | Num | Tipo Registro | `5` |
| 9-17 | 9 | Alfa | Uso FEBRABAN | brancos |
| 18-23 | 6 | Num | Qtde de Registros | contagem: header lote + todos os detalhes + trailer lote (todos tipos 1, 3, 5 desse lote) |
| 24-41 | 18 | Num | Somatória de Valores | soma dos valores de pagamento do lote em centavos (18 posições, 2 decimais) |
| 42-59 | 18 | Num | Somatória Quantidade Moedas | zeros |
| 60-65 | 6 | Num | Nº Aviso Débito | zeros |
| 66-230 | 165 | Alfa | Uso FEBRABAN | brancos |
| 231-240 | 10 | Alfa | Ocorrências | brancos |

---

## Trailer do Arquivo (Tipo 9)

Última linha do arquivo. Uma só.

| Pos | Tam | Tipo | Campo | Valor |
|-----|-----|------|-------|-------|
| 1-3 | 3 | Num | Banco | `237` |
| 4-7 | 4 | Num | Lote | `9999` |
| 8-8 | 1 | Num | Tipo Registro | `9` |
| 9-17 | 9 | Alfa | Uso FEBRABAN | brancos |
| 18-23 | 6 | Num | Qtde Lotes | número de lotes no arquivo |
| 24-29 | 6 | Num | Qtde Registros | total de linhas do arquivo (headers + todos detalhes + trailers) |
| 30-35 | 6 | Num | Qtde Contas Conc. | zeros |
| 36-240 | 205 | Alfa | Uso FEBRABAN | brancos |

---

## Tabela de referência: Códigos de Bancos (P002)

Para o Segmento A, campo "Banco do Favorecido":

| Banco | Código |
|---|---|
| Bradesco | 237 |
| Sicredi | 748 |
| Itaú | 341 |
| Banco do Brasil | 001 |
| Santander | 033 |
| Caixa | 104 |
| Nubank | 260 |
| Inter | 077 |
| C6 | 336 |
| Original | 212 |
| BTG | 208 |
| Safra | 422 |

Lista completa: consultar Bacen.

---

## Tabela de referência: Códigos Finalidade TED (P011)

Para o Segmento A, campo "Código Finalidade TED":

| Código | Descrição |
|---|---|
| 00001 | Crédito em Conta |
| 00003 | Pagamento a Fornecedor |
| 00005 | Pagamento de Salários |
| 00006 | Pagamento de Aluguel |
| 00007 | Pagamento de Duplicata |
| 00010 | Transferência Internacional em Reais |
| 00011 | DOC/TED para poupança |
| 00012 | Pagamento de Dividendos |

Para o BPO, geralmente usar `00003` (Pagamento a Fornecedor).

---

## Fluxo do gerador Python

O `gerador_cnab240_bradesco.py` recebe uma lista de despesas (cada uma com forma de pagamento definida) e monta o arquivo `.rem`:

```python
gerar_cnab240(
    despesas=[...],
    empresa={
        'cnpj': '09177564000179',
        'nome_reduzido': 'SILVA E SILVA ADVOGADOS ASSOCIADOS',
        'convenio': '99999999999999999999',  # o convênio de pagamento fornecido pelo Bradesco
        'agencia': '02149',
        'agencia_dv': '',
        'conta': '000000014339',
        'conta_dv': '1',
        'endereco': {...},
    },
    nsa=42,  # número sequencial do arquivo (incremental)
    data_geracao=datetime.now(),
    saida='REMESSA_BRADESCO_11-09-2026_143000.rem'
)
```

O gerador agrupa as despesas por tipo:
- Boletos → Lote 1 (Segmento J + J-52)
- PIX → Lote 2 (Segmento A + B + J-52 opcional)
- TED → Lote 3 (Segmento A + B)

Cada tipo tem sua própria função (`monta_lote_boletos`, `monta_lote_pix`, `monta_lote_ted`), tudo agrupado em `gerar_cnab240`.

---

## Validação

Após gerar o arquivo `.rem`, testar no **Multipag Bradesco** (validador oficial, roda local no PC):

https://banco.bradesco/html/pessoajuridica/solucoes-integradas/outros/layout-de-arquivo.shtm

Baixa, instala, abre o `.rem` no validador. Ele aponta erros de posição, tamanho, tipo, campos obrigatórios não preenchidos. Corrigir e reprocessar até sair "arquivo OK".

Só depois de OK no Multipag, o arquivo está pronto pra ir ao Bradesco Net Empresa.
