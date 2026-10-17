"use client";

import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import type { components } from "@/lib/api.generated";
import { api } from "@/lib/api";
import Markdown, { selectionSourceOffset } from "./markdown";

type Idea = components["schemas"]["IdeaView"];
type Comment = components["schemas"]["AnnotationView"];
type Span = components["schemas"]["Span"];
type Target = { sourceId: string; sourceVersion: number; sourceBody: string; span: Span | null };

function textareaOffset(source: string, offset: number) {
  // Textareas expose LF line endings even when an immutable source contains CRLF.
  let original = 0;
  for (let position = 0; position < offset && original < source.length; position++) {
    original += source[original] === "\r" && source[original + 1] === "\n" ? 2 : 1;
  }
  return original;
}

function markedText(body: string, ranges: { start_utf16: number; end_utf16: number }[]): ReactNode {
  const merged: { start: number; end: number }[] = [];
  for (const range of [...ranges].sort((a, b) => a.start_utf16 - b.start_utf16)) {
    const last = merged.at(-1);
    if (last && range.start_utf16 <= last.end) last.end = Math.max(last.end, range.end_utf16);
    else merged.push({ start: range.start_utf16, end: range.end_utf16 });
  }
  const pieces: ReactNode[] = [];
  let cursor = 0;
  for (const range of merged) {
    pieces.push(body.slice(cursor, range.start));
    pieces.push(<mark key={range.start}>{body.slice(range.start, range.end)}</mark>);
    cursor = range.end;
  }
  pieces.push(body.slice(cursor));
  return pieces;
}

