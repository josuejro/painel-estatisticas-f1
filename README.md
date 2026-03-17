# Painel de Estatísticas F1

Projeto desenvolvido com o objetivo de aprender na prática o consumo de APIs externas e a persistência de dados com banco de dados relacional. Utiliza a API Open F1 para buscar dados reais da temporada atual de Fórmula 1 e os armazena localmente em um banco SQLite, permitindo consultas offline após a primeira sincronização.

## O que o projeto faz

- Busca e armazena pilotos e sessões da temporada atual via API
- Salva resultados de corridas e outras sessões no banco de dados local
- Exibe o calendário completo da temporada com todas as sessões disponíveis
- Exibe o resultado detalhado de qualquer sessão salva, com posição, piloto e equipe
- Lista todos os pilotos da temporada com seus respectivos números e equipes

## Tecnologias utilizadas

- Python 3
- `requests` para consumo da API
- `sqlite3` para o banco de dados (nativo do Python)
- [Open F1 API](https://openf1.org/) como fonte de dados

## Pré-requisitos

- Python 3 instalado
- Conexão com a internet para a sincronização inicial dos dados

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/josuejro/painel-estatisticas-f1.git
cd painel-estatisticas-f1
```

2. Instale as dependências:
```bash
python -m pip install requests
```

3. Execute o programa:
```bash
python main.py
```

O banco de dados `f1.db` será criado automaticamente na primeira execução.

## Como usar

Ao iniciar, o programa exibe o menu principal:

```
===== PAINEL F1 2026 =====
1. Atualizar dados da temporada
2. Ver sessões disponíveis
3. Ver resultado de uma sessão
4. Ver pilotos
0. Sair
=================================
```

O fluxo recomendado para o primeiro uso é:

1. Selecione a opção **1** para buscar pilotos e sessões da temporada via API e salvar no banco
2. Selecione a opção **2** para ver as sessões disponíveis e anotar o `session_key` desejado
3. Selecione a opção **3**, informe o `session_key` e o programa buscará e exibirá o resultado

Nas execuções seguintes, os dados já estarão no banco e a opção 1 só adicionará o que for novo.

## Estrutura do banco de dados

O projeto utiliza três tabelas relacionadas entre si:

- `pilotos` armazena número, sigla, nome completo e equipe de cada piloto
- `sessoes` armazena cada sessão da temporada com seu identificador, tipo, data, país e circuito
- `resultados` armazena as posições finais de cada sessão, referenciando pilotos e sessões pelas suas chaves

## Estrutura do projeto

```
painel-estatisticas-f1/
├── main.py    # Script principal com todas as funções e menu CLI
├── f1.db      # Banco de dados local (gerado automaticamente)
└── README.md
```

## Aprendizados

Este projeto foi desenvolvido como exercício para consolidar e expandir os conhecimentos adquiridos no projeto anterior, introduzindo conceitos novos como:

- Relacionamento entre múltiplas tabelas com chaves estrangeiras no SQLite
- Consultas com `JOIN` para cruzar dados de tabelas diferentes
- Verificação de duplicatas antes de inserir registros no banco
- Tratamento de respostas de API que retornam dados históricos acumulados, exigindo filtragem para obter apenas o estado final
- Construção de um menu CLI com loop e múltiplas opções de navegação