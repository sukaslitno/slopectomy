---
name: slopectomy
description: "Use when reviewing Russian prose, marketing copy, essays, or UI text for clustered synthetic-writing cliches catalogued in the Novak field guide. Detects phrase, rhythm, metaphor, psychologizing, and narrative signatures; reports evidence without claiming authorship or AI provenance. Do not use as a standalone AI detector or as a replacement for Sasha's UI-copy rules."
---

# Slopectomy

Review Russian text for a recognizable cluster of synthetic-prose cliches from the supplied field guide by A. V. Novak. The goal is a useful stylistic diagnosis: show the exact wording, name the pattern, explain why it feels formulaic, and suggest a plainer or more specific direction only when the user asks for editing.

## Boundaries

- Do not call a text AI-generated, human-written, copied, or inauthentic. Report only the observed stylistic density.
- One phrase is weak evidence. Count distinct categories in the same passage and explain false-positive possibilities.
- Do not penalize a word merely because it appears in the catalog. `почти`, `честно`, `тело`, `кофе`, or `психика` can be appropriate in context.
- Separate intentional literary voice, quoted material, dialogue, fiction, therapy/medical language, legal language, and ordinary exposition from unexamined formulaic writing.
- Preserve the user's meaning. Do not flatten deliberate style into generic prose without permission.
- For Russian UI copy, use `sasha` for clarity, component patterns, and typography; use this skill only for the synthetic-prose layer.

## Workflow

1. Identify the scope: a sentence, paragraph, document, or repository. For a repository, inspect only text-like files and respect ignore directories.
2. Run the deterministic scan when the files are accessible:

   ```bash
   python3 slopectomy/scripts/slopectomy.py --text "..."
   python3 slopectomy/scripts/slopectomy.py path/to/file.md --format md
   ```

   The script is a triage aid, not the final judgment. Read `references/catalog.md` when interpreting a category and `references/rules.json` when extending or auditing the matcher.
3. Read the surrounding paragraph for every hit. Remove matches from code, URLs, placeholders, and markup unless the user explicitly wants those checked.
4. Deduplicate repeated hits from one category. Report category clusters, not a raw word count. Use the field guide's rough scale:
   - 1–2 categories: ordinary literary inertia or an isolated phrase;
   - 3–4: a noticeable synthetic patina;
   - 5–6: a strong cluster that merits revision or stylistic discussion;
   - 7+: very dense use of the catalog's voice.
5. Check whether the same paragraph combines several families: refusal/contrast, body or atmosphere, psychological explanation, honesty/maturity/permission language, manufactured metaphor, and a closure about choosing oneself or moving on.
6. Write the result in the user's language. Quote short spans, link each span to a category, mark confidence as `high`, `medium`, or `soft`, and state what is uncertain.

## Review format

Use this compact structure unless the user asks for another format:

```md
## Вывод
Короткий вывод о стилистической плотности, без заявления об авторстве.

## Найденные признаки
| Категория | Цитата | Уверенность | Наблюдение |
|---|---|---|---|
| ... | ... | ... | ... |

## Кластер
Какие независимые категории встречаются рядом и насколько это заметно.

## Что изменить
Только если нужна редактура: заменить готовую формулу конкретным наблюдением, действием, фактом или образом из сцены.
```

If there are no meaningful clusters, say so plainly and mention any isolated soft matches. Do not manufacture a verdict.

## Editing guidance

When rewriting is requested, prefer:

- a concrete fact or visible action over a universal psychological explanation;
- a specific sensory detail over stock body/air metaphors;
- a direct transition over a ceremonial bridge such as `Но здесь важно другое`;
- a precise ending over `И этого достаточно`, `Она выбрала себя`, or `Воздух снова стал обычным`;
- the author's actual subject over serial metaphors such as `точка опоры`, `внутренний компас`, `архитектура отношений`, and `точка невозврата`.

Do not rewrite medical, legal, consent, safety, or quoted text automatically. Flag semantic risk and ask for a narrower edit when a replacement could change meaning.

## Supporting files

- `references/catalog.md` — human-readable map of all 38 categories from the field guide.
- `references/rules.json` — matcher rules, representative examples, confidence, and source notes.
- `scripts/slopectomy.py` — deterministic local scan for text and common repository files.
