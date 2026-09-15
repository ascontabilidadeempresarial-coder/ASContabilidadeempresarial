---
name: processar-vt-vr
description: Processa o ciclo quinzenal de VT/VR (vale transporte e vale refeição) da A&S Contabilidade — duplica a última aba da planilha "VT E VR - A&S 2026.xlsx", calcula os dias de cada colaborador e lança as contas a pagar no Omie. Use esta skill sempre que a Camila pedir para "fazer o VT e VR", "gerar o próximo período de VT/VR", "lançar o VT e VR no Omie", ou quando a rotina agendada disparar no 3º dia útil do mês ou por volta do dia 17/18 (2 dias úteis antes do pagamento do dia 20). Cobre todo o fluxo: duplicar/renomear aba, calcular período e dias por colaborador (considerando home office), confirmar observações com a Camila, preencher a planilha e lançar VT e VR como dois lançamentos separados de conta a pagar no Omie.
---

# Processar VT/VR (vale transporte e vale refeição)

Rotina quinzenal da A&S Contabilidade. Toda vez que chega perto de uma data de pagamento, alguém
precisa: gerar a próxima aba da planilha de controle, calcular quantos dias de VT e VR cada
colaborador tem direito, e lançar os dois valores como conta a pagar no Omie (fornecedor iFood, que
é quem carrega os cartões). Esta skill documenta as regras de negócio como a Camila as passou —
elas vieram de uma conversa real e podem evoluir, então se algo aqui parecer desatualizado ou
incompleto, pergunte a ela em vez de assumir.

**Arquivo da planilha:** `OneDrive - A&S CONTABILIDADE LTDA\A&S CONTABILIDADE\COMPARTILHAMENTO -
DIRETORIA\_RH AS\ROTINAS DIÁRIAS\VT E VR - A&S 2026.xlsx`

## Ambiente Python (Windows)

Neste computador, os comandos `python`/`python3`/`py` no PATH são só os stubs da Microsoft Store e
não funcionam. O Python de verdade (com `openpyxl` instalado) está em:

