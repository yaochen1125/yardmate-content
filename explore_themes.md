# Explore Themes — Curated Collections

母本（single source of truth）。首页合集的标题 / 简介 / intro / 选株 / 推荐理由全部以本文件为准。最初 30 个是人工写的；之后每周日 21:00（太平洋时间）由服务器每周任务在文件**末尾**追加 1 个（带 `> added:`）。

**改版必须改这个文件**，然后在本仓库依次跑：`python3 build_explore_themes_json.py`（重建 `explore_themes.json`）→ `python3 translate_explore_themes.py`（重生成 10 种语言）→ `./ship.sh`。**禁止直接改 explore_themes.json**——下次从母本重建会覆盖掉。
（2026-10 之前母本在 yardmate-swiftui 的 `scripts/` 下，已挪到这里。）

格式约定（`build_explore_themes_json.py` 解析，任何不符合的行都会构建报错、不写盘）：

- `## N. Title` — 主题序号 + 标题
- `> id: slug` — 主题稳定 id，**必填**（i18n overlay 与主题头图按 id 键控；改标题不改 id）
- 首个非 `>` 普通行 — description（必填，单行）
- `> intro: ...` — 主题长简介（必填，单行，不可折行）
- `> added: YYYY-MM-DD` — 可选，该期上线的 UTC 日期（每周新合集才有）。写入 JSON 的 `addedAt`，App 用它把本周新合集置顶首页第 1 行；输出时带日期的按日期新 → 旧排最前（「全部合集」列表按数据顺序显示，老版本 App 也是），没日期的最初 30 个按本文件顺序排后面
- 带 `> added:` 的合集与其他任一合集重合的植物最多 3 株（最初 30 个之间本来就有重合，不受此限）；标题不能与已有合集重复（不分大小写）
- `N. 学名 — 俗名: 推荐理由` — 选株条目（单行，分隔符必须是 em-dash `—`；序号必须从 1 连号=实际数组序；俗名内不能含 `: `；每主题 ≥4 株，常规 10 株）；id 由脚本用 plants_index.json 按学名**严格**解析，解析不到直接报错

**株序承重**：per-plant 翻译（俗名/推荐理由）按 plants 数组下标对齐（App 端 ExploreThemeLocalization 按 index 套 overlay）——换株、调序、改文案后必须重跑 yardmate-content 的 `translate_explore_themes.py` 再 publish，否则非英语文案整体错位。

---

## 1. Love Tokens
> id: love-tokens

Plants traditionally given as symbols of love and devotion.
> intro: Some plants became emotional shorthand: roses for desire, violets for faithfulness, peonies for a prosperous marriage, forget-me-nots for love that survives distance. This collection gathers flowers people have used to say what a plain sentence could not.

1. Rosa damascena — Damask Rose: the perfume rose of Persia and the classic rose of romance, still distilled into rose attar.
2. Rosa gallica — Provence Rose: one of the old European roses behind centuries of love poetry, apothecary gardens, and red-rose symbolism.
3. Rosa 'Peace' — Peace Rose: a soft yellow-pink modern rose whose 1945 debut made it a symbol of reconciliation and hopeful love.
4. Viola odorata — Sweet Violet: a small, fragrant flower long associated with modesty, loyalty, and Napoleon's devotion to Josephine.
5. Dianthus caryophyllus — Clove Pink: the old carnation of love letters, corsages, and Mother's Day, with red and pink forms carrying affection.
6. Tulipa gesneriana — Garden Tulip: red tulips became a clean declaration of true love in Persian, Turkish, and later florist tradition.
7. Jasminum sambac — Arabian Jasmine: woven into bridal garlands and evening rituals across South and Southeast Asia for its intimate fragrance.
8. Paeonia lactiflora — Chinese Peony: China's luxuriant flower of romance, honor, and a fortunate marriage.
9. Lonicera japonica — Japanese Honeysuckle: its twining stems made it an easy Victorian emblem for the bonds of love.
10. Myosotis sylvatica — Wood Forget-Me-Not: the keepsake flower of lovers and friends who ask to be remembered.
---

## 2. Broken Hearts
> id: broken-hearts

Flowers of grief, longing, farewell, and remembrance.
> intro: Gardens do not only celebrate love; they also hold absence. These are plants of mythic loss, farewell bouquets, mourning customs, and memories that refuse to fade.

1. Narcissus poeticus — Poet's Daffodil: carries the Narcissus myth, where beauty bends into self-love and sorrow.
2. Hyacinthus orientalis — Hyacinth: linked to Hyacinthos, the beautiful youth mourned by Apollo in Greek myth.
3. Anemone coronaria — Poppy Anemone: associated with Adonis and the short-lived bloom of love cut down too soon.
4. Cyclamen persicum — Persian Cyclamen: a Victorian flower-language plant for resignation, departure, and goodbye.
5. Papaver rhoeas — Common Poppy: the remembrance flower of Flanders fields and lives lost in war.
6. Centaurea cyanus — Cornflower: a blue flower of memory, exile, and solitary devotion in European symbolism.
7. Helleborus niger — Christmas-Rose: a winter flower tied to Nativity tears and beauty appearing in the coldest season.
8. Salix babylonica — Weeping Willow: its drooping form made it one of the clearest garden emblems of mourning.
9. Lilium longiflorum — Easter Lily: a funeral and resurrection flower, balancing grief with the hope of renewal.
10. Myosotis sylvatica — Wood Forget-Me-Not: a small blue promise that the absent will not be erased.
---

## 3. Wedding Classics
> id: wedding-classics

Flowers woven into wedding bouquets, garlands, corsages, and altars.
> intro: Wedding flowers are a language of blessing: roses for love, peonies for prosperity, jasmine for fragrance and ceremony, lily of the valley for happiness returned. This collection follows the plants that have walked down aisles, temple steps, and garden paths with brides and grooms.

