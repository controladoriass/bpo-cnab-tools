# bpo-cnab-tools

Ferramentas de geração e leitura de arquivos CNAB 240 (remessa e retorno) do BPO Financeiro do Silva & Silva Advogados Associados.

## Status

**Manual técnico oficial recebido (Bradesco v08, jul/2025).**
**Gerador Python implementado e validado no Multipag.** Faltando apenas o convênio real de Multipag do Bradesco pra passar em produção.

### O que já está pronto (validado pelo Multipag)

- Estrutura CNAB 240 (240 chars por linha, CRLF, Header/Trailer)
- Header e Trailer do arquivo
- Header e Trailer de lote (com somatórias corretas)
- **Boleto:** Segmento J + J-52 (estrutura OK, aguarda boleto real recente)
- **PIX Transferência:** Segmento A + B + J + J-52 (estrutura OK, aguarda convênio com PIX habilitado)
- **TED:** Segmento A + B (estrutura OK, reconhecida pelo Multipag)

### O que falta pra rodar em produção

1. **Convênio de pagamento do Bradesco** (20 posições) — trocar em `exemplo_teste.py` variável `convenio`. Fornecido pelo gerente ou visível no Bradesco Net Empresa > Multipag.
2. **Habilitação do PIX no convênio** — PIX é essencial pro BPO (folha de salário). Sem PIX habilitado, o Multipag rejeita o lote com "Modalidade 45 não localizada".
3. **Ambiente de homologação** (opcional) — pra testar arquivo com dados reais sem processar pagamento.

## Uso previsto

Estas ferramentas são lidas pela **Rotina D** e pela **Rotina E** do BPO Automatizado (rotinas agendadas do Claude). O robô lê o código Python direto deste repositório (`raw.githubusercontent.com`) e executa a lógica passo a passo dentro da própria sessão agendada, sem depender de nenhum arquivo local do PC da controladoria.

## Estrutura

```
bpo-cnab-tools/
├── README.md
├── LICENSE
├── layout/
│   └── manual-tecnico-cnab240-bradesco.md   (documentação, quando chegar)
├── gerador_cnab240_bradesco.py              (a implementar)
├── leitor_retorno_cnab240_bradesco.py       (a implementar)
├── gerador_cnab240_sicredi.py               (a implementar)
├── exemplos/
│   ├── remessa_exemplo.rem                  (a implementar)
│   └── retorno_exemplo.ret                  (a implementar)
└── testes/
    └── test_gerador.py                      (a implementar)
```

## Segurança

Repositório público, mas **não contém dados sensíveis**:
- Sem PIX de fornecedores
- Sem CPF/CNPJ
- Sem saldos ou histórico bancário
- Sem senhas ou tokens

Apenas o código de geração/leitura do padrão CNAB 240 Febraban.

## Contexto

Silva & Silva Advogados Associados, controladoria, 2026.
Contato: `contasapagar@silvaesilva.com.br`
