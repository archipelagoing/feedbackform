"use client";

import { useEffect, useState } from "react";
import type { components } from "@/lib/api.generated";
import { api } from "@/lib/api";

type Board = components["schemas"]["PreferenceBoard"];
type Preference = components["schemas"]["PreferenceView"];
type Auth = components["schemas"]["AuthView"];
type Run = components["schemas"]["ExtractionRunView"];
type Correction = components["schemas"]["PreferenceCorrection"];

const runErrors: Record<string, string> = {
  stale_inputs: "The discussion changed during extraction. Run it again to use the latest input.",
  provider_auth: "OpenAI rejected the connection. Ask the app operator to check it.",
  provider_rate_limit: "OpenAI is at its usage limit. Try again later.",
  provider_timeout: "OpenAI took too long. You can retry.",
  provider_refused: "OpenAI declined this extraction. No interpretations were saved.",
  interrupted: "The app restarted during extraction. You can retry.",
};

function PreferenceCard({ preference, path, auth, onRefresh, onAuthError }: {
  preference: Preference; path: string; auth: Auth; onRefresh: () => Promise<void>;
  onAuthError: (error: unknown) => void;
}) {
  const [statement, setStatement] = useState(preference.statement);
  const [kind, setKind] = useState<Correction["kind"]>(preference.kind as Correction["kind"]);
  const [strength, setStrength] = useState<NonNullable<Correction["strength"]> | "">(
    preference.strength as NonNullable<Correction["strength"]> ?? "");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<Preference[] | null>(null);
  const own = preference.participant.id === auth.user.id;
  const changed = statement !== preference.statement || kind !== preference.kind;
  async function review(action: Correction["action"]) {
    setPending(true); setError("");
    try {
      await api<Preference>(`${path}/${preference.id}`, {
        method: "PATCH", body: JSON.stringify({ expected_revision_id: preference.revision_id,
          statement: action === "withdraw" ? preference.statement : statement,
          kind: action === "withdraw" ? preference.kind : kind,
          strength: strength || null, action }),
      }, auth.csrf_token);
      await onRefresh();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Could not save your review.");
      onAuthError(error);
    } finally { setPending(false); }
  }
  async function showHistory() {
    if (history) { setHistory(null); return; }
    try { setHistory(await api<Preference[]>(`${path}/${preference.id}/history`)); }
    catch (error) {
      setError(error instanceof Error ? error.message : "Could not load history."); onAuthError(error);
    }
  }
  return <article className="preference-card">
    <p className="preference-meta"><strong>{preference.participant.display_name}</strong>
      <span>{preference.status} · {preference.kind.replaceAll("_", " ")}</span></p>
    <p className="idea-body">{preference.statement}</p>
    {preference.strength && <p>Personal priority: {preference.strength.replaceAll("_", " ")}</p>}
    {preference.uncertainty_note && <p className="muted">AI uncertainty: {preference.uncertainty_note}</p>}
    <details><summary>Inspect original evidence</summary>
      {preference.sources.map(source => <div className="preference-evidence" key={source.version_id}>
        <p><strong>{source.kind === "annotation" ? "Original comment" : "Original idea"}</strong>
          {source.historical && " · historical source version"}</p>
        {source.quote && <blockquote>{source.quote}</blockquote>}
        <p className="idea-body">{source.text}</p>
      </div>)}
    </details>
    {own && preference.status !== "withdrawn" && <fieldset disabled={pending}>
      <legend>Your interpretation to review</legend>
      <label>What you mean<textarea maxLength={2000} value={statement}
        onChange={event => setStatement(event.target.value)} /></label>
      <div className="preference-fields"><label>Type<select value={kind}
        onChange={event => setKind(event.target.value as Correction["kind"])}>
        {["desire", "concern", "constraint", "question", "suggestion"].map(value =>
          <option key={value} value={value}>{value}</option>)}
      </select></label><label>Personal priority<select value={strength}
        onChange={event => setStrength(event.target.value as typeof strength)}>
        <option value="">Unspecified</option><option value="nice_to_have">Nice to have</option>
        <option value="important">Important</option><option value="essential">Essential</option>
      </select></label></div>
      <div className="actions">
        <button disabled={changed || !statement.trim()} onClick={() => void review("confirm")}>Confirm interpretation</button>
        <button className="secondary" disabled={!statement.trim() || !changed}
          onClick={() => void review("correct")}>Save correction</button>
        <button className="text-button" onClick={() => void review("withdraw")}>Withdraw interpretation</button>
      </div>
    </fieldset>}
    <button className="text-button" onClick={() => void showHistory()}>
      {history ? "Hide interpretation history" : "View interpretation history"}</button>
    {history && <ol className="history">{history.map(revision => <li key={revision.revision_id}>
      Version {revision.version} · {revision.status} · {revision.kind}<p>{revision.statement}</p>
    </li>)}</ol>}
    {error && <p role="alert" className="error">{error}</p>}
  </article>;
}

