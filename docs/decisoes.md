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

## Gráficos de tempo e reabertura

- **Decisão:** o tempo até a primeira resolução mostra a mediana (barra) e a média (losango) por severidade, e a taxa de reabertura mostra o tamanho do grupo no rótulo. No layout, o gráfico mensal e o de tempo ficam na linha de cima, e severidade e reabertura na de baixo.
- **Motivo:** média e mediana juntas mostram o quanto poucos bugs muito demorados puxam a média (em `minor`, 3,2 dias de mediana contra cerca de 93 de média). O tamanho do grupo avisa que taxas de grupos pequenos, como `blocker`, oscilam mais.

## Gráfico de componentes (Pareto)

- **Decisão:** barras de bugs por componente, da maior para a menor, com uma linha de porcentagem acumulada (gráfico de Pareto).
- **Motivo:** a pergunta é sobre concentração. Dois componentes (Core e UI) reúnem cerca de 69% dos bugs, e a linha de acumulado mostra isso sem precisar somar de cabeça. Uma rosca deixaria os componentes pequenos (APT com 2,1% e Doc com 0,9%) como fatias finas demais para ler.

## Evolução do backlog

- **Decisão:** o backlog é a soma acumulada de bugs criados menos bugs com primeira resolução, calculada desde o primeiro bug da base. O período do filtro escolhe só os meses mostrados, e as caixas de severidade e componente valem para a conta.
- **Motivo:** o backlog de um mês depende de tudo o que ficou aberto antes, então cortar o início pelo período daria valores errados.
- **Limitações:** reaberturas não entram na conta, e como a base só tem bugs que acabam resolvidos, a curva termina em zero por construção. O pico é de 531 bugs em março de 2007, com um platô entre 400 e 460 até 2009. Não foi possível dizer quanto da queda depois de 2009 é efeito da base, e a queda brusca dos últimos cinco meses é a parte mais suspeita. O dashboard avisa isso na legenda.

## Explorador de dados

- **Decisão:** a página mostra a tabela tratada com a tabela nativa do Streamlit (busca e ordenação por coluna), com colunas em português e datas no formato brasileiro. A exportação (download em CSV e cópia) fica desativada pela configuração `client.disableDataExport`.
- **Motivo:** a base não informa licença de uso, então o app não oferece a tabela para baixar.

## Tendência e sazonalidade: análise exploratória, sem gráfico

- **Decisão:** não há gráfico de sazonalidade no dashboard por enquanto. A tendência já aparece nos gráficos mensal e de backlog. A análise de sazonalidade ficou registrada aqui.
- **Motivo:** são poucos anos (4 a 5 observações por mês do calendário) e a explicação do método pesa mais que a informação entregue. Pode voltar numa versão futura ou em outra base.
- **Método:** primeiro dividir cada mês pela média do seu ano, mas a queda forte do volume (de 3.760 bugs criados em 2006 para 1.100 em 2010) faz os primeiros meses de cada ano parecerem altos só pela tendência. Refazer dividindo cada mês pela média móvel de 12 meses centrada nele.
- **Resultado:** março (índice médio de 1,21) e maio (1,47) ficam acima da média nos anos analisados, e dezembro (0,73) e janeiro (0,83) abaixo. Entre junho e dezembro os índices ficam perto de 0,9, com variação entre os anos.
- **Hipótese não verificada:** a queda brusca de maio para junho pode estar ligada ao ciclo de lançamentos anuais do Eclipse, que pela amostra parece fechar em maio/junho.
- **Limitações:** 4 a 5 anos por mês, a base termina em maio de 2011 e a mesma limitação de bugs só resolvidos já registrada vale aqui.

## Layout do dashboard

- **Decisão:** os filtros (período, severidade e componente) e o botão de explorar dados ficam na barra lateral, os gráficos ficam em grade de três colunas com altura fixa e margens reduzidas, e as explicações vão em tooltips ao lado dos títulos.
- **Motivo:** o objetivo é que filtros, cartões e gráficos caiam numa tela só, sem rolagem. Com os filtros na barra lateral, a área principal fica só com os resultados, e o botão da barra continua no mesmo lugar ao rolar a página.
- **Eixo de meses:** o intervalo entre as marcas é o menor que não passa de 8 marcas (1, 2, 3, 6 ou 12 meses), com os anos sozinhos quando o período é longo, para os rótulos não se sobreporem nas colunas estreitas.
- **Estilo:** um ajuste de CSS (em `app/estilo.py`) reduz o espaço em branco no topo. O Streamlit não tem opção nativa para isso, e o nome do elemento alterado muda entre versões, então é um ponto a rever ao atualizar o Streamlit.