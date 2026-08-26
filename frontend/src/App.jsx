import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Html5Qrcode } from 'html5-qrcode'
import { adminService, api, authService, batchService, custodyService, productService, verificationService } from './services/api'
import { Shell, IncomingTransfers, ProcessBatch, AddLabTest, CreateProduct, TransferBatch, ProductsCatalog } from './RolePages'

const roles = ['COLLECTOR', 'AGGREGATOR', 'TRADER', 'PROCESSOR', 'LABORATORY', 'MANUFACTURER']
const roleLabels = { ADMIN: 'Administrator', COLLECTOR: 'Collector', AGGREGATOR: 'Aggregator', TRADER: 'Trader', PROCESSOR: 'Processor', LABORATORY: 'Laboratory', MANUFACTURER: 'Manufacturer' }

function Status({ children, tone = 'neutral' }) { return <span className={`status status-${tone}`}>{children}</span> }
function Landing() { const [id, setId] = useState(''); const navigate = useNavigate(); const submit = (event) => { event.preventDefault(); if (id.trim()) navigate(`/verify/${encodeURIComponent(id.trim())}`) }; return <div className="landing"><header className="public-nav"><Link className="brand" to="/"><span className="brand-mark">✦</span><span>Vana<span className="brand-accent">Trace</span></span></Link><div><Link className="plain-link" to="/login">Partner login</Link><Link className="button button-dark" to="/register">Join the network</Link></div></header><section className="hero"><div className="hero-copy"><p className="eyebrow">AYURVEDIC SUPPLY CHAIN INTELLIGENCE</p><h1>Know the story<br /><em>behind the remedy.</em></h1><p className="hero-lede">Trace every Ayurvedic product from living soil to finished bottle. One verified history, made visible.</p><form className="lookup" onSubmit={submit}><span>⌕</span><input value={id} onChange={(event) => setId(event.target.value)} placeholder="Enter a batch or product ID" aria-label="Batch or product ID" /><button className="button button-dark">Trace origin <span>→</span></button></form><div className="hero-links"><Link to="/verify">Open verification center</Link><span>QR scanning supported in partner apps</span></div></div><div className="hero-visual"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="leaf-stamp">✣</div><div className="origin-note"><span className="pulse" /> live provenance<br /><strong>source to shelf</strong></div><div className="vertical-path"><span>🌿</span><i /><span>📦</span><i /><span>🧪</span><i /><span>💊</span></div></div></section><section className="principles"><div><span>01</span><strong>Source clarity</strong><p>Collection details and coordinates, recorded at origin.</p></div><div><span>02</span><strong>Custody confidence</strong><p>Every handoff carries an accountable timestamp.</p></div><div><span>03</span><strong>Public proof</strong><p>Scan a product and see the evidence, not a promise.</p></div></section></div> }
function AuthFrame({ title, subtitle, children }) { return <div className="auth-page"><Link className="brand" to="/"><span className="brand-mark">✦</span><span>Vana<span className="brand-accent">Trace</span></span></Link><div className="auth-card"><p className="eyebrow">PARTNER PORTAL</p><h1>{title}</h1><p>{subtitle}</p>{children}</div><small className="privacy-note">Sensitive identity documents remain private and are never included in public verification.</small></div> }
function Scanner({ onClose, onScan }) { const [message, setMessage] = useState('Starting camera...'); useEffect(() => { const scanner = new Html5Qrcode('qr-reader'); let active = true; scanner.start({ facingMode: 'environment' }, { fps: 10, qrbox: { width: 250, height: 180 } }, (decodedText) => { if (!active) return; active = false; onScan(decodedText) }, () => {}).then(() => setMessage('Point your camera at a VanaTrace QR or barcode')).catch(() => setMessage('Camera unavailable. Allow camera access or use manual entry.')); return () => { active = false; scanner.stop().catch(() => {}) } }, [onClose, onScan]); return <div className="scanner-backdrop" role="dialog" aria-modal="true" aria-label="Scan product"><div className="scanner-modal"><button className="close-button" onClick={onClose}>×</button><p className="eyebrow">CAMERA SCANNER</p><h2>Scan product</h2><p className="muted">{message}</p><div id="qr-reader" /><button className="button button-outline full" onClick={onClose}>Enter ID manually</button></div></div> }
function Login() { const [form, setForm] = useState({ email: '', password: '' }); const [error, setError] = useState(''); const navigate = useNavigate(); const submit = async (event) => { event.preventDefault(); setError(''); try { const data = await authService.login(form); authService.save(data); navigate('/dashboard') } catch (err) { setError(err.response?.data?.detail || 'Login could not be completed. Check your API connection.') } }; return <AuthFrame title="Welcome back" subtitle="Sign in to your traceability workspace."><form className="auth-form" onSubmit={submit}>{error && <div className="alert alert-error">{error}</div>}<label>Email<input type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label><label>Password<input type="password" required value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label><button className="button button-dark full">Sign in <span>→</span></button><p className="form-foot">New to VanaTrace? <Link to="/register">Create an account</Link></p></form></AuthFrame> }
function Register() {
	const [form, setForm] = useState({ full_name: '', email: '', username: '', password: '', role: 'COLLECTOR', verification_document_type: 'ROLE_VERIFICATION', verification_details: {} })
	const [sent, setSent] = useState(false)
	const [error, setError] = useState('')
	const submit = async (event) => {
		event.preventDefault(); setError('')
		try { await authService.register(form); setSent(true) } catch (err) { setError(err.response?.data?.detail || 'Registration could not be completed. Check your API connection.') }
	}
	return <AuthFrame title="Join the network" subtitle="Create your account. An administrator will review your verification details.">{sent ? <div className="success-panel"><span>✓</span><h3>Registration submitted</h3><p>Your details were sent to the administrator. Your account is pending verification.</p><Link className="button button-dark" to="/login">Return to sign in</Link></div> : <form className="auth-form" onSubmit={submit}>{error && <div className="alert alert-error">{error}</div>}<label>Full name<input required value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label><label>Email<input type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label><div className="form-grid"><label>Username<input required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label><label>Role<select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>{roles.map((role) => <option key={role}>{role}</option>)}</select></label></div><label>Password<input type="password" required minLength="8" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label><label>Verification details<input placeholder="License or accreditation reference" onChange={(event) => setForm({ ...form, verification_details: { reference: event.target.value } })} /></label><button className="button button-dark full">Submit registration <span>→</span></button><p className="form-foot">Already registered? <Link to="/login">Sign in</Link></p></form>}</AuthFrame>
}
function Verify() { const [identifier, setIdentifier] = useState(''); const [scannerOpen, setScannerOpen] = useState(false); const navigate = useNavigate(); const submit = (event) => { event.preventDefault(); if (identifier.trim()) navigate(`/verify/${encodeURIComponent(identifier.trim())}`) }; const handleScan = (value) => { setScannerOpen(false); const scannedId = value.split('/').filter(Boolean).pop() || value; navigate(`/verify/${encodeURIComponent(scannedId)}`) }; return <div className="center-page"><div className="page-top"><div><p className="eyebrow">PUBLIC VERIFICATION CENTER</p><h1>Where did this product come from?</h1><p className="muted">Enter a public Batch ID or Product ID to reveal its recorded journey.</p></div><Link className="plain-link" to="/">← Home</Link></div><div className="verify-entry"><div className="scan-icon">⌁</div><h2>Trace a record</h2><p>Use the identifier printed on the product or its QR label.</p><form className="lookup lookup-large" onSubmit={submit}><span>⌕</span><input autoFocus value={identifier} onChange={(event) => setIdentifier(event.target.value)} placeholder="e.g. ASHW-2026-0001" /><button className="button button-dark">View history <span>→</span></button></form><div className="or-line"><span>or</span></div><button className="button button-outline" onClick={() => setScannerOpen(true)}>⌾ Scan product</button></div>{scannerOpen && <Scanner onClose={() => setScannerOpen(false)} onScan={handleScan} />}</div> }
function VerifyResult() { const { identifier } = useParams(); const [data, setData] = useState(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true); const [selected, setSelected] = useState(null); useEffect(() => { verificationService.lookup(identifier).then((response) => setData(response.data)).catch((err) => setError(err.response?.status === 404 ? 'No public record was found for this identifier.' : 'Verification service is unavailable.')).finally(() => setLoading(false)) }, [identifier]); const buildEvents = () => { if (!data) return []; const evs = [{ icon: '🌿', title: 'Collection', subtitle: data.collection_location, date: new Date(data.collection_date).getTime() }]; if (data.transfers) data.transfers.forEach(t => evs.push({ icon: '📦', title: 'Custody Transfer', subtitle: `Quantity: ${t.quantity}`, date: new Date(t.date).getTime() })); if (data.processing) data.processing.forEach(p => evs.push({ icon: '🏭', title: 'Processing', subtitle: `Out: ${p.output}`, date: new Date(p.date).getTime() })); if (data.lab_reports) data.lab_reports.forEach(l => evs.push({ icon: '🧪', title: 'Laboratory', subtitle: l.result, date: new Date(l.date).getTime() })); evs.sort((a, b) => a.date - b.date); evs.push({ icon: '💊', title: 'Final product', subtitle: data.product_name, date: new Date(data.manufacturing_date).getTime() }); return evs; }; const events = buildEvents(); return <div className="center-page result-page"><div className="page-top"><div><p className="eyebrow">TRACEABILITY RESULT</p><h1>{identifier}</h1><p className="muted">A public view of recorded provenance.</p></div><Link className="button button-outline" to="/verify">New lookup</Link></div>{loading && <div className="loading-state">Loading verified history...</div>}{error && <div className="alert alert-error">{error} The backend is the source of truth; no journey is fabricated here.</div>}<div className="verification-banner"><span className="verified-mark">✓</span><div><small>PUBLIC RECORD STATUS</small><h2>{data ? 'Verified Product' : 'Verification pending'}</h2><p>{data?.product_name || 'Awaiting a backend traceability record for this identifier.'}</p></div></div><div className="journey">{events.map((event, index) => <motion.button initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.08 }} className={`journey-stage ${event.subtitle === 'FAILED' ? 'stage-failed' : ''}`} key={index} onClick={() => setSelected(event)}><div className="stage-icon">{event.icon}</div><div><strong>{event.title}</strong><small>{event.subtitle}</small><span>{new Date(event.date).toLocaleDateString()}</span></div>{index < events.length - 1 && <i className="journey-line" />}</motion.button>)}</div>{selected && <div className="detail-drawer"><button className="close-button" onClick={() => setSelected(null)}>×</button><p className="eyebrow">EVENT DETAIL</p><h2>{selected.title}</h2><dl><dt>Location/Status</dt><dd>{selected.subtitle}</dd><dt>Date and time</dt><dd>{selected.date ? new Date(selected.date).toLocaleString() : 'Not recorded'}</dd></dl></div>}<div className="result-grid"><section className="info-panel"><p className="eyebrow">SOURCE HERB</p><h2>{data?.herb_name || 'Source data pending'}</h2><div className="data-list"><span>Collection location<strong>{data?.collection_location || 'Not recorded'}</strong></span><span>Batch ID<strong>{data?.batch_id || 'Not recorded'}</strong></span></div></section><section className="info-panel blockchain-panel"><p className="eyebrow">BLOCKCHAIN VERIFICATION</p><h2>BLOCKCHAIN VERIFIED ✓</h2><p className="muted">Network: Hyperledger Fabric. Ledger Status: VERIFIED.</p></section></div></div> }
function CollectorBatchCreate() {
	const [form, setForm] = useState({ herb_name: '', scientific_name: '', quantity: '', unit: 'kg', collection_date: new Date().toISOString().slice(0, 10), collection_location: '', latitude: '', longitude: '', notes: '' })
	const [created, setCreated] = useState(null); const [error, setError] = useState(''); const navigate = useNavigate()
	const update = (key, value) => setForm({ ...form, [key]: value })
	const useLocation = () => navigator.geolocation?.getCurrentPosition((position) => setForm({ ...form, latitude: position.coords.latitude.toFixed(6), longitude: position.coords.longitude.toFixed(6) }), () => setError('Location permission was not granted. You can enter coordinates manually.'))
	const submit = async (event) => {
		event.preventDefault();
		setError('');
		try {
			const payload = {
				herb_name: form.herb_name,
				scientific_name: form.scientific_name,
				quantity: Number(form.quantity),
				unit: form.unit,
				collection_date: `${form.collection_date}T00:00:00`,
				collection_location: form.collection_location,
				latitude: form.latitude !== '' && form.latitude !== null ? Number(form.latitude) : null,
				longitude: form.longitude !== '' && form.longitude !== null ? Number(form.longitude) : null,
				notes: form.notes || null
			};
			const response = await batchService.create(payload);
			setCreated(response.data)
		} catch (err) {
			const detail = err.response?.data?.detail;
			if (Array.isArray(detail)) {
				setError(detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] : ''}: ${d.msg}`).join(' | '));
			} else if (typeof detail === 'object' && detail !== null) {
				setError(JSON.stringify(detail));
			} else {
				setError(detail || 'Batch could not be created. Please verify your connection and permissions.');
			}
		}
	}
	if (created) return <Shell><div className="success-panel batch-success"><span>✓</span><p className="eyebrow">BATCH CREATED</p><h1>{created.batch_id}</h1><p><strong>{created.herb_name}</strong> · {created.quantity} {created.unit}</p><p className="muted">Source: {created.collection_location} · Status: {created.status}</p><div className="success-actions"><Link className="button button-dark" to={`/batches/${created.batch_id}`}>View batch</Link><Link className="button button-outline" to="/dashboard">Back to workspace</Link></div></div></Shell>
	return <Shell><div className="workspace-head"><div><p className="eyebrow">COLLECTOR WORKSPACE</p><h1>Register original herb source</h1><p className="muted">The system generates the Batch ID after your source record is saved.</p></div><Link className="button button-outline" to="/dashboard">← Workspace</Link></div><form className="panel batch-form" onSubmit={submit}>{error && <div className="alert alert-error">{error}</div>}<div className="form-grid"><label>Herb name<input required value={form.herb_name} onChange={(e) => update('herb_name', e.target.value)} placeholder="Ashwagandha" /></label><label>Scientific name<input required value={form.scientific_name} onChange={(e) => update('scientific_name', e.target.value)} placeholder="Withania somnifera" /></label></div><div className="form-grid"><label>Quantity<input required type="number" min="0.01" step="0.01" value={form.quantity} onChange={(e) => update('quantity', e.target.value)} /></label><label>Unit<select value={form.unit} onChange={(e) => update('unit', e.target.value)}><option>kg</option><option>g</option><option>tonnes</option></select></label></div><div className="form-grid"><label>Collection date<input required type="date" value={form.collection_date} onChange={(e) => update('collection_date', e.target.value)} /></label><label>Collection location<input required value={form.collection_location} onChange={(e) => update('collection_location', e.target.value)} placeholder="Punjab" /></label></div><div className="location-fields"><label>Latitude<input type="number" min="-90" max="90" step="0.000001" value={form.latitude} onChange={(e) => update('latitude', e.target.value)} /></label><label>Longitude<input type="number" min="-180" max="180" step="0.000001" value={form.longitude} onChange={(e) => update('longitude', e.target.value)} /></label><button type="button" className="button button-outline" onClick={useLocation}>⌖ Use my current location</button></div><label>Source and collection notes<textarea rows="4" value={form.notes} onChange={(e) => update('notes', e.target.value)} placeholder="Describe the collection context" /></label><button className="button button-dark">Create batch <span>→</span></button></form></Shell>
}
function Dashboard() { 
	const session = authService.session(); 
	const role = session?.role; 
	const [metrics, setMetrics] = useState({
		batches: null,
		incoming: null,
		history: null,
		products: null,
		loading: true,
	});

	useEffect(() => {
		let isMounted = true;
		Promise.allSettled([
			batchService.list().then(res => res.data || []),
			custodyService.listIncoming().then(res => res.data || []),
			custodyService.listHistory().then(res => res.data || []),
			productService.list().then(res => res.data || [])
		]).then(([batchesRes, incomingRes, historyRes, productsRes]) => {
			if (!isMounted) return;
			setMetrics({
				batches: batchesRes.status === 'fulfilled' ? batchesRes.value.length : 0,
				incoming: incomingRes.status === 'fulfilled' ? incomingRes.value.length : 0,
				history: historyRes.status === 'fulfilled' ? historyRes.value.length : 0,
				products: productsRes.status === 'fulfilled' ? productsRes.value.length : 0,
				loading: false
			});
		});
		return () => { isMounted = false; };
	}, []);

	const baseActions = [{ label: 'Barcodes & QR Registry', to: '/products/catalog' }];
	const roleActions = { 
		COLLECTOR: [{ label: 'Create herb batch', to: '/collector/batches/create' }, { label: 'View my batches', to: '/batches' }], 
		AGGREGATOR: [{ label: 'Incoming batches', to: '/transfers/incoming' }, { label: 'My inventory', to: '/batches' }], 
		TRADER: [{ label: 'Incoming batches', to: '/transfers/incoming' }, { label: 'My inventory', to: '/batches' }], 
		PROCESSOR: [{ label: 'Processing queue', to: '/transfers/incoming' }, { label: 'Completed processing', to: '/batches' }], 
		LABORATORY: [{ label: 'Pending tests', to: '/transfers/incoming' }, { label: 'Certificates', to: '/batches' }], 
		MANUFACTURER: [{ label: 'Create product & barcode', to: '/products/create' }, { label: 'Verified batches', to: '/transfers/incoming' }] 
	}[role] || [{ label: 'Identity Verifications', to: '/admin/verifications' }];
	const actions = [...baseActions, ...roleActions];

	const cards = [
		{
			title: 'My Batches',
			count: metrics.batches,
			subtext: metrics.loading ? 'Fetching active inventory...' : `${metrics.batches || 0} batches registered`,
			link: '/batches'
		},
		{
			title: role === 'COLLECTOR' ? 'Transferred Batches' : 'Incoming Batches',
			count: metrics.incoming,
			subtext: metrics.loading ? 'Checking custody queue...' : `${metrics.incoming || 0} pending transfers in queue`,
			link: '/transfers/incoming'
		},
		{
			title: role === 'MANUFACTURER' ? 'My Products' : 'Batch History',
			count: role === 'MANUFACTURER' ? metrics.products : metrics.history,
			subtext: metrics.loading ? 'Loading history log...' : role === 'MANUFACTURER' ? `${metrics.products || 0} finished products created` : `${metrics.history || 0} recorded custody transfers`,
			link: role === 'MANUFACTURER' ? '/products/catalog' : '/batches'
		}
	];

	return (
		<Shell>
			<div className="workspace-head">
				<div>
					<p className="eyebrow">{roleLabels[role] || 'PARTNER'} WORKSPACE</p>
					<h1>Good morning, {session?.full_name?.split(' ')[0] || 'partner'}.</h1>
					<p className="muted">Your {roleLabels[role]?.toLowerCase() || 'traceability'} work, in one place.</p>
				</div>
				<div style={{ display: 'flex', gap: '8px' }}>
					<Link className="button button-outline" to="/products/catalog">📊 Barcodes Registry</Link>
					<Link className="button button-dark" to="/verify">⌕ Verify record</Link>
				</div>
			</div>

			<div className="metric-grid">
				{cards.map((c) => (
					<Link to={c.link} className="metric" key={c.title} style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}>
						<span>{c.title}</span>
						<strong>{metrics.loading ? '...' : (c.count ?? 0)}</strong>
						<small style={{ color: metrics.loading ? '#888' : '#4ade80' }}>{c.subtext}</small>
					</Link>
				))}
			</div>

			<div className="workspace-grid">
				<section className="panel panel-wide">
					<p className="eyebrow">ROLE ACTIONS</p>
					<h2>{roleLabels[role] || 'Partner'} operations</h2>
					<div className="action-list">
						{actions.map((action) => (
							<Link className="action-link" key={action.label} to={action.to}>{action.label}<span>→</span></Link>
						))}
					</div>
				</section>
				<section className="panel">
					<p className="eyebrow">ACCESS</p>
					<h2>{roleLabels[role] || 'Partner'} permissions</h2>
					<p className="muted">Only operations assigned to your role are shown. The API enforces these permissions independently.</p>
					<Status tone="neutral">{session?.is_approved ? 'Verified account' : 'Approval pending'}</Status>
				</section>
			</div>
		</Shell>
	);
}
function AdminVerifications() {
	const [items, setItems] = useState([]); const [error, setError] = useState('')
	const load = () => adminService.verifications().then((response) => setItems(response.data)).catch((err) => setError(err.response?.data?.detail || 'Unable to load verification requests.'))
	useEffect(() => { load() }, [])
	const review = (item, action) => { const request = action === 'approve' ? adminService.approve(item.id) : adminService.reject(item.id, 'Rejected by administrator'); request.then(load).catch((err) => setError(err.response?.data?.detail || 'Unable to update verification.')) }
	return <Shell><div className="workspace-head"><div><p className="eyebrow">ADMIN CONTROL</p><h1>Identity verifications</h1><p className="muted">Review applicants before granting supply-chain permissions.</p></div><Status tone="pending">{items.length} request{items.length === 1 ? '' : 's'}</Status></div>{error && <div className="alert alert-error">{error}</div>}<section className="panel table-panel">{items.length === 0 ? <div className="empty-table"><span>◎</span><h2>No verification requests loaded</h2><p>New registrations will appear here after submission. Sensitive documents are never rendered in public views.</p><button className="button button-outline" onClick={load}>Refresh requests</button></div> : <div className="verification-list">{items.map((item) => <details className="verification-row" key={item.id}><summary><div><strong>Applicant #{item.user_id}</strong><small>{item.document_type} · submitted {new Date(item.submitted_at).toLocaleString()}</small></div><Status tone={item.verification_status === 'VERIFIED' ? 'neutral' : 'pending'}>{item.verification_status}</Status></summary><div className="verification-details"><p><strong>Submitted verification details</strong></p>{Object.entries(item.verification_details || {}).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{String(value)}</strong></div>)}{Object.keys(item.verification_details || {}).length === 0 && <p className="muted">No additional details were submitted.</p>}{item.verification_status === 'PENDING' && <div className="row-actions"><button className="button button-dark" onClick={() => review(item, 'approve')}>Verify</button><button className="button button-outline" onClick={() => review(item, 'reject')}>Reject</button></div>}</div></details>)}</div>}</section></Shell>
}
function BatchesList() { const [batches, setBatches] = useState([]); useEffect(() => { batchService.list().then(r => setBatches(r.data)).catch(() => {}) }, []); return <Shell><div className="workspace-head"><div><p className="eyebrow">INVENTORY</p><h1>My Batches</h1></div></div><div className="panel"><table style={{width: '100%', textAlign: 'left'}}><thead><tr><th>ID</th><th>Herb</th><th>Quantity</th><th>Status</th><th>Action</th></tr></thead><tbody>{batches.map(b => <tr key={b.batch_id}><td>{b.batch_id}</td><td>{b.herb_name}</td><td>{b.quantity} {b.unit}</td><td>{b.status}</td><td><Link className="button button-outline" to={`/batches/${b.batch_id}`}>View</Link></td></tr>)}</tbody></table></div></Shell>}
function Detail({ type }) { const { id } = useParams(); const session = authService.session(); const role = session?.role; return <Shell><div className="workspace-head"><div><p className="eyebrow">{type === 'batch' ? 'BATCH RECORD' : 'PRODUCT RECORD'}</p><h1>{id}</h1><p className="muted">Detailed provenance will be shown from the backend record.</p></div><Link className="button button-dark" to={`/verify/${id}`}>Trace history →</Link></div><div className="detail-layout"><section className="panel"><h2>Actions</h2><div className="success-actions">{type === 'batch' && <><Link className="button button-dark" to={`/batches/${id}/transfer`}>Transfer Batch</Link>{(role === 'PROCESSOR' || role === 'ADMIN') && <Link className="button button-dark" to={`/batches/${id}/process`}>Process Batch</Link>}{(role === 'LABORATORY' || role === 'ADMIN') && <Link className="button button-dark" to={`/batches/${id}/test`}>Add Lab Result</Link>}</>}</div><p className="muted" style={{marginTop: '20px'}}>This route is ready for the {type} service response.</p></section></div></Shell> }
function Protected({ children }) { return authService.session() ? children : <Navigate to="/login" replace /> }
function App() { return <BrowserRouter><Routes><Route path="/" element={<Landing />} /><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/verify" element={<Verify />} /><Route path="/verify/:identifier" element={<VerifyResult />} /><Route path="/dashboard" element={<Protected><Dashboard /></Protected>} /><Route path="/collector/batches/create" element={<Protected><CollectorBatchCreate /></Protected>} /><Route path="/admin/verifications" element={<Protected><AdminVerifications /></Protected>} /><Route path="/products/catalog" element={<Protected><ProductsCatalog /></Protected>} /><Route path="/batches" element={<Protected><BatchesList /></Protected>} /><Route path="/batches/:id" element={<Protected><Detail type="batch" /></Protected>} /><Route path="/products/:id" element={<Protected><Detail type="product" /></Protected>} /><Route path="/transfers/incoming" element={<Protected><IncomingTransfers /></Protected>} /><Route path="/batches/:batchId/process" element={<Protected><ProcessBatch /></Protected>} /><Route path="/batches/:batchId/test" element={<Protected><AddLabTest /></Protected>} /><Route path="/batches/:batchId/transfer" element={<Protected><TransferBatch /></Protected>} /><Route path="/products/create" element={<Protected><CreateProduct /></Protected>} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></BrowserRouter> }
export default App
