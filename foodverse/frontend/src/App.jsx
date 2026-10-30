import { useState } from "react";
import { FoodScan, Freshness, Hygiene, Cooking, Kitchen, MealPlan, Dashboard } from "./panels.jsx";

const TABS = [
  { id: "scan", label: "Meal scan", hint: "Photo to calories and macros", C: FoodScan },
  { id: "fresh", label: "Freshness", hint: "Is it still good to eat?", C: Freshness },
  { id: "hygiene", label: "Kitchen hygiene", hint: "Audit a kitchen video", C: Hygiene },
  { id: "cook", label: "Recipes", hint: "Ingredients and steps", C: Cooking },
  { id: "kitchen", label: "Kitchen assistant", hint: "Live help while you cook", C: Kitchen },
  { id: "plan", label: "Meal plan", hint: "Days built around your goal", C: MealPlan },
  { id: "dash", label: "My week", hint: "Everything you have scanned", C: Dashboard },
];

export default function App() {
  const [tab, setTab] = useState("scan");
  const active = TABS.find((t) => t.id === tab);
  const Panel = active.C;
  return (
    <div className="shell">
      <aside className="rail">
        <h1 className="brand">Food Verse<span> AI</span></h1>
        <nav aria-label="Features">
          {TABS.map((t) => (
            <button key={t.id} className={t.id === tab ? "nav on" : "nav"} onClick={() => setTab(t.id)}>
              <strong>{t.label}</strong>
              <small>{t.hint}</small>
            </button>
          ))}
        </nav>
      </aside>
      <main className="stage">
        <header className="stage-head">
          <h2>{active.label}</h2>
          <p>{active.hint}</p>
        </header>
        <Panel key={tab} />
      </main>
    </div>
  );
}
