"use client";

import { FormEvent, useEffect, useState } from "react";
import type { components } from "@/lib/api.generated";
import { api, ApiError } from "@/lib/api";

type Auth = components["schemas"]["AuthView"];
type Workspace = components["schemas"]["WorkspaceView"];
type Idea = components["schemas"]["IdeaView"];
type History = components["schemas"]["IdeaHistoryView"];

function message(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong. Try again.";
}

function Login({ onLogin }: { onLogin: (auth: Auth) => Promise<void> }) {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault(); setPending(true); setError("");
    try {
      const auth = await api<Auth>("/auth/login", {
        method: "POST", body: JSON.stringify({ login_name: login, password }),
      });
      setPassword(""); await onLogin(auth);
    } catch (error) { setError(message(error)); }
    finally { setPending(false); }
  }
  return <form className="login panel" onSubmit={submit}>
    <h2>Welcome to your workspace</h2>
    <p>Sign in with the participant account your team set up.</p>
    <label htmlFor="login-name">Login name</label>
    <input id="login-name" autoComplete="username" required maxLength={120} value={login}
      onChange={event => setLogin(event.target.value)} />
    <label htmlFor="password">Password</label>
    <input id="password" type="password" autoComplete="current-password" required minLength={12}
      maxLength={256} value={password} onChange={event => setPassword(event.target.value)} />
    {error && <p className="error" role="alert">{error}</p>}
    <button disabled={pending}>{pending ? "Signing in…" : "Sign in"}</button>
  </form>;
}

