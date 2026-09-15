---
name: arquivar-processo-societario
description: Transporta os documentos de uma pasta de processo societário finalizado, em "PROCESSOS SOCIETÁRIOS\<EMPRESA>", para a pasta definitiva da empresa em "EMPRESAS\<EMPRESA>\SOCIETÁRIO", organizando cada documento na subpasta numerada certa (RECEITA_FEDERAL, PREFEITURA_MUNICIPAL, SEFAZ, CONSELHO, ALTERAÇÕES CONTRATUAIS, DOCUMENTOS). Use esta skill sempre que a Camila disser que um processo foi finalizado, deferido, averbado ou registrado (JUCESP, OAB, Receita Federal, Prefeitura, SEFAZ) e pedir para "transportar", "mover", "levar", "arquivar" ou "organizar" os documentos do processo para a pasta da empresa — mesmo sem ela detalhar o mapeamento das pastas. Cobre também o caso de a empresa ser nova e ainda não ter pasta em Empresas (processo de abertura/constituição finalizado): a skill sabe criar a pasta a partir do modelo "____MODELO CLIENTE". Use também sempre que houver uma alteração contratual com nome de arquivo genérico (sem número), pois a skill cobre como identificar e renomear corretamente.
---

# Arquivar processo societário finalizado

Quando um processo societário termina (ex: uma alteração contratual foi deferida na JUCESP), os
documentos que estavam na pasta de trabalho do processo precisam ir para a pasta permanente da
empresa. Esta skill descreve como fazer esse transporte com segurança e do jeito que a Camila
espera — sem criar bagunça de subpastas e sem apagar nada que ela não tenha apagado ela mesma.

## Visão geral do fluxo

1. Localizar a pasta de origem (processo) e a pasta de destino (empresa)
2. Se a empresa ainda não existe em Empresas (processo de abertura/constituição), criar a pasta
   dela a partir do modelo antes de continuar
3. Conferir os documentos e identificar do que se trata cada um
4. Mapear cada documento para a subpasta numerada certa dentro de SOCIETÁRIO
5. Copiar os arquivos, achatando qualquer subpasta da origem
6. Revisar o nome de cada arquivo e renomear o que estiver difícil de identificar
7. Perguntar quando houver ambiguidade real
8. Fechar com um resumo em tabela, documento → pasta de destino

## 1. Localizar as pastas

Origem: `PROCESSOS SOCIETÁRIOS\<EMPRESA>`
Destino: `EMPRESAS\<EMPRESA>\SOCIETÁRIO`

O nome da empresa nas duas árvores nem sempre é idêntico (ex: um processo pode estar em
"SOUL PROJETOS" enquanto a pasta em Empresas se chama só "SOUL"). Antes de assumir que achou a
pasta certa, confirme pelo conteúdo — CNPJ, razão social, NIRE — porque empresas com nomes
parecidos podem ser completamente diferentes (ex: "SOUL" e "BENKSOUL" são duas empresas distintas
na carteira). Um passo errado aqui joga documentos de um cliente na pasta de outro, então vale a
pena gastar uma leitura a mais para ter certeza.

Nem toda sociedade é registrada na JUCESP — sociedades de advogados, por exemplo, registram e
averbam alterações contratuais na OAB (a "averbação" é o equivalente ao deferimento da JUCESP).
A estrutura de pastas numeradas é a mesma; o requerimento e comprovantes de pagamento à OAB vão
em "4. CONSELHO".

Se não encontrar uma correspondência clara — inclusive se não existir NENHUMA pasta da empresa
em Empresas — não invente: veja a seção 2 se for o caso de empresa nova, ou pare e pergunte à
Camila.

## 2. Empresa nova (processo de abertura/constituição)

Quando o processo é de abertura de empresa (constituição), pode não existir ainda nenhuma pasta
dela em `EMPRESAS`. Nesse caso, não crie a estrutura do zero manualmente — duplique o modelo:

1. Localize a pasta `EMPRESAS\____MODELO CLIENTE` — ela tem a estrutura completa e padronizada
   (CONTÁBIL, DP, FINANCEIRO, FISCAL, SAÚDE FISCAL, SOCIETÁRIO, com as subpastas mensais/anuais
   já criadas para o ano corrente).
2. Copie essa estrutura para `EMPRESAS\<NOME DA EMPRESA>`, mas **só as pastas, nunca os arquivos**
   que estiverem dentro do modelo (ex: dentro de "SOCIETÁRIO\1. RECEITA_FEDERAL" o modelo tem um
   CNPJ.pdf de exemplo) — esses arquivos são de uma empresa real usada como referência para
   montar o modelo, e levá-los adiante misturaria documento de outro cliente na pasta nova.
