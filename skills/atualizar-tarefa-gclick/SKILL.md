---
name: atualizar-tarefa-gclick
description: Registra um comentário/observação (andamento) no histórico de uma tarefa no GClick (app.gclick.com.br), o sistema de gestão de tarefas/obrigações da A&S Contabilidade. Use esta skill sempre que a Camila pedir para "atualizar", "registrar", "colocar", "anotar" ou "puxar" algo no histórico/andamento de uma tarefa de um cliente no GClick — mesmo que ela não diga explicitamente "GClick", já que é o único sistema de tarefas da empresa. Cobre o fluxo de login manual (Claude nunca digita senha), busca do cliente, escolha da tarefa certa entre as tarefas abertas, e o passo de abrir a tarefa e salvar o comentário — este último passo ainda não foi validado ao vivo na primeira versão desta skill, então documente o que encontrar na primeira execução real.
---

# Atualizar histórico de tarefa no GClick

A Camila usa o GClick para acompanhar as tarefas/obrigações/solicitações da carteira de clientes
da A&S. Quando algo acontece num caso (resposta de cliente, decisão interna, documento recebido),
ela quer que isso fique registrado no histórico da tarefa certa — mas o conteúdo desse registro
vem de fontes que variam bastante (WhatsApp, e-mail, reunião, ou ela mesma ditando na hora), então
esta skill cobre a navegação no sistema, não o conteúdo do que vai escrito.

## O que é fato confirmado vs. o que ainda é hipótese

Esta skill nasceu de uma primeira sessão de exploração ao vivo no GClick, que foi interrompida
antes do passo final (abrir a tarefa e efetivamente salvar um comentário). Por isso, os passos 1
a 4 abaixo já foram testados e podem ser seguidos com confiança. O passo 5 (abrir a tarefa e
salvar o histórico) é uma hipótese — o termo "Andamento" apareceu no menu do sistema
("Relatórios > Andamentos" e "Ações em Lote > Adicionar Andamentos"), o que sugere fortemente que
é esse o nome do campo/registro que a Camila chama de "histórico", mas isso não foi confirmado
clicando de fato numa tarefa. Na primeira vez que esta skill for usada de verdade, trate o passo 5
como exploração guiada (veja "Como explorar com segurança" abaixo) e, depois de descobrir o fluxo
real, atualize esta skill (edite este arquivo) com os refs/nomes de campo exatos para que da
próxima vez o processo seja direto.

## Antes de tudo: confirme com a Camila, nunca invente

Não comece a navegar no sistema sem ter estas três coisas, mesmo que a Camila peça de forma
rápida ("atualiza a tarefa do cliente X"):

1. **Nome do cliente** (ou algo que permita buscar — CNPJ também serve).
2. **Qual tarefa**, se houver mais de uma em aberto para aquele cliente (é comum ter mais de uma —
   ver passo 4). Não escolha por conta própria qual tarefa é "a certa" quando isso não estiver
   óbvio; pergunte.
3. **O texto exato (ou o conteúdo) a registrar.** A origem varia — pode vir colado de uma conversa
   de WhatsApp, resumida de um e-mail, ou ditada na hora. Nunca invente ou resuma por conta
   própria o que aconteceu no caso: além de ser um registro formal do escritório, envolve
   terminologia contábil/jurídica onde uma imprecisão pode confundir quem ler depois. Se a Camila
   disser algo como "já te contei" ou "tá no histórico", mas você não tiver essa informação em
   nenhum lugar acessível (nem nesta conversa, nem em algum arquivo que ela indicar), diga
   claramente que não tem esse conteúdo disponível e peça para ela colar.

Só depois de ter os três, prossiga com a navegação.

## 1. Login

Login é sempre manual, feito pela própria Camila. Nunca digite usuário, senha ou qualquer
credencial nos campos do GClick — isso vale mesmo que ela peça diretamente.

Abra `https://app.gclick.com.br` (o sistema redireciona para o domínio real,
`https://appp.gclick.com.br`, depois do login). Se a sessão estiver expirada, a página mostra o
texto `INNUBEM::GCLICK::ERRO=Sua sessão expirou, favor se logar novamente.` — nesse caso, avise a
Camila e espere ela logar antes de continuar.

## 2. A interface não é confiável por screenshot

O GClick é uma aplicação web (SPA) cujo mecanismo de renderização frequentemente faz o
`screenshot` do navegador voltar em branco/cinza, mesmo com conteúdo real na tela. Não confie em
screenshot para "ver" o que está acontecendo neste sistema — use:

