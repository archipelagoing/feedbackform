"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import type { components } from "@/lib/api.generated";
import { api, ApiError } from "@/lib/api";

type Auth = components["schemas"]["AuthView"];
type Member = { login_name: string; display_name: string; password: string; confirmation: string };

export default function SetupForm({ onComplete, onAlreadySetup }: {
  onComplete: (auth: Auth) => Promise<void>; onAlreadySetup: () => void;
}) {
  const [step, setStep] = useState(0);
  const [title, setTitle] = useState("Our project");
  const [goal, setGoal] = useState("");
  const [members, setMembers] = useState<Member[]>(() => Array.from({ length: 4 }, () => ({
    login_name: "", display_name: "", password: "", confirmation: "",
  })));
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [step]);
  const member = members[step - 1];
  function update(field: keyof Member, value: string) {
    setMembers(previous => previous.map((row, index) => index === step - 1 ? { ...row, [field]: value } : row));
  }
  async function submit(event: FormEvent) {
    event.preventDefault(); setError("");
    if (step === 0 && (!title.trim() || !goal.trim())) {
      setError("Enter a workspace name and the question your team wants to answer."); return;
    }
    if (step > 0) {
      if (!member.display_name.trim()) { setError("Enter this participant’s display name."); return; }
      if (member.password !== member.confirmation) { setError("The passwords do not match."); return; }
      if (members.some((row, index) => index !== step - 1 && row.login_name && row.login_name === member.login_name)) {
        setError("Each participant needs a different login name."); return;
      }
    }
    if (step < 4) { setStep(step + 1); return; }
    setPending(true);
    try {
      const payload: components["schemas"]["PilotSetup"] = {
        title: title.trim(), goal: goal.trim(),
        members: members.map(({ login_name, display_name, password }) => ({ login_name, display_name: display_name.trim(), password })),
      };
      const auth = await api<Auth>("/setup", { method: "POST", body: JSON.stringify(payload) });
      // Credentials stay in memory only and are discarded once the setup is saved.
      setMembers(previous => previous.map(row => ({ ...row, password: "", confirmation: "" })));
      await onComplete(auth);
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        // Setup may have completed in another tab, or its response may have been lost.
        // Reloading state will show sign-in rather than offering to replace accounts.
        setError(error.message);
      } else setError(error instanceof Error ? error.message : "Could not create the workspace. Try again.");
    } finally { setPending(false); }
  }
  return <section className="setup">
    <p className="eyebrow">Welcome to FeedbackForm · Step {step + 1} of 5</p>
    <h1 tabIndex={-1} ref={heading}>{step === 0 ? "Create your team’s workspace." : `Set up participant ${step}.`}</h1>
    <p className="intro">{step === 0 ? "Start with the question you want to answer together. Then add four participant logins." :
      step === 1 ? "This participant will own the workspace. You’ll be signed in as them when setup is complete." : "Each person gets their own login to keep ideas and feedback attributed correctly."}</p>
    <form className="panel setup-form" onSubmit={submit}>
      <fieldset disabled={pending} key={step}>
        <legend className="sr-only">{step === 0 ? "Workspace details" : `Participant ${step} details`}</legend>
        {step === 0 ? <>
          <label htmlFor="setup-title">Workspace name</label>
          <input id="setup-title" required maxLength={200} value={title} onChange={e => setTitle(e.target.value)} />
          <label htmlFor="setup-goal">Decision question</label>
          <textarea id="setup-goal" required maxLength={20000} placeholder="What will our final project be?" value={goal} onChange={e => setGoal(e.target.value)} />
        </> : <>
          <label htmlFor="setup-display">Display name</label>
          <input id="setup-display" required maxLength={120} autoComplete="off" value={member.display_name} onChange={e => update("display_name", e.target.value)} />
          <label htmlFor="setup-login">Login name</label>
          <input id="setup-login" required pattern="[a-z0-9_.\-]+" maxLength={120} autoComplete="off"
            aria-describedby="login-help" value={member.login_name} onChange={e => update("login_name", e.target.value)} />
          <p id="login-help" className="field-help">Use lowercase letters, numbers, periods, underscores, or hyphens.</p>
          <label htmlFor="setup-password">Password</label>
          <input id="setup-password" type="password" required minLength={12} maxLength={256} autoComplete="new-password"
            aria-describedby="password-help" value={member.password} onChange={e => update("password", e.target.value)} />
          <p id="password-help" className="field-help">Use 12–256 characters.</p>
          <label htmlFor="setup-confirm">Confirm password</label>
          <input id="setup-confirm" type="password" required minLength={12} maxLength={256} autoComplete="new-password"
            value={member.confirmation} onChange={e => update("confirmation", e.target.value)} />
        </>}
      </fieldset>
      {step === 4 && <p className="setup-summary">Creating <strong>{title}</strong> for {members.map(row => row.display_name || "Participant 4").join(", ")}.</p>}
      {error && <p role="alert" className="error">{error}</p>}
      <div className="actions">
        {step > 0 && <button className="secondary" type="button" disabled={pending} onClick={() => { setStep(step - 1); setError(""); }}>Back</button>}
        <button disabled={pending}>{pending ? "Creating workspace…" : step < 4 ? "Continue" : "Create workspace"}</button>
      </div>
      {error && <button className="text-button" type="button" disabled={pending} onClick={onAlreadySetup}>Check setup status</button>}
    </form>
  </section>;
}