1. Rosa 'Peace' — Peace Rose: a luminous modern rose for marriage as a public promise of hope.
2. Paeonia lactiflora — Chinese Peony: a lavish June wedding flower associated with prosperity, romance, and good fortune.
3. Stephanotis floribunda — Madagascar Jasmine: the waxy white bridal flower once prized for crowns, corsages, and formal bouquets.
4. Gardenia jasminoides — Common Gardenia: a creamy, fragrant corsage flower with old associations of secret love.
5. Lilium longiflorum — Easter Lily: a white ceremonial lily used where purity, faith, and renewal are part of the wedding language.
6. Convallaria majalis — European Lily Of The Valley: the royal bouquet flower of delicate bells and the return of happiness.
7. Hydrangea macrophylla — Mophead Hydrangea: a modern florist workhorse for lush white, blue, and blush wedding arrangements.
8. Tulipa gesneriana — Garden Tulip: a clean spring wedding flower, especially in white for grace and new beginnings.
9. Dianthus caryophyllus — Clove Pink: the durable carnation behind generations of boutonnieres and family corsages.
10. Jasminum sambac — Arabian Jasmine: a sacred, fragrant wedding-garland flower across South and Southeast Asian traditions.
---

## 4. Secret Language
> id: secret-language

Victorian floriography, where each plant carries a coded message.
> intro: In the flower-language craze, a bouquet could behave like a letter: heartsease said think of me, mignonette praised inner worth, and lily of the valley promised happiness returned. These plants turn a garden into a private vocabulary.

1. Viola tricolor — Wild Pansy: the heartsease of flower language, sent as a tender request to be remembered.
2. Viola odorata — Sweet Violet: a coded sign of modesty, faithfulness, and quiet affection.
3. Dianthus barbatus — Sweet-William: the old floriographic emblem of gallantry and courtly attention.
4. Rosa damascena — Damask Rose: a rose of gratitude, perfume, and romantic acknowledgement.
5. Ipomoea purpurea — Common Morning-Glory: a flower for affection that also hints at love's brief, morning-only brightness.
6. Pelargonium graveolens — Rose-Scented Geranium: a scented-leaf geranium used to say preference: you are my choice.
7. Myosotis sylvatica — Wood Forget-Me-Not: the most direct little sentence in the garden: remember me.
8. Lonicera japonica — Japanese Honeysuckle: a living image of attachment, with paired flowers and twining stems.
9. Reseda odorata — Mignonette: valued less for show than scent, making it the flower-language praise of inner qualities.
10. Convallaria majalis — European Lily Of The Valley: the classic promise that happiness can return.
---

## 5. Famous Legends
> id: famous-legends

Plants that live as strongly in myth and legend as they do in soil.
> intro: Before botany sorted plants into families and genera, stories sorted them into desire, grief, victory, rebirth, and protection. These species carry some of the oldest myths gardeners still recognize.

1. Narcissus pseudonarcissus — Wild Daffodil: echoes the Narcissus myth, where self-adoration becomes a flower by the water.
2. Hyacinthus orientalis — Hyacinth: said to rise from the blood of Hyacinthos after Apollo's grief.
3. Laurus nobilis — Bay Laurel: Daphne's transformed tree and the crown of poets, athletes, and victors.
4. Papaver rhoeas — Common Poppy: a flower of sleep, death, and Demeter's mourning in classical imagination.
5. Anemone coronaria — Poppy Anemone: linked to Aphrodite's tears and the brief life of Adonis.
6. Nelumbo nucifera — Sacred Lotus: a rebirth flower in Egyptian imagery and an enlightenment symbol in Buddhism.
7. Helleborus niger — Christmas-Rose: a medieval Nativity legend made into a winter-blooming garden plant.
8. Viola tricolor — Wild Pansy: Shakespeare's love-in-idleness, the enchanted flower that scrambles desire.
9. Taxus baccata — Common Yew: a churchyard tree of death, protection, and uneasy immortality.
10. Myrtus communis — Common Myrtle: sacred to Aphrodite and used for love, marriage, and classical garlands.
---

## 6. Royal Favorites
> id: royal-favorites

Plants named for royalty, adopted by courts, or used as dynastic emblems.
> intro: Courts turn plants into status symbols: Queen Victoria's water lily, Ottoman tulips, imperial peonies, Lancaster roses, and chrysanthemums of the Japanese throne. Each plant here carries a little ceremony in its petals or leaves.

1. Strelitzia reginae — Common Bird-Of-Paradise Flower: named for Queen Charlotte of Mecklenburg-Strelitz, giving a tropical flower a royal signature.
2. Victoria amazonica — Amazon Giant Waterlily: the giant water lily named for Queen Victoria and famously grown at Chatsworth.
3. Agave victoriae-reginae — Queen Victoria Agave: a compact desert jewel carrying the queen's name in its botanical identity.
4. Rosa 'Queen Elizabeth' — Queen Elizabeth: a landmark 1950s grandiflora rose named for the young Elizabeth II.
5. Paeonia lactiflora — Chinese Peony: the flower of wealth and honor in Tang court culture and later Chinese art.
6. Tulipa gesneriana — Garden Tulip: the flower of Ottoman court spectacle, especially during the Tulip Era.
7. Convallaria majalis — European Lily Of The Valley: a delicate royal bouquet flower, carried by Grace Kelly and Catherine Middleton.
8. Gladiolus x gandavensis — Gladiolus: Josephine's Malmaison gardens helped make dramatic exotics a courtly obsession.
9. Rosa gallica 'Officinalis' — Apothecary's Rose: the red rose of Lancaster, still carrying the memory of dynastic conflict.
10. Chrysanthemum morifolium — Florist's Chrysanthemum: the cultivated chrysanthemum behind one of the world's most recognizable imperial floral emblems.
---

## 7. Explorer's Prize
> id: explorer-s-prize

Plants introduced to Western gardens through plant hunting and botanical expeditions.
> intro: Plant hunters crossed Yunnan ravines, Himalayan passes, and South African valleys for species European gardens had never seen. These plants arrived with danger, ambition, and a little bit of obsession attached.

