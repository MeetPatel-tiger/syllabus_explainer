import React, { useRef, useState } from "react";

export default function App() {
  const fileInput = useRef(null);
  const [fileName, setFileName] = useState("");
  const [rawText, setRawText] = useState("");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const API_BASE = "http://127.0.0.1:5000";

  const pickFile = () => fileInput.current?.click();

  const readError = async (res) => {
    const clone = res.clone();
    try {
      const j = await clone.json();
      return j?.error || JSON.stringify(j);
    } catch {
      const t = await res.text().catch(() => "");
      return t || `HTTP ${res.status}`;
    }
  };

  const upload = async (file) => {
    if (!file) return;
    setErr("");
    setRawText("");
    setSummary(null);
    setFileName(file.name);
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API_BASE}/extract`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) throw new Error(await readError(res));

      const data = await res.json();
      const extractedText = (data.text || data.raw_text || "").trim();
      setRawText(extractedText);
      
      // Show success message
      if (extractedText) {
        setErr(`✓ Extracted ${data.characters_found || extractedText.length} characters. Click "Summarize" to analyze.`);
      }
    } catch (e) {
      setErr(e.message || "Upload failed");
    } finally {
      setLoading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  const onChange = (e) => upload(e.target.files?.[0]);

  const summarize = async () => {
    if (!rawText.trim()) return;
    setLoading(true);
    setErr("");
    setSummary(null);
    try {
      const res = await fetch(`${API_BASE}/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rawText }),
      });

      if (!res.ok) throw new Error(await readError(res));

      const data = await res.json();
      setSummary(data.summary);
    } catch (e) {
      setErr(e.message || "Summarize failed");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setErr("");
    setRawText("");
    setSummary(null);
    setFileName("");
    if (fileInput.current) fileInput.current.value = "";
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: 24 
    }}>
      <div style={{ 
        maxWidth: 900, 
        margin: "0 auto",
        background: "white",
        borderRadius: 15,
        padding: 40,
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
      }}>
        <h1 style={{ 
          textAlign: "center", 
          fontSize: 40, 
          margin: "12px 0",
          color: "#667eea"
        }}>
          📚 Syllabus Explainer
        </h1>
        <p style={{ 
          textAlign: "center", 
          margin: "0 0 30px", 
          color: "#666",
          fontSize: 18
        }}>
          Upload a syllabus file (PNG/JPG/PDF), then click Summarize to extract key information
        </p>

        <div style={{
          border: "3px dashed #667eea",
          borderRadius: 12,
          padding: 24,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 16,
          background: "#f8f9ff",
          marginBottom: 20
        }}>
          <div style={{ fontSize: 48 }}>📄</div>
          
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
            <button
              onClick={pickFile}
              style={{ 
                padding: "12px 24px", 
                borderRadius: 25, 
                border: "none",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                color: "white",
                cursor: "pointer",
                fontWeight: "bold",
                fontSize: 16
              }}
            >
              Choose File
            </button>

            <input
              ref={fileInput}
              type="file"
              accept=".png,.jpg,.jpeg,.pdf"
              onChange={onChange}
              style={{ display: "none" }}
            />

            <button
              onClick={summarize}
              disabled={!rawText || loading}
              style={{
                padding: "12px 24px",
                borderRadius: 25,
                border: "none",
                background: rawText && !loading ? "#10b981" : "#d1d5db",
                color: "#fff",
                cursor: !rawText || loading ? "not-allowed" : "pointer",
                fontWeight: "bold",
                fontSize: 16
              }}
            >
              {loading ? "⏳ Analyzing..." : "✨ Summarize"}
            </button>

            <button
              onClick={reset}
              style={{ 
                padding: "12px 24px", 
                borderRadius: 25, 
                border: "2px solid #667eea",
                background: "white",
                color: "#667eea",
                cursor: "pointer",
                fontWeight: "bold",
                fontSize: 16
              }}
            >
              🔄 Reset
            </button>
          </div>

          <span style={{ color: "#666", fontSize: 14, fontWeight: 500 }}>
            {fileName || "No file selected"}
          </span>
        </div>

        {err && (
          <div style={{ 
            color: err.startsWith("✓") ? "#10b981" : "#dc2626", 
            marginBottom: 20,
            padding: 12,
            background: err.startsWith("✓") ? "#d1fae5" : "#fee2e2",
            borderRadius: 8,
            border: `2px solid ${err.startsWith("✓") ? "#10b981" : "#dc2626"}`
          }}>
            {err}
          </div>
        )}

        {summary && (
          <div style={{ marginTop: 20 }}>
            <h2 style={{ color: "#667eea", marginBottom: 20, fontSize: 28 }}>
              📋 Summary
            </h2>

            {summary.course && (
              <Section title="📖 Course Information" content={summary.course} />
            )}

            {summary.term && (
              <Section title="📅 Term" content={summary.term} />
            )}

            {summary.meeting_time && (
              <Section title="🕐 Meeting Time" content={summary.meeting_time} />
            )}

            {summary.room && (
              <Section title="🏫 Room" content={summary.room} />
            )}

            {summary.instructor && (
              <Section title="👨‍🏫 Instructor" content={summary.instructor} />
            )}

            {summary.email && (
              <Section title="📧 Email" content={summary.email} />
            )}

            {summary.office && (
              <Section title="🚪 Office" content={summary.office} />
            )}

            {summary.office_hours && (
              <Section title="⏰ Office Hours" content={summary.office_hours} />
            )}

            {summary.grading_weights && summary.grading_weights.length > 0 && (
              <div style={sectionStyle}>
                <h3 style={titleStyle}>📊 Grading Breakdown</h3>
                <div style={contentStyle}>
                  {summary.grading_weights.map((item, idx) => (
                    <div key={idx} style={{ 
                      display: "flex", 
                      justifyContent: "space-between",
                      padding: "8px 0",
                      borderBottom: idx < summary.grading_weights.length - 1 ? "1px solid #e5e7eb" : "none"
                    }}>
                      <span>{item.component}</span>
                      <span style={{ fontWeight: "bold", color: "#667eea" }}>
                        {item.weight_percent}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {summary.attendance_policy && (
              <Section title="✅ Attendance Policy" content={summary.attendance_policy} />
            )}

            {summary.important_dates && summary.important_dates.length > 0 && (
              <div style={sectionStyle}>
                <h3 style={titleStyle}>📅 Important Dates</h3>
                <div style={contentStyle}>
                  {summary.important_dates.slice(0, 10).map((date, idx) => (
                    <div key={idx} style={{ 
                      padding: "6px 0",
                      borderLeft: "3px solid #667eea",
                      paddingLeft: 12,
                      marginBottom: 8,
                      background: "#f8f9ff"
                    }}>
                      {date}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!summary && rawText && (
          <div style={{
            marginTop: 20,
            padding: 20,
            background: "#f9fafb",
            borderRadius: 8,
            border: "1px solid #e5e7eb"
          }}>
            <h3 style={{ marginBottom: 10, color: "#667eea" }}>Raw Extracted Text (Preview)</h3>
            <div style={{ 
              maxHeight: 200, 
              overflow: "auto",
              whiteSpace: "pre-wrap",
              fontSize: 14,
              color: "#666"
            }}>
              {rawText.substring(0, 1000)}...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper component for sections
function Section({ title, content }) {
  if (!content) return null;
  return (
    <div style={sectionStyle}>
      <h3 style={titleStyle}>{title}</h3>
      <div style={contentStyle}>{content}</div>
    </div>
  );
}

const sectionStyle = {
  background: "#f8f9ff",
  padding: 20,
  marginBottom: 16,
  borderRadius: 10,
  borderLeft: "4px solid #667eea"
};

const titleStyle = {
  color: "#667eea",
  marginBottom: 10,
  fontSize: 18
};

const contentStyle = {
  color: "#333",
  lineHeight: 1.6,
  whiteSpace: "pre-wrap"
};