3. Para o nome da pasta, use o nome pelo qual a empresa é conhecida/registrada (ex: o nome
   fantasia ou a razão social simplificada que aparece no contrato social) — se não estiver óbvio
   pelos documentos do processo, pergunte à Camila antes de decidir.
4. Depois de criada a estrutura vazia, siga o fluxo normal desta skill (seções 3 em diante) para
   preencher o SOCIETÁRIO com os documentos do processo. Numa constituição não existe ainda
   "alteração contratual" — o próprio Contrato Social de constituição e sua minuta vão em
   "5. ALTERAÇÕES CONTRATUAIS", que serve para qualquer ato constitutivo do contrato social
   (constituição, alteração, transformação), não só alterações propriamente ditas.

## 3. Estrutura de destino

Dentro de `EMPRESAS\<EMPRESA>\SOCIETÁRIO` normalmente já existe uma estrutura numerada assim
(pode variar um pouco de empresa para empresa — confira a que existe antes de assumir):

```
1. RECEITA_FEDERAL
2. PREFEITURA_MUNICIPAL
3. SEFAZ
4. CONSELHO
5. ALTERAÇÕES CONTRATUAIS
6. DOCUMENTOS
```

Regra de ouro: **essas pastas numeradas só devem conter arquivos, nunca subpastas.** Se a pasta
de origem do processo tiver subpastas (ex: "FORMULÁRIOS ELETRÔNICOS", "MINUTAS", "ASSINADOS"
dentro da pasta do JUCESP), não replique essa estrutura no destino — traga os arquivos direto
para dentro da pasta numerada correspondente ("achatar"/flatten). A Camila já corrigiu isso uma
vez; o motivo é manter a pasta da empresa simples de navegar no dia a dia, sem precisar abrir
camadas de subpasta para achar um documento.

Se dois arquivos de origens diferentes acabarem com o mesmo nome ao serem trazidos para a mesma
pasta (ex: duas cópias de "3ª ALTERAÇÃO CONTRATUAL.pdf" vindas de lugares diferentes do
processo), não sobrescreva silenciosamente — pare e pergunte à Camila o que fazer (manter as
duas com nomes diferentes, ou confirmar que é a mesma cópia duplicada e trazer só uma).

## 4. Mapear por assunto

Regra geral de mapeamento (ajuste pelo bom senso quando o conteúdo deixar claro outra coisa):

| Conteúdo típico da origem | Destino |
|---|---|
| CNPJ, QSA, DBE, comprovantes da Receita Federal | 1. RECEITA_FEDERAL |
| Alvará, licenciamento municipal, documentos da Prefeitura | 2. PREFEITURA_MUNICIPAL |
| Inscrição estadual, documentos do SEFAZ | 3. SEFAZ |
| Registro em conselho profissional | 4. CONSELHO |
| Contratos sociais, alterações contratuais, capa de requerimento JUCESP, formulários eletrônicos e minutas relacionadas a uma alteração | 5. ALTERAÇÕES CONTRATUAIS |
| Documentos de apoio que não são nenhum dos anteriores (IPTU, contrato de locação/escritório virtual, comprovantes diversos) | 6. DOCUMENTOS |

Pastas de origem vazias (ex: "4. PREFEITURA" sem nenhum arquivo dentro) simplesmente não geram
nada para copiar — não é erro, só não havia documento daquele tipo neste processo.

## 5. Copiar, não mover, por padrão

Copie os arquivos da origem para o destino — não mova e não apague a origem, a menos que a
Camila peça explicitamente para mover. Isso preserva o histórico do processo até ela mesma
decidir arquivá-lo ou não. Se ela pedir para mover, o resultado prático (copiar + ela apagar a
origem depois) é o mesmo; veja a seção de exclusão abaixo sobre quem apaga o quê.

Antes de copiar, olhe o que já existe no destino. É comum a pasta da empresa já ter documentos de
alterações anteriores arquivados do mesmo jeito (ex: já existe "2ª ALTERAÇÃO CONTRATUAL.pdf" e
alguns documentos de apoio de quando aquela alteração foi processada). Não recopie o que já está
lá — só traga o que é novo neste processo. Isso evita duplicar arquivo à toa e deixa mais rápido
enxergar o que de fato mudou.

## 6. Revisar e renomear os nomes dos arquivos

A pasta de processo acumula nomes de arquivo de todo tipo — muitos gerados automaticamente por
sistema (protocolo, portal da prefeitura, assinatura eletrônica), que não dizem nada pra quem
abrir a pasta da empresa depois. Antes de finalizar, revise o nome de **cada** documento que for
para o destino, não só os de alteração contratual, e renomeie o que não estiver claro à primeira
vista. A pasta da empresa é consultada por qualquer pessoa da equipe, não só por quem fez o
transporte — o nome do arquivo precisa se explicar sozinho.

