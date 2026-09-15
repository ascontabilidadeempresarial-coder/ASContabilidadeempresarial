"""
MCP server para integração com a API do Omie Financeiro (https://app.omie.com.br/api/v1).

Autenticação: app_key + app_secret enviados no corpo (body) de cada requisição JSON
(não vão em header nem em query string). Gerados em: Omie > Meus Aplicativos >
engrenagem > "Resumo do App" > "Chave de Integração (API)", ou em
developer.omie.com.br > Aplicativos.

Variáveis de ambiente necessárias:
  OMIE_APP_KEY
  OMIE_APP_SECRET

Limites de consumo da API (ver "Limites de Consumo da API do Omie" na ajuda Omie):
  - 960 requisições/minuto por Endereço IP
  - 240 requisições/minuto por Endereço IP + App Key + Método
  - 4 requisições simultâneas por Endereço IP + App Key + Método
  - Após 10 falhas seguidas na mesma combinação IP+AppKey+Método: bloqueio de 30
    minutos (HTTP 425)
  - Máximo de 100 registros por página

Particularidade importante: a API do Omie pode responder HTTP 200 mesmo em caso de
erro de negócio — o corpo da resposta deve sempre ser verificado quanto aos campos
"faultstring"/"faultcode".
"""

import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

BASE_URL = "https://app.omie.com.br/api/v1"

APP_KEY = os.environ.get("OMIE_APP_KEY")
APP_SECRET = os.environ.get("OMIE_APP_SECRET")

mcp = MCPServer("omie")


def _call(path: str, call: str, param: dict[str, Any]) -> Any:
    if not APP_KEY or not APP_SECRET:
        raise RuntimeError(
            "OMIE_APP_KEY / OMIE_APP_SECRET não configurados. Gere as credenciais em "
            "Omie > Meus Aplicativos > engrenagem > Resumo do App > Chave de Integração (API)."
        )

    body = {
        "call": call,
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": [param],
    }

    resp = httpx.post(f"{BASE_URL}{path}", json=body, timeout=30)

    if resp.status_code == 425:
        raise RuntimeError(
            "Bloqueio temporário da API do Omie (HTTP 425): 10 falhas seguidas na mesma "
            "combinação IP + App Key + Método. Aguarde 30 minutos antes de tentar novamente."
        )
    if resp.status_code == 429:
        raise RuntimeError(
            "Rate limit da API do Omie atingido (HTTP 429): máximo de 240 requisições/minuto "
            "por IP + App Key + Método (ou 960/minuto por IP). Aguarde e tente novamente."
        )
    resp.raise_for_status()

    data = resp.json()
    if isinstance(data, dict) and ("faultstring" in data or "faultcode" in data):
        raise RuntimeError(f"Erro da API do Omie ({data.get('faultcode', '?')}): {data.get('faultstring', data)}")
    return data


@mcp.tool()
def omie_listar_clientes(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    apenas_importado_api: bool = False,
) -> Any:
    """Lista clientes/fornecedores cadastrados no Omie, com paginação.

    Máximo de 100 registros por página. Retorna, entre outros campos, codigo_cliente_omie
    (usado para identificar o cliente em outras chamadas) e cnpj_cpf.
    """
    return _call(
        "/geral/clientes/",
        "ListarClientes",
        {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, 100),
            "apenas_importado_api": "S" if apenas_importado_api else "N",
        },
    )


@mcp.tool()
def omie_upsert_cliente(
    codigo_cliente_integracao: str,
    razao_social: str,
    cnpj_cpf: str,
    email: str | None = None,
    telefone1_numero: str | None = None,
    nome_fantasia: str | None = None,
) -> Any:
    """Cria ou atualiza (upsert) um cliente/fornecedor no Omie.

    codigo_cliente_integracao é a chave de identificação do registro no seu sistema
    (não é o codigo_cliente_omie interno) — usar o mesmo valor em chamadas futuras para
    atualizar o mesmo cliente em vez de duplicá-lo.
    """
    param: dict[str, Any] = {
        "codigo_cliente_integracao": codigo_cliente_integracao,
        "razao_social": razao_social,
        "cnpj_cpf": cnpj_cpf,
    }
    if email is not None:
        param["email"] = email
    if telefone1_numero is not None:
        param["telefone1_numero"] = telefone1_numero
    if nome_fantasia is not None:
        param["nome_fantasia"] = nome_fantasia
    return _call("/geral/clientes/", "UpsertCliente", param)


@mcp.tool()
def omie_listar_contas_pagar(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    apenas_importado_api: bool = False,
) -> Any:
    """Lista contas a pagar cadastradas no Omie, com paginação (máximo 100 por página).

    Sem filtro de data, a API considera por padrão os últimos 30 dias.
    """
    return _call(
        "/financas/contapagar/",
        "ListarContasPagar",
        {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, 100),
            "apenas_importado_api": "S" if apenas_importado_api else "N",
        },
    )


