# Ida para o CurseForge

## Regra que muda tudo
Um modpack do CurseForge é um `.zip` com um `manifest.json` que aponta para **projectID + fileID de arquivos hospedados no próprio CurseForge**. Mod que só existe no Modrinth não pode ir no pack. A exceção é uma lista pequena de mods liberados para ir na pasta `overrides`. Então **todo mod do Thaumora precisa ter um arquivo 1.21.1 NeoForge no CurseForge**, ou ser trocado ou removido.

## Primeiro mapeamento (2026-11-25), sem chave da API
`tools/cf_map.py` usa a API pública da cfwidget e gera `data/cf_map.json`.

Resultado nos 210 itens (199 do `lock.json` + 11 que já eram só do CurseForge):

| Status | Qtde | O que significa |
|---|---|---|
| mesmo_arquivo | 156 | o mesmo jar já está no CurseForge, pronto |
| outra_versao | 9 | existe para 1.21.1 NeoForge, com outra versão |
| sem_versao | 15 | projeto achado, mas sem arquivo 1.21.1 NeoForge na lista |
| nao_encontrado | 30 | o slug não bateu |

**Esse resultado tem ruído.**
- A busca por slug da cfwidget dá 404 em mods que com certeza estão no CurseForge (Balm, FerriteCore, Architectury). Na maioria, os "não encontrados" são slugs diferentes ou projetos que a cfwidget não indexou.
- A YUNG's publica os jars NeoForge da 1.21.1 de um jeito que a lista da cfwidget não mostra.
- Achados reais:
  - O CurseForge marca um jar 26.2 do **Structory: Towers** como 1.21.1, o mesmo erro do Modrinth. Fixar a versão.
  - O **Serene Seasons** no CurseForge está numa versão um pouco mais antiga que no Modrinth.

## O jeito certo: fingerprint
O CurseForge identifica cada jar por um hash (murmur2) e tem um endpoint que recebe os hashes e devolve o projeto e o arquivo exatos. Assim não há chute de slug. Há dois caminhos:

1. **Exportar pelo Prism, sem chave.** Menu *Exportar → CurseForge* da instância. O Prism usa a chave dele, faz o fingerprint de cada jar e gera o `.zip` do modpack. O que não achar vai para `overrides`, e ele avisa. É um passo manual de 1 minuto, mas não fica no script.
2. **Chave própria da API, automação completa.** Chave gratuita em console.curseforge.com. Com ela, um script faz tudo:
   - fingerprint dos 199 jars, com a lista exata do que falta no CurseForge;
   - download automático dos 11 mods que só estão no CurseForge;
   - `manifest.json` + `.zip` do pack, prontos para enviar;
   - aviso de atualização dos mods.

## O que já dá para automatizar
- [x] `lock.json` (versões travadas) e o cache de jars
- [x] mapeamento preliminar para o CurseForge (`cf_map.py`)
- [ ] fingerprint exato (precisa da chave ou do export do Prism)
- [ ] baixar os 11 mods só do CurseForge (precisa da chave; sem ela, o Prism instala pela aba CurseForge do navegador de mods)
- [ ] gerar o `.zip` do modpack (`manifest.json`, `modlist.html`, `overrides/` com configs, KubeJS e quests)
- [ ] enviar o pack ao CurseForge (a API de upload de modpack pede um token de autor; o primeiro envio do projeto é manual no site)
