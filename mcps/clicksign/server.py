"""
MCP server para integração com a API do Clicksign (https://developers.clicksign.com).

Autenticação: access_token estático, enviado no header "Authorization" (sem prefixo "Bearer").
Gerado em: Clicksign > Configurações da conta > Integração/API. Expira a cada 90 dias.

Variáveis de ambiente necessárias:
  CLICKSIGN_ACCESS_TOKEN
  CLICKSIGN_ENV       "sandbox" (padrão, sem valor jurídico) ou "production"

Rate limit da API: 50 req/10s em produção, 20 req/10s em sandbox (por conta).
"""

import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

ACCESS_TOKEN = os.environ.get("CLICKSIGN_ACCESS_TOKEN")
ENVIRONMENT = os.environ.get("CLICKSIGN_ENV", "sandbox").strip().lower()

BASE_URLS = {
    "sandbox": "https://sandbox.clicksign.com/api/v3",
    "production": "https://app.clicksign.com/api/v3",
}
BASE_URL = BASE_URLS.get(ENVIRONMENT, BASE_URLS["sandbox"])

mcp = MCPServer("clicksign")


def _request(method: str, path: str, **kwargs) -> Any:
    if not ACCESS_TOKEN:
        raise RuntimeError(
            "CLICKSIGN_ACCESS_TOKEN não configurado. Gere o token em Clicksign > "
            "Configurações da conta > Integração/API e defina a variável de ambiente."
        )

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = ACCESS_TOKEN
    headers["Content-Type"] = "application/vnd.api+json"
    headers["Accept"] = "application/vnd.api+json"
    url = f"{BASE_URL}{path}"

    resp = httpx.request(method, url, headers=headers, timeout=30, **kwargs)

    if resp.status_code == 429:
        raise RuntimeError(
            "Rate limit da API do Clicksign atingido (HTTP 429). "
            f"Limite no ambiente '{ENVIRONMENT}': "
            f"{'50' if ENVIRONMENT == 'production' else '20'} requisições/10s. Aguarde e tente novamente."
        )
    if resp.status_code == 401:
        raise RuntimeError(
            "Token inválido ou expirado (HTTP 401). O access_token do Clicksign expira "
            "a cada 90 dias — gere um novo em Configurações da conta > Integração/API."
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"Erro HTTP {resp.status_code} do Clicksign: {resp.text}")

    if not resp.content:
        return {"status": "ok", "http_status": resp.status_code}
    return resp.json()


@mcp.tool()
def clicksign_listar_envelopes(
    status: str | None = None,
    nome: str | None = None,
    page_size: int = 20,
    page_number: int = 1,
) -> Any:
    """Lista envelopes (processos de assinatura) da conta Clicksign.

    status: draft | running | closed | canceled
    nome: filtra por nome (completo) do envelope
    """
    params: dict[str, Any] = {
        "page[size]": page_size,
        "page[number]": page_number,
    }
    if status:
        params["filter[status]"] = status
    if nome:
        params["filter[name]"] = nome
    return _request("GET", "/envelopes", params=params)


@mcp.tool()
def clicksign_detalhes_envelope(envelope_id: str) -> Any:
    """Retorna os detalhes/estado atual de um envelope específico do Clicksign."""
    return _request("GET", f"/envelopes/{envelope_id}")


@mcp.tool()
def clicksign_criar_envelope(
    nome: str,
    deadline_at: str | None = None,
    locale: str = "pt-BR",
    auto_close: bool = True,
    remind_interval: int | None = None,
) -> Any:
    """Cria um novo envelope (rascunho) no Clicksign, para depois adicionar documentos e signatários.

    deadline_at: data limite no formato ISO 8601 (ex: 2026-12-31T23:59:59-03:00)
    remind_interval: intervalo em dias para lembretes automáticos de assinatura
    """
    attributes: dict[str, Any] = {
        "name": nome,
        "locale": locale,
        "auto_close": auto_close,
    }
    if deadline_at:
        attributes["deadline_at"] = deadline_at
    if remind_interval is not None:
        attributes["remind_interval"] = str(remind_interval)

    body = {"data": {"type": "envelopes", "attributes": attributes}}
    return _request("POST", "/envelopes", json=body)