function IdeaCard({ idea, own, csrf, onRefresh, onAuthError }: {
  idea: Idea; own: boolean; csrf: string; onRefresh: () => Promise<void>;
  onAuthError: (error: unknown) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(idea.title ?? "");
  const [body, setBody] = useState(idea.body);
  const [baseVersion, setBaseVersion] = useState(idea.version_id);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<History[] | null>(null);
  async function save(event: FormEvent) {
    event.preventDefault(); setPending(true); setError("");
    try {
      await api<Idea>(`/workspaces/${idea.workspace_id}/ideas/${idea.id}`, {
        method: "PATCH", body: JSON.stringify({ title: title.trim() || null, body,
          expected_version_id: baseVersion }),
      }, csrf);
      setEditing(false); setHistory(null); await onRefresh();
    } catch (error) { setError(message(error)); onAuthError(error); }
    finally { setPending(false); }
  }
  async function showHistory() {
    setPending(true); setError("");
    try {
      setHistory(await api<History[]>(`/workspaces/${idea.workspace_id}/ideas/${idea.id}/history`));
    } catch (error) { setError(message(error)); onAuthError(error); }
    finally { setPending(false); }
  }
  return <article className="idea panel" data-idea-id={idea.id}>
    <div className="idea-meta"><span>{idea.author.display_name}</span><span>Version {idea.version}</span></div>
    {editing ? <form onSubmit={save}>
      <label htmlFor={`title-${idea.id}`}>Edit title <span className="optional">(optional)</span></label>
      <input id={`title-${idea.id}`} maxLength={200} value={title} onChange={e => setTitle(e.target.value)} />
      <label htmlFor={`body-${idea.id}`}>Edit idea</label>
      <textarea id={`body-${idea.id}`} required maxLength={20000} value={body}
        onChange={e => setBody(e.target.value)} />
      <div className="actions"><button disabled={pending || !body.trim()}>Save new version</button>
        <button className="secondary" type="button" disabled={pending} onClick={() => {
          setEditing(false); setError(""); void onRefresh();
        }}>Cancel edit</button></div>
    </form> : <>
      {idea.title && <h3>{idea.title}</h3>}
      <p className="idea-body">{idea.body}</p>
      <div className="actions">
        {own && <button className="secondary" disabled={pending} onClick={() => {
          setTitle(idea.title ?? ""); setBody(idea.body); setBaseVersion(idea.version_id);
          setError(""); setEditing(true);
        }}>Edit idea</button>}
        <button className="text-button" disabled={pending} onClick={() => {
          if (history) setHistory(null); else void showHistory();
        }}>{history ? "Hide history" : "View history"}</button>
      </div>
    </>}
    {error && <p className="error" role="alert">{error}</p>}
    {history && <div className="history"><h4>Version history</h4>{history.map(version =>
      <div key={version.version_id}><strong>Version {version.version}{version.title ? ` · ${version.title}` : ""}</strong>
        <p className="idea-body">{version.body}</p></div>)}</div>}
  </article>;
}

function WorkspacePanel({ workspace, auth, onAuthError }: {
  workspace: Workspace; auth: Auth; onAuthError: (error: unknown) => void;
}) {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [pending, setPending] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const path = `/workspaces/${workspace.id}/ideas`;
  async function refresh() {
    setError("");
    try {
      const rows = await api<Idea[]>(path);
      setIdeas(rows); setHasMore(rows.length === 100);
    } catch (error) { setError(message(error)); onAuthError(error); }
    finally { setLoading(false); }
  }
  useEffect(() => { void refresh(); }, [workspace.id]);
  async function submit(event: FormEvent) {
    event.preventDefault(); setPending(true); setError(""); setNotice("");
    try {
      await api<Idea>(path, { method: "POST", body: JSON.stringify({ title: title.trim() || null, body }) }, auth.csrf_token);
      setTitle(""); setBody(""); setNotice("Your idea was saved."); await refresh();
    } catch (error) { setError(message(error)); onAuthError(error); }
    finally { setPending(false); }
  }
  async function more() {
    setLoading(true); setError("");
    try {
      const rows = await api<Idea[]>(`${path}?offset=${ideas.length}`);
      setIdeas(previous => [...previous, ...rows]); setHasMore(rows.length === 100);
    } catch (error) { setError(message(error)); onAuthError(error); }
    finally { setLoading(false); }
  }
  return <section className="workspace">
    <p className="eyebrow">Your team’s shared space</p><h1>{workspace.title}</h1>
    <p className="intro">{workspace.goal}</p>
    <ul className="members" aria-label="Workspace participants">{workspace.members.map(member =>
      <li key={member.user.id}>{member.user.display_name}{member.role === "owner" && <span> · owner</span>}</li>)}</ul>
    <div className="workspace-grid"><div>
      <div className="feed-header"><h2>Shared ideas</h2><button className="text-button" onClick={() => void refresh()}>Refresh ideas</button></div>
      {loading && <p role="status">Loading ideas…</p>}
      {!loading && ideas.length === 0 && <div className="empty panel"><h3>Start with a thought.</h3><p>A sentence is enough. Share a possibility, a question, or something you want to explore.</p></div>}
      <div className="idea-list">{ideas.map(idea => <IdeaCard key={idea.id} idea={idea}
        own={idea.author.id === auth.user.id} csrf={auth.csrf_token} onRefresh={refresh} onAuthError={onAuthError} />)}</div>
      {hasMore && <button className="secondary" disabled={loading} onClick={() => void more()}>Load more ideas</button>}
    </div><aside><form className="composer panel" onSubmit={submit}>
      <h2>Share an idea</h2><p>Rough thoughts are welcome.</p>
      <label htmlFor="idea-title">Title <span className="optional">(optional)</span></label>
      <input id="idea-title" maxLength={200} value={title} onChange={e => setTitle(e.target.value)} />
      <label htmlFor="idea-body">Your idea</label>
      <textarea id="idea-body" placeholder="What should we explore?" required maxLength={20000}
        value={body} onChange={e => setBody(e.target.value)} />
      <button disabled={pending || !body.trim()}>{pending ? "Saving…" : "Share idea"}</button>
      {notice && <p className="notice" role="status">{notice}</p>}
    </form></aside></div>
    {error && <p className="error" role="alert">{error}</p>}
  </section>;
}

export default function Home() {
  const [auth, setAuth] = useState<Auth | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selected, setSelected] = useState("");
  const [state, setState] = useState<"boot" | "ready" | "unavailable">("boot");
  const [error, setError] = useState("");
  async function enter(auth: Auth) {
    const rows = await api<Workspace[]>("/workspaces");
    setWorkspaces(rows); setSelected(rows[0]?.id ?? ""); setAuth(auth); setState("ready"); setError("");
  }
  async function boot() {
    setState("boot");
    try {
      await api("/health");
      try { await enter(await api<Auth>("/auth/me")); }
      catch (error) { if (!(error instanceof ApiError && error.status === 401)) throw error; }
      setState("ready");
    } catch { setState("unavailable"); }
  }
  useEffect(() => { void boot(); }, []);
  function authError(error: unknown) {
    if (error instanceof ApiError && error.status === 401) {
      setAuth(null); setWorkspaces([]); setError("Your session expired. Sign in again to continue.");
    }
  }
  async function logout() {
    if (!auth) return;
    try {
      await api<void>("/auth/logout", { method: "POST" }, auth.csrf_token);
      setAuth(null); setWorkspaces([]); setError("");
    } catch (error) { setError(message(error)); authError(error); }
  }
  const workspace = workspaces.find(row => row.id === selected);
  return <main>
    <header><span className="mark" aria-hidden="true">ff</span><span>FeedbackForm</span>
      {auth ? <div className="account"><span>{auth.user.display_name}</span><button className="secondary" onClick={() => void logout()}>Sign out</button></div>
        : <span className="tag">Team pilot</span>}</header>
    {error && <p className="error" role="alert">{error}</p>}
    {state === "boot" && <p className="connection" role="status">Opening your workspace…</p>}
    {state === "unavailable" && <section className="welcome"><h1>Your workspace is taking a moment.</h1>
      <p role="status">Connection unavailable. Try again shortly or ask your team owner for help.</p>
      <button onClick={() => void boot()}>Try again</button></section>}
    {state === "ready" && !auth && <section className="welcome">
      <div><p className="eyebrow">A place for shared thinking</p>
        <h1>From scattered thoughts<br />to shared direction.</h1>
        <p className="intro">Capture what matters. Explore the trade-offs. Develop a proposal your whole team can stand behind.</p>
        <p className="connection" role="status"><span className="dot ready" aria-hidden="true" />Connected</p>
      </div><Login onLogin={enter} /></section>}
    {state === "ready" && auth && <>
      {workspaces.length > 1 && <label className="workspace-picker">Workspace<select value={selected} onChange={event => setSelected(event.target.value)}>
        {workspaces.map(row => <option key={row.id} value={row.id}>{row.title}</option>)}</select></label>}
      {workspace ? <WorkspacePanel key={`${auth.user.id}-${workspace.id}`} workspace={workspace} auth={auth} onAuthError={authError} />
        : <section><h1>No workspace assigned yet.</h1><p>Ask your team owner to check the pilot setup.</p></section>}
    </>}
    <footer>Ideas → Feedback → Alternatives → Shared decisions</footer>
  </main>;
}
