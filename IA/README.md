# PriceAI - Sistema Ultra Seguro de Análise de Preços Inteligente

Este projeto é uma aplicação de alta segurança para análise de preços utilizando Inteligência Artificial (Gemini).

## 🚀 Tecnologias Utilizadas

- **Backend:** FastAPI (Python 3.10+)
- **Servidor:** Uvicorn
- **AI:** Google Gemini Pro
- **Segurança:** 
  - JWT (JSON Web Tokens)
  - Rate Limiting (Slowapi)
  - Cabeçalhos de Segurança (CSP, HSTS, XSS Protection, nosniff)
  - Validação rigorosa de inputs com Pydantic
  - Trusted Host Middleware

## 🛡️ Segurança de Alto Nível

O sistema foi desenvolvido seguindo as melhores práticas de segurança da OWASP:
1. **HSTS**: Força conexões HTTPS.
2. **CSP (Content Security Policy)**: Previne ataques de XSS.
3. **Prevenção de XSS & Sniffing**: Cabeçalhos específicos para proteger o navegador.
4. **Rate Limiting**: Proteção contra ataques de força bruta e negação de serviço (DoS).
5. **Secret Key Management**: Utilização de variáveis de ambiente para chaves sensíveis.

## 📦 Como Instalar

1. Clone o repositório.
2. Acesse a pasta `backend`:
   ```bash
   cd backend
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure sua chave do Gemini no arquivo `.env` (ou variável de ambiente):
   ```env
   GEMINI_API_KEY=seu_token_aqui
   ```

## 🏃 Como Executar

Para rodar o servidor backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Documentação da API

Acesse a documentação interativa (Swagger UI) em:
`http://localhost:8000/api/v1/docs`

## 🎨 Frontend (Vite + React)

Localizado na pasta `/frontend`, o frontend oferece uma interface premium com:
- Modo Escuro (Dark Mode)
- Glassmorphism design
- Micro-animações suaves
- Design responsivo
