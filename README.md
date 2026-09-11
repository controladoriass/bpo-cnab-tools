# bpo-cnab-tools

Ferramentas de geração e leitura de arquivos CNAB 240 (remessa e retorno) do BPO Financeiro do Silva & Silva Advogados Associados.

## Status

**Em espera.** Aguardando Bradesco liberar módulo CNAB 240 e entregar o layout técnico oficial (Manual Técnico CNAB 240 v084 Bradesco). Sem o manual, o gerador fica genérico e sujeito a rejeição no banco.

Quando o manual chegar:
- `gerador_cnab240_bradesco.py`, gera arquivo `.rem` de remessa
- `leitor_retorno_cnab240_bradesco.py`, lê arquivo `.ret` de retorno
- `gerador_cnab240_sicredi.py`, quando Sicredi liberar

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
