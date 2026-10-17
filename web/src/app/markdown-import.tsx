"use client";

import { useRef, useState, type FormEvent } from "react";
import type { components } from "@/lib/api.generated";
import { api } from "@/lib/api";

type Auth = components["schemas"]["AuthView"];

export default function MarkdownImport({ workspaceId, auth, onImported, onAuthError }: {
  workspaceId: string; auth: Auth; onImported: () => Promise<void>;
  onAuthError: (error: unknown) => void;
}) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [filename, setFilename] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [reviewed, setReviewed] = useState(false);
  const [reading, setReading] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function select(file?: File) {
    setFilename(""); setTitle(""); setBody(""); setReviewed(false); setError(""); setNotice("");
    if (!file) return;
    if (!/\.(md|markdown)$/i.test(file.name)) {
      setError("Choose a Markdown file ending in .md or .markdown."); return;
    }
    if (file.size > 80_000) {
      setError("This file is too large. Use at most 80 KB and 20,000 text characters."); return;
    }
    setReading(true);
    try {
      const text = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
      if (!text.trim()) throw new Error("The Markdown file is empty.");
      if (text.includes("\0")) throw new Error("Choose a UTF-8 text file, not a binary file.");
      if (text.length > 20_000) throw new Error("Use at most 20,000 text characters per file.");
      const heading = text.match(/^#\s+(.+?)\s*#*\s*$/m)?.[1]?.trim();
      setTitle(Array.from(heading || file.name.replace(/\.(md|markdown)$/i, "")).slice(0, 200).join(""));
      setBody(text); setFilename(file.name);
    } catch (error) {
      setError(error instanceof TypeError ? "The file must contain valid UTF-8 text."
        : error instanceof Error ? error.message : "Could not read the file.");
    } finally {
      setReading(false);
      // Allow selecting the same file again after fixing it outside the app.
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!reviewed || !body.trim() || body.length > 20_000) return;
    setPending(true); setError(""); setNotice("");
    try {
      await api(`/workspaces/${workspaceId}/ideas`, {
        method: "POST", body: JSON.stringify({ title: title.trim() || null, body }),
      }, auth.csrf_token);
      setFilename(""); setTitle(""); setBody(""); setReviewed(false);
      setNotice("Markdown imported. Use Extract preferences from new feedback to interpret it.");
      await onImported();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Could not import the document.");
      onAuthError(error);
    } finally { setPending(false); }
  }

  return <form className="panel markdown-import" onSubmit={submit} aria-labelledby="markdown-import-title">
    <h2 id="markdown-import-title">Import a Markdown document</h2>
    <p>Bring an AI-generated idea or project brief. Review the text, then share it as
      your contribution. Other participants’ preferences still need their own review.</p>
    <a href="/templates/idea-template.md" download="feedbackform-idea-template.md">Download Markdown template</a>
    <details className="markdown-format"><summary>Markdown format and AI prompt</summary>
      <p>Use one document per participant. Start with a # title, then ## Context,
        ## Proposed idea, ## Preferences, ## Concerns, ## Personal requirements,
        ## Open questions, and ## Uncertainty. Use short bullet points and keep
        conditions and disagreements explicit. Plain Markdown with other headings also works.</p>
      <p>You can ask your AI: “Fill out the attached FeedbackForm template using only
        my supplied notes. Preserve negation and conditions, leave unknowns explicit,
        and do not invent preferences, team agreement, or approvals. Return a UTF-8 .md file.”</p>
    </details>
    <label htmlFor="markdown-file">Markdown file</label>
    <input id="markdown-file" ref={fileInput} type="file" accept=".md,.markdown,text/markdown,text/plain"
      disabled={pending || reading} onChange={event => void select(event.target.files?.[0])}
      aria-describedby="markdown-limits" />
    <p id="markdown-limits" className="field-help">UTF-8 .md or .markdown; up to 80 KB and 20,000 text characters.
      Selecting a file only opens a preview. Importing saves it to your shared workspace;
      extraction sends its text to OpenAI.</p>
    {reading && <p role="status">Reading Markdown…</p>}
    {filename && <fieldset disabled={pending}>
      <legend>Review {filename}</legend>
      <label htmlFor="markdown-title">Document title</label>
      <input id="markdown-title" maxLength={200} value={title}
        onChange={event => { setTitle(event.target.value); setReviewed(false); }} />
      <label htmlFor="markdown-preview">Markdown preview</label>
      <textarea id="markdown-preview" maxLength={20000} value={body}
        onChange={event => { setBody(event.target.value); setReviewed(false); }} />
      <label className="markdown-confirm"><input type="checkbox" checked={reviewed}
        onChange={event => setReviewed(event.target.checked)} />
        I reviewed this document and am sharing it as my contribution.</label>
      <div className="actions"><button disabled={!reviewed || !body.trim() || pending}>
        {pending ? "Importing…" : "Import reviewed Markdown"}</button>
        <button className="secondary" type="button" disabled={pending} onClick={() => {
          setFilename(""); setBody(""); setTitle(""); setReviewed(false); setError("");
        }}>Cancel import</button></div>
    </fieldset>}
    {error && <p className="error" role="alert">{error}</p>}
    {notice && <p className="notice" role="status">{notice}</p>}
  </form>;
}
