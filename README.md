# Thaumora — modpack de magia

> Modpack singleplayer focado **em magia**: sem cabos, sem energia elétrica (RF/FE).
> Tudo — armazenamento, automação, transporte, combate — é resolvido com rituais, espíritos, feitiços e alquimia.
> **Única exceção tech: Create**, tratado como "engenharia arcana" — mecânico, manual, visual, sem eletricidade.

| Item | Escolha |
|---|---|
| Versão | **Minecraft 1.21.1** |
| Loader | **NeoForge** (21.1.x) |
| Launcher | Prism Launcher |
| Tamanho alvo | ~170–200 mods |
| RAM | 12 GB alocados (8 GB mínimo) |
| Estilo | Exploração + progressão em tiers, quests guiando, bosses como marcos |

> **English:** Thaumora is a magic-focused Minecraft 1.21.1 NeoForge modpack (to be published on CurseForge). This repo holds the mod list and the small build tools: `tools/resolve_mods.py` locks exact Modrinth versions, `tools/cf_sync.py` matches every jar to its CurseForge project/file via the fingerprint API and exports the CurseForge modpack zip (`manifest.json` + overrides). No mod files are redistributed here.

### Ferramentas
| Script | O que faz |
|---|---|
| `tools/resolve_mods.py` | trava a versão exata de cada mod (Modrinth, 1.21.1 NeoForge) em `data/lock.json` e baixa os jars para o cache local |
| `tools/cf_sync.py` | casa cada jar com o CurseForge por fingerprint (`tools/Murmur2.java`), baixa os mods que só estão lá e, com `--export`, gera o `.zip` do modpack |
| `tools/cf_map.py` | mapeamento preliminar para o CurseForge, sem chave (cfwidget) |
| `tools/build_page.py` | gera a página `thaumora.html` a partir de `data/mods.json` |

