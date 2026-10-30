import { useState, useEffect, useRef } from "react";
import { postFile, postJson, getJson, postForm } from "./api.js";

/* ---------- shared bits ---------- */
function useJob() {
  const [state, set] = useState({ loading: false, error: "", data: null });
  const run = async (fn) => {
    set({ loading: true, error: "", data: null });
    try { set({ loading: false, error: "", data: await fn() }); }
    catch (e) { set({ loading: false, error: e.message, data: null }); }
  };
  return [state, run];
}

function Status({ s, label }) {
  if (s.loading) return <p className="status" role="status">{label}</p>;
  if (s.error) return <p className="error" role="alert">{s.error}</p>;
  return null;
}

function Upload({ accept, kind, onSubmit, busy, cta }) {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  useEffect(() => {
    if (!file) return setUrl("");
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);
  return (
    <div className="upload">
      <label className="drop">
        <input type="file" accept={accept} onChange={(e) => setFile(e.target.files[0] || null)} />
        {url ? (
          kind === "video" ? <video src={url} controls /> : <img src={url} alt="Selected upload" />
        ) : (
          <span>Choose {kind === "video" ? "a kitchen video" : "a photo"} or drop it here</span>
        )}
      </label>
      <button className="primary" disabled={!file || busy} onClick={() => onSubmit(file)}>{cta}</button>
    </div>
  );
}

const Score = ({ value, label }) => (
  <div className="score" style={{ "--p": Math.max(0, Math.min(100, value)) }}>
    <b>{Math.round(value)}</b><span>{label}</span>
  </div>
);

const Disclaimer = ({ text }) => text ? <p className="fine">{text}</p> : null;

const List = ({ title, items }) =>
  items?.length ? (<><h4>{title}</h4><ul>{items.map((x, i) => <li key={i}>{x}</li>)}</ul></>) : null;

/* ---------- 1. meal scan ---------- */
export function FoodScan() {
  const [s, run] = useJob();
  const d = s.data;
  return (
    <>
      <Upload accept="image/*" kind="image" busy={s.loading} cta="Analyze meal"
              onSubmit={(f) => run(() => postFile("/api/food/analyze", f))} />
      <Status s={s} label="Reading your plate..." />
      {d && (
        <section className="result">
          <div className="row">
            <div><h3>{d.dish}</h3><p className="muted">Confidence: {d.confidence}</p></div>
            <Score value={d.health_score} label="health" />
          </div>
          <div className="macros">
            {[["Calories", d.totals.calories, "kcal"], ["Protein", d.totals.protein_g, "g"],
              ["Carbs", d.totals.carbs_g, "g"], ["Fat", d.totals.fat_g, "g"]].map(([k, v, u]) => (
              <div key={k}><b>{Math.round(v)}</b><span>{u}</span><small>{k}</small></div>
            ))}
          </div>
          <table>
            <thead><tr><th>Item</th><th>Portion</th><th>kcal</th><th>P</th><th>C</th><th>F</th></tr></thead>
            <tbody>{d.items.map((i, k) => (
              <tr key={k}><td>{i.name}</td><td>{i.portion}</td><td>{i.calories}</td>
                <td>{i.protein_g}</td><td>{i.carbs_g}</td><td>{i.fat_g}</td></tr>))}</tbody>
          </table>
          {d.image_quality?.map((w, i) => <p key={i} className="warn">{w}</p>)}
          {d.score_breakdown?.macro_split_pct && (
            <p className="muted">Macro split: protein {d.score_breakdown.macro_split_pct.protein}%,
              carbs {d.score_breakdown.macro_split_pct.carbs}%, fat {d.score_breakdown.macro_split_pct.fat}%.
              {d.reference_checked_items > 0 && ` ${d.reference_checked_items} item(s) checked against reference values.`}</p>)}
          {d.score_breakdown?.notes?.length > 0 && <p><b>Watch:</b> {d.score_breakdown.notes.join(". ")}.</p>}
          <p>{d.health_notes}</p>
          <p className="muted">Saved to your meal log, so your meal plan can use it.</p>
          <Disclaimer text={d.disclaimer} />
        </section>
      )}
    </>
  );
}

/* ---------- 2. freshness ---------- */
export function Freshness() {
  const [s, run] = useJob();
  const d = s.data;
  const tone = d?.status === "Fresh" ? "good" : d?.status === "Spoiled" ? "bad" : "warning";
  return (
    <>
      <Upload accept="image/*" kind="image" busy={s.loading} cta="Check freshness"
              onSubmit={(f) => run(() => postFile("/api/freshness/check", f))} />
      <Status s={s} label="Inspecting color and texture..." />
      {d && (
        <section className="result">
          <div className="row">
            <div><h3>{d.food}</h3><span className={`pill ${tone}`}>{d.status}</span></div>
            <Score value={d.freshness_score} label="fresh" />
          </div>
          <ul className="signals">{d.indicators.map((i, k) => (
            <li key={k} className={i.severity}><b>{i.signal}</b> {i.observation}</li>))}</ul>
          {d.quality_warnings?.map((w, i) => <p key={i} className="warn">{w}</p>)}
          {d.cautions?.map((w, i) => <p key={i} className="warn">{w}</p>)}
          <p className="muted">Confidence {d.confidence_pct}%. Safe to eat: {d.safe_to_eat ? "yes" : "no"}.</p>
          <p><b>Safety:</b> {d.safety_recommendation}</p>
          {d.features && <p className="muted">Measured: brown/dark {Math.round(d.features.brown_dark_ratio * 100)}%,
            green {Math.round(d.features.green_ratio * 100)}%, pale patches {Math.round(d.features.pale_patch_ratio * 100)}%,
            texture sharpness {d.features.texture_sharpness}.</p>}
          <p><b>What to do:</b> {d.recommendation}</p>
          <p><b>Storage:</b> {d.storage_tip}</p>
          <Disclaimer text={d.disclaimer} />
        </section>
      )}
    </>
  );
}

/* ---------- 3. hygiene ---------- */
export function Hygiene() {
  const [s, run] = useJob();
  const d = s.data;
  return (
    <>
      <Upload accept="video/*" kind="video" busy={s.loading} cta="Run hygiene audit"
              onSubmit={(f) => run(() => postFile("/api/hygiene/analyze", f))} />
      <Status s={s} label="Sampling frames and auditing. This can take a minute..." />
      {d && (
        <section className="result">
          <div className="row">
            <div><h3>Audit result</h3>
              <span className={`pill ${d.risk_level === "low" ? "good" : d.risk_level === "high" ? "bad" : "warning"}`}>
                {d.risk_level} risk</span>
              <p className="muted">{d.frames_analyzed} frames analyzed</p></div>
            <Score value={d.overall_score} label="hygiene" />
          </div>
          <table>
            <thead><tr><th>Check</th><th>Status</th><th>Evidence</th></tr></thead>
            <tbody>{d.checks.map((c, k) => (
              <tr key={k}><td>{c.item}</td>
                <td><span className={`pill ${c.status === "pass" ? "good" : c.status === "fail" ? "bad" : "warning"}`}>{c.status}</span></td>
                <td>{c.evidence}</td></tr>))}</tbody>
          </table>
          {d.insufficient_evidence && <p className="warn">Many checks could not be confirmed from the video. Film hands, head and work surfaces clearly.</p>}
          {d.alerts?.length > 0 && <div className="alert"><List title="Alerts" items={d.alerts} /></div>}
          <List title="Violations" items={d.violations?.map((v) => `Frame ${v.frame}: ${v.description}`)} />
          <List title="Recommendations" items={d.recommendations} />
          <Disclaimer text={d.disclaimer} />
        </section>
      )}
    </>
  );
}

/* ---------- 4. cooking ---------- */
export function Cooking() {
  const [s, run] = useJob();
  const [f, setF] = useState({ query: "", servings: 2, dietary: "", skill: "beginner", question: "" });
  const up = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const d = s.data;
  return (
    <>
      <div className="form">
        <label className="wide">Dish or ingredients
          <input value={f.query} onChange={up("query")} placeholder="Palak paneer, or: eggs, spinach, rice" /></label>
        <label>Servings<input type="number" min="1" value={f.servings} onChange={up("servings")} /></label>
        <label>Skill
          <select value={f.skill} onChange={up("skill")}>
            <option>beginner</option><option>intermediate</option><option>advanced</option></select></label>
        <label className="wide">Dietary needs<input value={f.dietary} onChange={up("dietary")} placeholder="vegetarian, no garlic" /></label>
        <label className="wide">Something going wrong? (optional)
          <input value={f.question} onChange={up("question")} placeholder="My gravy is too thick" /></label>
        <button className="primary" disabled={!f.query || s.loading}
                onClick={() => run(() => postJson("/api/cooking/recipe", { ...f, servings: +f.servings }))}>
          Get recipe</button>
      </div>
      <h4 style={{ marginTop: "1.5rem" }}>Or start from a photo of your ingredients</h4>
      <Upload accept="image/*" kind="image" busy={s.loading} cta="Recipe from photo"
              onSubmit={(file) => run(() => postForm("/api/cooking/from-image",
                { servings: f.servings, dietary: f.dietary, skill: f.skill }, file))} />
      <Status s={s} label="Writing your recipe..." />
      {d && (
        <section className="result">
          <h3>{d.title}</h3>
          <p className="muted">{d.servings} servings, {d.prep_minutes} min prep, {d.cook_minutes} min cook</p>
          {d.detected_ingredients?.length > 0 && <p><b>Detected:</b> {d.detected_ingredients.join(", ")}</p>}
          <h4>Ingredients</h4>
          <ul className="cols">{d.ingredients.map((i, k) => <li key={k}><b>{i.quantity}</b> {i.item}</li>)}</ul>
          <h4>Method</h4>
          <ol className="steps">{d.steps.map((st, k) => (
            <li key={k}>{st.step}
              {st.tip && <em className="tip">Tip: {st.tip}</em>}
              {st.timer_minutes ? <span className="pill warning">{st.timer_minutes} min</span> : null}</li>))}</ol>
          <List title="Substitutions" items={d.substitutions} />
          <List title="Safety" items={d.safety_notes} />
        </section>
      )}
    </>
  );
}

/* ---------- 5. meal plan ---------- */
export function MealPlan() {
  const [s, run] = useJob();
  const [p, setP] = useState({ age: 25, sex: "female", height_cm: 165, weight_kg: 60, activity: "moderate",
                               goal: "maintain", diet: "vegetarian", allergies: "", dislikes: "", days: 3, use_history: false });
  const up = (k) => (e) => setP({ ...p, [k]: e.target.value });
  const d = s.data;
  const num = ["age", "height_cm", "weight_kg", "days"];
  return (
    <>
      <div className="form">
        <label>Age<input type="number" value={p.age} onChange={up("age")} /></label>
        <label>Sex<select value={p.sex} onChange={up("sex")}><option>female</option><option>male</option></select></label>
        <label>Height (cm)<input type="number" value={p.height_cm} onChange={up("height_cm")} /></label>
        <label>Weight (kg)<input type="number" value={p.weight_kg} onChange={up("weight_kg")} /></label>
        <label>Activity<select value={p.activity} onChange={up("activity")}>
          <option>sedentary</option><option>light</option><option>moderate</option><option>active</option></select></label>
        <label>Goal<select value={p.goal} onChange={up("goal")}>
          <option value="lose">lose weight</option><option>maintain</option><option value="gain">gain weight</option></select></label>
        <label>Diet<input value={p.diet} onChange={up("diet")} /></label>
        <label>Days<input type="number" min="1" max="7" value={p.days} onChange={up("days")} /></label>
        <label className="wide">Allergies<input value={p.allergies} onChange={up("allergies")} /></label>
        <label className="wide">Dislikes<input value={p.dislikes} onChange={up("dislikes")} /></label>
        <label className="wide check">
          <input type="checkbox" checked={p.use_history} onChange={(e) => setP({ ...p, use_history: e.target.checked })} />
          Adjust the plan using the meals I scanned this week</label>
        <button className="primary" disabled={s.loading}
                onClick={() => run(() => postJson("/api/mealplan/generate",
                  Object.fromEntries(Object.entries(p).map(([k, v]) => [k, num.includes(k) ? +v : v]))))}>
          Build my plan</button>
      </div>
      <Status s={s} label="Planning your meals..." />
      {d && (
        <section className="result">
          <div className="macros">
            {[["Calories", d.daily_targets.calories, "kcal"], ["Protein", d.daily_targets.protein_g, "g"],
              ["Carbs", d.daily_targets.carbs_g, "g"], ["Fat", d.daily_targets.fat_g, "g"]].map(([k, v, u]) => (
              <div key={k}><b>{Math.round(v)}</b><span>{u}</span><small>daily {k.toLowerCase()}</small></div>))}
          </div>
          {d.energy_estimate && <p className="muted">Estimated resting energy {d.energy_estimate.bmr} kcal, daily use {d.energy_estimate.tdee} kcal.</p>}
          {d.allergen_warnings?.length > 0 && <div className="alert"><b>Check these against your allergies:</b>
            <ul>{d.allergen_warnings.map((w, i) => <li key={i}>{w.allergen}: {w.found_in}</li>)}</ul></div>}
          {d.weekly_summary && <p>{d.weekly_summary}</p>}
          {d.days.map((day, i) => (
            <details key={i} open={i === 0} className="day">
              <summary>{day.day} <span className="muted">{Math.round(day.total_calories)} kcal</span></summary>
              {day.meals.map((m, k) => (
                <p key={k}><b>{m.type}: {m.name}</b> <span className="muted">{m.calories} kcal, {m.protein_g} g protein</span><br />{m.description}{m.why && <em className="tip">Why: {m.why}</em>}
                {m.alternatives?.length > 0 && <em className="tip">Swap: {m.alternatives.map((a) => `${a.name} (${a.calories} kcal)`).join(" or ")}</em>}</p>))}
            </details>))}
          <List title="Grocery list" items={d.grocery_list} />
          <List title="Notes" items={d.notes} />
          <Disclaimer text={d.disclaimer} />
        </section>
      )}
    </>
  );
}

/* ---------- 6. kitchen assistant ---------- */
export function Kitchen() {
  const [ctx, setCtx] = useState("");
  const [msg, setMsg] = useState("");
  const [photo, setPhoto] = useState(null);
  const [turns, setTurns] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const [recording, setRecording] = useState(false);
  const recRef = useRef(null);
  const toggleMic = async () => {
    if (recording) { recRef.current.stop(); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const chunks = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setRecording(false);
        try {
          const r = await postFile("/api/audio/transcribe", new File(chunks, "voice.webm", { type: rec.mimeType || "audio/webm" }));
          setMsg((m) => (m ? m + " " : "") + r.text);
        } catch (e) { setErr(e.message); }
      };
      recRef.current = rec; rec.start(); setRecording(true);
    } catch { setErr("Microphone not available. Allow access in your browser."); }
  };

  const send = async () => {
    const text = msg.trim();
    if (!text) return;
    setBusy(true); setErr("");
    const history = turns.map((t) => ({ role: t.role, text: t.text }));
    setTurns((t) => [...t, { role: "user", text, photo: !!photo }]);
    setMsg("");
    try {
      const r = await postForm("/api/kitchen/assist",
        { message: text, history: JSON.stringify(history), recipe_context: ctx }, photo);
      setTurns((t) => [...t, { role: "assistant", text: r.reply, next: r.next_action,
                               timer: r.timer_minutes, safety: r.safety_flag ? r.safety_note : "" }]);
      setPhoto(null);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  return (
    <>
      <div className="form">
        <label className="wide">What are you cooking? (optional)
          <input value={ctx} onChange={(e) => setCtx(e.target.value)} placeholder="Chicken curry, step 4: simmering" /></label>
      </div>
      <div className="chat" aria-live="polite">
        {turns.length === 0 && <p className="muted">Ask anything mid-cook. Attach a photo of the pan and I will judge color, texture and doneness.</p>}
        {turns.map((t, i) => (
          <div key={i} className={`bubble ${t.role}`}>
            <p>{t.text}{t.photo && " (photo attached)"}</p>
            {t.next && <p><b>Next:</b> {t.next}</p>}
            {t.timer ? <span className="pill warning">Set a {t.timer} min timer</span> : null}
            {t.safety && <p className="error">Safety: {t.safety}</p>}
          </div>
        ))}
      </div>
      {err && <p className="error" role="alert">{err}</p>}
      <div className="composer">
        <input value={msg} onChange={(e) => setMsg(e.target.value)} placeholder="Is the onion browned enough?"
               onKeyDown={(e) => e.key === "Enter" && !busy && send()} />
        <label className="attach">{photo ? photo.name : "Add photo"}
          <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files[0] || null)} /></label>
        <button className="attach" onClick={toggleMic} aria-pressed={recording}>{recording ? "Stop recording" : "Speak"}</button>
        <button className="primary" disabled={busy || !msg.trim()} onClick={send}>{busy ? "Thinking..." : "Send"}</button>
      </div>
    </>
  );
}