Exemplos de nomes ruins encontrados na prática e como ficam melhores:
- `2025123998977_1772048294478.pdf` → identifique o conteúdo (abrindo o arquivo se precisar) e
  renomeie para algo como `CNH-e Bruno Victor.pdf` ou `Comprovante Endereço.pdf`
- `CadastroContribuinteMobiliario_34255980_2026-05-14_195928.pdf` → `Cadastro Contribuinte Mobiliário.pdf`
- `shareFile_1787573798443 - conselho.pdf` → `Comprovante Envio Conselho.pdf`
- `DOC ERINEU _assinado__1786990100558.pdf` → `Documento Erineu (assinado).pdf`

Um caso específico e recorrente é a **Alteração Contratual com nome genérico**, tipo
"ALTERAÇÃO CONTRATUAL.pdf", sem indicar se é a 1ª, 2ª, 3ª alteração etc. Antes de colocar esse
arquivo em "5. ALTERAÇÕES CONTRATUAIS", abra e leia o conteúdo do PDF: o próprio documento
normalmente informa o número da alteração no título ou no corpo do texto (ex: "2ª Alteração e
Consolidação do Contrato Social"), e a certidão da JUCESP (ou a averbação da OAB) mostra a data
de deferimento e o protocolo, o que ajuda a confirmar que é mesmo um documento definitivo e não
uma minuta. Renomeie para refletir o número correto (ex: de "ALTERAÇÃO CONTRATUAL.pdf" para
"2ª ALTERAÇÃO CONTRATUAL.pdf") — isso evita que alterações fiquem soltas com nome ambíguo, ou que
uma alteração antiga seja confundida com a mais recente do processo atual.

O que **não** precisa renomear: nomes já claros e específicos (ex: "CNPJ.pdf", "QSA.pdf",
"IPTU - Alphaville.pdf") — a ideia não é padronizar tudo à força, é só garantir que ninguém vá
precisar abrir o arquivo pra saber o que é.

## 7. Nunca excluir arquivos — nem se a Camila pedir diretamente

Esta é uma regra do ambiente, não uma preferência: você não pode apagar arquivos ou pastas com
conteúdo, mesmo que a Camila peça diretamente ("apaga", "pode excluir", "exclui essa pasta").
Isso vale mesmo depois de já ter copiado os arquivos para o destino — a cópia não muda a regra.

Quando isso acontecer:
- Não recuse a conversa inteira nem trave o fluxo — explique rapidamente que não pode excluir e
  siga adiante com o que pode fazer (copiar, mover, renomear, organizar).
- Liste exatamente o que precisa ser apagado, com caminho completo, para ela apagar em poucos
  cliques.
- Ofereça abrir a pasta no Explorer para facilitar (`explorer.exe "<caminho>"` via PowerShell é
  uma ação segura e não destrutiva).
- Remover uma pasta *vazia* que você mesmo criou como parte da reorganização (ex: depois de mover
  os arquivos de dentro dela para o destino final) não é a mesma coisa que apagar um documento —
  isso pode ser feito normalmente, já que não há conteúdo sendo destruído.

## 8. Pergunte quando for ambíguo

Situações que valem uma pergunta objetiva antes de agir, em vez de assumir:
- Minutas/rascunhos do processo devem ser transportados junto ou ficam de fora?
- Um documento não se encaixa claramente em nenhuma subpasta numerada — onde ele deveria ir?
- A pasta da empresa em "EMPRESAS" não foi encontrada com um nome parecido o suficiente para ter
  certeza — qual é a pasta certa?
- Dois documentos parecem ser a mesma coisa duplicada, mas não é possível confirmar pelo conteúdo.
- É uma empresa nova e o nome a usar na pasta de Empresas não está claro pelos documentos.

Fora essas situações, siga o mapeamento e execute — a Camila prefere ver o resultado organizado
do que ser interrompida a cada passo óbvio.

## 9. Resumo final

Termine sempre com uma tabela objetiva mostrando o que foi transportado e para onde, seguindo o
padrão de comunicação da Camila (direto, sem texto longo):

| Documento | Foi para |
|---|---|
| CNPJ.pdf | 1. RECEITA_FEDERAL |
| 3ª ALTERAÇÃO CONTRATUAL.pdf | 5. ALTERAÇÕES CONTRATUAIS |
| ... | ... |

Se algo ficou pendente de exclusão manual, liste separadamente com o caminho completo, como
descrito na seção 7.
