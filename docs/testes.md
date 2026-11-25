# Testes do Thaumora

## 2026-11-25 — primeiro teste

**Ferramentas:** `tools/resolve_mods.py` gera `data/lock.json` com a versão exata de cada mod (Modrinth, 1.21.1 NeoForge) e baixa os jars para `games/minecraft/shared/mod-cache/`.

### Servidor NeoForge 21.1.267 (sem conta)
- ✅ **Subiu com 179 mods** e gerou o mundo em 56 s.
- Fora do teste: Malum e Relics (dependem de bibliotecas que só estão no CurseForge) e os 9 mods que só existem no CurseForge.
- Erros não fatais no log: receitas de compatibilidade opcionais (Unusual End × Farmer's Delight, Silent Gear × netherwood, trilhos do Steam 'n' Rails para madeiras de outros mods). É normal em packs grandes e não afeta o jogo.

### Correções feitas no caminho
- Dependências que os mods não declaram no Modrinth → `data/deps.json`: Player Animator (Iron's Spells), Kambrik (Bountiful), Atlas API (Iron's Jewelry).
- Só no CurseForge: **Lodestone** (para o Malum) e **OctoLib** (para o Relics).
- Structory e Structory: Towers estavam pegando um jar feito para 26.x → versão fixada (`pin`) em `mods.json`.

### Cliente no Prism
- Instância **Thaumora** criada (NeoForge 21.1.267, 12 GB, 178 mods).
- ❌ Não deu para abrir: os logins Microsoft salvos no Prism **expiraram** e precisam ser refeitos (até o modo offline exige uma conta válida). Falta você entrar de novo no Prism.

### Cliente: segunda tentativa (depois de você entrar de novo no Prism)
- 1ª abertura travou: faltava o **Smart Brain Lib** (exigido pelo Occultism). Eu tinha montado a instância só com os mods que o Modrinth marca como "do cliente".
- **Regra:** no singleplayer o jogo roda um servidor interno, então a instância do cliente precisa de **todos** os mods. Só o pacote de servidor dedicado leva menos: ele deixa de fora os mods com `server: unsupported`.
- Copiei os 20 que faltavam (estruturas, YUNG's, Lithostitched, Smart Brain Lib etc.) → 198 jars.
- ✅ **2ª abertura: entrou no mundo `ThaumoraTeste`** cerca de 2 min depois de abrir o jogo. Carregou 22.502 receitas e usou cerca de 7 GB de RAM.
- Erros não fatais no log: os mesmos do servidor, mais 271 loot tables que não carregam (`minecraft:root`, de compatibilidade entre mods), algumas animações GeckoLib e a config padrão do Improved Mobs para mobs do Ars. Nada impediu o jogo de rodar.
- Um "Can't keep up" logo depois de entrar no mundo é normal enquanto os chunks são gerados.

### Pack completo (mods do CurseForge instalados pelo Prism)
- Prism instalou 16 projetos do CurseForge: Thaumaturge + 3 addons, Create: Thaumaturgy, Botania Revived, Roots Classic, Ars Elemental, **Ars Elemancy** (novo), Twilight Forest, FTB Quests/Ultimine/Library/Teams, Lodestone, OctoLib. IDs em `data/cf_prism.json`.
- Malum e Relics voltaram (as bibliotecas deles estão instaladas).
- ✅ **215 jars: entrou no mundo** cerca de 1 min 40 s depois de abrir. Carregou 28.112 receitas e usou cerca de 8,4 GB de RAM.
- Nenhum erro dos mods novos. Os erros do log são as mesmas receitas/loot de compatibilidade (quase todos dos trilhos do Steam 'n' Rails).

### + Guard Villagers e MVS (Moog's Voyager Structures)
- ✅ **217 jars: entrou no mundo** 1 min 44 s depois de abrir. Carregou 28.215 receitas e usou cerca de 8,9 GB de RAM.
- Nenhum erro dos dois mods novos (só o aviso de sempre de `refmap` do Guard Villagers, que é inofensivo).
- Os erros do log são os mesmos de antes: 247 loot tables de compatibilidade, receitas opcionais (Malum, Unusual End, Silent Gear, Create), animações GeckoLib e a config padrão do Improved Mobs.
- A observar: logo depois de entrar, o watchdog do **VerseWorks** registrou um travamento de 5,6 s do servidor na dimensão `thaumictinkerer:bedrock` (Thaumaturgic Tinkerer). Aconteceu uma vez só, enquanto o mundo carregava, e o jogo seguiu normal. Se repetir durante o jogo, investigar.

### Pufferfish's Skills fica, Rechiseled no lugar do Chipped
- Decisões: fica o **Pufferfish's Skills** (sai o Project MMO, que por padrão exige nível para usar ferramentas e armaduras); entra o **Rechiseled + Rechiseled: Create** (sai o Chipped, parado desde out/2024).
- Lock: saíram Chipped, Athena e PMMO; entraram Rechiseled, Rechiseled: Create, Fusion e as bibliotecas Core Lib e Config Lib do SuperMartijn642. Os jars removidos foram para `.minecraft/mods-removidos/2026-11-25/` da instância.
- A instância confere com o lock: 203 jars do Modrinth com sha1 correto + 16 do CurseForge = 219.
- ✅ **219 jars: entrou no mundo** 1 min 34 s depois de abrir. Carregou 28.152 receitas e usou cerca de 8,9 GB de RAM.
- Nenhum erro dos mods novos. No mundo antigo aparecem, uma vez só, avisos de dados que sobraram dos mods removidos (`pmmo:placed_data`, receitas e conquistas do Chipped). Mundo novo não terá isso.
- O travamento do VerseWorks em `thaumictinkerer:bedrock` não se repetiu.

### Sem Level Hearts, Hardcore Revival e MineColonies
- Saíram **Level Hearts** e **Hardcore Revival** (o pack é singleplayer; o Level Hearts ainda era listado como incompatível com o Hardcore Revival). Não deixaram dependência sobrando. Jars em `mods-removidos/2026-11-25/`.
- **MineColonies** adiado: `s: no` no `mods.json`, pode voltar depois. Nunca chegou a ser instalado.
- ✅ **217 jars: entrou no mundo** 1 min 44 s depois de abrir, com 28.149 receitas.
- Só os avisos esperados de dados que sobraram do Level Hearts no mundo de teste (`levelhearts:player_data` e receitas de coração). Se a vida máxima do jogador ficou diferente de 10 corações nesse mundo: `/attribute @s minecraft:generic.max_health base set 20`.

### Nullscape × Unusual End × End Remastered
- O Nullscape troca a geração do End por uma lista fixa de biomas; a dúvida era se os biomas do Unusual End (adicionados por código) ainda apareceriam.
- ✅ **Convivem.** `/locate` no End achou `unusualend:gloopstone_lands` (1.288 blocos), `unusualend:warped_reef` (1.838), `nullscape:crystal_peaks` (2.058), a estrutura `unusualend:flying_end_ship` (1.810) e `minecraft:end_city` (2.354).
- O End Remastered não mexe no terreno do End, só no portal (olhos achados em dungeons). Sem conflito com os outros dois.
- Sem erros de geração do End no log. O "Can't keep up" de 17 s logo depois é dos `/locate`, que são pesados.
- ⚠️ O travamento do VerseWorks em `thaumictinkerer:bedrock` **voltou** (5,1 s, logo depois do teleporte). A pilha passa pelo Galosphere (`MobEvents.handleBurrowAnchorTeleporting` → carregamento síncrono de chunk). Investigar por que essa dimensão é processada sem ninguém nela.

### Pack do CurseForge (0.1.0-beta), instalado como um jogador instalaria
- Export do Prism (fingerprint) achou 196 dos 217 jars. Os outros 21 foram achados pela API pública do site do CurseForge e conferidos por dentro: o código é idêntico, muda só o `META-INF/MANIFEST.MF` (data de build). TerraBlender NeoForge fica num projeto separado no CurseForge ("TerraBlender (NeoForge)").
- **Serene Seasons** fixado na 10.1.0.3 (`pin`): as versões 10.1.0.7–10.1.0.9 só existem no Modrinth. A 10.1.0.9 corrige um "mixin stack overflow" que só aparece em certas combinações; testar se aparece com a 10.1.0.3.
- IDs de todos os jars em `data/cf_lock.json`; `.zip` gerado com `cf_sync.py --export-only` (sem chave).
- Importado no Prism como **Thaumora Beta** (10 GB): baixou os 217 mods. 197 idênticos byte a byte aos testados, 17 só com o `MANIFEST.MF` diferente, 3 com o mesmo conteúdo e compactação diferente.
- **Structory** e **Structory: Towers** bloqueiam download por launchers de terceiros: o Prism pede para baixar à mão (o app do CurseForge baixa sozinho). Os jars do nosso cache são os mesmos (mesmo hash).
- ✅ Menu em 1 min 20 s; **mundo novo** `BetaTeste` criado e jogável. Sem erros novos.
- Primeira sessão com 27.922 receitas; na segunda, **28.169**. O Cucumber (Mystical Agriculture) só resolve as tags de lingotes/gemas depois do primeiro mundo carregar, e as receitas dependentes aparecem na abertura seguinte. Afeta só a primeira sessão de cada jogador.
- As configs geradas do zero na Beta saíram mais completas que as da instância de desenvolvimento (ex.: Neo Vitae reconhece o âmbar do Thaumaturge), que acumulou configs de antes de alguns mods entrarem.

### Pendente

1. Investigar o travamento recorrente na dimensão `thaumictinkerer:bedrock` (VerseWorks/Galosphere).