1. Davidia involucrata — Dove Tree: E. H. Wilson's famous China prize, pursued after an earlier collector's tree had vanished.
2. Rhododendron augustinii — Augustine's Rhododendron: one of Augustine Henry's Chinese discoveries, prized for clear blue-lavender flowers.
3. Meconopsis betonicifolia — Himalayan Blue Poppy: a near-mythic blue flower introduced from high Himalayan and Tibetan country.
4. Metasequoia glyptostroboides — Dawn Redwood: known first as a fossil, then rediscovered alive in China in the 1940s.
5. Magnolia campbellii — Pink Tulip Tree: a Himalayan magnolia that brought huge rose-pink spring flowers into collector gardens.
6. Paeonia rockii — Paeonia rockii: Joseph Rock's tree peony became a collector's plant for its dramatic blotched flowers.
7. Rodgersia sambucifolia — Rodgersia sambucifolia: a Sichuan foliage perennial gathered into the great early-1900s plant-hunting wave.
8. Callicarpa giraldii — Callicarpa giraldii: a Chinese beautyberry linked to Giuseppe Giraldi's Shaanxi collections.
9. Holboellia latifolia — Sausage Vine: a Himalayan vine brought into cultivation through early colonial botany.
10. Strelitzia reginae — Common Bird-Of-Paradise Flower: Francis Masson's South African collection became one of Kew's great exotic trophies.
---

## 8. Pioneer Plants
> id: pioneer-plants

Crops, hedges, and homestead plants that shaped early American settlement.
> intro: Frontier gardens were practical before they were pretty. Corn, beans, squash, sunflowers, apples, sweet potatoes, willow, and Osage orange fed families, fenced animals, shaded wells, and made hard places livable.

1. Zea mays — Maize: the central Indigenous grain that became indispensable to colonial and frontier foodways.
2. Helianthus annuus — Common Sunflower: a North American crop for seed, oil, feed, and a bright marker of open land.
3. Helianthus tuberosus — Jerusalem Artichoke: an Indigenous tuber crop that could survive rough soils and cold winters.
4. Phaseolus vulgaris — Common Bean: one of the Three Sisters, twining through corn and feeding families with protein.
5. Cucurbita pepo — American Pumpkin: a storage crop for pies, soups, livestock feed, and autumn household ritual.
6. Rudbeckia hirta — Black-Eyed Susan: a tough prairie flower that followed roadsides, fields, and disturbed ground.
7. Malus domestica — Apple: the orchard tree of cider, winter storage, and the Johnny Appleseed frontier myth.
8. Ipomoea batatas — Sweet Potato: a Southern homestead staple that yields heavily in heat and modest soil.
9. Maclura pomifera — Osage Orange: the living fence of the Plains before barbed wire made hedges obsolete.
10. Salix babylonica — Weeping Willow: planted near wells and homesteads for shade, quick growth, and usable withes.
---

## 9. Revolutionary Brews
> id: revolutionary-tea

The tea plant and the herbs colonists brewed when imported tea became political.
> intro: The American tea boycott turned kitchens into small acts of resistance. Imported Camellia tea became suspect, so households brewed New Jersey tea, bee balm, mint, raspberry leaves, sage, chamomile, and other homegrown infusions.

1. Camellia sinensis — Tea: the imported Chinese tea at the center of taxation, boycott, and the Boston Tea Party.
2. Ceanothus americanus — New Jersey Tea: the best-known native substitute, with leaves dried for patriotic tea.
3. Monarda didyma — Scarlet Beebalm: Oswego tea, learned from Indigenous use and brewed by settlers in New York.
4. Monarda fistulosa — Wild Bergamot: an aromatic native mint family plant that made a strong frontier infusion.
5. Rubus idaeus — Red Raspberry: raspberry leaves were a household herbal tea long before tea bags.
6. Mentha spicata — Spearmint: easy to grow, hard to kill, and pleasant enough for daily kitchen brewing.
7. Mentha x piperita — Black Peppermint: a brisk cultivated mint that became a standard domestic infusion.
8. Matricaria chamomilla — German Chamomile: a calming flower tea suited to the household apothecary.
9. Salvia officinalis — Garden Sage: sage tea was a common home remedy and a practical substitute when imported tea was avoided.
10. Achillea millefolium — Common Yarrow: a bitter tonic herb that could be gathered or grown for medicinal teas.
---

## 10. Literary Icons
> id: literary-icons

Plants made unforgettable by poems, plays, novels, scripture, and song.
> intro: Some plants arrive in the mind already quoted: Ophelia's rosemary, Wordsworth's daffodils, Shakespeare's heartsease, Tennyson's lotus, Gray's yew. This collection is a bookshelf planted in soil.

1. Viola tricolor — Wild Pansy: Shakespeare's love-in-idleness, the flower that makes desire misfire in A Midsummer Night's Dream.
2. Rosmarinus officinalis — Rosemary: Ophelia's remembrance herb in Hamlet, still one of literature's clearest plant cues.
3. Rosa damascena — Damask Rose: the scented old rose behind countless sonnets, love poems, and comparisons.
4. Narcissus pseudonarcissus — Wild Daffodil: Wordsworth fixed the golden daffodil as the flower of remembered joy.
5. Papaver rhoeas — Common Poppy: the red poppy of sleep, war remembrance, and the dangerous poppy fields of story.
6. Nelumbo nucifera — Sacred Lotus: Tennyson's lotos-eaters made the lotus a flower of dreamy forgetting.
7. Prunus serrulata — Japanese Cherry: a flowering cherry that fits the literary tradition of brief beauty at its peak.
8. Lilium candidum — Madonna Lily: the white lily of biblical, Marian, and medieval devotional imagery.
9. Laurus nobilis — Bay Laurel: the poet's laurel, a plant that became shorthand for literary honor itself.
10. Taxus baccata — Common Yew: the graveyard tree that gives churchyard poetry its dark, rooted presence.
---

## 11. Old Apothecary
> id: ancient-medicine

