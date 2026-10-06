"use client";

import { useState } from "react";

type Source = {
  repository: string;
  url: string;
  type: string;
};

const API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const suggestions = [
  "What projects demonstrate my AI experience?",
  "What has Ashwin worked on recently?",
  "Which projects use machine learning?",
  "Explain the fraud detection project.",
];

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);

  const ask = async (q: string = question) => {
    if (!q.trim() || loading) return;

    setQuestion(q);
    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: q,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Request failed");
      }

      setAnswer(data.answer || "");
      setSources(data.sources || []);
    } catch (error) {
      setAnswer(
        error instanceof Error
          ? error.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      id="ask"
      className="container"
      style={{ padding: "70px 0" }}
    >
      <div className="card" style={{ padding: 28 }}>
        <div
          style={{
            fontSize: 13,
            letterSpacing: 2,
            color: "#999",
          }}
        >
          REPO-MIND AI
        </div>

        <h2 style={{ fontSize: 38, margin: "10px 0" }}>
          Ask my GitHub.
        </h2>

        <p className="muted">
          Ask about projects, technologies and development history.
          Answers are grounded in indexed GitHub data.
        </p>

        <div
          style={{
            display: "flex",
            gap: 10,
            marginTop: 22,
          }}
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                ask();
              }
            }}
            placeholder="What projects demonstrate my AI experience?"
            style={{
              flex: 1,
              padding: 15,
              borderRadius: 12,
              border: "1px solid #333",
              background: "#080808",
              color: "white",
              outline: "none",
            }}
          />

          <button
            onClick={() => ask()}
            disabled={loading}
            style={{
              padding: "0 20px",
              borderRadius: 12,
              border: 0,
              background: "white",
              color: "black",
              fontWeight: 700,
            }}
          >
            {loading ? "Thinking…" : "Ask"}
          </button>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            marginTop: 14,
          }}
        >
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => ask(suggestion)}
              style={{
                padding: "9px 12px",
                borderRadius: 999,
                border: "1px solid #2b2b2b",
                background: "#151515",
                color: "#ccc",
                cursor: "pointer",
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>

        {answer && (
          <div
            style={{
              marginTop: 28,
              borderTop: "1px solid #242424",
              paddingTop: 25,
            }}
          >
            <h3>RepoMind</h3>

            <p
              style={{
                lineHeight: 1.75,
                whiteSpace: "pre-wrap",
                color: "#ddd",
              }}
            >
              {answer}
            </p>

            {sources.length > 0 && (
              <div style={{ marginTop: 20 }}>
                <div
                  className="muted"
                  style={{
                    fontSize: 13,
                    marginBottom: 8,
                  }}
                >
                  SOURCES
                </div>

                {sources.map((source, index) => (
                  <a
                    key={`${source.url}-${index}`}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: "block",
                      padding: "9px 0",
                      color: "#fff",
                    }}
                  >
                    ↗ {source.repository}{" "}
                    <span className="muted">
                      · {source.type}
                    </span>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}