**Por que 1.21.1 e não a última?** É a versão "estável" do modding atual: quase todos os grandes mods de magia (Ars Nouveau, Iron's Spells, Occultism, Malum, Forbidden & Arcanus) estão nela. Versões mais novas ainda têm poucos mods de magia portados.

---

## 1. Conceito / narrativa

O mundo foi um dia governado por escolas de magia que se destruíram. Você começa como um aprendiz sem mana, encontrando ruínas, livros e torres abandonadas. Cada **escola** é um mod (ou grupo de mods) e a progressão força você a dominar uma para destrancar a próxima — até reunir todas para enfrentar os bosses finais.

**As 5 escolas (tiers):**

| Tier | Escola | Tema | Mods principais |
|---|---|---|---|
| 1 | **Naturalismo** | ervas, poções, bruxaria de caldeirão | Hexerei, Hexalia, Botania Revived (início) |
| 2 | **Arcanismo** | glifos, feitiços customizáveis, "fonte" de mana | Ars Nouveau + addons, Forbidden & Arcanus |
| 3 | **Ocultismo** | demônios, espíritos, almas | Occultism, Malum, Eidolon Repraised |
| 4 | **Batalha arcana** | escolas de feitiço de combate, encantamento profundo | Iron's Spells 'n Spellbooks, Apotheosis |
| 5 | **Magia proibida** | sangue, sacrifício, artefatos lendários | Neo Vitae, EvilCraft, Botania endgame, Malum endgame, Reliquary |

---

## 2. Levantamento de mods (NeoForge 1.21.1)

Legenda de status: ✅ estável e oficial · 🟡 port não-oficial ou beta · 🔍 verificar versão antes de instalar

### 2.1 Sistemas de magia (núcleo)

| Mod | Status | O que traz |
|---|---|---|
| **Ars Nouveau** | ✅ | Feitiços montados com glifos (forma + efeitos + aumentos), familiares, rituais, automação mágica (Source, Starbuncles). Coração do pack. |
| **Iron's Spells 'n Spellbooks** | ✅ | Magia de combate estilo RPG: escolas (fogo, gelo, raio, sangue, ender, sagrado, evocação, natureza), pergaminhos, armaduras de mago, bosses e estruturas próprias. |
| **Occultism** | ✅ | Invocação de demônios/djinns que trabalham pra você — inclusive **armazenamento dimensional** (substitui AE2/RS) e mineração automática. |
| **Malum** | ✅ | Magia de almas/espíritos: colher espíritos de mobs, transmutação, totens, rituais. Visual lindíssimo. |
| **Forbidden & Arcanus** | ✅ | Artefatos, Hephaestus Forge, rituais, itens poderosos de progressão média. |
| **Thaumaturge** (+ addons) | 🟡 | Reimaginação moderna do **Thaumcraft** (vis, cristais, pesquisa) — não é port oficial. Addons: Thaumaturgic Infusion, Thaumaturgic Brewing, Thaumaturgic Tinkerer, **Create: Thaumaturgy**. **Escolhido** (Thavma descartado). O Thaumcraft 7 oficial (Team CoFH) ainda não tem release. |
| **Theurgy** | ✅ | Alquimia "de verdade" (destilação, calcinação, divisão de matéria) — duplicação de minérios via magia. |
| **Mahou Tsukai** | ✅ | Magia inspirada em anime (projeção, reforço, magia de selamento), estilo "Fate". |
| **Hexerei** | ✅ | Bruxaria: caldeirão, mesa de mistura, vassouras voadoras, herbalismo. Ótimo pro início. |
| **Hexalia** | ✅ | Herbalismo e magia natural, combina com Hexerei. |
| **Eidolon: Repraised** | 🟡 beta | Necromancia, devoção a divindades, cânticos. |
| **Botania Revived** | 🟡 port | Magia natural técnica (flores geram e consomem mana). Endgame forte (Gaia Guardian).  **Usar versão fixa** + backup; testar Gaia e Corporea na montagem. Port oficial 1.21.1 em andamento (branch `1.21.1-porting`). |
| **Neo Vitae** | 🟡 experimental | Magia de sangue inspirada no Blood Magic (altar, sacrifício, rituais). Substitui o port do Blood Magic. |
| **Roots Classic** | 🟡 port (CurseForge) | Roots clássico: cajado druídico, ervas, pós e pedras rituais. Complemento do Naturalismo. |
| ❌ ~~Blood Magic (Unofficial Port)~~ | — | Fora: alpha arriscado num mundo longo. EvilCraft + Neo Vitae cobrem. |
| **Enchanted: Witchcraft** | ✅ | Bruxaria clássica (altar, destilaria, poppets, familiares). Tier I junto com Hexerei. |
| **Apotheosis** (+ Apothic Enchanting / Attributes / **Spawners**) | ✅ | Encantamento muito mais profundo, gemas, afixos, "boss loot". Encaixa como "encantamento arcano". |
| **Reliquary Reincarnations** | ✅ | Relíquias e itens mágicos clássicos (Mercy Cross, Handgun, Tomos). |
| **EvilCraft** | ✅ | Magia sombria com sangue, Dark Gems, inclui o "Spirit Furnace". |

### 2.2 Addons e integrações

| Mod | Status | Função |
|---|---|---|
| Ars Elemental | ✅ | Escolas elementais, focos, armaduras elementais pro Ars. |
| Ars Additions | ✅ | Glifos e utilidades extras. |
| Ars Creo | 🔍 | Integração Ars + Create (Starbuncles e Source interagindo com máquinas do Create). |
| Too Many Glyphs | 🔍 | Mais glifos pro Ars. |
| Ars 'n' Spells | 🔍 | **Unifica a barra de mana** do Ars e do Iron's. Altamente recomendado se existir pra 1.21.1. |
| Iron's Spells addons (ex.: T.O Magic 'n Extras, Traveloptics, Cataclysm Spellbooks) | 🔍 | Novas escolas/feitiços. Escolher 1–2, não todos. |
| Occultism + Ars compat / Malum compat | — | Muitas integrações já são nativas; o resto faremos via KubeJS. |

### 2.3 Bibliotecas (dependências obrigatórias)

Curios API · Patchouli · Modonomicon · GeckoLib · Lodestone (Malum) · Architectury · Cloth Config · Citadel · Caelus API · Player Animator · Terrablender · Kotlin for Forge (se algum pedir). *O Prism resolve a maioria automaticamente.*