Plants that shaped ancient, medieval, and early modern medicine.
> intro: Before modern pharmacology, healers worked from bark, roots, leaves, flowers, and bitter resins. These plants belonged to household remedies, monastery gardens, battlefield treatments, and early medical texts.

1. Aloe vera — Aloe Vera: one of the oldest recorded skin-soothing plants, used for burns and wounds across Mediterranean and Egyptian traditions.
2. Papaver somniferum — Opium Poppy: the ancient source of opium, pain relief, sedation, and one of medicine's most complicated legacies.
3. Salix alba — White Willow: willow bark was used for pain and fever long before salicin led toward aspirin chemistry.
4. Digitalis purpurea — Purple Foxglove: an old folk remedy transformed by William Withering into a landmark heart medicine.
5. Artemisia absinthium — Absinthe Wormwood: a bitter herb of ancient and medieval medicine, especially for digestion and parasites.
6. Achillea millefolium — Common Yarrow: the soldier's wound herb, traditionally used to staunch bleeding.
7. Salvia officinalis — Garden Sage: a monastery and kitchen herb once valued for throat, mouth, and digestive complaints.
8. Thymus vulgaris — Common Thyme: a strongly aromatic herb whose thymol-rich scent made it a traditional cleansing plant.
9. Mentha x piperita — Black Peppermint: a cooling digestive herb that bridges old apothecary use and modern menthol products.
10. Sambucus nigra — European Elderberry: elder flowers and berries have been part of European household medicine for centuries.
---

## 12. Native Remedies
> id: native-remedies

North American plants with Indigenous food, medicine, and ceremonial histories.
> intro: North American Indigenous plant knowledge is deep, regional, and specific. This collection highlights species later absorbed into American herbalism, often without enough credit to the communities that knew them first.

1. Echinacea purpurea — Purple Coneflower: a Plains-associated medicinal plant used for wounds, bites, toothache, and later American herbal products.
2. Monarda fistulosa — Wild Bergamot: an aromatic native mint used by several tribes for teas, poultices, and antiseptic washes.
3. Asclepias tuberosa — Butterfly Milkweed: known as pleurisy root in American herbalism, with Indigenous respiratory uses behind the name.
4. Lobelia inflata — Indian Tobacco: a powerful medicinal plant historically used with caution for respiratory and emetic purposes.
5. Lobelia cardinalis — Cardinal Flower: a brilliant wetland plant with ceremonial and medicinal associations in northeastern traditions.
6. Sagittaria latifolia — Broadleaf Arrowhead: wapato tubers were an important food in many wetland and Pacific Northwest communities.
7. Arctostaphylos uva-ursi — Bearberry: kinnikinnick leaves were used in smoking mixtures and urinary remedies.
8. Achillea millefolium — Common Yarrow: a widespread wound plant, valued for poultices and bleeding control.
9. Eupatorium purpureum — Spotted Joe-Pye Weed: linked to the Mohican healer Joseph Shauquethqueat and later fever-remedy traditions.
10. Rudbeckia hirta — Black-Eyed Susan: used in some Indigenous traditions for colds, swelling, and topical preparations.
---

## 13. Modern Drugs
> id: modern-drugs

Plants that directly produced or inspired important pharmaceutical medicines.
> intro: The pharmacy still grows in the garden. Some modern drugs began as plant defenses, latex, bark chemistry, or alkaloids, then became heart medicines, cancer therapies, antimalarials, anesthetics, and painkillers.

1. Digitalis purpurea — Purple Foxglove: source of digitalis glycosides that reshaped heart medicine.
2. Taxus baccata — Common Yew: part of the yew story behind paclitaxel, one of the major plant-derived cancer drugs.
3. Taxus cuspidata — Japanese Yew: a source of taxane precursors used in semi-synthetic paclitaxel production.
4. Salix alba — White Willow: willow salicylates helped lead to aspirin, the most famous plant-inspired pain medicine.
5. Artemisia annua — Sweet Wormwood: source of artemisinin, a Nobel-recognized breakthrough in malaria treatment.
6. Catharanthus roseus — Madagascar Periwinkle: source of vincristine and vinblastine, vital drugs in cancer chemotherapy.
7. Papaver somniferum — Opium Poppy: source of morphine and codeine, foundational but high-risk analgesic compounds.
8. Atropa belladonna — Deadly Nightshade: source of atropine, used in ophthalmology, emergency medicine, and anesthesia.
9. Podophyllum peltatum — Mayapple: inspired podophyllotoxin-derived cancer drugs such as etoposide.
10. Ephedra sinica — Ma Huang: source of ephedrine, an important bronchodilator and decongestant compound.
---

## 14. Healing Herbs
> id: healing-herbs

Everyday herbs traditionally kept for minor household care.
> intro: These are the gentle end of the apothecary: soothing teas, aromatic steams, salves, gargles, and kitchen remedies. They are not a replacement for medical care, but they explain why herb gardens have always belonged close to the door.

1. Aloe vera — Aloe Vera: kept on windowsills for cooling gel on minor burns and irritated skin.
2. Matricaria chamomilla — German Chamomile: a classic calming tea for bedtime and unsettled stomachs.
3. Mentha x piperita — Black Peppermint: a bright digestive herb used for nausea, heaviness, and cooling aroma.
4. Salvia officinalis — Garden Sage: traditionally used as a throat gargle and strongly flavored kitchen medicine.
5. Thymus vulgaris — Common Thyme: an aromatic herb long used in cough syrups, steams, and antimicrobial household preparations.
6. Lavandula angustifolia — Common Lavender: grown for calming scent, bath blends, sachets, and minor skin salves.
7. Melissa officinalis — Lemon Balm: a lemon-scented mint traditionally brewed for stress, sleep, and digestion.
8. Calendula officinalis — Pot Marigold: the orange flower of homemade salves for chapped, dry, or scraped skin.
9. Echinacea purpurea — Purple Coneflower: a modern herbal staple with roots in North American medicinal plant traditions.
10. Rosmarinus officinalis — Rosemary: used in invigorating rinses, rubs, and teas, with a reputation for memory and circulation.
---

