# Conexión Higgsfield (MCP)

Higgsfield expone un servidor MCP hospedado que da acceso a sus modelos de imagen y
video (Soul, Cinema Studio, Flux, Seedream, Kling, Minimax Hailuo, Veo, etc.) desde
cualquier agente compatible. La autenticación es por cuenta de Higgsfield vía OAuth:
no hay API key que guardar en el repo.

**Endpoint:** `https://mcp.higgsfield.ai/mcp` (transporte HTTP)

## 1. Claude Code (este repo)

El archivo `.mcp.json` en la raíz ya registra el servidor. Al abrir el repo con
Claude Code, aprueba el servidor cuando lo pida y completa el login de Higgsfield
en el navegador. La sesión queda autenticada con tu cuenta.

Para tenerlo disponible en todos tus proyectos, no solo aquí:

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp
```

Verificar:

```bash
claude mcp list
```

## 2. claude.ai (web / Desktop / Cowork)

Higgsfield todavía no aparece en el directorio público de conectores, así que se
agrega como conector personalizado:

1. Settings → Connectors → **Add custom connector**
2. Nombre: `Higgsfield`
3. URL: `https://mcp.higgsfield.ai/mcp`
4. Conectar y autenticar con la cuenta de Higgsfield
5. Habilitarlo en el chat donde se vaya a usar (el toggle por conversación es
   independiente de la conexión a nivel cuenta)

## 3. API directa (alternativa, solo si se necesita automatización sin agente)

Higgsfield también tiene API REST asíncrona (`docs.higgsfield.ai`, cuenta en
`cloud.higgsfield.ai`). Autenticación por header:

```
Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}
```

Las credenciales van en variables de entorno o en el gestor de secretos —
**nunca** commiteadas en este repo.

## Notas operativas

- Consume créditos del plan de Higgsfield de la cuenta autenticada.
- Las skills `diseno-suite`, `disenador-persona` y `roger-hub` apuntan a una skill
  `higgsfield-video` que hoy no existe en el manifest sincronizado; mientras no se
  cree, el enrutamiento a video AI debe ir directo a las herramientas MCP de
  Higgsfield.