### 2.4 Mundo, estruturas e inimigos (pra dar o que fazer com a magia)

| Mod | Por quê |
|---|---|
| **The Aether** | Dimensão celestial — tema "paraíso arcano". |
| **L_Ender's Cataclysm** | Bosses épicos (Ignis, Leviathan, Ender Guardian) — marcos de progressão. |
| **Tectonic** (sem mod de biomas) | Só biomas vanilla + os dos mods; Tectonic muda o formato do terreno. Biomes O' Plenty ficou fora (pode voltar depois). |
| **YUNG's** (Better Dungeons, Strongholds, Mineshafts, Desert Temples…) | Estruturas melhores com loot de magia injetado. |
| **Towns and Towers** | Vilas e torres pra exploração. |
| **Deeper and Darker** | Dimensão do Warden — "abismo". |
| **Waystones** | Teleporte mágico entre pedras (substitui transporte tech). |

### 2.5 Qualidade de vida

O "kit básico" presente em praticamente todo modpack:

| Área | Mods |
|---|---|
| **Inventário e baús** | Inventory Profiles Next (ordenar baú/inventário com um botão, reabastecer hotbar) · Mouse Tweaks (arrastar/mover itens rápido) · Trash Slot 🔍 · Carry On (carregar baús com itens dentro) · Sophisticated Backpacks · Sophisticated Storage (baús com upgrades e ordenação) · Storage Drawers |
| **Receitas e informação** | EMI (ou JEI) · Jade (info do bloco olhado) · Polymorph (resolve conflito de receitas) · AppleSkin · Searchables/Controlling (buscar keybinds) |
| **Mapa e exploração** | Xaero's Minimap + World Map (ou JourneyMap) · Nature's Compass · Explorer's Compass · Waystones |
| **Mineração e coleta** | FTB Ultimine (minerar veios inteiros) · FallingTree (derrubar árvore inteira) 🔍 · Fast Leaf Decay · Clumps (junta orbs de XP) |
| **Crafting** | FastWorkbench/FastSuite · Crafting Tweaks (girar/balancear grid) · Easy Anvils / Easy Magic 🔍 |
| **Segurança/conforto** | Corpse ou Gravestone (não perder itens) · Comforts (saco de dormir) · Torchmaster (impede spawn — tem "cara" mágica) |
| **Progressão** | FTB Quests + FTB Library · **KubeJS** (receitas/gating) |

### 2.6 Create — "engenharia arcana"

Create entra como a **única exceção tech**, porque é mecânico e manual: rotação, engrenagens, esteiras, contraptions visíveis — nada de energia invisível em cabos. Na narrativa, é a tecnologia dos anões/artífices que alimenta a magia.

| Mod | Status | Função |
|---|---|---|
| **Create** (6.x) | ✅ | Base: kinetic, processamento, contraptions, trens. |
| **Ars Creo** | 🔍 | Ponte Ars Nouveau ↔ Create (ex.: Starbuncle Wheel gera rotação). |
| **Create: Enchantment Industry** | 🔍 | Experiência líquida, encantamento automático — conversa com Apotheosis. |
| **Create Deco** / **Copycats+** | 🔍 | Blocos decorativos industriais-medievais. |
| **Create: Steam 'n' Rails** | 🔍 | Mais opções de trens (opcional, se curtir ferrovias). |

**Proibidos mesmo com Create:** Create Crafts & Additions (adiciona FE/eletricidade), Create: New Age, e qualquer addon que traga energia elétrica.

**Integração planejada (KubeJS):**
- Rodas de Starbuncle / rituais geram rotação (via Ars Creo ou receita custom).
- Ingredientes mágicos processados no Create: moer Source Gems, misturar poções no Mixer, "Haunting" com fogo de alma pra itens do Malum/Occultism.
- Create fica **no tier 2–3**: liberado depois do Arcanismo, exigindo um componente mágico no Andesite Alloy ou na Mechanical Press.

### 2.7 Visual (opcional, leve)

