# Decisões do projeto

Registro das escolhas feitas ao longo do desenvolvimento, com o motivo de cada uma.

## Base de dados: Eclipse and Mozilla Defect Tracking Dataset (JDT)

- **Decisão:** usar os bugs do JDT, uma base real com histórico de mudanças de status.
- **Motivo:** o histórico permite derivar tempo de resolução e reabertura. Outras bases avaliadas foram descartadas: uma tinha todas as tarefas "Done", fechamentos em lote e sem histórico de status; outra era sintética, com 100 linhas.

## Dados fora do repositório

- **Decisão:** os dados não são versionados. Um script baixa o pacote original e extrai só o JDT em `data/raw/jdt/`.
- **Motivo:** a base não informa licença de uso, então não é seguro redistribuí-la. O repositório traz o script e a citação da base.

## Primeira resolução

- **Decisão:** a primeira resolução de um bug é a primeira ocorrência de `RESOLVED`, `VERIFIED` ou `CLOSED`.
- **Motivo:** 351 dos 10.814 bugs vão direto de `NEW` ou `ASSIGNED` para `CLOSED`. Contar só `RESOLVED` deixaria esses bugs sem tempo de resolução e distorceria as médias sem aviso.

## Prioridade fora da tabela

- **Decisão:** a coluna de prioridade não entra na tabela.
- **Motivo:** cerca de 96% dos bugs não têm prioridade preenchida.

## Duas colunas de severidade

- **Decisão:** a tabela tem `severidade` (valor final, usada no dashboard) e `severidade_na_resolucao` (valor no instante da primeira resolução, destinada ao modelo de reabertura).
- **Motivo:** evitar vazamento de dados no modelo. Em 53 bugs (cerca de 0,5%) a severidade mudou depois da primeira resolução.

## Limitação conhecida: todos os bugs terminam resolvidos

- **Situação:** na base, nenhum bug termina aberto. Por isso o backlog reconstruído a partir do histórico tende a parecer baixo nos meses mais recentes.
- **Tratamento:** avisar isso no dashboard. A causa exata (filtro da base ou recorte) ainda não foi verificada.

## Validação da tabela com pandera

- **Decisão:** a tabela de bugs é validada por um esquema (`core/qa/esquema.py`) com tipos, `id` único, valores não negativos e regras entre colunas: a primeira resolução não pode ser anterior à criação, e `reaberto` deve ser coerente com `n_reaberturas`.
- **Motivo:** os testes unitários conferem o código com dados inventados, e o esquema confere os dados reais toda vez que a tabela é montada.

## Valores de severidade

- **Decisão:** `severidade` e `severidade_na_resolucao` têm listas de valores permitidos diferentes. O valor `enhancement` só é aceito na segunda.
- **Motivo:** 4 bugs eram `enhancement` no momento da primeira resolução e foram reclassificados depois, então esse valor não existe na severidade final. A lista foi definida olhando os valores reais da base.

## KPIs: média e mediana, e divisor da taxa de reabertura

- **Decisão:** o tempo de resolução é mostrado com **média e mediana**, e a taxa de reabertura é calculada só sobre bugs que já tiveram primeira resolução.
- **Motivo:** poucos bugs com resolução muito longa puxam a média (59 dias contra mediana de 2,8). Só quem foi resolvido pode ser reaberto, então bugs sem resolução não entram no divisor.
- **Observação:** a taxa conta bugs reabertos pelo menos uma vez (não eventos), e as funções de KPI recebem a tabela já validada.

## Filtros e gráfico de bugs criados do dashboard

- **Decisão:** os cartões do topo consideram os bugs **criados** no período escolhido. No gráfico, criados e resolvidos são contados cada um pela **própria data**, só dentro do período, e o eixo mostra apenas os meses do período.
- **Motivo:** contar as resoluções dos bugs criados no período arrastava a linha de resolvidos até 2011 mesmo com um período curto, o que confundia a leitura. A contagem de cada linha pela sua data responde "quantos bugs entraram e quantos saíram em cada mês?".
- **Consequência:** a soma de resolvidos no gráfico pode diferir da soma dos cartões, porque inclui resoluções de bugs criados antes do período.
- **Limitação:** a base termina em 05/05/2011, então o último mês é incompleto. O dashboard avisa isso na legenda.
- **Filtros de categoria:** severidade e componente usam caixas de seleção (uma por opção, em 2 linhas de 3) e não o seletor múltiplo padrão, por ficarem todas visíveis e por serem mais intuitivas para quem não é da área.

## Gráfico de severidade

- **Decisão:** barras horizontais, da severidade mais grave para a mais leve, com número e porcentagem em cada barra e cores quentes para as mais graves.
- **Motivo:** a distribuição é muito desigual (cerca de 77% `normal` e menos de 1% `blocker`), e em gráfico de rosca as fatias pequenas ficariam quase invisíveis. Nas barras a comparação é por comprimento, e o rótulo mostra o valor mesmo para barras curtas.