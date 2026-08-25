# Alexandra Novak — No Bee No May

No Bee No May is a small Codex skill and local checker for Russian prose. It looks for clusters of repeated phrases, rhythms, metaphors, psychological explanations, and narrative endings associated with synthetic-sounding writing.

It does not decide who wrote a text and it does not prove that a language model was involved. One familiar phrase can be ordinary writing. The useful signal is the density and combination of independent patterns in the same passage.

## What it checks

The catalog covers 38 families, including:

- negative triads and clipped anaphora;
- escalating adjective lists and `почти` / `слишком` intensifiers;
- thoughts that “arrive,” bodily certainty, thick air, weighted silence, and object aftertaste;
- the psyche as an independent character, control narratives, pseudo-therapy, inner parts, and maturity or permission language;
- paragraph bridges, universal conclusions, “she chose herself” endings, serial metaphors, bad coffee, and institutions that “stopped pretending.”

See [`references/catalog.md`](references/catalog.md) for the full map and [`references/rules.json`](references/rules.json) for the machine-readable rules.

## Thanks

Thanks to Alexandra Vasilyevna Novak for the original field guide. Its sharp, playful taxonomy made this project possible. A public bibliographic listing identifies her as the author of a 2026 monograph on legal and information asymmetries around AI and autonomous digital agents: [LitRes](https://www.litres.ru/book/aleksandra-novak-339/informacionnye-i-pravovye-asimmetrii-razumnyh-tehnolo-74028718/).

## Use it in Codex

Install the skill folder under `~/.codex/skills/no-bee-no-may`, then invoke it explicitly:

```text
$no-bee-no-may Проверь этот текст на скопление синтетических клише и покажи точные фрагменты.
```

For Russian UI copy, pair it with `sasha`: `sasha` handles clarity, component conventions, and typography; No Bee No May checks for the catalogued synthetic-prose layer.

## Use the checker directly

```bash
python3 scripts/no_bee_no_may.py --text "Не страх, не слабость, не привычка. Психика уже всё поняла."
python3 scripts/no_bee_no_may.py draft.md --format md
python3 scripts/no_bee_no_may.py notes/ --format json
```

The text report shows the category, matched span, confidence, and a rough cluster diagnosis. JSON is intended for other tooling. The checker skips common repository noise such as `.git`, `node_modules`, `dist`, and fenced code blocks.

## Interpreting the result

The rough scale follows the supplied field guide:

- 1–2 categories: an isolated phrase or ordinary literary inertia;
- 3–4: a noticeable synthetic patina;
- 5–6: a strong cluster worth revising or discussing;
- 7 or more: very dense use of the catalog's voice.

These are review prompts, not authorship labels. Keep deliberate fiction, quoted text, dialogue, therapy or medical terminology, legal copy, and technical language in context.

## Source

The catalog is derived from the user-provided PDF *Полевой определитель речевых клише ChatGPT* by A. V. Novak, accessed on 2026-08-25. The PDF presents the categories as a field guide to recurring formulas and explicitly treats a single match as insufficient evidence. The author’s full name and related public bibliography were cross-checked against [LitRes](https://www.litres.ru/book/aleksandra-novak-339/informacionnye-i-pravovye-asimmetrii-razumnyh-tehnolo-74028718/) and [LitPortal](https://litportal.ru/avtory/aleksandra-novak-33940838/read/page/5/kniga-informacionnye-i-pravovye-asimmetrii-razumnyh-tehnolo-74028718-1328716/). No public source URL was supplied for the PDF itself.

## License

No license is declared yet. Add one before redistributing the repository.