Sem mexer em câmera/animações — só o que informa ou melhora o ambiente:
Neat (vida dos mobs) · Legendary Tooltips + Iceberg (raridade dos itens) · LambDynamicLights 🔍 (tocha na mão ilumina) · Sound Physics Remastered · Ambient Sounds.

**Resource packs:** Fresh Animations · Stay True (opcional).

### 2.8 Performance e shaders

Sodium (NeoForge) + Iris · ModernFix · FerriteCore · ImmediatelyFast · Entity Culling · Noisium (worldgen). Distant Horizons ficou fora (pesado e desnecessário).
Shader sugerido: **Complementary Reimagined** + **Euphoria Patches** (ou **BSL**). Malum e Ars têm efeitos de brilho que ficam ótimos com shader.

---

### 2.9 Dimensões

| Mod | Status | Papel |
|---|---|---|
| **The Twilight Forest** (4.8, CurseForge) | ✅ | Floresta mágica com progressão de bosses — dimensão do tier II. |
| The Aether + **Deep Aether** | ✅ | Céu — tier III. |
| **Eternal Starlight** | ✅ | Dimensão mística estrelada com bosses. |
| The Undergarden · Deeper and Darker | ✅ | Subterrâneo sombrio / abismo. |
| The Bumblezone | ✅ | Opcional. |
| Incendium · Nether Depths Upgrade | ✅ | Nether reformulado. |
| Nullscape · Unusual End · **End Remastered** | ✅ | End reformulado; End Remastered exige olhos de dungeons pro portal (marco do tier V). |
| ❌ Blue Skies · The Midnight · Aether Redux | — | Sem versão NeoForge 1.21.1. |

### 2.10 Fazenda e culinária

Farmer's Delight · Ars Delight · Occultism Delight · Iron's Spells Delight · Ender's Delight · Brewin' and Chewin' · Serene Seasons (estações) · **Mystical Agriculture** (sementes de recursos — encaixa como magia) · Cooking for Blockheads · Farming for Blockheads · Aquaculture 2 · Easy Villagers · *(opcional)* Pam's HarvestCraft 2 Crops · *(avaliar)* Botany Pots.

### 2.11 Construção e decoração

Supplementaries + Amendments · Handcrafted · Macaw's (série) · Chipped **ou** Rechiseled · Arcane Lanterns · Quark (módulos configuráveis).

### 2.12 Aventura e criaturas

