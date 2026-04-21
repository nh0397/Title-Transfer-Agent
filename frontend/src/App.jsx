/**
 * Author: Naisarg H.
 * File: App.jsx
 * Description: This is the main React component for the Title Transfer Agent
 * dashboard. It handles file uploads, runs the three-phase AI pipeline
 * (extract, map, generate), shows real-time logs, renders PDF previews
 * with inline editing, and provides download options for individual forms
 * and the full merged transfer packet.
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Upload, FileText, CheckCircle,
  Download, Sparkles, AlertCircle,
  Zap, Clock, RefreshCw, ChevronLeft, ChevronRight, Edit3, Save, Eye, Package
} from 'lucide-react';

const API = 'http://localhost:8000';

const PHASES = [
  { id: 1, name: 'Scanning Document', desc: 'Reading title certificate' },
  { id: 2, name: 'Mapping Fields', desc: 'Matching data to HCD forms' },
  { id: 3, name: 'Generating PDFs', desc: 'Filling government templates' },
  { id: 4, name: 'Review & Download', desc: 'Preview and edit' },
];

const FORM_LABELS = {
  hcd_476_6g: { name: 'HCD 476.6G', desc: 'Multi-Purpose Transfer Form' },
  hcd_480_5: { name: 'HCD 480.5', desc: 'Application for Registration' },
  hcd_476_6: { name: 'HCD 476.6', desc: 'Statement of Facts' },
};

function App() {
  const [phase, setPhase] = useState(0);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [extraction, setExtraction] = useState(null);
  const [mapping, setMapping] = useState(null);
  const [editableMapping, setEditableMapping] = useState(null);
  const [generated, setGenerated] = useState(null);
  const [previews, setPreviews] = useState(null);
  const [logs, setLogs] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [activePreview, setActivePreview] = useState(null);
  const [previewPage, setPreviewPage] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [buyerData, setBuyerData] = useState({ name: '', address: '', salePrice: '', date: '' });
  const fileInput = useRef(null);
  const logRef = useRef(null);

  const addLog = useCallback((msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev, { time, msg, type }]);
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs]);

  useEffect(() => {
    if (!startTime || phase === 4) return;
    const timer = setInterval(() => setElapsed(((Date.now() - startTime) / 1000).toFixed(1)), 100);
    return () => clearInterval(timer);
  }, [startTime, phase]);

  useEffect(() => {
    if (previews && !activePreview) {
      const firstKey = Object.keys(previews)[0];
      if (firstKey) setActivePreview(firstKey);
    }
  }, [previews, activePreview]);

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;

    // Only allow PDF files
    if (f.type !== 'application/pdf') {
      setError('Invalid file type. Please upload a PDF document.');
      addLog('Rejected non-PDF file', 'error');
      setFile(null);
      if (fileInput.current) fileInput.current.value = '';
      return;
    }

    setFile(f);
    setError(null);
    setPhase(0);
    setExtraction(null);
    setMapping(null);
    setEditableMapping(null);
    setGenerated(null);
    setPreviews(null);
    setActivePreview(null);
    setLogs([]);
    setEditMode(false);
    setPreviewPage(0);
    addLog(`Document loaded: ${f.name} (${(f.size / 1024).toFixed(0)} KB)`, 'success');
  };

  const runFullPipeline = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setStartTime(Date.now());

    setPhase(1);
    addLog('Starting document scan...', 'info');

    try {
      const form = new FormData();
      form.append('file', file);
      const res1 = await fetch(`${API}/api/extract`, { method: 'POST', body: form });
      if (!res1.ok) throw new Error((await res1.json()).detail || 'Extraction failed');
      const result1 = await res1.json();

      // Document validation — AI checks if it is actually a title
      if (result1.data.is_valid_title === false) {
        throw new Error(result1.data.validation_error || 'This does not appear to be a California Certificate of Title.');
      }

      setExtraction(result1.data);
      const fieldCount = Object.values(result1.data).filter(v => v && v !== true && v !== null).length;
      addLog(`Extracted ${fieldCount} data fields from title`, 'success');

      setPhase(2);
      addLog('Mapping data to HCD form fields...', 'info');

      const res2 = await fetch(`${API}/api/map`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ extracted_data: result1.data, buyer_data: buyerData }),
      });
      if (!res2.ok) throw new Error((await res2.json()).detail || 'Mapping failed');
      const result2 = await res2.json();
      setMapping(result2.data);
      setEditableMapping(JSON.parse(JSON.stringify(result2.data)));

      const totalFields = Object.values(result2.data).reduce(
        (sum, form) => sum + Object.values(form).filter(v => v).length, 0
      );
      addLog(`Mapped data to ${totalFields} fields across 3 forms`, 'success');

      setPhase(3);
      addLog('Filling PDF templates...', 'info');

      const res3 = await fetch(`${API}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result2.data),
      });
      if (!res3.ok) throw new Error((await res3.json()).detail || 'Generation failed');
      const result3 = await res3.json();
      setGenerated(result3.data.generated_files);
      setPreviews(result3.data.previews);
      setPhase(4);

      addLog('All 3 HCD forms generated successfully', 'success');
      addLog('Transfer packet ready. Review the previews below.', 'info');

    } catch (e) {
      setError(e.message);
      addLog(`Error: ${e.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    addLog('Regenerating PDFs with updated data...', 'info');

    try {
      const res = await fetch(`${API}/api/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mapping: editableMapping }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Regeneration failed');
      const result = await res.json();
      setGenerated(result.data.generated_files);
      setPreviews(result.data.previews);
      setMapping(JSON.parse(JSON.stringify(editableMapping)));
      setEditMode(false);
      setPreviewPage(0);
      addLog('PDFs regenerated with your edits', 'success');
    } catch (e) {
      addLog(`Error: ${e.message}`, 'error');
    } finally {
      setRegenerating(false);
    }
  };

  const updateField = (formKey, fieldName, newValue) => {
    setEditableMapping(prev => ({
      ...prev,
      [formKey]: {
        ...prev[formKey],
        [fieldName]: newValue,
      },
    }));
  };

  const reset = () => {
    setPhase(0);
    setFile(null);
    if (fileInput.current) fileInput.current.value = '';
    setExtraction(null);
    setMapping(null);
    setEditableMapping(null);
    setGenerated(null);
    setPreviews(null);
    setActivePreview(null);
    setError(null);
    setLogs([]);
    setStartTime(null);
    setElapsed(0);
    setEditMode(false);
    setPreviewPage(0);
    setBuyerData({ name: '', address: '', salePrice: '', date: '' });
  };

  const getStepClass = (stepId) => {
    if (stepId < phase) return 'step completed';
    if (stepId === phase) return 'step active';
    return 'step';
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">H</div>
          <div className="header-title">
            Harmony Title Transfer Agent
            <span className="header-version">v1.0</span>
          </div>
        </div>
        <div className="header-right">
          {loading && (
            <div className="header-timer"><Clock size={14} />{elapsed}s</div>
          )}
          <div className="header-status">
            <div className={`status-dot ${loading ? 'processing' : ''}`}></div>
            {loading ? 'Processing' : 'Ready'}
          </div>
        </div>
      </header>

      <div className="dashboard">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="card">
            <div className="card-title">Document Input</div>
            <div
              className={`dropzone ${file ? 'has-file' : ''}`}
              onClick={() => !loading && fileInput.current?.click()}
            >
              <input ref={fileInput} type="file" accept=".pdf" style={{ display: 'none' }} onChange={handleFile} />
              {file ? (
                <>
                  <FileText size={28} className="dropzone-icon" style={{ color: 'var(--success)' }} />
                  <div className="dropzone-label" style={{ color: 'var(--success)' }}>Document Loaded</div>
                  <div className="dropzone-filename">{file.name}</div>
                </>
              ) : (
                <>
                  <Upload size={28} className="dropzone-icon" />
                  <div className="dropzone-label">Upload Title Document</div>
                  <div className="dropzone-hint">California Certificate of Title (PDF)</div>
                </>
              )}
            </div>
            {file && phase === 0 && (
              <div className="buyer-form" style={{ marginTop: '1.5rem' }}>
                <div className="card-title">Buyer Information (Optional)</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem', marginBottom: '1.5rem' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-light)', marginBottom: '0.25rem', display: 'block' }}>Buyer Full Name</label>
                    <input 
                      type="text" 
                      className="edit-input" 
                      placeholder="e.g. Jane Doe" 
                      value={buyerData.name} 
                      onChange={(e) => setBuyerData({...buyerData, name: e.target.value})} 
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-light)', marginBottom: '0.25rem', display: 'block' }}>New Mailing Address</label>
                    <input 
                      type="text" 
                      className="edit-input" 
                      placeholder="e.g. 123 Main St, Los Angeles, CA 90001" 
                      value={buyerData.address} 
                      onChange={(e) => setBuyerData({...buyerData, address: e.target.value})} 
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-light)', marginBottom: '0.25rem', display: 'block' }}>Sale Price</label>
                    <input 
                      type="text" 
                      className="edit-input" 
                      placeholder="e.g. $15,000" 
                      value={buyerData.salePrice} 
                      onChange={(e) => setBuyerData({...buyerData, salePrice: e.target.value})} 
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-light)', marginBottom: '0.25rem', display: 'block' }}>Date of Sale (Date Picker)</label>
                    <input 
                      type="date" 
                      className="edit-input" 
                      value={buyerData.date} 
                      onChange={(e) => setBuyerData({...buyerData, date: e.target.value})} 
                    />
                  </div>
                </div>
              </div>
            )}
            {phase === 0 && (
              <button
                className="btn btn-primary btn-full"
                onClick={runFullPipeline}
                disabled={!file || loading}
                style={{ filter: !file ? 'grayscale(1) opacity(0.5)' : 'none' }}
              >
                <Zap size={16} /> Run Agent
              </button>
            )}
            {phase === 4 && (
              <button className="btn btn-ghost btn-full" onClick={reset}>
                <RefreshCw size={14} /> Process Another
              </button>
            )}
          </div>

          <div className="card">
            <div className="card-title">Pipeline</div>
            <div className="steps">
              {PHASES.map((p) => (
                <div key={p.id} className={getStepClass(p.id)}>
                  <div className="step-icon">
                    {p.id < phase ? <CheckCircle size={14} /> : p.id === phase && loading ? <span className="spinner-sm"></span> : p.id}
                  </div>
                  <div className="step-info">
                    <div className="step-name">{p.name}</div>
                    <div className="step-desc">{p.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="main">
          {/* Welcome */}
          {phase === 0 && !file && !error && (
            <div className="card hero-card">
              <Sparkles size={48} style={{ color: 'var(--primary-light)', marginBottom: '1.5rem' }} />
              <h2 className="main-title">Title Transfer Agent</h2>
              <p className="main-subtitle" style={{ maxWidth: 480, marginTop: '0.75rem' }}>
                Upload a California Manufactured Home Title. The agent will extract data,
                map it to HCD forms, and produce filled PDFs for your review.
              </p>
            </div>
          )}

          {phase === 0 && file && !error && (
            <div className="card hero-card">
              <FileText size={48} style={{ color: 'var(--success)', marginBottom: '1.5rem' }} />
              <h2 className="main-title">Ready to Process</h2>
              <p className="main-subtitle" style={{ maxWidth: 480, marginTop: '0.75rem' }}>
                <strong>{file.name}</strong> loaded. Click <strong>"Run Agent"</strong> to start.
              </p>
            </div>
          )}

          {/* Error card — shown at any phase */}
          {error && (
            <div className="card error-card">
              <div className="error-header"><AlertCircle size={18} /><strong>Pipeline Error</strong></div>
              <p className="error-text">{error}</p>
              <button className="btn btn-ghost" onClick={reset} style={{ marginTop: '1rem' }}>
                <RefreshCw size={14} /> Try Again
              </button>
            </div>
          )}

          {phase >= 1 && (
            <>
              {/* Agent Log */}
              <div className="card">
                <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Agent Activity</span>
                  {loading && <span className="processing-badge"><span className="spinner-sm"></span> Working</span>}
                  {phase === 4 && !loading && <span className="complete-badge"><CheckCircle size={12} /> Done</span>}
                </div>
                <div className="log-stream" ref={logRef}>
                  {logs.map((l, i) => (
                    <div key={i} className={`log-entry ${l.type}`}>
                      <span className="log-time">{l.time}</span>
                      <span className="log-msg">{l.msg}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Extracted Data */}
              {extraction && (
                <div className="card">
                  <div className="card-title">Extracted Data</div>
                  <div className="data-grid">
                    {Object.entries(extraction).map(([key, value]) => (
                      value && key !== 'is_valid_title' && key !== 'validation_error' && (
                        <div key={key} className="data-item">
                          <div className="data-label">{key.replace(/_/g, ' ')}</div>
                          <div className="data-value">{String(value)}</div>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}

              {/* PDF Preview & Edit Section */}
              {previews && phase === 4 && (
                <div className="card preview-section">
                  <div className="preview-header">
                    <div className="card-title" style={{ margin: 0 }}>Document Preview</div>
                    <div className="preview-actions">
                      <button
                        className={`btn ${editMode ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setEditMode(!editMode)}
                        style={{ padding: '0.5rem 0.875rem' }}
                      >
                        {editMode ? <><Eye size={14} /> Preview</> : <><Edit3 size={14} /> Edit Fields</>}
                      </button>
                      {editMode && (
                        <button
                          className="btn btn-success"
                          onClick={handleRegenerate}
                          disabled={regenerating}
                          style={{ padding: '0.5rem 0.875rem' }}
                        >
                          {regenerating ? <><span className="spinner-sm"></span> Saving...</> : <><Save size={14} /> Save & Regenerate</>}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Form Tabs */}
                  <div className="preview-tabs">
                    {Object.keys(previews).map((formKey) => {
                      const label = FORM_LABELS[formKey] || { name: formKey };
                      return (
                        <button
                          key={formKey}
                          className={`preview-tab ${activePreview === formKey ? 'active' : ''}`}
                          onClick={() => { setActivePreview(formKey); setPreviewPage(0); }}
                        >
                          {label.name}
                        </button>
                      );
                    })}
                  </div>

                  {/* Preview + Edit split */}
                  <div className={editMode ? 'preview-split' : ''}>
                    <div className="preview-viewer">
                      {activePreview && previews[activePreview] && (
                        <>
                          <img
                            src={`data:image/png;base64,${previews[activePreview][previewPage]}`}
                            alt={`Preview of ${activePreview} page ${previewPage + 1}`}
                            className="preview-image"
                          />
                          {previews[activePreview].length > 1 && (
                            <div className="preview-pagination">
                              <button
                                className="btn btn-ghost btn-icon"
                                disabled={previewPage === 0}
                                onClick={() => setPreviewPage(p => p - 1)}
                              >
                                <ChevronLeft size={16} />
                              </button>
                              <span className="preview-page-info">
                                Page {previewPage + 1} of {previews[activePreview].length}
                              </span>
                              <button
                                className="btn btn-ghost btn-icon"
                                disabled={previewPage >= previews[activePreview].length - 1}
                                onClick={() => setPreviewPage(p => p + 1)}
                              >
                                <ChevronRight size={16} />
                              </button>
                            </div>
                          )}
                        </>
                      )}
                    </div>

                    {/* Editable Fields Panel */}
                    {editMode && activePreview && editableMapping[activePreview] && (
                      <div className="edit-panel">
                        <div className="edit-panel-title">
                          {FORM_LABELS[activePreview]?.desc || activePreview}
                        </div>
                        <div className="edit-fields">
                          {Object.entries(editableMapping[activePreview]).map(([fieldName, value]) => (
                            <div key={fieldName} className="edit-field">
                              <label className="edit-label">{fieldName}</label>
                              <input
                                type="text"
                                className="edit-input"
                                value={value || ''}
                                onChange={(e) => updateField(activePreview, fieldName, e.target.value)}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Download section */}
                  <div className="download-bar" style={{ flexDirection: 'column', gap: '0.75rem' }}>
                    {/* Full Packet download */}
                    <a
                      className="btn btn-primary btn-full"
                      href={`${API}/api/download/full_packet`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ textDecoration: 'none', padding: '0.75rem' }}
                    >
                      <Package size={16} /> Download Full Transfer Packet
                    </a>
                    {/* Individual form downloads */}
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {generated && generated.map((f) => {
                        const label = FORM_LABELS[f.form] || { name: f.form, desc: '' };
                        return (
                          <a
                            key={f.form}
                            className="btn btn-ghost"
                            href={`${API}/api/download/${f.form}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ textDecoration: 'none', flex: 1 }}
                          >
                            <FileText size={14} /> {label.name}
                          </a>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
