# Guia de Segurança - PriceAI

Este documento detalha as medidas de segurança implementadas e recomendações para o ambiente de produção.

## 1. Proteção de Transporte (TLS/SSL)
Embora o FastAPI forneça o middleware `Strict-Transport-Security`, é altamente recomendável utilizar um proxy reverso como **Nginx** ou **Traefik** para gerenciar os certificados SSL/TLS (Let's Encrypt).

## 2. Autenticação e Autorização
Atualmente, o sistema suporta integração com JWT. Para habilitar em produção:
- Altere `SECRET_KEY` no `.env`.
- Use chaves de pelo menos 32 bytes (256 bits).

## 3. Rate Limiting
Configurado via `slowapi` para prevenir abusos:
- Endpoints de análise têm limites mais rigorosos para evitar custos excessivos com a API de IA.

## 4. Segurança de Headers
O sistema injeta automaticamente:
- `X-Frame-Options: DENY`: Previne Clickjacking.
- `X-Content-Type-Options: nosniff`: Previne MIME sniffing.
- `X-XSS-Protection`: Proteção legada contra XSS.
- `Content-Security-Policy`: Restringe a origem dos scripts.

## 5. Validação de Dados
Todos os dados recebidos são validados via Pydantic. Não há execução de SQL bruto ou chamadas de sistema inseguras (`eval`, `exec`).

## 6. Variáveis de Ambiente
NUNCA versione arquivos `.env` com chaves reais. Utilize segredos do GitHub ou gerenciadores de segredos do seu provedor de nuvem.