export default function IdeaDiscussion({ idea, csrf, onAuthError }: {
  idea: Idea; csrf: string; onAuthError: (error: unknown) => void;
}) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [open, setOpen] = useState(false);
  const [keyboard, setKeyboard] = useState(false);
  const [query, setQuery] = useState("");
  const [target, setTarget] = useState<Target | null>(null);
  const [selection, setSelection] = useState<Target | null>(null);
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [pending, setPending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [sourceView, setSourceView] = useState(false);
  const source = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const keyboardSource = useRef<HTMLTextAreaElement>(null);
  const path = `/workspaces/${idea.workspace_id}/ideas/${idea.id}/annotations`;
  const normalizedSource = idea.body.replace(/\r\n?/g, "\n");
  const normalizedQuery = query.replace(/\r\n?/g, "\n");
  const matches: { start: number; end: number }[] = [];
  if (normalizedQuery.trim()) {
    let start = normalizedSource.indexOf(normalizedQuery);
    while (start !== -1 && matches.length < 20) {
      matches.push({ start: textareaOffset(idea.body, start),
        end: textareaOffset(idea.body, start + normalizedQuery.length) });
      start = normalizedSource.indexOf(normalizedQuery, start + 1);
    }
  }

  async function load(offset = 0) {
    setLoading(true);
    try {
      const rows = await api<Comment[]>(`${path}?offset=${offset}`);
      setComments(previous => offset ? [...previous, ...rows] : rows);
      setHasMore(rows.length === 100);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Could not load comments."); onAuthError(error);
    } finally { setLoading(false); }
  }
  useEffect(() => { void load(); setSelection(null); }, [idea.version_id]);
  function selectionTarget(start: number, end: number): Target | null {
    if (start === end) return null;
    // JS selection positions are UTF-16 offsets. Avoid splitting a surrogate pair.
    const quote = idea.body.slice(start, end);
    if (!quote.trim() || /[\uD800-\uDBFF]$/.test(quote) || /^[\uDC00-\uDFFF]/.test(quote)) return null;
    // Context is optional; omitting it avoids cutting a surrogate in a fixed-size context window.
    return { sourceId: idea.version_id, sourceVersion: idea.version, sourceBody: idea.body,
      span: { start_utf16: start, end_utf16: end, quote, prefix: "", suffix: "" } };
  }
  function captureSelection() {
    const range = window.getSelection();
    const root = source.current;
    if (!root || !range || range.rangeCount !== 1 || range.isCollapsed) return;
    const selectedRange = range.getRangeAt(0);
    if (!root.contains(selectedRange.startContainer) || !root.contains(selectedRange.endContainer)) return;
    const start = selectionSourceOffset(root, selectedRange.startContainer, selectedRange.startOffset);
    const end = selectionSourceOffset(root, selectedRange.endContainer, selectedRange.endOffset);
    setSelection(start !== null && end !== null ? selectionTarget(start, end) : null);
  }
  function startComment(next: Target) {
    setTarget(next); setOpen(true); setError(""); setNotice("");
    window.setTimeout(() => composer.current?.focus(), 0);
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!target) return;
    setPending(true); setError(""); setNotice("");
    try {
      await api<Comment>(path, { method: "POST", body: JSON.stringify({
        idea_version_id: target.sourceId, anchor: target.span ? "passage" : "whole_idea",
        span: target.span, body,
      }) }, csrf);
      setBody(""); setTarget(null); setSelection(null); setNotice("Your comment was saved.");
      await load();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Could not save your comment."); onAuthError(error);
    } finally { setPending(false); }
  }
  return <div className="discussion">
    <div className="idea-body" ref={source} onMouseUp={captureSelection} onKeyUp={captureSelection}>
      <Markdown body={idea.body} raw={sourceView} ranges={comments.filter(comment =>
        comment.idea_version_id === idea.version_id && comment.span).map(comment => comment.span!)} />
    </div>
    <div className="actions discussion-actions">
      <button className="text-button" onClick={() => { setSourceView(!sourceView); setSelection(null); }}>
        {sourceView ? "Show formatted Markdown" : "Show Markdown source"}</button>
      <button className="text-button" aria-label="Comments" aria-expanded={open}
        aria-controls={`comments-${idea.id}`} onClick={() => setOpen(!open)}>Comments · {comments.length}{hasMore ? "+" : ""}</button>
      <button className="text-button" onClick={() => startComment({ sourceId: idea.version_id,
        sourceVersion: idea.version, sourceBody: idea.body, span: null })}>Comment on idea</button>
      <button className="text-button" aria-expanded={keyboard} onClick={() => {
        setKeyboard(!keyboard); window.setTimeout(() => keyboardSource.current?.focus(), 0);
      }}>Choose a passage with keyboard</button>
    </div>
    {keyboard && <div className="passage-picker">
      <label htmlFor={`source-${idea.id}`}>Find passage text</label>
      <p id={`instructions-${idea.id}`}>Type or paste the passage. Tab to a matching excerpt and press Enter to comment.</p>
      <textarea id={`source-${idea.id}`} aria-describedby={`instructions-${idea.id}`} ref={keyboardSource}
        value={query} maxLength={20000} onChange={event => setQuery(event.target.value)} />
      {query.trim() && <p role="status">{matches.length ? `${matches.length}${matches.length === 20 ? "+" : ""} matching passages` : "No matching passage. Use the exact text from this idea."}</p>}
      {matches.map((match, index) => <div className="passage-match" key={match.start}>
        <blockquote>{idea.body.slice(Math.max(0, match.start - 35), match.start)}<mark>{idea.body.slice(match.start, match.end)}</mark>{idea.body.slice(match.end, match.end + 35)}</blockquote>
        <button className="secondary" onClick={() => {
          const next = selectionTarget(match.start, match.end);
          if (next) startComment(next);
        }}>Comment on this passage{matches.length > 1 ? ` · match ${index + 1}` : ""}</button>
      </div>)}
    </div>}
    {selection && !keyboard && <div className="selection-preview"><blockquote>{selection.span?.quote}</blockquote>
      <button className="secondary" onClick={() => startComment(selection)}>Comment on selected passage</button></div>}
    <div id={`comments-${idea.id}`} hidden={!open} className="comments-panel">
      <div className="feed-header"><h4>Comments</h4><button className="text-button" onClick={() => void load()}>Refresh comments</button></div>
      {loading && <p role="status">Loading comments…</p>}
      {!loading && comments.length === 0 && <p>No comments yet. What resonates or needs a change?</p>}
      <ol className="comment-list">{comments.map(comment => <li key={comment.id} className="comment">
        <div className="idea-meta"><strong>{comment.author.display_name}</strong>
          <time dateTime={comment.created_at}>{new Date(comment.created_at).toLocaleString()}</time></div>
        <p className="source-label">On version {comment.source_version}{comment.idea_version_id !== idea.version_id ? " · earlier version" : " · current version"}</p>
        {comment.span && <blockquote>{comment.span.quote}</blockquote>}
        <div className="idea-body"><Markdown body={comment.body} /></div>
        <details><summary>View version {comment.source_version} context</summary>
          <p className="idea-body">{markedText(comment.source_body, comment.span ? [comment.span] : [])}</p></details>
      </li>)}</ol>
      {hasMore && <button className="secondary" disabled={loading} onClick={() => void load(comments.length)}>Load more comments</button>}
      {target && <form onSubmit={submit} className="comment-composer">
        <p className="source-label">Commenting on version {target.sourceVersion}{target.sourceId !== idea.version_id ? " · earlier version" : ""}</p>
        {target.span && <blockquote>{target.span.quote}</blockquote>}
        <label htmlFor={`comment-${idea.id}`}>Your comment</label>
        <textarea id={`comment-${idea.id}`} ref={composer} required maxLength={20000} value={body} onChange={event => setBody(event.target.value)} />
        <div className="actions"><button disabled={pending || !body.trim()}>{pending ? "Saving comment…" : "Save comment"}</button>
          <button className="secondary" type="button" disabled={pending} onClick={() => { setTarget(null); setError(""); }}>Cancel comment</button></div>
      </form>}
      {notice && <p className="notice" role="status">{notice}</p>}
    </div>
    {error && <p className="error" role="alert">{error}</p>}
  </div>;
}