```
C:\Users\camil\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Use o caminho completo em todo script. Não há LibreOffice instalado nesta máquina, então
`recalc.py` (do skill de xlsx) não funciona aqui — depois de qualquer edição com `openpyxl`, defina
`wb.calculation = CalcProperties(fullCalcOnLoad=True)` antes de salvar (`from
openpyxl.workbook.properties import CalcProperties`). Isso força o Excel a recalcular tudo sozinho
quando a Camila abrir o arquivo, já que não dá pra recalcular por aqui.

Se `load_workbook`/`wb.save` falhar com `PermissionError: [Errno 13]`, o arquivo está aberto no
Excel (provavelmente pela própria Camila). Peça para ela fechar antes de tentar de novo — não tem
como contornar isso.

## Passo 0 — Confirmar que o ciclo ainda não foi processado

Antes de duplicar qualquer coisa, abra a última aba existente e veja o "Período Vigente" dela.
Calcule qual é a data de pagamento do ciclo que você está prestes a processar (5º dia útil ou dia
20, conforme o caso). Se o **fim** do período da última aba já for igual ou posterior a essa data
de pagamento, esse ciclo **já foi processado** (por você mesmo antes, ou manualmente pela Camila) —
não duplique de novo. Isso importa principalmente para a execução agendada, que roda sozinha sem
ninguém acompanhando: se o trabalho já estiver adiantado (por exemplo, alguém já criou a aba do
próximo ciclo manualmente), rodar de novo criaria uma aba e um lançamento duplicados no Omie.

## Passo 1 — Duplicar e renomear a aba

Abra o arquivo, pegue a última aba (`wb.sheetnames[-1]`), duplique com `wb.copy_worksheet(...)` e
renomeie. O padrão de nomes dos meses recentes é `MM-AA` (ex: `10-26` para outubro/2026) — os nomes
mais antigos têm inconsistências (pontos, superíndices, "(2)" vs "(3)") porque foram digitados à
mão; não replique esses erros, siga o padrão limpo `MM-AA` para o primeiro lançamento do mês e
`MM-AA (2)` para o segundo, salvo se a Camila pedir outro nome.

## Passo 2 — Calcular o período

Duas datas de pagamento por mês:

- **5º dia útil do mês**
- **Dia 20**

**Regra de dia útil para achar a data de pagamento:** sábado conta como dia útil, só domingo não
conta. Isso é diferente da contagem de dias trabalhados (passo 3), que é só segunda a sexta — são
duas contagens com propósitos diferentes, não confunda uma com a outra.

**Antecipação:** se a data de pagamento calculada cair num domingo (ou, pela definição acima, isso
só pode acontecer no caso do dia 20, já que o 5º dia útil nunca cai em domingo por construção),
antecipa para o dia útil anterior.

**Limites da aba (período):**
- **Início:** o 1º dia útil (segunda a sexta) depois da data de pagamento anterior.
- **Fim:** a nova data de pagamento calculada acima.

Exemplo real: pagamento anterior em 18/09/2026 (sexta, dia 20 antecipado porque 20/09 caiu num
domingo) → próximo período começa 21/09/2026 (segunda) e vai até a data do 5º dia útil de outubro.

Depois de calcular, preencha na aba nova:
- `Período Vigente` (célula mesclada logo abaixo do rótulo "Período Vigente:") — formato
  `DD/MM/AAAA a DD/MM/AAAA`.
- `DIAS` (célula ao lado) — total de dias úteis (segunda a sexta) dentro do período.
- A notinha "home office" / "X dias" (fica ao lado do rótulo "Descontos Gerais", na linha da
  primeira colaboradora) — quantidade de segundas e sextas dentro do período (ver passo 3).

## Passo 3 — Calcular os dias por colaborador

**Regra geral:** home office é sempre às **segundas e sextas-feiras**. Nesses dias a pessoa não
desloca até o escritório, então **desconta o VT** (mas não o VR — ela ainda almoça/janta nesse
dia).

- **Quant. Dias VT** = total de dias úteis do período **menos** as segundas e sextas do período.
- **Quant. Dias VR** = total de dias úteis do período (sem desconto), **a não ser que exista falta
  real reportada** (atestado, ausência) — isso reduz tanto VT quanto VR, porque a pessoa nem esteve
  presente.

**Exceções permanentes (não descontam VT nunca, ficam sempre com o total de dias do período):**
Samuel, Camila, Bruno, Andreza. Essa lista está inclusive anotada na própria planilha ("Samuel/
Camila/Bruno/Andreza - não descontar dias"). Samuel não recebe VT de forma alguma (a taxa fica em
branco); o VT dele nunca teve valor.

**Andreza e Camila** têm o VT combinado com o VR numa única coluna "Total Saldo Livre" (fórmula na
célula ao lado do rótulo, tipo `=F14+F16` ou `=F26+E24+F24`) — o "Total a Pagar VT" (ver passo 4)
não inclui essas duas linhas, porque o valor delas já está embutido no total de VR/Saldo Livre.

**Renato** é um caso à parte: nunca recebe VT (fica sempre 0, taxa em branco). O VR dele segue a
mesma regra de todo mundo — pago por dia de comparecimento ao escritório, sem desconto de home
office — só que com uma taxa diária diferente, que já está configurada na planilha/app (não
precisa recalcular a taxa, só a quantidade de dias).

**Vanessa Costa** tem uma taxa de VR diferente dos demais (historicamente 29, não 31) — mantenha a
taxa como está na aba duplicada, só atualize a quantidade de dias.

**Sempre confirme com a Camila antes de fechar os números:** pergunte se há alguma observação ou
desconto extra pro período (falta, atestado, sábado presencial, VR em dobro, novo colaborador,
mudança de taxa, etc.). Se ela não informar nada, **deixe a coluna Observações em branco** — não
carregue observações de períodos anteriores (elas são datadas e não se aplicam ao novo período) e
não invente um motivo. Se sobrar alguma dúvida que você não conseguir resolver sozinho (um
colaborador com padrão fora do comum, por exemplo), pergunte diretamente em vez de supor — já
aconteceu de casos assim (Renato) precisarem de esclarecimento antes de fechar.

## Passo 4 — Ler os totais

A própria planilha já soma os totais certos, não precisa recalcular na mão se conseguir ler os
valores em cache (célula "Total a Pagar VT:" e "Total a Pagar VR/Saldo Livre:", na área à direita
da tabela de colaboradores — geralmente colunas J-K perto das linhas 9-13):

- **Total VT** = soma de `Total VT` de cada colaborador, **exceto** Andreza e Camila (que entram no
  outro total, ver passo 3) e Renato (que nunca tem VT).
- **Total VR/Saldo Livre** = soma de `Total VR` de todo mundo, incluindo o saldo livre combinado de
  Andreza e Camila.

Se o arquivo tiver acabado de ser salvo por `openpyxl` (sem recálculo do Excel ainda), os valores
em cache vêm `None` — nesse caso, calcule na mão multiplicando taxa (coluna "Dia VT"/"Dia VR") ×
quantidade de dias (coluna "Quant. Dias") linha por linha, seguindo as mesmas fórmulas que já estão
na planilha (ex: `=C9*D9`). Confira a conta duas vezes antes de reportar — são valores que viram
lançamento financeiro de verdade.

## Passo 5 — Lançar as duas contas a pagar no Omie

São **dois lançamentos separados**, sempre com o **valor total** (não por colaborador), usando
`mcp__omie__omie_incluir_conta_pagar`:

| Campo | VT | VR |
|---|---|---|
| `codigo_categoria` | `2.03.11` | `2.03.12` |
| `valor_documento` | Total VT (passo 4) | Total VR/Saldo Livre (passo 4) |
| `codigo_cliente_fornecedor` | `10366274657` (iFood) | `10366274657` (iFood) |
| `id_conta_corrente` | `10361411805` | `10361411805` |
| `data_vencimento` e `data_previsao` | **dia de início do período** (não a data de pagamento final) | idem |
| `codigo_lancamento_integracao` | único, ex: `VTVR-<ano>-<mes>-<ciclo>-VT` | ex: `VTVR-<ano>-<mes>-<ciclo>-VR` |

`<ciclo>` distingue os dois pagamentos do mesmo mês — use `5DU` pro pagamento do 5º dia útil e `D20`
pro pagamento do dia 20, senão os códigos colidem quando os dois ciclos caem no mesmo mês.

**A data de vencimento/previsão é sempre o dia que INICIA o período, não o dia do pagamento final**
— confirmado explicitamente pela Camila, é assim que ela quer o registro contábil, mesmo que pareça
contraintuitivo à primeira vista (provavelmente porque o crédito no cartão precisa estar disponível
desde o início do período de uso).

**Observação de todo lançamento** (padrão fixo, sempre incluir):

```
Lançamento gerado via IA. Em caso de dúvida ou divergência, confirmar com Camila Rocha antes do pagamento.
```

Complemente com o período, ex: `"VT - Período 21/09/2026 a 06/10/2026"` + a linha acima.

Não existe ferramenta de edição de conta a pagar no MCP do Omie (só `incluir`) — se precisar
corrigir um lançamento já criado, avise a Camila para ajustar direto no Omie, você não consegue
fazer isso por aqui.

## Resumo final

Depois de lançar, responda no formato objetivo que a Camila prefere: aba criada, período,
quantidade de dias por colaborador (se relevante mostrar), os dois totais e os dois códigos de
lançamento do Omie. Sinalize claramente qualquer ponto que ficou sem confirmação (observação não
respondida, colaborador com padrão fora do comum, etc.) em vez de escapar por baixo do tapete.