## 15. Air Purifiers
> id: air-purifiers

Houseplants made famous by sealed-chamber air-cleaning studies.
> intro: The NASA Clean Air Study turned ordinary houseplants into modern icons. Real rooms need ventilation more than a few pots, but these plants still earn their place with leaf area, humidity, dust-trapping surfaces, and a reputation for tolerating indoor life.

1. Epipremnum aureum — Golden Pothos: a famously resilient vine from the NASA list, tolerant of dim rooms and irregular care.
2. Spathiphyllum wallisii — Peace Lily: a glossy, flowering houseplant included in VOC chamber studies and loved for low-light performance.
3. Sansevieria trifasciata — Snake Plant: a sculptural CAM plant that handles dry indoor air and neglect unusually well.
4. Chlorophytum comosum — Spider Plant: easy, pet-friendlier than many houseplants, and a classic formaldehyde-study species.
5. Dracaena marginata — Madagascar Dragon Tree: a narrow, architectural dracaena associated with xylene and formaldehyde chamber tests.
6. Ficus benjamina — Weeping Fig: a leafy indoor tree with major dust-trapping surface and NASA-study fame.
7. Chamaedorea elegans — Parlour Palm: a low-light palm that brings soft foliage without demanding bright sun.
8. Aglaonema commutatum — Philippine Evergreen: a durable low-light foliage plant included in indoor air-quality conversations.
9. Hedera helix — Common Ivy: a trailing plant studied for indoor pollutants and valued for dense evergreen leaves.
10. Nephrolepis exaltata — Southern Sword Fern: the Boston fern type, prized for humidity, fine fronds, and formaldehyde-study reputation.
---

## 16. Bedroom Allies
> id: bedroom-allies

Quiet, calming, low-fuss plants suited to bedrooms and nightstands.
> intro: A bedroom plant should be calm company: not fussy, not messy, and comfortable in softer light. These plants bring fragrance, sculptural leaves, gentle humidity, or simple resilience to the room where the day winds down.

1. Sansevieria trifasciata — Snake Plant: upright, tidy, drought-tolerant, and famous for CAM nighttime gas exchange.
2. Aloe vera — Aloe Vera: a compact succulent for bright bedrooms, with useful gel close at hand.
3. Lavandula angustifolia — Common Lavender: the classic calming scent for a sunny bedroom window or bedside bouquet.
4. Jasminum sambac — Arabian Jasmine: an evening-fragrant plant for bright rooms where scent is part of the ritual.
5. Spathiphyllum wallisii — Peace Lily: soft white flowers and broad leaves suit low-light bedrooms with steady moisture.
6. Chlorophytum comosum — Spider Plant: a relaxed hanging plant that is easy to maintain and visually light.
7. Epipremnum aureum — Golden Pothos: a forgiving trailing vine for shelves, dressers, and lower-light corners.
8. Chamaedorea elegans — Parlour Palm: a soft-textured palm that brings hotel-room calm without high light.
9. Zamioculcas zamiifolia — Zanzibar Gem: a nearly silent partner for low-light bedrooms and forgetful watering schedules.
10. Ficus elastica — Rubber Plant: a bold, glossy-leaved plant for bedrooms that have enough space and filtered light.
---

## 17. Office Buddies
> id: office-buddies

Low-maintenance plants for desks, cubicles, and fluorescent-lit offices.
> intro: Office plants must survive dry air, weekend droughts, uneven light, and human distraction. These are the forgiving desk companions that keep looking alive while everyone else is in meetings.

1. Zamioculcas zamiifolia — Zanzibar Gem: glossy, architectural, and tolerant of weeks between waterings.
2. Sansevieria trifasciata — Snake Plant: upright leaves, low water needs, and a tiny footprint for tight office corners.
3. Epipremnum aureum — Golden Pothos: the classic office vine because it forgives shade, missed care, and awkward shelves.
4. Chlorophytum comosum — Spider Plant: easy, cheerful, and generous with baby plantlets for coworkers.
5. Aglaonema commutatum — Philippine Evergreen: colorful foliage that performs well in low-light commercial interiors.
6. Chamaedorea elegans — Parlour Palm: a Victorian survivor that still handles dry rooms and modest light.
7. Philodendron hederaceum — Heart-Leaf Philodendron: a forgiving trailing plant with friendly heart-shaped leaves.
8. Peperomia obtusifolia — Baby Rubber Plant: compact, tidy, and better suited to desks than many full-size houseplants.
9. Pilea peperomioides — Chinese Money Plant: a small conversation plant that propagates into easy colleague gifts.
10. Ficus elastica — Rubber Plant: a glossy statement plant for offices with a brighter corner.
---

## 18. Low-Light Champs
> id: low-light-champs

Plants that remain handsome where brighter plants fade.
> intro: Low light is not no light, but some plants cope with dim rooms far better than others. These are the reliable choices for north windows, hallways, offices, and apartments where sun is a rumor.

1. Aspidistra elatior — Cast-Iron Plant: the Victorian dark-hallway classic, famous for patience and endurance.
2. Zamioculcas zamiifolia — Zanzibar Gem: stores water in thick rhizomes and keeps its shape in subdued light.
3. Sansevieria trifasciata — Snake Plant: handles low light and drought better than most sculptural houseplants.
4. Aglaonema commutatum — Philippine Evergreen: bred and beloved for malls, offices, and shaded rooms.
5. Epipremnum aureum — Golden Pothos: a trailing vine that stays useful even when variegation softens in shade.
6. Philodendron hederaceum — Heart-Leaf Philodendron: an understory aroid that accepts the lower light of real homes.
7. Spathiphyllum wallisii — Peace Lily: one of the few common houseplants that can flower in gentle indoor light.
8. Chamaedorea elegans — Parlour Palm: named for the kind of shaded interior where it made its reputation.
9. Dracaena fragrans — Cornstalk Dracaena: a sturdy cane plant for corners, lobbies, and rooms with filtered light.
10. Calathea orbifolia — Goeppertia Orbifolia: a rainforest-floor foliage plant for bright shade and careful watering.
---

