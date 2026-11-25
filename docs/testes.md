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

### Pendente
1. Decidir Pufferfish's Skills **ou** Project MMO: hoje os dois estão instalados e ativos ao mesmo tempo.
2. Decidir Chipped **ou** Rechiseled (o Chipped está instalado).
3. Instalar o MineColonies pelo Prism (já está no `mods.json`, falta na instância) e anotar os IDs em `data/cf_prism.json`.
4. Testar Level Hearts × Hardcore Revival.
5. Testar Nullscape × End Remastered × Unusual End.