@mcp.tool()
def clicksign_upload_documento(
    envelope_id: str,
    filename: str,
    content_base64: str,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """Adiciona um documento a um envelope (upload via conteúdo em base64).

    filename: nome do arquivo com extensão (.pdf, .docx, .doc, .txt, .png, .jpeg)
    content_base64: conteúdo do arquivo já codificado em base64
    """
    attributes: dict[str, Any] = {"filename": filename, "content_base64": content_base64}
    if metadata:
        attributes["metadata"] = metadata

    body = {"data": {"type": "documents", "attributes": attributes}}
    return _request("POST", f"/envelopes/{envelope_id}/documents", json=body)


@mcp.tool()
def clicksign_criar_signatario(
    envelope_id: str,
    nome: str,
    email: str | None = None,
    phone_number: str | None = None,
    documentation: str | None = None,
    has_documentation: bool = True,
    refusable: bool = False,
) -> Any:
    """Adiciona um signatário a um envelope do Clicksign.

    nome: nome completo (mínimo 2 palavras)
    email: obrigatório para notificação por e-mail
    phone_number: DDD + número (10-11 dígitos), obrigatório para SMS/WhatsApp
    documentation: CPF no formato 000.000.000-00
    """
    attributes: dict[str, Any] = {
        "name": nome,
        "has_documentation": has_documentation,
        "refusable": refusable,
    }
    if email:
        attributes["email"] = email
    if phone_number:
        attributes["phone_number"] = phone_number
    if documentation:
        attributes["documentation"] = documentation

    body = {"data": {"type": "signers", "attributes": attributes}}
    return _request("POST", f"/envelopes/{envelope_id}/signers", json=body)


@mcp.tool()
def clicksign_criar_requisito_autenticacao(
    envelope_id: str,
    document_id: str,
    signer_id: str,
    auth: str = "email",
) -> Any:
    """Vincula um requisito de autenticação a um signatário/documento (necessário antes de ativar o envelope).

    auth: email | sms | whatsapp | icp_brasil | selfie | official_document | address_proof |
          liveness | facial_biometrics | pix | handwritten, entre outros.
    Cada signatário precisa de ao menos um requisito de autenticação para o envelope poder ser ativado.
    """
    body = {
        "data": {
            "type": "requirements",
            "attributes": {"action": "provide_evidence", "auth": auth},
            "relationships": {
                "document": {"data": {"type": "documents", "id": document_id}},
                "signer": {"data": {"type": "signers", "id": signer_id}},
            },
        }
    }
    return _request("POST", f"/envelopes/{envelope_id}/requirements", json=body)


@mcp.tool()
def clicksign_ativar_envelope(envelope_id: str) -> Any:
    """Ativa o envelope (muda status de 'draft' para 'running'), disparando o envio para assinatura.

    Requer que todo documento tenha sido adicionado e todo signatário já tenha ao menos
    um requisito de autenticação cadastrado (ver clicksign_criar_requisito_autenticacao).
    Ação irreversível: o envelope não pode voltar para 'draft' depois de ativado.
    """
    body = {"data": {"id": envelope_id, "type": "envelopes", "attributes": {"status": "running"}}}
    return _request("PATCH", f"/envelopes/{envelope_id}", json=body)


@mcp.tool()
def clicksign_notificar_signatario(envelope_id: str, signer_id: str) -> Any:
    """Reenvia a notificação de solicitação de assinatura para um signatário específico."""
    return _request("POST", f"/envelopes/{envelope_id}/signers/{signer_id}/notifications", json={})


if __name__ == "__main__":
    mcp.run(transport="stdio")