## 19. Deadly Beauty
> id: deadly-beauty

Gorgeous plants with serious toxicity.
> intro: Beauty is not the same as harmlessness. These plants are admired in gardens, old estates, and containers, but their chemistry demands respect, labels, and distance from children and pets.

1. Nerium oleander — Oleander: a dazzling flowering shrub whose cardiac glycosides make every part dangerous if eaten.
2. Digitalis purpurea — Purple Foxglove: beautiful spires with heart-active glycosides, medicine at dose and poison at dose.
3. Aconitum carmichaelii — Azure Monkshood: a blue-flowered perennial with aconitine, one of the garden's most serious poisons.
4. Ricinus communis — Castor Bean: bold tropical foliage and ornamental seedpods hiding ricin in the seeds.
5. Taxus baccata — Common Yew: a classic hedge and churchyard tree with deadly taxine alkaloids outside the red aril.
6. Brugmansia suaveolens — Night Bells: angelic hanging trumpets with dangerous tropane alkaloids.
7. Datura stramonium — Jimsonweed: a notorious annual whose hallucinogenic alkaloids can cause severe poisoning.
8. Lilium longiflorum — Easter Lily: elegant and fragrant, but extremely dangerous to cats even in small exposures.
9. Convallaria majalis — European Lily Of The Valley: tiny bells with potent cardiac glycosides throughout the plant.
10. Narcissus pseudonarcissus — Wild Daffodil: spring-bright flowers with bulbs that can poison people or pets when mistaken for food.
---

## 20. Toxic Twins
> id: toxic-twins

Common plants that look gentle but deserve caution.
> intro: These are not gothic villains; they are ordinary houseplants, hedges, and vegetables. The surprise is the point: familiar leaves can still contain oxalates, cyanogenic compounds, alkaloids, or pet hazards.

1. Hydrangea macrophylla — Mophead Hydrangea: lush florist looks, but leaves and flowers contain cyanogenic glycosides.
2. Rhododendron austrinum — Orange Azalea: azaleas and rhododendrons contain grayanotoxins that can affect the heart and nerves.
3. Philodendron hederaceum — Heart-Leaf Philodendron: a friendly-looking vine with calcium oxalate crystals that irritate mouth and throat.
4. Monstera deliciosa — Swiss Cheese Plant: a beloved houseplant whose unripe tissues and leaves contain irritating oxalates.
5. Spathiphyllum wallisii — Peace Lily: the peaceful name hides the same oxalate issue common to many aroids.
6. Dieffenbachia seguine — Tuftroot: the classic dumb cane, notorious for painful oral irritation if chewed.
7. Solanum lycopersicum — Tomato: ripe fruit is dinner, but leaves, stems, and green parts are not pet-safe snacks.
8. Prunus laurocerasus — Cherry Laurel: a common hedge with cyanogenic leaves that can endanger livestock and pets.
9. Taxus x media — Anglo-Japanese Yew: a neat suburban evergreen whose seeds and foliage are dangerously toxic.
10. Ligustrum sinense — Chinese Privet: an everyday hedge with berries that can sicken pets and children.
---

## 21. Thorny Defenders
> id: thorny-defenders

Armed plants for security hedges and intruder-resistant borders.
> intro: Before cameras and chain link, people planted boundaries that fought back. These shrubs, vines, cactus pads, and spiny rosettes make edges feel deliberate and difficult to cross.

1. Rosa rugosa — Rugosa Rose: a salt-tolerant hedge rose with dense prickles and fragrant flowers.
2. Pyracantha coccinea — Scarlet Firethorn: the classic wall-trained security shrub, armed with thorns and bright berries.
3. Ilex aquifolium — European Holly: spiny evergreen leaves make a glossy but unfriendly barrier.
4. Berberis thunbergii — Japanese Barberry: dense twiggy growth and fine thorns create a low, difficult hedge.
5. Crataegus monogyna — Common Hawthorn: the old rural hedgerow thorn of Britain and Europe.
6. Rosa multiflora — Multiflora Rose: once promoted as a living fence, now a cautionary example of a hedge plant turned invasive.
7. Maclura pomifera — Osage Orange: the pre-barbed-wire cattle hedge of the Great Plains.
8. Poncirus trifoliata — Trifoliate Orange: cold-hardy citrus kin with long, rigid thorns.
9. Opuntia ficus-indica — Indian Fig Opuntia: a pad-forming cactus used as living fence in dry regions.
10. Agave americana — American Century Plant: massive rosettes with leaf-edge teeth and terminal spines.
---

## 22. Hummingbird Magnets
> id: hummingbird-magnets

Tubular, nectar-rich flowers for hummingbird gardens.
> intro: Hummingbirds read flowers by shape as much as color. Red, orange, and blue tubes from spring columbine through late-season sage can turn a garden into a nectar route.

1. Monarda didyma — Scarlet Beebalm: a red native mint family flower built for hummingbird visits.
2. Lonicera sempervirens — Coral Honeysuckle: a native vine with tubular coral flowers and a long feeding season.
3. Salvia coccinea — Tropical Sage: bright red trumpets that rebloom through heat.
4. Salvia guaranitica — Anise-Scented Sage: deep blue tubes that hummingbirds work heavily from summer into fall.
5. Aquilegia canadensis — Red Columbine: one of the great early spring native flowers for returning hummingbirds.
6. Lobelia cardinalis — Cardinal Flower: streamside scarlet flowers that seem designed around hummingbird bills.
7. Penstemon barbatus — Beardlip Penstemon: a Southwestern red-tubed penstemon with classic hummingbird architecture.
8. Mandevilla sanderi — Brazilian Jasmine: a patio vine with large tropical funnels for warm-climate nectar seekers.
9. Ipomoea coccinea — Red Morning Glory: a light annual climber with small red trumpets at hummingbird scale.
10. Hibiscus rosa-sinensis — Spider Hibiscus: a warm-zone hibiscus with showy flowers that draw hummingbird attention.
---