export function PreferenceBoard({ workspaceId, auth, onAuthError }: {
  workspaceId: string; auth: Auth; onAuthError: (error: unknown) => void;
}) {
  const [board, setBoard] = useState<Board | null>(null);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const [requestKey, setRequestKey] = useState<string | null>(null);
  const path = `/workspaces/${workspaceId}/preferences`;
  const running = board?.latest_run?.status === "queued" || board?.latest_run?.status === "running";
  async function refresh() {
    try { setBoard(await api<Board>(path)); setError(""); }
    catch (error) {
      setError(error instanceof Error ? error.message : "Could not load interpretations."); onAuthError(error);
    }
  }
  useEffect(() => { void refresh(); }, [workspaceId]);
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => { void refresh(); }, 1500);
    return () => clearInterval(timer);
  }, [running, workspaceId]);
  async function extract() {
    setPending(true); setError("");
    const key = requestKey ?? crypto.randomUUID(); setRequestKey(key);
    try {
      const run = await api<Run>(`/workspaces/${workspaceId}/preference-extractions`, {
        method: "POST", body: JSON.stringify({ request_key: key }),
      }, auth.csrf_token);
      setRequestKey(null);
      setBoard(previous => previous ? { ...previous, latest_run: run } : previous);
      await refresh();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Could not start extraction."); onAuthError(error);
      // A new key is needed after an explicit server rejection; a lost response
      // keeps its key so a retry can recover the already accepted run.
      if (error instanceof Error && "status" in error) setRequestKey(null);
    } finally { setPending(false); }
  }
  return <section className="panel preference-board" aria-labelledby="preferences-title">
    <div className="feed-header"><h2 id="preferences-title">Understand everyone’s priorities</h2>
      <button className="text-button" onClick={() => void refresh()}>Refresh interpretations</button></div>
    <p>AI interpretations are drafts. Review your own wording and inspect the evidence.
      Confirming a personal requirement does not make it a binding team constraint.</p>
    <p className="muted">Extraction sends the decision question, ideas, comments and existing
      interpretations to OpenAI. Original feedback stays unchanged.</p>
    {!board && !error && <p role="status">Loading interpretations…</p>}
    {board && !board.configured && <p role="status">OpenAI connection needed. The app operator must
      connect OpenAI before extraction is available.</p>}
    <button disabled={!board?.configured || running || pending} onClick={() => void extract()}>
      {running || pending ? "Interpreting discussion…" : "Extract preferences from new feedback"}</button>
    {board?.latest_run?.status === "failed" && <p className="error" role="alert">
      {runErrors[board.latest_run.error_code ?? ""] ?? "Extraction failed validation or could not finish. No interpretations from this run were saved. You can retry."}</p>}
    {board?.latest_run?.status === "succeeded" && <p role="status">Extraction completed. Interpretations await each participant’s review.</p>}
    {board?.preferences.length === 0 && <p>No interpretations yet. Share ideas or comments, then run extraction.</p>}
    <div className="preference-list">{board?.preferences.map(preference =>
      <PreferenceCard key={preference.revision_id} preference={preference} path={path}
        auth={auth} onRefresh={refresh} onAuthError={onAuthError} />)}</div>
    {error && <p className="error" role="alert">{error}</p>}
  </section>;
}
