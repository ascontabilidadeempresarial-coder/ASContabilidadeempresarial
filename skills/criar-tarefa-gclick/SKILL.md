---
name: criar-tarefa-gclick
description: Cria uma tarefa/solicitação nova no GClick (app.gclick.com.br) para alguém da equipe executar, usando o MCP gclick (~/.claude/mcps/gclick). Use esta skill sempre que a Camila pedir para "abrir", "criar" ou "montar" uma tarefa/solicitação/demanda para um colaborador no GClick — mesmo que ela não diga "GClick" explicitamente, ou diga algo direto como "cria uma solicitação pro Bruno puxar um relatório fiscal" ou "abre uma tarefa pra Vanessa revisar isso". Não confundir com a skill atualizar-tarefa-gclick, que registra andamento em tarefa JÁ EXISTENTE via navegador — esta skill aqui é para CRIAR tarefa nova, e usa o MCP (chamadas de ferramenta gclick_*), não navegação manual.
---

# Criar tarefa/solicitação no GClick

A Camila delega demandas para a equipe abrindo tarefas no GClick. Esta skill usa o MCP `gclick`
(`~/.claude/mcps/gclick/server.py`) para criar essas tarefas pela API em vez de navegar na
interface. As regras abaixo vieram de uma correção real que ela fez na primeira tarefa criada por
IA — a tarefa funcionava, mas o formato estava errado em vários pontos. Seguir esse checklist evita
repetir os mesmos erros.

## Antes de criar: o que você precisa ter em mãos

Não chame `gclick_criar_pretarefa` até ter isto:

1. **O que precisa ser feito** — vira o assunto da tarefa (ver regra 1 abaixo).
2. **Quem vai executar** — precisa do e-mail da pessoa se você ainda não souber o `responsavelId`
   dela (ver "Descobrir o responsavelId" abaixo).
3. **Cliente envolvido, se houver** — nome ou CNPJ, para achar `clienteId`/`inscricao`.
4. **Categoria** — Solicitação, Agendamento ou Obrigação (ver regra 4).
5. **Data meta e prazo fatal (vencimento)** — a não ser que o pedido já traga essas datas
   explicitamente, você tem que perguntar antes de criar. Ver regra 2.

Se faltar e-mail da pessoa, cliente ambíguo, categoria pouco clara, ou as datas, pergunte — não
adivinhe. É melhor uma pergunta a mais do que uma tarefa criada errada que alguém vai ter que
corrigir na mão depois.

## 1. Assunto = categoria curta, EM CAIXA ALTA, no máximo 5 a 7 palavras

O campo `assunto` é o título da tarefa como ele aparece na lista do GClick — precisa ser
escaneável rapidamente, como um rótulo de categoria, não uma frase descrevendo o pedido em
detalhe. Duas regras:

- **Sempre em CAIXA ALTA.**
- **Um rótulo curto e genérico do tipo de demanda, não uma frase específica do caso.** Pense em
  como os títulos de tarefas já existentes no GClick são escritos — coisas como `"TFE -
  PROCESSOS"`, `"REGULARIZAÇÃO CNPJ"`, `"CONSULTA DE PENDÊNCIAS"`, `"ANÁLISE - CONSULTA DE
  PENDÊNCIAS"`. Um pedido como "verificar se há desenquadramento de MEI no eCAC e o total de notas
  emitidas em 2026" não vira o assunto — vira uma categoria como `"ANÁLISE - CONSULTA DE
  PENDÊNCIAS"`, e todo o detalhe específico (o que exatamente verificar, pra qual cliente, etc.)
  vai no `andamento` (regra 3).

Não coloque o nome do cliente no assunto — o cliente é um campo separado
(`clienteId`/`inscricoes`) e já aparece na tela do GClick junto com a tarefa.

Se não tiver certeza de qual rótulo/categoria usar para o tipo de demanda, procure uma tarefa
parecida já existente (via `gclick_listar_tarefas`, filtrando pelo mesmo departamento) e reaproveite
o padrão de nome que a equipe já usa — é melhor seguir uma convenção existente do que inventar uma
nova.

**Casos específicos já corrigidos pela Camila (use como referência de padrão):**