## 23. Butterfly Havens
> id: butterfly-havens

Host and nectar plants for monarchs, swallowtails, fritillaries, and more.
> intro: A butterfly garden needs both nursery and dining room. Milkweed feeds monarch caterpillars, parsley feeds swallowtails, violets feed fritillaries, and late flowers fuel adults before migration and frost.

1. Asclepias tuberosa — Butterfly Milkweed: a monarch host plant with brilliant orange nectar flowers.
2. Asclepias incarnata — Swamp Milkweed: a wet-soil milkweed that supports monarch caterpillars and summer pollinators.
3. Buddleja davidii — Butterfly Bush: a nectar powerhouse, best used where it is not invasive or where sterile cultivars are preferred.
4. Echinacea purpurea — Purple Coneflower: sturdy landing-pad flowers for swallowtails, fritillaries, and skippers.
5. Liatris spicata — Dense Blazing Star: late-summer spikes that feed monarchs and other butterflies.
6. Zinnia elegans — Elegant Zinnia: an easy annual with all-summer color and accessible nectar.
7. Lantana camara — Common Lantana: nonstop warm-climate nectar clusters for adult butterflies.
8. Eupatorium purpureum — Spotted Joe-Pye Weed: a towering late-season banquet for monarchs and swallowtails.
9. Verbena bonariensis — Purpletop Vervain: airy purple stems that butterflies can find and land on easily.
10. Petroselinum crispum — Garden Parsley: a familiar kitchen herb that doubles as black swallowtail caterpillar food.
---

## 24. Bee Banquets
> id: bee-banquets

Season-long flowers for native bees and honeybees.
> intro: Different bees want different flowers, but a good bee garden keeps the table set from spring to frost. Aromatic herbs, native composites, goldenrod, asters, and phacelia make a genuine pollen-and-nectar calendar.

1. Salvia officinalis — Garden Sage: early-summer flowers that bees work enthusiastically when herbs are allowed to bloom.
2. Lavandula angustifolia — Common Lavender: a Mediterranean bee magnet with long bloom and concentrated fragrance.
3. Monarda fistulosa — Wild Bergamot: a native mint family flower especially good for bumblebees.
4. Echinacea purpurea — Purple Coneflower: broad daisy heads provide easy access for many bee sizes.
5. Solidago canadensis — Canada Goldenrod: critical late-season pollen and nectar when colonies are preparing for winter.
6. Symphyotrichum novae-angliae — New England Aster: fall flowers that keep bees active near the end of the season.
7. Nepeta x faassenii — Catmint: a long-blooming, low-fuss perennial adored by bumblebees.
8. Agastache foeniculum — Anise Hyssop: fragrant purple spikes that feed bees for weeks.
9. Origanum vulgare — Oregano: when allowed to flower, oregano becomes a tiny-flowered bee highway.
10. Phacelia tanacetifolia — Lacy Phacelia: a famously nectar-rich annual used in pollinator plantings and cover crops.
---

## 25. Drought Warriors
> id: drought-warriors

Plants for summer-dry, water-restricted, and xeriscape gardens.
> intro: These plants ask gardeners to stop loving them with the hose. Agaves, lavender, rosemary, sages, manzanita, ceanothus, sedum, yucca, and cactus are built for lean soil, sun, and dry spells.

1. Agave americana — American Century Plant: a Southwestern icon storing water in massive armored leaves.
2. Lavandula x intermedia — Dutch Lavender: a dry-garden lavender hybrid that thrives with sun, drainage, and restraint.
3. Salvia apiana — White Sage: a California chaparral plant adapted to dry summers and open sun.
4. Rosmarinus officinalis — Rosemary: a woody Mediterranean herb that dislikes overwatering once established.
5. Sedum spectabile — Butterfly Stonecrop: a succulent perennial that stores moisture and blooms when many borders tire.
6. Yucca elephantipes — Spineless Yucca: a bold drought-tolerant rosette plant for containers and warm gardens.
7. Eriogonum fasciculatum — California Buckwheat: a dry-slope native with nectar-rich summer flowers and minimal water needs.
8. Ceanothus thyrsiflorus — Blueblossom: a California lilac that wants winter rain, summer dryness, and good drainage.
9. Arctostaphylos manzanita — Common Manzanita: a sculptural chaparral shrub that fails faster from summer water than drought.
10. Opuntia ficus-indica — Indian Fig Opuntia: a true cactus for heat, sun, and long dry stretches.
---

## 26. Shade Savers
> id: shade-savers

Deep-shade and woodland performers for north walls, trees, and quiet corners.
> intro: Shade gardens succeed when they stop pretending to be sunny borders. These plants work with lower light: foliage, texture, spring ephemerality, winter bloom, and woodland grace instead of nonstop summer flowers.

1. Hosta sieboldiana — Siebold's Plantain Lily: big blue-green foliage, the classic foundation of shade planting.
2. Astilbe x arendsii — Astilbe: feathery plumes for moist shade where many perennials sulk.
3. Hydrangea quercifolia — Oakleaf Hydrangea: a native shrub for partial shade, with flowers, fall color, and peeling bark.
4. Tiarella cordifolia — Heartleaf Foamflower: a woodland groundcover with soft leaves and spring foamlike flowers.
5. Heuchera americana — American Alumroot: a tough native foliage plant that handles dry shade better than many perennials.
6. Helleborus orientalis — Lenten-Rose: winter-to-spring bloom for the season when shade gardens need it most.
7. Aspidistra elatior — Cast-Iron Plant: deep-shade evergreen foliage for mild gardens and dim interiors.
8. Polygonatum biflorum — Solomon's Seal: arching stems turn dappled shade into a deliberate woodland scene.
9. Dicentra spectabilis — Bleeding Heart: a spring shade classic with romantic flowers before summer dormancy.
10. Pulmonaria saccharata — Bethlehem-Sage: silver-spotted leaves and early blue flowers brighten the woodland floor.
---

