# Portfólio Dados & QA

![CI](https://github.com/nxxxlxs/portfolio-dados-qa/actions/workflows/ci.yml/badge.svg)

## Dados

Os dados vêm do **Eclipse and Mozilla Defect Tracking Dataset** (Lamkanfi, Pérez e Demeyer, MSR 2013), que reúne o histórico de bugs de projetos do Eclipse e do Mozilla. Este projeto usa apenas os bugs do **JDT**.

A base não informa nenhuma licença de uso. Por isso os dados **não são redistribuídos neste repositório**: a pasta `data/` é ignorada pelo Git e um script baixa o pacote original do repositório [ansymo/msr2013-bug_dataset](https://github.com/ansymo/msr2013-bug_dataset) e extrai só os arquivos do JDT em `data/raw/jdt/`.

Para baixar e extrair (a partir da raiz do projeto):

```bash
uv run python -c "from core.qa.download import baixar_pacote, extrair_jdt; baixar_pacote(); extrair_jdt()"
```

Se os arquivos já existirem, o script não baixa nem extrai de novo.

### Como citar a base

```bibtex
@inproceedings{LamkanfiMSR13,
  author    = {Ahmed Lamkanfi and Javier Perez and Serge Demeyer},
  title     = {The Eclipse and Mozilla Defect Tracking Dataset:
               a Genuine Dataset for Mining Bug Information},
  booktitle = {MSR '13: Proceedings of the 10th Working Conference on
               Mining Software Repositories, May 18--19, 2013.
               San Francisco, California, USA},
  year      = {2013},
}
```