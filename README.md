# Alexandra Novak — No Bee No May

No Bee No May is a Codex skill and a small local checker for Russian prose. It finds clusters of repeated phrases, rhythms, metaphors, psychological explanations, and narrative endings that can make a passage sound synthetic.

The checker shows concrete matches and pattern density. It is a review aid, not a conclusion about where a text came from.

## What it checks

The catalog contains 38 families, including:

- negative triads and clipped anaphora;
- escalating adjective lists and `почти` / `слишком` intensifiers;
- bodily certainty, thick air, weighted silence, and object aftertaste;
- the psyche as a character, control narratives, pseudo-therapy, and inner parts;
- paragraph bridges, universal conclusions, serial metaphors, bad coffee, and institutions that stop pretending.

Read the full map in [`references/catalog.md`](references/catalog.md) or inspect the machine-readable rules in [`references/rules.json`](references/rules.json).

## Thanks

Thanks to Alexandra Vasilyevna Novak for the original field guide. Its sharp, playful taxonomy is the inspiration for this project.

## Use it in Codex

Install the skill folder under `~/.codex/skills/no-bee-no-may`, then invoke it explicitly:

```text
$no-bee-no-may Проверь этот текст на скопление синтетических клише и покажи точные фрагменты.
```

For Russian UI copy, pair it with `sasha`: `sasha` handles clarity, component conventions, and typography; No Bee No May checks the synthetic-prose layer.

## Run the checker

```bash
python3 scripts/no_bee_no_may.py --text "Не страх, не слабость, не привычка. Психика уже всё поняла."
python3 scripts/no_bee_no_may.py draft.md --format md
python3 scripts/no_bee_no_may.py notes/ --format json
```

The text report includes the category, matched span, confidence, and a rough cluster diagnosis. JSON is intended for other tools. The checker skips common repository noise such as `.git`, `node_modules`, `dist`, and fenced code blocks.

## Read the result

The rough scale follows the supplied field guide:

- 1–2 categories: an isolated phrase or ordinary literary inertia;
- 3–4: a noticeable synthetic patina;
- 5–6: a strong cluster worth revising or discussing;
- 7 or more: very dense use of the catalog's voice.

Keep fiction, dialogue, quotations, therapy or medical language, legal copy, and technical language in context. A familiar word is not a problem by itself.

## Source

The catalog is based on the user-provided PDF *Полевой определитель речевых клише ChatGPT* by A. V. Novak, accessed on 2026-08-25. The guide presents recurring formulas as stylistic signals and treats one match as insufficient evidence, so the checker reports clusters rather than isolated words.

## License

No license is declared yet. Add one before redistributing the repository.
