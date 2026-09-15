# ASContabilidadeempresarial

Repositório de automações internas da **A&S Contabilidade**: servidores MCP e skills do Claude Code usados na rotina do escritório (societário, tarefas, financeiro).

## Estrutura

```
mcps/
  gclick/     servidor MCP de integração com a API do GClick (app.gclick.com.br)
  omie/       servidor MCP de integração com a API do Omie
skills/
  arquivar-processo-societario/   transporta documentos de processo societário finalizado para a pasta definitiva da empresa
  atualizar-tarefa-gclick/        registra andamento/comentário no histórico de uma tarefa no GClick
  criar-tarefa-gclick/            cria tarefa/solicitação nova no GClick para a equipe
  processar-vt-vr/                processa o ciclo quinzenal de VT/VR e lança as contas a pagar no Omie
```

## MCPs

### gclick

Integração com a API do GClick (OAuth2 client_credentials).

```bash
cd mcps/gclick
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements.txt
```

Variáveis de ambiente necessárias:

```
GCLICK_CLIENT_ID
GCLICK_CLIENT_SECRET
```

Credenciais geradas em: GClick > Configurações > API > Criar aplicação.

### omie

Integração com a API do Omie.

```bash
cd mcps/omie
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements.txt
```

Variáveis de ambiente necessárias:

```
OMIE_APP_KEY
OMIE_APP_SECRET
```

## Skills

Skills usadas pelo Claude Code (`~/.claude/skills`). Cada uma documenta um fluxo real da operação da A&S — ver o `SKILL.md` de cada pasta para o passo a passo completo e as regras de negócio.

| Skill | O que faz |
|---|---|
| `arquivar-processo-societario` | Move documentos de um processo societário finalizado para a pasta definitiva da empresa, organizando por subpasta (Receita Federal, Prefeitura, SEFAZ, Conselho, Alterações Contratuais, Documentos) |
| `atualizar-tarefa-gclick` | Registra um comentário/andamento no histórico de uma tarefa existente no GClick |
| `criar-tarefa-gclick` | Cria uma tarefa/solicitação nova no GClick para um colaborador executar |
| `processar-vt-vr` | Processa o ciclo quinzenal de vale-transporte/vale-refeição e lança os valores como conta a pagar no Omie |

## Segurança

Nenhuma credencial fica no código — ambos os MCPs leem client ID/secret de variáveis de ambiente. Nunca commitar arquivos `.env` ou pastas `.venv` (já cobertos pelo `.gitignore`).