- Taxa municipal de abertura de empresa (2ª via de ISS/taxas cobradas pela prefeitura na abertura):
  `"TAXA DE ABERTURA - PREFEITURA <CIDADE>"` — o nome do órgão/município entra no assunto (não o
  tipo de tributo como "ISS"), no singular ("TAXA", não "TAXAS"). Ex: para um cliente em Itu,
  `"TAXA DE ABERTURA - PREFEITURA ITU"`.

**Por quê:** um assunto longo alaga a listagem de tarefas do GClick, que é a visão em que a Camila
e a equipe navegam entre várias tarefas ao mesmo tempo. Título curto e direto, detalhe completo no
andamento.

## 2. Datas: dataAcao é automática, dataMeta e dataVencimento você pergunta

- `dataAcao` (data de ação) é sempre o dia em que a tarefa está sendo aberta — preencha com a data
  de hoje automaticamente, sem perguntar.
- `dataMeta` (o dia que a pessoa deveria mirar entregar) e o prazo fatal (`dataVencimento`) são
  decisões da Camila, não suas. Se o pedido original já trouxe essas datas, use-as. Se não trouxe,
  pergunte antes de criar a tarefa — mesmo que pareça um detalhe pequeno para um pedido rápido.
  Presumir essas datas errado pode fazer alguém entregar tarde (ou a Camila cobrar cedo demais).

> Nota técnica (confirmada): `POST /v2/tarefas/preTarefas` **rejeita com erro 400** se você
> mandar `dataMeta` ou `dataVencimento` no corpo (`"Campo [dataMeta] não reconhecido"`) — não é só
> falta de documentação, a API realmente não aceita esses campos nessa versão. Toda tarefa criada
> por ele sai com `dataAcao`, `dataMeta` e `dataVencimento` iguais à data de criação (hoje), sem
> exceção. Ainda assim pergunte as datas à Camila (regra acima) — mas avise que elas **não vão
> refletir no GClick automaticamente**: registre a data meta/prazo combinado no texto do
> `andamento`, e diga a ela que vai precisar ajustar essas datas manualmente na tela da tarefa se
> forem diferentes de hoje.

## 3. Andamento: um parágrafo de verdade, não uma frase solta

O campo `andamento` é o que a pessoa designada vai ler para entender o que fazer. Escreva um
parágrafo com contexto real — o que foi pedido, para quem, e qualquer detalhe relevante que você
tenha na conversa — em vez de uma linha genérica tipo "Solicito que fulano faça X". Pense em como
explicaria a demanda para alguém que não estava na conversa com a Camila.

Sempre termine o `andamento` com esta linha, em uma linha própria — ela avisa que **a tarefa
inteira** (não só o texto do andamento) foi criada com apoio de IA:

```
🤖 Esta tarefa foi criada pela IA. Em caso de dúvidas ou inconsistências, falar com a Camila.
```

## 4. Escolher a categoria certa

`gclick_criar_pretarefa` cria a tarefa dentro de uma categoria/fluxo de departamento
(`departamentoId`). Pense no tipo de demanda:

- **Solicitação** — pedido pontual para alguém fazer algo (a maioria dos casos do dia a dia).
- **Agendamento** — algo com data/hora específica marcada.
- **Obrigação** — vinculado a uma obrigação fiscal/contábil recorrente já cadastrada no sistema.

Se não estiver óbvio pelo pedido, pergunte à Camila em vez de usar Solicitação como padrão fixo —
ela mencionou explicitamente que isso precisa ser avaliado caso a caso.

Para achar o `departamentoId` certo, use `gclick_listar_tarefas` filtrando por uma tarefa parecida
já existente (mesmo departamento/assunto) e reaproveite o `departamentoId` que aparece no
resultado, ou pergunte à Camila qual departamento é responsável por aquele tipo de demanda.

## 5. Descobrir o `responsavelId` da pessoa

Não existe endpoint na API do GClick para buscar um usuário por nome ou e-mail. O jeito que
funcionou na prática:

1. Peça o e-mail da pessoa (ex: `bruno@ascontabilidadeempresarial.com.br`).
2. Chame `gclick_listar_tarefas` com `categoria="Obrigacao"` e vá paginando (`page=0,1,2...`,
   `size=100`) algumas páginas.
