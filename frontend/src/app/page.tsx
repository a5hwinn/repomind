import Chat from "@/components/Chat";

const projects = [
  {name: "Agentic Fraud Detection", text: "Agentic fraud analysis combining machine learning, memory and reasoning.", url: "https://github.com/a5hwinn/agentic-fraud-detection"},
  {name: "Diabetic Retinopathy Research", text: "Uncertainty-aware deep learning for stage classification and risk progression.", url: "#"},
  {name: "AIGovernor", text: "An enterprise AI security control plane concept for visibility and governance.", url: "#"},
];

export default function Home() {
  return <main>
    <header className="container" style={{padding: "28px 0", display: "flex", justifyContent: "space-between"}}><strong>AA.</strong><nav style={{display: "flex", gap: 20}}><a href="#projects">Projects</a><a href="#ask">Ask AI</a><a href="https://github.com/a5hwinn" target="_blank" rel="noreferrer">GitHub ↗</a></nav></header>
    <section className="container" style={{padding: "100px 0 80px"}}>
      <div className="muted" style={{letterSpacing: 2, fontSize: 13}}>AI / ML ENGINEER · DEVELOPER</div>
      <h1 style={{fontSize: "clamp(54px, 9vw, 105px)", lineHeight: .95, letterSpacing: -5, margin: "18px 0"}}>Ashwin<br/>Abhilash.</h1>
      <p className="muted" style={{fontSize: 21, maxWidth: 650, lineHeight: 1.6}}>Building intelligent systems across machine learning, computer vision, generative AI and developer tooling.</p>
      <div style={{display: "flex", gap: 12, marginTop: 30}}><a href="#ask" style={{padding: "13px 18px", borderRadius: 10, background: "white", color: "black", textDecoration: "none", fontWeight: 700}}>Ask my GitHub</a><a href="https://github.com/a5hwinn" target="_blank" rel="noreferrer" style={{padding: "13px 18px", borderRadius: 10, border: "1px solid #333", textDecoration: "none"}}>View GitHub</a></div>
    </section>
    <section id="projects" className="container" style={{padding: "50px 0"}}><div className="muted" style={{letterSpacing: 2, fontSize: 13}}>SELECTED WORK</div><h2 style={{fontSize: 40}}>Projects</h2><div style={{display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 14}}>{projects.map(p => <a key={p.name} href={p.url} target={p.url.startsWith("http") ? "_blank" : undefined} rel="noreferrer" className="card" style={{padding: 22, textDecoration: "none"}}><h3>{p.name}</h3><p className="muted" style={{lineHeight: 1.6}}>{p.text}</p><span className="muted">Explore ↗</span></a>)}</div></section>
    <Chat />
    <footer className="container" style={{padding: "40px 0 70px", borderTop: "1px solid #222"}}><span className="muted">RepoMind · AI-aware developer portfolio</span></footer>
  </main>;
}