/* ---------- 7. dashboard ---------- */
export function Dashboard() {
  const [s, setS] = useState(null);
  const [meals, setMeals] = useState([]);
  const [err, setErr] = useState("");
  useEffect(() => {
    Promise.all([getJson("/api/history/summary"), getJson("/api/history/meals")])
      .then(([a, b]) => { setS(a); setMeals(b); }).catch((e) => setErr(e.message));
  }, []);
  if (err) return <p className="error" role="alert">{err}</p>;
  if (!s) return <p className="status">Loading...</p>;
  if (!s.meal_count) return <p className="muted">No meals yet. Scan a meal and it will show up here.</p>;
  return (
    <section className="result">
      <div className="macros">
        {[["Meals", s.meal_count, ""], ["Calories", s.total_calories, "kcal"], ["Protein", s.total_protein_g, "g"],
          ["Avg health", s.avg_health_score ?? "-", "/100"]].map(([k, v, u]) => (
          <div key={k}><b>{typeof v === "number" ? Math.round(v) : v}</b><span>{u}</span><small>{k}, last 7 days</small></div>))}
      </div>
      <table>
        <thead><tr><th>When</th><th>Dish</th><th>kcal</th><th>Protein</th><th>Health</th></tr></thead>
        <tbody>{meals.map((m) => (
          <tr key={m.id}><td>{m.ts}</td><td>{m.dish}</td><td>{Math.round(m.calories)}</td>
            <td>{Math.round(m.protein_g)} g</td><td>{m.health_score}</td></tr>))}</tbody>
      </table>
    </section>
  );
}