3. Cada tarefa retornada traz um objeto `departamento` com um campo `supervisor` (e a cadeia
   `supervisor.supervisor` sobe até a diretoria) — esses objetos têm `id`, `nome` e `email`.
   Procure pelo e-mail informado dentro dessa cadeia de supervisores até achar a pessoa.
4. Guarde o `id` encontrado — é o `responsavelId` a usar.

Isso funciona bem para quem é supervisor de algum departamento. Se a pessoa não aparecer como
supervisor em nenhuma tarefa das páginas amostradas, tente aumentar o número de páginas ou buscar
em outra categoria (`Solicitacao` etc.) — e se ainda assim não achar, avise a Camila que não
conseguiu localizar o ID automaticamente e pergunte se ela sabe o ID ou pode confirmar de outra
forma.

## 6. Descobrir `clienteId`/`inscricao` do cliente (quando houver cliente envolvido)

Use `gclick_buscar_cliente` passando o CNPJ (campo `inscricao`) — é o jeito direto e confiável,
retorna `id`, nome, apelido e status (ATIVO/INATIVO) do cliente. Se a Camila só te deu o nome do
cliente (sem CNPJ), peça o CNPJ ou procure uma tarefa existente desse cliente via
`gclick_listar_tarefas` para descobrir o CNPJ primeiro.

## 7. Criar a tarefa

Chame `gclick_criar_pretarefa` com os campos reunidos: `departamentoId`, `assunto` (regra 1),
`andamento` (regra 3), `responsavelId` (regra 5), e `clienteId`/`inscricoes` quando houver cliente
(regra 6).

## 8. Depois de criar: reconfira e mostre prova real, não só a resposta de sucesso

A resposta de criação (`{"status": "ok", "id": ..., "msg": "... criado com sucesso"}`) não é prova
suficiente — já aconteceu de uma tarefa "criada com sucesso" não ter o vínculo de cliente realmente
salvo. Sempre, depois de criar:

1. **Monte o ID completo com prefixo de categoria.** A resposta de criação devolve o `id` sem
   prefixo (ex: `4470`). Para reconsultar, é preciso o ID completo como aparece nas listagens —
   `3.<id>` para Solicitação, `4.<id>` para Obrigação (os prefixos de Cobrança/Certificado
   Digital/Agendamento ainda não foram confirmados; se for uma dessas categorias, descubra o
   prefixo certo filtrando `gclick_listar_tarefas` por `responsaveisIds` da pessoa e achando a
   tarefa recém-criada pelo nome/data).
2. **Reconsulte** com `gclick_tarefa_responsaveis` (ID completo) e/ou `gclick_listar_tarefas`
   filtrando por `responsaveisIds` e `categoria`, para confirmar responsável, departamento, status
   e se `clienteId`/`clienteInscricao` realmente ficaram gravados.
3. **Avise proativamente sobre estas duas limitações conhecidas da API**, sem esperar a Camila
   descobrir sozinha:
   - Tarefas criadas por `POST /v2/tarefas/preTarefas` costumam sair com **status "P"**
     (Solicitado — tratado como se fosse aberto externamente/por e-mail, aguardando autorização).
     Isso pode significar que alguém (a Camila ou o responsável) vai precisar autorizar a tarefa
     manualmente no GClick antes dela entrar no fluxo normal.
   - O vínculo de cliente (`clienteId`/`inscricoes`) enviado na criação **às vezes não persiste** —
     confirme no passo 2 acima e avise se `clienteId`/`clienteApelido` voltaram vazios, para que a
     Camila (ou o próprio responsável) possa vincular o cliente manualmente se precisar.

## Resumo final

Depois de confirmar a criação, responda no formato direto que a Camila prefere:

```
Cliente — Tarefa criada
```

Incluindo: ID da tarefa, responsável confirmado, categoria/departamento, e qualquer aviso relevante
do passo 8 (status pendente de autorização, cliente não vinculado, etc.). Não repita o texto
inteiro do andamento se ele já foi combinado na conversa — só confirme o que foi salvo e o que
ainda precisa de atenção.
