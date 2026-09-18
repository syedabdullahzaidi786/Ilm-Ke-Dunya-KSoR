---
type: Document
title: Ilm Ke Dunya MCP
description: Connect Claude and other MCP clients to the live public Ilm Ke Dunya server.
status: stable
order: 2
generated: { by: "human:you", at: 2026-09-18T18:30:00Z }
ksor:
  audience: [public]
  owner: "the record owner"
  approval: { by: "human:you", at: 2026-09-18T18:30:05Z }
---

<div align="center">
  <img src="https://ilm-ke-dunya-ksor.vercel.app/logo.png" alt="Ilm Ke Dunya logo" width="180" />
</div>

# Ilm Ke Dunya MCP

> [!IMPORTANT]
> This connector is currently in beta. The public MCP endpoint is live and supported for testing, but it may continue to improve as usage grows.

Ilm Ke Dunya exposes a live MCP endpoint that lets AI assistants and compatible
clients use the project’s governed knowledge, Islamic reference tools, and
searchable content in real workflows.

## Connect it now

Use this public MCP endpoint:

```text
https://ilm-ke-dunya-ksor.vercel.app/mcp
```

## User guide

### Step 1: Open the custom connector form

Open Claude, then go to Customize → Connectors.

Select Add custom connector.

![Claude Add custom connector dialog showing Ilm Ke Dunya MCP and its URL](https://ilm-ke-dunya-ksor.vercel.app/add_custom_connector.png)

Enter these values exactly:

- Name: `Ilm Ke Dunya MCP`
- MCP server URL: `https://ilm-ke-dunya-ksor.vercel.app/mcp`

Then click `Continue`.

### Step 2: Leave No sign-in selected

After clicking Continue, Claude opens the Authentication screen.

Leave `No sign-in — Detected` selected.

Claude will show a warning explaining that anyone with the server URL can use the connector. This warning is expected because the current Ilm Ke Dunya MCP endpoint is public.

Then click `Add`.

![Claude Authentication screen showing No sign-in detected for Ilm Ke Dunya MCP](https://ilm-ke-dunya-ksor.vercel.app/add_custom_connector_authantication.png)

> [!IMPORTANT]
> Do not enter an OAuth client ID, OAuth client secret, username, password, or API key. This endpoint does not use OAuth.

## What the connection gives you

The live server includes the record tools and the Islamic knowledge tools that are
implemented in the project.

- `search` — search the governance-backed record for relevant answers.
- `outline` — explore the document structure.
- `read` — read a specific document or section.
- `ilm_quran_lookup` — look up Quran references and verse content.
- `ilm_hadith_search` — search Hadith collections and references.
- `ilm_dua_search` — search duas and supplications.
- `ilm_names_search` — find Islamic names and related metadata.
- `ilm_asma_lookup` — browse the 99 Names of Allah.
- `ilm_moon_today` — get moon and Hijri information.
- `ilm_hijri_convert` — convert Gregorian and Hijri dates.

## Troubleshooting

### The server is not connecting

- Check that the URL is exactly: `https://ilm-ke-dunya-ksor.vercel.app/mcp`
- Refresh the connector list inside your client.
- Re-authorize the connection if it was previously rejected.
- Make sure the client is using the public endpoint rather than a local dev port.

### Claude shows no tools

This usually means the connector was saved but not authorized, or the client did
not refresh after the server was added. Remove and re-add it, then authorize and
try again.

### The endpoint responds but tools look incomplete

Use the public deployed server, not a local development port. The public route is
what this beta guide is based on.

## Security and usage notes

This is a public beta connector. It is intended as the live public environment and
should be treated as the main supported path while the service is still evolving.

## Related resources

- [Ecosystem](index.md)
- [What is Ilm Ke Dunya?](../what-is-ilm-ke-dunya.md)
- [Ilm Ke Dunya OpenAPI](../openapi.md)
