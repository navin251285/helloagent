import { useEffect, useMemo, useRef, useState } from "react";

const DEFAULT_WS_PATH = "/mcp";
const DEFAULT_API_BASE = "";

const formatTime = (timestamp) => {
  if (!timestamp) return "-";
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

const shortJson = (value) => {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return String(value);
  }
};

export default function App() {
  const [wsPath, setWsPath] = useState(DEFAULT_WS_PATH);
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE);
  const [wsStatus, setWsStatus] = useState("disconnected");
  const [tools, setTools] = useState([]);
  const [messages, setMessages] = useState([]);
  const [stats, setStats] = useState(null);
  const [traffic, setTraffic] = useState([]);
  const [streamText, setStreamText] = useState("");
  const [streamActive, setStreamActive] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const [savedStatus, setSavedStatus] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);
  const [updatedRecord, setUpdatedRecord] = useState(null);
  const [diseaseKeyword, setDiseaseKeyword] = useState("diabetes");
  const [patientId, setPatientId] = useState("25");
  const [summaryDraft, setSummaryDraft] = useState("");
  const [customMethod, setCustomMethod] = useState("tools/list");
  const [customParams, setCustomParams] = useState("{}");
  const [apiError, setApiError] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [searchResults, setSearchResults] = useState([]);
  const [rawSearchText, setRawSearchText] = useState("");
  const [lastSearchResponse, setLastSearchResponse] = useState(null);
  const socketRef = useRef(null);
  const requestIdRef = useRef(0);
  const requestMapRef = useRef(new Map());
  const requestMetaRef = useRef(new Map());
  const lastMethodRef = useRef("");
  const lastToolRef = useRef("");
  const streamTextRef = useRef("");
  const patientIdRef = useRef("");
  const setUpdatedRecordRef = useRef(null);

  const wsUrl = useMemo(() => {
    // In development, use the proxy - construct URL based on current page location
    // This works whether accessed via localhost or network IP
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host; // includes port
    return `${protocol}//${host}${wsPath}`;
  }, [wsPath]);

  const apiUrl = useMemo(() => {
    if (!apiBase) return "";
    return apiBase.endsWith("/") ? apiBase.slice(0, -1) : apiBase;
  }, [apiBase]);

  const apiFetch = async (path) => {
    const target = apiUrl || "";
    const response = await fetch(`${target}${path}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  };

  const pushTraffic = (entry) => {
    setTraffic((prev) => [entry, ...prev].slice(0, 120));
  };

  const connectWebSocket = () => {
    if (socketRef.current) {
      socketRef.current.close();
    }

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;
    setWsStatus("connecting");

    socket.onopen = () => {
      console.log("[WS] ✓✓✓ WebSocket CONNECTED to:", wsUrl);
      setWsStatus("connected");
      pushTraffic({
        direction: "system",
        label: "connected",
        time: Date.now(),
        payload: wsUrl
      });
      console.log("[WS] Sending initialize request...");
      sendRequest("initialize", {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "ui-observer", version: "1.0.0" }
      });
      setTimeout(() => {
        console.log("[WS] Requesting tools list...");
        requestTools();
      }, 200);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data?.type === "stream_token") {
          setStreamActive(true);
          setIsGenerating(false);
          setStreamText((prev) => prev + (data.token || ""));
          return;
        }
        // Set streamActive to false when receiving non-stream messages
        if (streamActive) {
          setStreamActive(false);
        }
        setLastResponse(data);
        if (data?.result?.tools) {
          setTools(data.result.tools);
        }
        
        // Get the method for this response ID
        const requestMeta = data?.id ? requestMetaRef.current.get(data.id) : null;
        const responseMethod = requestMeta?.method || lastMethodRef.current;
        const responseTool = requestMeta?.toolName || null;
        console.log("[WS] 📨 RESPONSE ID:", data?.id, "| Method:", responseMethod, "| Tool:", responseTool);
        console.log("[WS] Full data object:", data);
        
        // Parse search results if this is a search response
        if (responseTool === "search_patients_by_disease") {
                    setLastSearchResponse(data);
          console.log("[WS] 🔍 SEARCH RESPONSE detected");
          console.log("[WS] data.result:", data?.result);
          console.log("[WS] data.result.content:", data?.result?.content);
          
          if (data?.result?.content && data.result.content.length > 0) {
            const content = data.result.content[0]?.text || "";
            console.log("[WS] ✓ Content available, length:", content.length);
            console.log("[WS] Content preview:", content.substring(0, 200));
            console.log("[WS] 🔧 Setting rawSearchText state...");
            setRawSearchText(content);
            
            console.log("[WS] 🔧 Calling parseSearchResults...");
            const patients = parseSearchResults(content);
            console.log("[WS] 🔧 Got", patients.length, "patients from parser:", patients);
            console.log("[WS] 🔧 Setting searchResults state...");
            setSearchResults(patients);
            console.log("[WS] ✓✓✓ Search response FULLY processed");
          } else {
            console.log("[WS] ✗✗✗ NO CONTENT in result!");
            console.log("[WS] Result object:", JSON.stringify(data?.result, null, 2));
          }
        } else {
          console.log("[WS] Not a search response, method was:", responseMethod, "tool:", responseTool);
        }
        
        // Check if this is a generate_summary response (streaming complete)
        if (responseTool === "generate_summary" && data?.result) {
          console.log("[WS] ✓ Generate summary completed");
          setStreamActive(false);
          setIsUpdating(true);
        }
        
        // Check if update was successful - match both by tool name and by checking if we're updating
        if (responseTool === "update_patient_summary" || lastToolRef.current === "update_patient_summary") {
          console.log("[WS] 💾 SAVE RESPONSE detected");
          console.log("[WS] responseTool:", responseTool);
          console.log("[WS] lastToolRef:", lastToolRef.current);
          console.log("[WS] Update response:", JSON.stringify(data, null, 2));
          console.log("[WS] Current streamText length:", streamTextRef.current?.length);
          console.log("[WS] Current patientId:", patientIdRef.current);
          
          setIsUpdating(false);
          
          // Set the updated record with current state values from refs
          if (streamTextRef.current && patientIdRef.current) {
            const record = {
              patientId: patientIdRef.current,
              summary: streamTextRef.current,
              timestamp: new Date().toLocaleString()
            };
            setUpdatedRecord(record);
            console.log("[WS] 📝 Updated record SET successfully:", { patientId: record.patientId, summaryLength: record.summary.length });
          } else {
            console.log("[WS] ⚠️ Cannot set record - streamText:", !!streamTextRef.current, "patientId:", patientIdRef.current);
          }
          
          setSavedStatus("✓ Summary saved successfully!");
          setTimeout(() => setSavedStatus(""), 5000);
        }
        
        pushTraffic({
          direction: "in",
          label: requestMapRef.current.get(data?.id) || data?.id || "response",
          time: Date.now(),
          payload: data
        });
      } catch (error) {
        console.error("[WS] 💥 Error parsing message:", error);
        pushTraffic({
          direction: "in",
          label: "non-json",
          time: Date.now(),
          payload: event.data
        });
      }
    };

    socket.onerror = () => {
      setWsStatus("error");
    };

    socket.onclose = () => {
      setWsStatus("disconnected");
      pushTraffic({
        direction: "system",
        label: "closed",
        time: Date.now(),
        payload: "connection closed"
      });
    };
  };

  const sendRequest = (method, params = {}) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error("[WS] ✗ Cannot send - WebSocket not connected. State:", socketRef.current?.readyState);
      pushTraffic({
        direction: "system",
        label: "not-connected",
        time: Date.now(),
        payload: method
      });
      return;
    }
    requestIdRef.current += 1;
    const message = {
      jsonrpc: "2.0",
      id: requestIdRef.current,
      method,
      params
    };
    const toolName = method === "tools/call" ? params?.name : null;
    requestMapRef.current.set(requestIdRef.current, toolName || method);
    requestMetaRef.current.set(requestIdRef.current, {
      method,
      toolName
    });
    lastMethodRef.current = method;
    console.log("[WS] 📤 SENDING REQUEST:", message);
    console.log("[WS] Request ID:", requestIdRef.current, "mapped to method:", method);
    socketRef.current.send(JSON.stringify(message));
    pushTraffic({
      direction: "out",
      label: method,
      time: Date.now(),
      payload: message
    });
  };

  const requestTools = () => {
    sendRequest("tools/list");
  };

  const callTool = (name, argumentsPayload) => {
    console.log("[TOOL] 🔧 Calling tool:", name, "with args:", argumentsPayload);
    lastToolRef.current = name;
    
    // Only clear streamText when generating a new summary
    if (name === "generate_summary") {
      setStreamText("");
      setStreamActive(false);
      setIsGenerating(true);
      setUpdatedRecord(null);
    }
    
    sendRequest("tools/call", { name, arguments: argumentsPayload });
  };

  const handleCustomSend = () => {
    let parsed = {};
    try {
      parsed = customParams.trim() ? JSON.parse(customParams) : {};
    } catch (error) {
      pushTraffic({
        direction: "system",
        label: "invalid-json",
        time: Date.now(),
        payload: error.message
      });
      return;
    }
    sendRequest(customMethod, parsed);
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const [recent, statistics] = await Promise.all([
          apiFetch("/api/messages/recent?count=80"),
          apiFetch("/api/stats")
        ]);
        setMessages(recent?.messages || []);
        setStats(statistics?.statistics || null);
        setApiError("");
      } catch (error) {
        setApiError("API unavailable. Check server or proxy.");
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [apiUrl]);

  useEffect(() => {
    streamTextRef.current = streamText;
  }, [streamText]);

  useEffect(() => {
    patientIdRef.current = patientId;
  }, [patientId]);

  useEffect(() => {
    setUpdatedRecordRef.current = setUpdatedRecord;
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [wsUrl]);

  useEffect(() => {
    // Auto-save summary when streaming is done and we have text and a selected patient
    if (!streamActive && streamText && patientId && lastToolRef.current === "generate_summary") {
      console.log("[AUTO-SAVE] 💾 Triggering auto-save for patient:", patientId);
      setTimeout(() => {
        setSavedStatus("Saving summary...");
        console.log("[AUTO-SAVE] Calling update_patient_summary...");
        callTool("update_patient_summary", {
          patient_id: patientId,
          summary: streamText
        });
      }, 500);
    }
  }, [streamActive, streamText, patientId]);

  // DEBUG: Log when searchResults changes
  useEffect(() => {
    console.log("[STATE] searchResults changed:", searchResults.length, searchResults);
  }, [searchResults]);

  // DEBUG: Log when rawSearchText changes
  useEffect(() => {
    console.log("[STATE] rawSearchText changed:", rawSearchText.length, "chars");
  }, [rawSearchText]);

  const filteredMessages = useMemo(() => {
    if (activeFilter === "all") return messages;
    return messages.filter(
      (msg) => msg.message_type === activeFilter || msg.source === activeFilter
    );
  }, [messages, activeFilter]);

  const parseSearchResults = (text) => {
    console.log("[PARSE] ===== START PARSE =====");
    console.log("[PARSE] Input text length:", text.length);
    const patients = [];
    const lines = text.split("\n");
    console.log("[PARSE] Total lines:", lines.length);
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) {
        console.log(`[PARSE] Line ${i}: EMPTY`);
        continue;
      }
      
      // Try to match the format: "1. ID: 11  | Name: Jerry Rivera  | Age: ..."
      const match = line.match(/^\s*\d+\.\s+ID:\s*(\d+)\s*\|\s*Name:\s*([^|]+)/);
      
      if (match) {
        const id = match[1].trim();
        const name = match[2].trim();
        console.log(`[PARSE] Line ${i}: ✓ MATCHED - ID=${id}, Name=${name}`);
        if (id && name) {
          patients.push({ id, name });
        }
      } else {
        console.log(`[PARSE] Line ${i}: ✗ NO MATCH - "${line.substring(0, 60)}..."`);
      }
    }
    
    console.log("[PARSE] ===== COMPLETE =====");
    console.log("[PARSE] Found", patients.length, "patients:", patients);
    return patients;
  };

  return (
    <div className="app">
      <header className="top-bar">
        <div>
          <p className="kicker">MCP WebSocket Observatory</p>
          <h1>Live LLM + Tooling Command Center</h1>
          <p className="subtitle">
            Trace user intent, tool calls, streaming tokens, and event timing in
            one view.
          </p>
        </div>
        <div className="status-stack">
          <div className={`chip ${wsStatus}`}>
            WebSocket: {wsStatus}
          </div>
          <div className="chip">WS: {wsUrl}</div>
          <div className="chip">API: {apiUrl || "proxy"}</div>
          {apiError ? <div className="chip error">{apiError}</div> : null}
        </div>
      </header>

      <section className="grid">
        <div className="panel command">
          <div className="panel-header">
            <h2>Patient Summary Generator</h2>
            <div className="panel-actions">
              <button className="ghost" onClick={connectWebSocket}>
                Reconnect
              </button>
            </div>
          </div>

          {/* STEP 1: SEARCH */}
          <div className="workflow-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Search by Disease</h3>
              <label className="field">
                Disease or Symptom
                <input
                  value={diseaseKeyword}
                  onChange={(event) => setDiseaseKeyword(event.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      console.log("[UI] 🔍 SEARCH button pressed");
                      setSearchResults([]);
                      setRawSearchText("");
                      callTool("search_patients_by_disease", {
                        disease_keyword: diseaseKeyword
                      });
                    }
                  }}
                  placeholder="e.g., diabetes, fever, hypertension"
                />
              </label>
              <button
                className="primary"
                onClick={() => {
                  console.log("[UI] 🔍 SEARCH button clicked - diseaseKeyword:", diseaseKeyword);
                                    setLastSearchResponse(null);
                  setSearchResults([]);
                  setRawSearchText("");
                  callTool("search_patients_by_disease", {
                    disease_keyword: diseaseKeyword
                  });
                }}
              >
                Search Patients
              </button>
              
              {/* DEBUG PANEL */}
              <div style={{
                marginTop: "12px",
                padding: "10px",
                background: "#f9f3ed",
                borderRadius: "8px",
                fontSize: "11px",
                fontFamily: "monospace",
                border: "1px solid #e8d5c4"
              }}>
                <div style={{ fontWeight: "bold", marginBottom: "6px", color: "#5a4f4b" }}>🐛 Debug Info:</div>
                <div>WebSocket: <strong>{wsStatus}</strong></div>
                <div>rawSearchText length: <strong>{rawSearchText.length}</strong> chars</div>
                <div>searchResults count: <strong>{searchResults.length}</strong> patients</div>
                <div>patientId: <strong>{patientId || "(empty)"}</strong></div>
                <div>streamText length: <strong>{streamText.length}</strong> chars</div>
                                <div>lastSearchResponse: <strong>{lastSearchResponse ? "YES" : "NO"}</strong></div>
                <button 
                  style={{
                    marginTop: "8px",
                    padding: "4px 8px",
                    fontSize: "10px",
                    background: "#0c6b5a",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer"
                  }}
                  onClick={() => {
                    console.log("=== MANUAL STATE DUMP ===");
                    console.log("rawSearchText:", rawSearchText);
                    console.log("searchResults:", searchResults);
                    console.log("patientId:", patientId);
                    console.log("streamText:", streamText);
                    console.log("wsStatus:", wsStatus);
                    console.log("lastResponse:", lastResponse);
                  }}
                >
                  📋 Dump State to Console
                                <button 
                                  style={{
                                    marginTop: "4px",
                                    padding: "4px 8px",
                                    fontSize: "10px",
                                    background: "#c9681f",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer"
                                  }}
                                  onClick={() => {
                                    console.log("=== LAST SEARCH RESPONSE ===");
                                    console.log(lastSearchResponse);
                                    if (lastSearchResponse?.result?.content) {
                                      const text = lastSearchResponse.result.content[0]?.text || "";
                                      console.log("Content text:", text);
                                      alert("Search response received! Check console. Length: " + text.length);
                                    } else {
                                      alert("No search response received yet!");
                                    }
                                  }}
                                >
                                  🔍 Show Last Search Response
                                </button>
                </button>
              </div>
            </div>
          </div>

          {/* STEP 2: SELECT PATIENT - ALWAYS VISIBLE */}
          <div className="workflow-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Select Patient</h3>
              
              {/* DIAGNOSTIC INFO */}
              <div style={{
                padding: "8px",
                background: "#fff1e0",
                borderRadius: "6px",
                fontSize: "11px",
                marginBottom: "10px",
                fontFamily: "monospace"
              }}>
                <div>🔍 lastSearchResponse: {lastSearchResponse ? "✓ Received" : "✗ None"}</div>
                <div>📝 rawSearchText: {rawSearchText.length} chars</div>
                <div>👥 searchResults: {searchResults.length} patients</div>
              </div>

              {!rawSearchText && (
                <p className="step-meta" style={{ color: "#945419" }}>
                  ⏳ No search performed yet. Click "Search Patients" in Step 1.
                </p>
              )}
              
              {rawSearchText && searchResults.length === 0 && (
                <div>
                  <p className="step-meta" style={{ color: "#8c2b2b" }}>
                    ⚠️ Failed to parse results. Use manual entry below.
                  </p>
                  <pre className="results-text" style={{ fontSize: "11px", maxHeight: "150px" }}>
                    {rawSearchText}
                  </pre>
                </div>
              )}
              
              {searchResults.length > 0 && (
                <div>
                  <p className="step-meta" style={{ color: "#1b5b4c" }}>
                    ✓ Found {searchResults.length} patients - Click to select:
                  </p>
                  <div className="patients-grid">
                    {searchResults.map((patient) => (
                      <button
                        key={patient.id}
                        className={`patient-card ${patientId === patient.id ? "active" : ""}`}
                        onClick={() => {
                          console.log("[UI] 👤 Selected patient:", patient.id, patient.name);
                          setPatientId(patient.id);
                          setStreamText("");
                          callTool("get_patient_summary", {
                            patient_id: patient.id
                          });
                        }}
                      >
                        <div className="patient-id">ID: {patient.id}</div>
                        <div className="patient-name">{patient.name}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* ALWAYS SHOW MANUAL ENTRY OPTION */}
              <div className="patient-selector" style={{ marginTop: "12px" }}>
                <label className="field">
                  Or enter Patient ID manually
                  <input
                    type="text"
                    value={patientId}
                    onChange={(event) => setPatientId(event.target.value)}
                    placeholder="e.g., 11, 45, 70"
                     disabled={!rawSearchText}
                  />
                </label>
                <button
                  className="secondary"
                   disabled={!patientId.trim() || !rawSearchText}
                  onClick={() => {
                    if (patientId.trim()) {
                      console.log("[UI] 📋 Loading summary for patient:", patientId);
                      setStreamText("");
                      callTool("get_patient_summary", {
                        patient_id: patientId
                      });
                    }
                  }}
                >
                  Load Patient Summary
                </button>
              </div>
            </div>
          </div>

          {/* STEP 3: GENERATE SUMMARY - ALWAYS VISIBLE */}
          <div className="workflow-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Generate AI Summary</h3>
              {!patientId ? (
                <p className="step-meta" style={{ color: "#945419" }}>
                  ⏳ Select a patient from Step 2 first
                </p>
              ) : (
                <div>
                  <p className="step-meta">Patient ID: <strong>{patientId}</strong></p>
                  <button
                    className="primary"
                    onClick={() => {
                      console.log("[UI] 🤖 Generating summary for patient:", patientId);
                      setStreamText("");
                      setSavedStatus("");
                      callTool("generate_summary", { patient_id: patientId });
                    }}
                  >
                    Generate Summary
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* STEP 4: DISPLAY SUMMARY - ALWAYS VISIBLE */}
          <div className="workflow-step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Generated Summary</h3>
              {isGenerating && !streamText ? (
                <div className="loading-container">
                  <div className="spinner"></div>
                  <p className="step-meta" style={{ color: "#945419", marginTop: "12px" }}>
                    Generating summary, please wait...
                  </p>
                </div>
              ) : !streamText ? (
                <p className="step-meta" style={{ color: "#945419" }}>
                  ⏳ Waiting for summary generation... Click "Generate Summary" in Step 3.
                </p>
              ) : (
                <div>
                  <div className="summary-box">
                    <pre>{streamText}</pre>
                  </div>
                  {streamActive ? (
                    <p className="step-meta" style={{ color: "#945419" }}>
                      ⏳ Streaming...
                    </p>
                  ) : (
                    <p className="step-meta" style={{ color: "#1b5b4c" }}>
                      ✓ Summary generated successfully
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* STEP 5: RECORD UPDATE */}
          <div className="workflow-step">
            <div className="step-number">5</div>
            <div className="step-content">
              <h3>Record Update</h3>
              {!streamText ? (
                <p className="step-meta" style={{ color: "#945419" }}>
                  ⏳ Waiting for summary to be generated...
                </p>
              ) : isUpdating ? (
                <div className="loading-container">
                  <div className="spinner"></div>
                  <p className="step-meta" style={{ color: "#945419", marginTop: "12px" }}>
                    Updating patient_summaries.csv...
                  </p>
                </div>
              ) : updatedRecord ? (
                <div>
                  <div className="update-success-box">
                    <div className="update-header">
                      <span className="update-icon">💾</span>
                      <strong>Record Updated Successfully</strong>
                    </div>
                    <div className="update-details">
                      <div className="update-field">
                        <span className="field-label">Patient ID:</span>
                        <span className="field-value highlighted">{updatedRecord.patientId}</span>
                      </div>
                      <div className="update-field">
                        <span className="field-label">Summary:</span>
                        <div className="field-value highlighted summary-preview">
                          {updatedRecord.summary.substring(0, 800)}
                        </div>
                      </div>
                      <div className="update-field">
                        <span className="field-label">Updated At:</span>
                        <span className="field-value">{updatedRecord.timestamp}</span>
                      </div>
                    </div>
                  </div>
                  {savedStatus && (
                    <p className="step-meta" style={{ color: "#1b5b4c", fontWeight: 600, marginTop: "12px" }}>
                      {savedStatus}
                    </p>
                  )}
                </div>
              ) : (
                <p className="step-meta" style={{ color: "#945419" }}>
                  ⏳ Waiting for database update...
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="panel stream">
            <div className="panel-header">
              <h2>LLM Stream Console</h2>
              <span className={`chip ${streamActive ? "connected" : "idle"}`}>
                {streamActive ? "streaming" : "idle"}
              </span>
            </div>
            <div className="stream-box">
              <pre>{streamText || "Streaming tokens will appear here."}</pre>
            </div>
            <div className="panel-sub">
              <h3>Last JSON-RPC Response</h3>
              <pre className="response-box">
                {lastResponse ? shortJson(lastResponse) : "No response yet."}
              </pre>
            </div>
          </div>

        <div className="panel timeline">
            <div className="panel-header">
              <h2>Event Timeline</h2>
              <div className="panel-actions">
                <select
                  value={activeFilter}
                  onChange={(event) => setActiveFilter(event.target.value)}
                >
                  <option value="all">All events</option>
                  <option value="user_input">User input</option>
                  <option value="server_process">Server process</option>
                  <option value="websocket_send">WebSocket send</option>
                  <option value="websocket_receive">WebSocket receive</option>
                  <option value="ollama">Ollama</option>
                  <option value="chroma_db">Chroma DB</option>
                  <option value="csv_operation">CSV operation</option>
                  <option value="error">Errors</option>
                </select>
              </div>
            </div>

            <div className="stats">
              <div>
                <span className="label">Messages</span>
                <strong>{stats?.total_messages ?? "-"}</strong>
              </div>
              <div>
                <span className="label">Avg Duration</span>
                <strong>{stats?.average_duration_ms ?? "-"} ms</strong>
              </div>
              <div>
                <span className="label">Total Data</span>
                <strong>{stats?.total_data_bytes ?? "-"} bytes</strong>
              </div>
            </div>

            <div className="timeline-list">
              {filteredMessages.length === 0 ? (
                <p className="empty">No events yet. Run a tool call.</p>
              ) : (
                filteredMessages.map((msg) => (
                  <div key={msg.id} className={`timeline-item ${msg.status}`}>
                    <div>
                      <span className="mono">{formatTime(msg.timestamp)}</span>
                      <span className="tag">{msg.source}</span>
                      <span className="tag">{msg.message_type}</span>
                      {msg.tool_name ? (
                        <span className="tag">tool: {msg.tool_name}</span>
                      ) : null}
                    </div>
                    <div className="meta">
                      {msg.duration ? <span>{msg.duration} ms</span> : null}
                      {msg.status ? <span>{msg.status}</span> : null}
                      {msg.patient_id ? <span>patient {msg.patient_id}</span> : null}
                    </div>
                    <pre>{shortJson(msg.content)}</pre>
                  </div>
                ))
              )}
            </div>
          </div>
      </section>

      <section className="grid bottom">
        <div className="panel traffic">
          <div className="panel-header">
            <h2>WebSocket Traffic</h2>
            <span className="chip">Local UI feed</span>
          </div>
          <div className="traffic-list">
            {traffic.map((entry, index) => (
              <div key={`${entry.time}-${index}`} className={`traffic-item ${entry.direction}`}>
                <div className="meta">
                  <span className="mono">{formatTime(entry.time)}</span>
                  <span className="tag">{entry.direction}</span>
                  <span className="tag">{entry.label}</span>
                </div>
                <pre>{shortJson(entry.payload)}</pre>
              </div>
            ))}
          </div>
        </div>

        <div className="panel tools">
          <div className="panel-header">
            <h2>Tools Blueprint</h2>
          </div>
          <div className="tool-map">
            {(tools.length ? tools : []).map((tool) => (
              <div key={tool.name} className="tool-card">
                <h3>{tool.name}</h3>
                <p>{tool.description}</p>
                <pre>{shortJson(tool.inputSchema)}</pre>
              </div>
            ))}
            {tools.length === 0 ? (
              <p className="empty">Load tools to see schemas.</p>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  );
}
