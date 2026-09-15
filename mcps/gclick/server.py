"""
MCP server para integração com a API do Omie.G-Click (https://api.gclick.com.br).

Autenticação: OAuth2 client_credentials.
Credenciais geradas em: G-Click > Configurações > API > Criar aplicação.

Variáveis de ambiente necessárias:
  GCLICK_CLIENT_ID
  GCLICK_CLIENT_SECRET
"""

import os
import time
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

BASE_URL = "https://api.gclick.com.br"
TOKEN_URL = f"{BASE_URL}/oauth/token"

CLIENT_ID = os.environ.get("GCLICK_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GCLICK_CLIENT_SECRET")

mcp = MCPServer("gclick")

_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0}


def _get_access_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "GCLICK_CLIENT_ID / GCLICK_CLIENT_SECRET não configurados. "
            "Gere as credenciais em G-Click > Configurações > API."
        )

    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    resp = httpx.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 86399)
    return _token_cache["access_token"]


def _request(method: str, path: str, **kwargs) -> Any:
    token = _get_access_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    url = f"{BASE_URL}{path}"

    resp = httpx.request(method, url, headers=headers, timeout=30, **kwargs)

    if resp.status_code == 429:
        raise RuntimeError("Rate limit da API do GClick atingido (HTTP 429). Aguarde e tente novamente.")
    if resp.status_code == 401:
        _token_cache["access_token"] = None
        raise RuntimeError("Token expirado/inválido (HTTP 401). Verifique client_id/client_secret.")
    resp.raise_for_status()

    if not resp.content:
        return {"status": "ok", "http_status": resp.status_code}
    return resp.json()


@mcp.tool()
def gclick_listar_tarefas(
    categoria: str = "Obrigacao",
    clientes_inscricoes: str | None = None,
    clientes_ids: str | None = None,
    nome: str | None = None,
    data_acao_inicio: str | None = None,
    data_acao_fim: str | None = None,
    data_vencimento_inicio: str | None = None,
    data_vencimento_fim: str | None = None,
    responsaveis_ids: str | None = None,
    departamentos_ids: str | None = None,
    page: int = 0,
    size: int = 20,
) -> Any:
    """Lista tarefas/obrigações no GClick com filtros.

    categoria: Obrigacao | Cobranca | CertificadoDigital | Solicitacao | Agendamento
    clientes_inscricoes: CNPJ(s) do cliente, separados por vírgula
    Datas no formato AAAA-MM-DD.
    """
    params: dict[str, Any] = {"categoria": categoria, "page": page, "size": size}
    optional = {
        "clientesInscricoes": clientes_inscricoes,
        "clientesIds": clientes_ids,
        "nome": nome,
        "dataAcaoInicio": data_acao_inicio,
        "dataAcaoFim": data_acao_fim,
        "dataVencimentoInicio": data_vencimento_inicio,
        "dataVencimentoFim": data_vencimento_fim,
        "responsaveisIds": responsaveis_ids,
        "departamentosIds": departamentos_ids,
    }
    params.update({k: v for k, v in optional.items() if v is not None})
    return _request("GET", "/tarefas", params=params)


@mcp.tool()
def gclick_tarefa_responsaveis(tarefa_id: str) -> Any:
    """Lista os responsáveis (usuários internos) de uma tarefa específica do GClick."""
    return _request("GET", f"/tarefas/{tarefa_id}/responsaveis")


@mcp.tool()
def gclick_tarefa_convidados(tarefa_id: str) -> Any:
    """Lista os convidados (usuários externos/clientes) de uma tarefa específica do GClick."""
    return _request("GET", f"/tarefas/{tarefa_id}/convidados")


@mcp.tool()
def gclick_buscar_cliente(inscricao: str) -> Any:
    """Busca um cliente cadastrado no GClick pelo CNPJ/CPF (campo 'inscricao').

    Retorna id, nome, apelido e status (ATIVO/INATIVO) do cliente, entre outros dados
    cadastrais. Use o "id" do resultado como clienteId ao chamar gclick_criar_pretarefa.
    """
    return _request("GET", "/clientes", params={"inscricao": inscricao})


@mcp.tool()
def gclick_listar_fluxos(departamento_id: int | None = None, page: int = 0, size: int = 20) -> Any:
    """Lista os fluxos (workflows) cadastrados no GClick, opcionalmente filtrando por departamento."""
    params: dict[str, Any] = {"page": page, "size": size}
    if departamento_id is not None:
        params["departamentoId"] = departamento_id
    return _request("GET", "/fluxos", params=params)


@mcp.tool()
def gclick_criar_pretarefa(
    departamento_id: str,
    assunto: str,
    andamento: str,
    inscricoes: list[str] | None = None,
    cliente_id: str | None = None,
    responsavel_id: str | None = None,
    processo_id: str | None = None,
    fluxo_id: str | None = None,
    convidados_ids: list[str] | None = None,
    arquivos: list[str] | None = None,
) -> Any:
    """Cria uma nova pré-tarefa (solicitação) no GClick via API v2.

    Campos obrigatórios: departamento_id, assunto, andamento.
    inscricoes: lista de CNPJs/CPFs do(s) cliente(s) associados.
    """
    body: dict[str, Any] = {
        "departamentoId": departamento_id,
        "assunto": assunto,
        "andamento": andamento,
        "inscricoes": inscricoes or [],
        "arquivos": arquivos or [],
        "convidadosIds": convidados_ids or [],
    }
    if cliente_id is not None:
        body["clienteId"] = cliente_id
    if responsavel_id is not None:
        body["responsavelId"] = responsavel_id
    if processo_id is not None:
        body["processoId"] = processo_id
    if fluxo_id is not None:
        body["fluxoId"] = fluxo_id

    return _request("POST", "/v2/tarefas/preTarefas", json=body)


if __name__ == "__main__":
    mcp.run(transport="stdio")