- `get_page_text` para ler o texto visível da tela (é o mais confiável aqui).
- `read_page` com `filter: interactive` (ou `all` quando precisar de mais contexto) para achar
  elementos clicáveis e seus `ref_N`.
- `find` para localizar um texto específico e pegar o `ref_N` correspondente.

## 3. Buscar o cliente

Há uma caixa de busca global no topo, com placeholder "Digite aqui para começar a pesquisa...".
Clique nela e digite o nome do cliente. Isso abre um menu dropdown com categorias: Clientes,
Tarefas, Responsáveis, Contatos, Equipes, Sites Favoritos — e, abaixo, já aparece um preview do
cliente encontrado (nome, CNPJ, tipo, status, status complementar, datas). Use esse preview para
confirmar que é o cliente certo antes de prosseguir (nomes parecidos podem ser empresas
diferentes — mesmo cuidado que se aplica em outras skills societárias da A&S).

## 4. Achar a tarefa certa

Dentro do mesmo dropdown de busca, clique na categoria **Tarefas**. Isso abre um painel pedindo
para "Selecione uma categoria para consultar suas tarefas", com as opções:

- Obrigação
- Cobrança
- Certificados e Procurações
- Solicitação
- Agendamento

Ainda não se sabe de forma geral qual categoria corresponde a qual tipo de caso — isso varia.
Uma pista útil: o status complementar do cliente (visto no preview do passo 3) pode indicar o tipo
de processo — por exemplo, um cliente com status complementar "Em Abertura" teve suas tarefas
relevantes encontradas em "Solicitação". Se não estiver óbvio pela pista, ou se a categoria escolhida
não trouxer a tarefa esperada, tente outra categoria ou pergunte à Camila qual departamento/tipo
está tratando o caso.

Depois de escolher a categoria, aparece a lista de tarefas abertas relacionadas ao cliente
buscado, cada uma mostrando: título da tarefa (ex: "REVISÃO DE PROCESSO FINAL",
"DEMANDA - EXPEDIÇÃO"), departamento responsável (ex: "Sucesso do Cliente", "Expedição"), as datas
A: (início/ação) M: (meta) e V: (vencimento), e o nome + CNPJ do cliente.

Se houver mais de uma tarefa aberta para o cliente, não escolha sozinho qual é "a certa" a menos
que o assunto deixe isso óbvio (ex: a Camila já disse que é sobre expedição, e só uma tarefa é de
Expedição) — confirme com ela.

## 5. Abrir a tarefa e registrar o histórico (passo a validar/documentar)

Clique na tarefa identificada no passo 4 para abrir seus detalhes. A partir daqui o fluxo exato
ainda não foi mapeado ao vivo — proceda como uma exploração guiada:

1. Use `get_page_text` e `read_page` (não screenshot) para entender a tela que abriu.
2. Procure por algo relacionado a **"Andamento"** — é o termo que aparece em outras partes do
   sistema (relatório "Andamentos", ação em lote "Adicionar Andamentos") e é o candidato mais
   provável para o que a Camila chama de "histórico da tarefa". Pode aparecer como uma aba, um
   botão, ou uma seção já visível na tela de detalhe da tarefa.
3. Ao achar o campo de texto certo, confirme com a Camila o texto exato antes de salvar (a menos
   que ela já tenha te passado o texto definitivo), digite o conteúdo e procure o botão de
   salvar/confirmar (ex: "Salvar", "Adicionar", ícone de confirmação).
4. Depois de salvar, confira que o comentário aparece de fato no histórico/lista de andamentos da
   tarefa antes de considerar concluído — não assuma sucesso só porque o clique no botão não deu
   erro.
5. **Atualize esta skill** com o que você descobrir: nome exato da aba/campo, se existe diferença
   de fluxo entre categorias (Obrigação vs. Solicitação vs. Cobrança etc.), e qualquer clique que
   não foi óbvio. Isso evita que a próxima execução comece do zero na exploração.

## Resumo final

Depois de salvar, confirme para a Camila em formato direto, seguindo o padrão de comunicação dela:

```
Cliente — Tarefa atualizada
```

Exemplo: `DORVITA FARMA LTDA — REVISÃO DE PROCESSO FINAL: histórico atualizado com "<resumo curto do que foi registrado>"`

Não é necessário repetir o texto inteiro que foi registrado se ele já foi fornecido por ela na
própria conversa — só confirme que foi salvo e onde.