@mcp.tool()
def omie_incluir_conta_pagar(
    codigo_lancamento_integracao: str,
    codigo_cliente_fornecedor: int,
    data_vencimento: str,
    valor_documento: float,
    codigo_categoria: str,
    data_previsao: str,
    id_conta_corrente: int,
    observacao: str | None = None,
) -> Any:
    """Cadastra uma nova conta a pagar no Omie.

    Datas no formato DD/MM/AAAA. codigo_cliente_fornecedor é o codigo_cliente_omie do
    fornecedor (ver omie_listar_clientes). observacao é o texto livre de descrição do
    lançamento. Retorna codigo_lancamento_omie, a ser usado em omie_baixar_conta_pagar.
    """
    param: dict[str, Any] = {
        "codigo_lancamento_integracao": codigo_lancamento_integracao,
        "codigo_cliente_fornecedor": codigo_cliente_fornecedor,
        "data_vencimento": data_vencimento,
        "valor_documento": valor_documento,
        "codigo_categoria": codigo_categoria,
        "data_previsao": data_previsao,
        "id_conta_corrente": id_conta_corrente,
    }
    if observacao is not None:
        param["observacao"] = observacao
    return _call("/financas/contapagar/", "IncluirContaPagar", param)


@mcp.tool()
def omie_baixar_conta_pagar(
    codigo_lancamento: int,
    codigo_conta_corrente: int,
    valor: float,
    data: str,
) -> Any:
    """Registra a baixa (pagamento/liquidação) de uma conta a pagar existente no Omie.

    codigo_lancamento é o codigo_lancamento_omie retornado por omie_incluir_conta_pagar
    ou por omie_listar_contas_pagar. Data no formato DD/MM/AAAA.
    """
    return _call(
        "/financas/contapagar/",
        "LancarPagamento",
        {
            "codigo_lancamento": codigo_lancamento,
            "codigo_conta_corrente": codigo_conta_corrente,
            "valor": valor,
            "data": data,
        },
    )


@mcp.tool()
def omie_listar_contas_receber(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    apenas_importado_api: bool = False,
) -> Any:
    """Lista contas a receber cadastradas no Omie, com paginação (máximo 100 por página).

    Sem filtro de data, a API considera por padrão os últimos 30 dias.
    """
    return _call(
        "/financas/contareceber/",
        "ListarContasReceber",
        {
            "pagina": pagina,
            "registros_por_pagina": min(registros_por_pagina, 100),
            "apenas_importado_api": "S" if apenas_importado_api else "N",
        },
    )


@mcp.tool()
def omie_incluir_conta_receber(
    codigo_lancamento_integracao: str,
    codigo_cliente_fornecedor: int,
    data_vencimento: str,
    valor_documento: float,
    codigo_categoria: str,
    data_previsao: str,
    id_conta_corrente: int,
    observacao: str | None = None,
) -> Any:
    """Cadastra uma nova conta a receber no Omie.

    Datas no formato DD/MM/AAAA. codigo_cliente_fornecedor é o codigo_cliente_omie do
    cliente (ver omie_listar_clientes). observacao é o texto livre de descrição do
    lançamento. Retorna codigo_lancamento_omie, a ser usado em omie_baixar_conta_receber.
    """
    param: dict[str, Any] = {
        "codigo_lancamento_integracao": codigo_lancamento_integracao,
        "codigo_cliente_fornecedor": codigo_cliente_fornecedor,
        "data_vencimento": data_vencimento,
        "valor_documento": valor_documento,
        "codigo_categoria": codigo_categoria,
        "data_previsao": data_previsao,
        "id_conta_corrente": id_conta_corrente,
    }
    if observacao is not None:
        param["observacao"] = observacao
    return _call("/financas/contareceber/", "IncluirContaReceber", param)


@mcp.tool()
def omie_baixar_conta_receber(
    codigo_lancamento: int,
    codigo_conta_corrente: int,
    valor: float,
    data: str,
) -> Any:
    """Registra a baixa (recebimento/liquidação) de uma conta a receber existente no Omie.

    codigo_lancamento é o codigo_lancamento_omie retornado por omie_incluir_conta_receber
    ou por omie_listar_contas_receber. Data no formato DD/MM/AAAA.
    """
    return _call(
        "/financas/contareceber/",
        "LancarRecebimento",
        {
            "codigo_lancamento": codigo_lancamento,
            "codigo_conta_corrente": codigo_conta_corrente,
            "valor": valor,
            "data": data,
        },
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