Artifacts · Relics · Dungeons and Taverns · Simply Swords · Naturalist · Galosphere. *(Alex's Mobs não existe pra 1.21.1.)*

### 2.13 Automação mágica

**Substituto do AE2 (storage + autocrafting):**
- Armazenamento central → **Occultism Dimensional Storage** (terminal, busca, crafting grid, Storage Remote, Stable Wormhole).
- Autocrafting por pedido → **logística do Create 6** (Stock Keeper + Packager + Factory Gauge).
- Manter estoque de itens → **Wixies** (Ars Nouveau) puxando dos baús linkados.
- Pedir item por nome → **Corporea** (Botania) + Crafty Crate.
- Não existe um "AE2 mágico" 1:1 — é a combinação desses.


- **Ars Nouveau** — o mais forte: Starbuncles (transporte), Wixies (auto-crafting/poções), Whirlisprig (fazenda), Drygmy (drops de mobs), Source Relays.
- **Occultism** — Dimensional Storage, demônios mineradores, spirits transportadores/zeladores, crusher spirits.
- **Botania** — flores funcionais, rede Corporea (armazenamento/pedidos), spreaders de mana.
- **Mystical Agriculture**, **Theurgy** (alquimia em série), addons do Thaumaturge, **Create + Ars Creo**.
- **Embers Re-Ignited** 🟡 (port beta do Embers Rekindled p/ 1.21.1) — máquinas anãs movidas a ember, com integração com Create. Tier III.
- **Nature's Aura** ✅ — máquinas que consomem a aura natural. **Psi** ✅ (opcional) — feitiços programáveis.

### 2.14 RPG, skills e desafios

| Mod | Papel |
|---|---|
| **Pufferfish's Skills** | Árvores de skill configuráveis — uma árvore por escola de magia, pontos ganhos via quests. |
| Iron's Spells Dynamic Skill Trees | Skill trees das escolas do Iron's. |
| *(alternativa)* Project MMO | Upa skill fazendo a atividade. Escolher **ou** Pufferfish **ou** PMMO. |
| **Improved Mobs** | Mobs escalam com tempo/distância, usam equipamento. |
| **Mowzie's Mobs** | Bosses e criaturas de alta qualidade. |
| **When Dungeons Arise** | Dungeons gigantes. |
| **Bountiful** | Quadro de contratos nas vilas. |
| Level Hearts · Iron's Gems 'n Jewelry · Loot Journal · *(opc.)* Hardcore Revival | Progressão de vida, joias, feed de loot, reanimação. |
| ❌ Epic Fight (mexe na câmera) · ❌ Champions (sem 1.21.1 — Apotheosis já cobre elites) | — |

## 3. Progressão e objetivo final

**Progressão livre** (decidido): nenhuma receita é travada. Existe só um *caminho sugerido* (Naturalismo → Arcanismo → Ocultismo/Alquimia → Batalha → Magia proibida), que o FTB Quests pode mostrar sem bloquear nada.

**Objetivo final: EM ABERTO.** Fica para decidir depois de jogar a base do pack. Ideias guardadas em [`docs/lore.md`](docs/lore.md): a favorita é um portal para uma dimensão própria (mod nosso, feito do zero), possivelmente aberto por um item no estilo ATM Star.

## 4. Regras de design

- ❌ **Sem tech elétrico:** nada de Mekanism, Thermal, AE2, Refined Storage, Immersive Engineering, addons de FE do Create, etc.
- ✅ **Create é a exceção** — mecânico/manual, integrado com magia via KubeJS.
- ✅ Automação: mágica (Starbuncles/Ars, demônios do Occultism, Botania, rituais do Malum) ou mecânica do Create.
- ✅ Armazenamento = Occultism Dimensional Storage (+ Sophisticated Storage só se ficar apertado).
- ✅ Uma barra de mana unificada se possível (Ars 'n' Spells) — senão, aceitar as duas.
- ⚠️ Mods 🟡 (ports/beta) entram por último e com backup de mundo antes.

---

## 5. Próximos passos

- [ ] Instalar Prism Launcher e criar instância NeoForge 1.21.1
- [ ] Adicionar núcleo (2.1 ✅) + bibliotecas e testar se abre
- [ ] Adicionar addons, mundo, QoL, performance — testar a cada lote (~10 mods)
- [ ] Verificar itens 🔍 no Modrinth/CurseForge
- [ ] Escrever scripts KubeJS de gating (em `kubejs/`)
- [ ] Montar capítulos do FTB Quests (um por escola)
- [ ] Ajustar configs (salvar cópias em `config/`)
- [ ] Criar mundo e jogar 🧙

## Fontes do levantamento

- [8bittoast — 15 Best Magic Mods (2026)](https://8bittoast.com/minecraft-magic-mods/)
- [Malum 1.21.1 (CurseForge)](https://www.curseforge.com/minecraft/mc-mods/malum/files/7307339)
- [Eidolon Repraised 1.21.1 (Modrinth)](https://modrinth.com/mod/eidolonrepraised/version/0.5.0.0-pre20)
- [Blood Magic Unofficial Port](https://www.curseforge.com/minecraft/mc-mods/blood-magic-unofficial-port) · [Neo Vitae](https://www.curseforge.com/minecraft/mc-mods/neo-vitae)
- [Botania Revived](https://www.curseforge.com/minecraft/mc-mods/botania-revived)
- [Hexalia 1.21.1](https://modrinth.com/mod/hexalia/version/1.3.1-1.21.1+neoforge?dep=1)
- Modpacks de referência: [Mystic Foundations II](https://www.curseforge.com/minecraft/modpacks/mystic-foundations-ii/files/7651618), [Mystic Arts & Spellbooks](https://www.curseforge.com/minecraft/modpacks/mystic-arts-spellbooks/files/7214871)