## 27. Kitchen Herbs
> id: kitchen-herbs

Essential herbs for sunny windowsills, balcony pots, and everyday cooking.
> intro: A kitchen herb garden should answer dinner quickly. Basil for tomatoes, rosemary for roasts, thyme for poultry, cilantro for tacos, dill for pickles, parsley for nearly everything: these are the daily-use plants worth keeping close.

1. Ocimum basilicum — Sweet Basil: the tomato, pesto, and summer salad herb no sunny kitchen should skip.
2. Rosmarinus officinalis — Rosemary: a woody herb for roasted vegetables, lamb, chicken, and bread.
3. Salvia officinalis — Garden Sage: the savory leaf behind stuffing, brown butter, beans, and winter cooking.
4. Thymus vulgaris — Common Thyme: a bouquet-garni workhorse for soups, poultry, stews, and roasted roots.
5. Origanum vulgare — Oregano: the pizza and grilled-vegetable herb that often tastes stronger dried.
6. Mentha spicata — Spearmint: the mint for tea, peas, fruit, salads, and summer drinks.
7. Petroselinum crispum — Garden Parsley: a universal finishing herb and the base of sauces from chimichurri to gremolata.
8. Coriandrum sativum — Coriander: cilantro leaves and coriander seeds make one plant useful in two different ways.
9. Anethum graveolens — Dill: the fresh herb of pickles, salmon, potatoes, yogurt, and spring vegetables.
10. Allium schoenoprasum — Chives: a tidy onion-flavored perennial for eggs, soups, potatoes, and garnishes.
---

## 28. Edible Weeds
> id: edible-weeds

Common lawn and field weeds with edible parts.
> intro: Some plants we fight in lawns are older food plants in disguise. Identification matters, pollution matters, and moderation matters, but these weeds reveal how much food knowledge hides underfoot.

1. Taraxacum officinale — Common Dandelion: young leaves, flowers, and roasted roots all have long food traditions.
2. Stellaria media — Common Chickweed: a mild, tender green for salads when harvested young and clean.
3. Portulaca oleracea — Common Purslane: a lemony, succulent green notable for omega-3 fatty acids.
4. Amaranthus retroflexus — Redroot Amaranth: young greens and seeds are edible, though mature plants become coarse.
5. Chenopodium album — Common Lambsquarters: a spinach-like wild green with a long history as a pot herb.
6. Plantago major — Greater Plantain: young leaves are edible and the seeds connect it to psyllium relatives.
7. Urtica dioica — Great Stinging Nettle: stinging raw, excellent cooked as a mineral-rich green.
8. Rumex crispus — Curled Dock: tart young leaves are edible in moderation, especially cooked because of oxalates.
9. Oxalis triangularis — False Shamrock: sour oxalis leaves are edible as a small accent, not a main green.
10. Capsella bursa-pastoris — Shepherd's-Purse: peppery seedpods and young leaves turn a sidewalk weed into a salad note.
---

## 29. Lucky Charms
> id: lucky-charms

Plants grown for luck, wealth, blessing, and household protection.
> intro: Luck plants work because people keep retelling them: coin-shaped leaves, braided trunks, sacred courtyard basil, four-leaf clover, lotus rising clean from mud. This collection gathers plants that make prosperity feel visible.

1. Pilea peperomioides — Chinese Money Plant: round coin leaves and easy offsets made it a modern friendship-and-prosperity plant.
2. Crassula ovata — Jade Plant: a classic wealth plant, with plump leaves that suggest stored fortune.
3. Pachira aquatica — Provision Tree: the braided money tree of offices, shops, and gift plants for financial luck.
4. Dracaena sanderiana — Lucky Bamboo: sold by stalk number in feng-shui gift culture, despite not being true bamboo.
5. Epipremnum aureum — Golden Pothos: widely called money plant in India and grown for household prosperity.
6. Trifolium repens — White Clover: the rare four-leaf form is one of the world's clearest luck symbols.
7. Nandina domestica — Heavenly Bamboo: an East Asian good-fortune shrub with red berries and New Year associations.
8. Ocimum sanctum — Holy Basil: tulsi is a sacred Hindu household plant associated with protection and blessing.
9. Zamioculcas zamiifolia — Zanzibar Gem: a modern fortune plant in offices because it looks prosperous and refuses to fail.
10. Nelumbo nucifera — Sacred Lotus: a Buddhist and Asian prosperity symbol rising cleanly from muddy water.
---

## 30. Gothic Garden
> id: gothic-garden

Dark, dramatic plants for moody borders and shadowy containers.
> intro: A gothic garden is not just black flowers. It is contrast, restraint, velvet foliage, winter bloom, black stems, and plants that feel a little theatrical even in daylight.

1. Aeonium arboreum 'Zwartkop' — Black Aeonium: near-black succulent rosettes with a sculptural, almost architectural silhouette.
2. Alocasia reginula — Black Velvet Alocasia: black-green velvet leaves with silver veins, perfect for indoor drama.
3. Sambucus nigra 'Black Lace' — Black Lace Elderberry: cutleaf purple-black foliage with a lacy, Victorian silhouette.
4. Alcea rosea 'Nigra' — Black Hollyhock: towering spires of wine-black flowers for the back of a moody border.
5. Aquilegia vulgaris 'Black Barlow' — Black Barlow Columbine: dark double flowers that look more antique than sweet.
6. Tulipa 'Queen of Night' — Queen of Night Tulip: the iconic near-black tulip, glossy and theatrical in spring.
7. Helleborus orientalis — Lenten-Rose: winter flowers in smoky plum and dark forms that suit shaded borders.
8. Viola 'Molly Sanderson' — Black Viola: small almost-black flowers for containers and cool-season edges.
9. Phyllostachys nigra — Black Bamboo: mature culms turn polished black, giving height without flowers.
10. Ophiopogon planiscapus 'Nigrescens' — Black Mondo Grass: low black strap leaves that make pale flowers and gravel look sharper.
