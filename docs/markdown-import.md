# Markdown import format

FeedbackForm accepts AI-generated or manually written UTF-8 `.md` and `.markdown`
files. Use **Import a Markdown document** below Share an idea in the workspace.
Download the [template](../web/public/templates/idea-template.md) from the form,
or open `/templates/idea-template.md` in the running app.

The recommended format is one participant's contribution per document:

| Heading | Information to include |
| --- | --- |
| `# Title` | A short project or idea title, up to 200 characters. |
| `## Context` | Decision question, target users, and problem. |
| `## Proposed idea` | Proposed solution and smallest useful demonstration. |
| `## Preferences` | Desires and alternatives the participant prefers or rejects. |
| `## Concerns` | Risks, objections, and reasons. |
| `## Personal requirements` | Conditions for the participant's support. These are not group-approved constraints. |
| `## Open questions` | Questions that need answers before deciding. |
| `## Uncertainty` | Tentative views, assumptions, and missing information. |
| `## References` | Optional supporting links or citations. |

Use short bullet points. Keep “not,” “only if,” and “unless” explicit. Omit unused
sections or write “Unknown”; remove example placeholders before sharing. Other
headings and ordinary Markdown are also accepted. The format is guidance for
the model and reviewers, not a parser that silently discards unfamiliar sections.

Suggested prompt for an AI writing the document:

> Fill out the attached FeedbackForm Markdown template using only my supplied
> notes. Write one participant's contribution. Preserve negation, conditions,
> disagreement, and uncertainty. Do not invent preferences, facts, team agreement,
> votes, or approvals. Mark unknown information explicitly and remove unfilled
> placeholders. Keep the file under 20,000 text characters. Return the document
> itself as a UTF-8 .md file, without an enclosing code fence.

## Import and extraction behavior

1. Choose the file. This reads it locally into an editable plain-text preview;
   it does not save or call OpenAI yet.
2. Review the title and complete text. The first level-one heading supplies the
   suggested title; the filename without its extension is the fallback.
3. Check that you reviewed the document and are sharing it as your contribution.
   Changing the title or text clears this confirmation.
4. Select **Import reviewed Markdown**. It saves one idea through the existing
   authenticated API, attributed to the signed-in participant. Reload retains it,
   and later edits create new versions. The reviewed Markdown text is preserved,
   including headings and source references; uploaded file bytes and filenames
   are not retained as separate attachments. A UTF-8 BOM is removed on decoding.
5. Select **Extract preferences from new feedback**. The document enters the same
   snapshot/evidence workflow as typed ideas. OpenAI produces draft interpretations
   with exact source references. Each participant reviews their own interpretations.

Names, author fields, roles, or approvals written inside a file cannot impersonate
another participant or create votes. If a document reports someone else's views,
those remain reported text; that participant should contribute and review their
own preferences. Reviewing an AI-generated file is not proof that its claims are
true, and model interpretation still needs correction where necessary.

## Limits and rendering

Files must be at most 80,000 bytes and 20,000 text characters in the browser's
counter (emoji can count as two). Empty, invalid UTF-8, and NUL-containing files
are rejected. The API independently applies its existing idea title/body limits,
session, membership, Origin, and CSRF checks. Idea cards, comments, and idea history
render Markdown headings, lists, emphasis, quotes, code, and tables. HTTP(S) and
email links are clickable; unsafe URL schemes remain text. Raw HTML stays escaped,
and embedded images are displayed as alt text without fetching them.

**Show Markdown source** switches an idea back to its original text. Display
formatting never changes saved content or extraction inputs. Passage selections
on mapped text retain original UTF-16 source offsets and highlights. For decoded
entities, escaped characters, or code whose rendered text differs from its source,
use the source view or keyboard passage search for exact annotation.

Import works without model credentials. Extraction requires the server-side
OpenAI configuration in [README.md](../README.md) and sends the document text to
OpenAI. Downloading or uploading this template does not bypass human review or
establish semantic extraction quality.
