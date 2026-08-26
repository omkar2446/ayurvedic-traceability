import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { authService, batchService, custodyService, laboratoryService, processingService, productService, userService } from './services/api';
import { formatDateTime } from './utils/formatters';

const roleLabels = {
    ADMIN: 'Administrator',
    COLLECTOR: 'Collector',
    AGGREGATOR: 'Aggregator',
    TRADER: 'Trader',
    PROCESSOR: 'Processor',
    LABORATORY: 'Laboratory',
    MANUFACTURER: 'Manufacturer'
};

// 1D Linear Barcode Component (Code 39 Standard)
export function LinearBarcode({ value, width = 260, height = 55 }) {
    const CODE39_MAP = {
        '0': '101001101101', '1': '110100101011', '2': '101100101011', '3': '110110010101',
        '4': '101001101011', '5': '110100110101', '6': '101100110101', '7': '101001011011',
        '8': '110100101101', '9': '101100101101', 'A': '110101001011', 'B': '101101001011',
        'C': '110110100101', 'D': '101011001011', 'E': '110101100101', 'F': '101101100101',
        'G': '101010011011', 'H': '110101001101', 'I': '101101001101', 'J': '101011001101',
        'K': '110101010011', 'L': '101101010011', 'M': '110110101001', 'N': '101011010011',
        'O': '110101101001', 'P': '101101101001', 'Q': '101010110011', 'R': '110101011001',
        'S': '101101011001', 'T': '101011011001', 'U': '110010101011', 'V': '100110101011',
        'W': '110011010101', 'X': '100101101011', 'Y': '110010110101', 'Z': '100110110101',
        '-': '100101011011', '.': '110010101101', ' ': '100110101101', '$': '100100100101',
        '/': '100100101001', '+': '100101001001', '%': '101001001001', '*': '100101101101'
    };

    const str = `*${(value || '').toUpperCase()}*`;
    let bits = '';
    for (let char of str) {
        bits += (CODE39_MAP[char] || CODE39_MAP['*']) + '0';
    }

    const barWidth = width / bits.length;

    return (
        <div style={{ textAlign: 'center', background: '#ffffff', padding: '12px', borderRadius: '8px', display: 'inline-block' }}>
            <svg width={width} height={height} style={{ display: 'block', margin: '0 auto' }}>
                {bits.split('').map((bit, idx) => (
                    bit === '1' ? (
                        <rect
                            key={idx}
                            x={idx * barWidth}
                            y={0}
                            width={barWidth + 0.2}
                            height={height}
                            fill="#000000"
                        />
                    ) : null
                ))}
            </svg>
            <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#111', fontWeight: 'bold', letterSpacing: '1px', display: 'block', marginTop: '4px' }}>
                {value}
            </span>
        </div>
    );
}

export function Shell({ children }) {
    const session = authService.session();
    const navigate = useNavigate();
    const logout = () => { authService.logout(); navigate('/login'); };

    return (
        <div className="shell">
            <header className="shell-head">
                <Link className="brand" to="/dashboard">
                    <span className="brand-mark">✦</span>
                    <span>Vana<span className="brand-accent">Trace</span></span>
                </Link>
                <nav className="shell-nav" style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <Link to="/dashboard">Workspace</Link>
                    <Link to="/products/catalog">Barcodes & QR Registry</Link>
                    <Link to="/batches">Inventory</Link>
                    {session?.role === 'ADMIN' && <Link to="/admin/verifications">Verifications</Link>}
                </nav>
                <div className="shell-user">
                    <span className="role-tag">{roleLabels[session?.role] || 'Partner'}</span>
                    <button className="plain-button" onClick={logout}>Sign out</button>
                </div>
            </header>
            <main className="shell-main">{children}</main>
        </div>
    );
}

export function IncomingTransfers() {
    const [transfers, setTransfers] = useState([]);
    const [error, setError] = useState('');
    const load = () => custodyService.listIncoming().then(r => setTransfers(r.data)).catch(err => setError(err.response?.data?.detail || 'Failed to load transfers'));

    useEffect(() => { load(); }, []);

    const action = async (id, act) => {
        try {
            if (act === 'accept') await custodyService.accept(id);
            else await custodyService.reject(id);
            load();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to perform action');
        }
    };

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">CUSTODY TRANSFER QUEUE</p>
                    <h1>Incoming Batches</h1>
                </div>
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <div className="panel table-panel">
                {transfers.length === 0 ? (
                    <div className="empty-table">
                        <span>◎</span>
                        <h2>No incoming batch transfers pending</h2>
                    </div>
                ) : (
                    <table style={{ width: '100%', textAlign: 'left' }}>
                        <thead>
                            <tr>
                                <th>Transfer ID</th>
                                <th>Batch ID</th>
                                <th>From User</th>
                                <th>Quantity</th>
                                <th>Date & Time</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transfers.map(t => (
                                <tr key={t.id}>
                                    <td>#{t.id}</td>
                                    <td><strong>{t.batch_id}</strong></td>
                                    <td>User #{t.from_user_id}</td>
                                    <td>{t.quantity}</td>
                                    <td>{formatDateTime(t.created_at || t.updated_at)}</td>
                                    <td>
                                        <button className="button button-dark" style={{ marginRight: '8px' }} onClick={() => action(t.id, 'accept')}>Accept</button>
                                        <button className="button button-outline" onClick={() => action(t.id, 'reject')}>Reject</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </Shell>
    );
}

export function ProcessBatch() {
    const { batchId } = useParams();
    const navigate = useNavigate();
    const [batch, setBatch] = useState(null);
    const [form, setForm] = useState({ process_type: 'EXTRACTION', input_quantity: '', output_quantity: '', facility_location: '', notes: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (batchId) {
            batchService.get(batchId)
                .then(res => {
                    const b = res.data;
                    setBatch(b);
                    if (b && b.quantity) {
                        setForm(prev => ({
                            ...prev,
                            input_quantity: String(b.quantity),
                            output_quantity: String((Number(b.quantity) * 0.9).toFixed(2)) // Default 10% processing loss suggestion
                        }));
                    }
                })
                .catch(err => {
                    console.error('Failed to load batch info:', err);
                })
                .finally(() => setLoading(false));
        }
    }, [batchId]);

    const submit = async (e) => {
        e.preventDefault();
        setError('');

        const inQty = Number(form.input_quantity);
        const outQty = Number(form.output_quantity);

        if (batch && inQty > Number(batch.quantity)) {
            setError(`Input quantity (${inQty} ${batch.unit}) exceeds available batch quantity (${batch.quantity} ${batch.unit})`);
            return;
        }

        if (outQty > inQty) {
            setError(`Output quantity (${outQty}) cannot be greater than input quantity (${inQty})`);
            return;
        }

        try {
            await processingService.process(batchId, {
                ...form,
                input_quantity: inQty,
                output_quantity: outQty
            });
            navigate('/dashboard');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] : ''}: ${d.msg}`).join(' | '));
            } else if (typeof detail === 'object' && detail !== null) {
                setError(JSON.stringify(detail));
            } else {
                setError(detail || 'Failed to record processing');
            }
        }
    };

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">PROCESSOR WORKSPACE</p>
                    <h1>Record Processing Stage</h1>
                    <p className="muted">Batch: <strong>{batchId}</strong></p>
                </div>
            </div>

            {batch && (
                <div className="panel" style={{ marginBottom: '20px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <p className="eyebrow" style={{ marginBottom: '8px' }}>BATCH DETAILS</p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', fontSize: '0.9rem' }}>
                        <div><strong>Herb:</strong> {batch.herb_name} ({batch.scientific_name})</div>
                        <div><strong>Available Quantity:</strong> <span style={{ color: '#4ade80', fontWeight: 'bold' }}>{batch.quantity} {batch.unit}</span></div>
                        <div><strong>Origin:</strong> {batch.collection_location}</div>
                        <div><strong>Collection Date & Time:</strong> {formatDateTime(batch.collection_date)}</div>
                        <div><strong>Status:</strong> {batch.status}</div>
                    </div>
                </div>
            )}

            <form className="panel batch-form" onSubmit={submit}>
                {error && <div className="alert alert-error">{error}</div>}
                <div className="form-grid">
                    <label>Process Type
                        <input required value={form.process_type} onChange={e => setForm({ ...form, process_type: e.target.value })} placeholder="e.g. EXTRACTION, GRINDING" />
                    </label>
                    <label>Facility Location
                        <input required value={form.facility_location} onChange={e => setForm({ ...form, facility_location: e.target.value })} placeholder="Mysuru Facility #2" />
                    </label>
                </div>
                <div className="form-grid">
                    <label>Input Quantity {batch && `(Max ${batch.quantity} ${batch.unit})`}
                        <input required type="number" step="0.01" max={batch ? batch.quantity : undefined} value={form.input_quantity} onChange={e => setForm({ ...form, input_quantity: e.target.value })} />
                    </label>
                    <label>Output Quantity (Yield)
                        <input required type="number" step="0.01" max={form.input_quantity || undefined} value={form.output_quantity} onChange={e => setForm({ ...form, output_quantity: e.target.value })} />
                    </label>
                </div>
                <label>Notes / Processing Logs<textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Extraction details, solvent ratio, yields..." /></label>
                <button className="button button-dark" disabled={loading}>Submit Processing Record</button>
            </form>
        </Shell>
    );
}

export function AddLabTest() {
    const { batchId } = useParams();
    const navigate = useNavigate();
    const [form, setForm] = useState({ certificate_id: '', result: 'PASSED', report_url: '', notes: '' });
    const [error, setError] = useState('');

    const submit = async (e) => {
        e.preventDefault();
        try {
            await laboratoryService.addReport(batchId, form);
            navigate('/dashboard');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] : ''}: ${d.msg}`).join(' | '));
            } else if (typeof detail === 'object' && detail !== null) {
                setError(JSON.stringify(detail));
            } else {
                setError(detail || 'Failed to submit lab report');
            }
        }
    };

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">LABORATORY TESTING</p>
                    <h1>Issue Lab Certificate</h1>
                    <p className="muted">Batch: {batchId}</p>
                </div>
            </div>
            <form className="panel batch-form" onSubmit={submit}>
                {error && <div className="alert alert-error">{error}</div>}
                <div className="form-grid">
                    <label>Certificate ID<input required value={form.certificate_id} onChange={e => setForm({ ...form, certificate_id: e.target.value })} placeholder="AYUSH-LAB-2026-001" /></label>
                    <label>Result
                        <select value={form.result} onChange={e => setForm({ ...form, result: e.target.value })}>
                            <option value="PASSED">PASSED</option>
                            <option value="FAILED">FAILED</option>
                        </select>
                    </label>
                </div>
                <label>Report URL / Document Link<input value={form.report_url} onChange={e => setForm({ ...form, report_url: e.target.value })} placeholder="https://..." /></label>
                <label>Analysis Notes<textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Purity, Heavy Metals, Pesticides..." /></label>
                <button className="button button-dark">Submit Certificate</button>
            </form>
        </Shell>
    );
}

export function CreateProduct() {
    const [batches, setBatches] = useState([]);
    const [selectedBatch, setSelectedBatch] = useState(null);
    const [form, setForm] = useState({ name: '', description: '', batch_id: '', quantity_used: '' });
    const [product, setProduct] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        batchService.list().then(res => {
            setBatches(res.data || []);
            if (res.data && res.data.length > 0) {
                const first = res.data[0];
                setForm(prev => ({ ...prev, batch_id: first.batch_id }));
                setSelectedBatch(first);
            }
        }).catch(err => console.error(err));
    }, []);

    const handleBatchChange = (bId) => {
        const found = batches.find(b => b.batch_id === bId);
        setForm(prev => ({ ...prev, batch_id: bId }));
        setSelectedBatch(found || null);
    };

    const submit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const res = await productService.create({
                ...form,
                quantity_used: Number(form.quantity_used)
            });
            setProduct(res.data);
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] : ''}: ${d.msg}`).join(' | '));
            } else if (typeof detail === 'object' && detail !== null) {
                setError(JSON.stringify(detail));
            } else {
                setError(detail || err.message || 'Failed to create product.');
            }
        }
    };

    const printQR = () => { window.print(); };

    if (product) {
        const verifyUrl = `${window.location.origin}/verify/${product.product_id}`;
        return (
            <Shell>
                <div className="success-panel batch-success">
                    <span>✓</span>
                    <p className="eyebrow">PRODUCT CREATED & BARCODE / QR GENERATED</p>
                    <h1>{product.product_id}</h1>
                    <p><strong>{product.name}</strong></p>
                    <p className="muted">Manufactured Date & Time: <strong>{formatDateTime(product.created_at)}</strong></p>
                    <p className="muted">Public verification URL: <a href={verifyUrl} target="_blank" rel="noreferrer">{verifyUrl}</a></p>

                    <div style={{ marginTop: '20px', display: 'flex', gap: '20px', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }}>
                        <div style={{ background: '#fff', padding: '16px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                            <p style={{ fontSize: '0.75rem', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>2D QR CODE (SCAN WITH CAMERA)</p>
                            <QRCodeSVG id="product-qr-svg" value={verifyUrl} size={180} includeMargin={true} />
                        </div>
                        <div style={{ background: '#fff', padding: '16px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                            <p style={{ fontSize: '0.75rem', color: '#666', marginBottom: '8px', fontWeight: 'bold' }}>1D LINEAR BARCODE</p>
                            <LinearBarcode value={product.product_id} width={240} height={70} />
                        </div>
                    </div>

                    <div className="success-actions" style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <button onClick={printQR} className="button button-outline">Print Barcode Labels</button>
                        <a href={verifyUrl} target="_blank" rel="noreferrer" className="button button-dark">Open Verification Page</a>
                        <Link className="button button-outline" to="/products/catalog">View Barcodes Registry</Link>
                    </div>
                </div>
            </Shell>
        );
    }

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">MANUFACTURER</p>
                    <h1>Create Final Product</h1>
                </div>
            </div>
            <form className="panel batch-form" onSubmit={submit}>
                {error && <div className="alert alert-error">{error}</div>}

                <div className="form-grid">
                    <label>Product Name
                        <input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Ashwagandha Capsules" />
                    </label>
                    <label>Description
                        <input required value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Standardized Extract 500mg" />
                    </label>
                </div>

                <div className="form-grid">
                    <label>Batch ID (Select or Enter Manually)
                        {batches.length > 0 ? (
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <select
                                    value={form.batch_id}
                                    onChange={e => handleBatchChange(e.target.value)}
                                    style={{ flex: 1 }}
                                >
                                    <option value="">Select from available batches...</option>
                                    {batches.map(b => (
                                        <option key={b.batch_id} value={b.batch_id}>
                                            {b.batch_id} — {b.herb_name} ({b.quantity} {b.unit})
                                        </option>
                                    ))}
                                </select>
                                <input
                                    required
                                    value={form.batch_id}
                                    onChange={e => handleBatchChange(e.target.value)}
                                    placeholder="or type Batch ID"
                                    style={{ flex: 1 }}
                                />
                            </div>
                        ) : (
                            <input
                                required
                                value={form.batch_id}
                                onChange={e => handleBatchChange(e.target.value)}
                                placeholder="e.g. ASHW-2026-000001"
                            />
                        )}
                    </label>
                    <label>Quantity Used
                        <input required type="number" min="0.01" step="0.01" value={form.quantity_used} onChange={e => setForm({ ...form, quantity_used: e.target.value })} placeholder="e.g. 20" />
                    </label>
                </div>

                {selectedBatch && (
                    <div className="info-panel" style={{ marginTop: '16px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                        <p className="eyebrow" style={{ marginBottom: '8px' }}>SELECTED BATCH PROVENANCE</p>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', fontSize: '0.9rem' }}>
                            <div><strong>Herb:</strong> {selectedBatch.herb_name}</div>
                            <div><strong>Scientific:</strong> {selectedBatch.scientific_name}</div>
                            <div><strong>Location:</strong> {selectedBatch.collection_location}</div>
                            <div><strong>Collection Date & Time:</strong> {formatDateTime(selectedBatch.collection_date)}</div>
                            <div><strong>Available:</strong> {selectedBatch.quantity} {selectedBatch.unit}</div>
                            <div><strong>Status:</strong> {selectedBatch.status}</div>
                        </div>
                    </div>
                )}

                <button className="button button-dark" style={{ marginTop: '20px' }}>Create Product & Generate Barcodes</button>
            </form>
        </Shell>
    );
}

export function TransferBatch() {
    const { batchId } = useParams();
    const navigate = useNavigate();
    const [batch, setBatch] = useState(null);
    const [toUserId, setToUserId] = useState('');
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        userService.list().then(res => setUsers(res.data)).catch(err => console.error(err));
        if (batchId) {
            batchService.get(batchId).then(res => setBatch(res.data)).catch(err => console.error(err));
        }
    }, [batchId]);

    const submit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await custodyService.transfer(batchId, { to_user_id: Number(toUserId) });
            navigate('/dashboard');
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] : ''}: ${d.msg}`).join(' | '));
            } else if (typeof detail === 'object' && detail !== null) {
                setError(JSON.stringify(detail));
            } else {
                setError(detail || 'Failed to transfer batch.');
            }
        }
    };

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">CUSTODY TRANSFER</p>
                    <h1>Transfer Batch {batchId}</h1>
                </div>
            </div>

            {batch && (
                <div className="panel" style={{ marginBottom: '20px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <p className="eyebrow" style={{ marginBottom: '8px' }}>BATCH INFORMATION</p>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', fontSize: '0.9rem' }}>
                        <div><strong>Herb:</strong> {batch.herb_name} ({batch.scientific_name})</div>
                        <div><strong>Quantity:</strong> {batch.quantity} {batch.unit}</div>
                        <div><strong>Origin:</strong> {batch.collection_location}</div>
                        <div><strong>Collection Date & Time:</strong> {formatDateTime(batch.collection_date)}</div>
                        <div><strong>Status:</strong> {batch.status}</div>
                    </div>
                </div>
            )}

            <form className="panel batch-form" onSubmit={submit}>
                {error && <div className="alert alert-error">{error}</div>}
                <label>Recipient User & Role
                    <select value={toUserId} onChange={e => setToUserId(e.target.value)} required>
                        <option value="">Select a user...</option>
                        {users.map(u => (
                            <option key={u.id} value={u.id}>{u.full_name} ({u.role}) — ID #{u.id}</option>
                        ))}
                    </select>
                </label>
                <button className="button button-dark" style={{ marginTop: '20px' }}>Initiate Transfer</button>
            </form>
        </Shell>
    );
}

export function ProductsCatalog() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState('ALL'); // 'ALL' | 'QR' | 'BARCODE'

    useEffect(() => {
        productService.list().then(res => {
            setProducts(res.data || []);
        }).catch(err => console.error(err)).finally(() => setLoading(false));
    }, []);

    const printCatalog = () => { window.print(); };

    return (
        <Shell>
            <div className="workspace-head">
                <div>
                    <p className="eyebrow">VERIFICATION HUB</p>
                    <h1>Barcodes & QR Code Registry</h1>
                    <p className="muted">Scan 2D QR Code with Google Lens or 1D Barcode with any commercial scanner to open the verified product journey.</p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        className={`button ${viewMode === 'ALL' ? 'button-dark' : 'button-outline'}`}
                        onClick={() => setViewMode('ALL')}
                    >
                        Show All
                    </button>
                    <button
                        className={`button ${viewMode === 'QR' ? 'button-dark' : 'button-outline'}`}
                        onClick={() => setViewMode('QR')}
                    >
                        QR Codes
                    </button>
                    <button
                        className={`button ${viewMode === 'BARCODE' ? 'button-dark' : 'button-outline'}`}
                        onClick={() => setViewMode('BARCODE')}
                    >
                        1D Barcodes
                    </button>
                    <button onClick={printCatalog} className="button button-dark">🖨 Print Barcode Labels</button>
                </div>
            </div>

            {loading ? (
                <div className="loading-state">Loading product barcode registry...</div>
            ) : products.length === 0 ? (
                <div className="panel empty-table">
                    <span>◎</span>
                    <h2>No Products Registered Yet</h2>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
                    {products.map(p => {
                        const verifyUrl = `${window.location.origin}/verify/${p.product_id}`;
                        return (
                            <div key={p.product_id} className="panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '24px', position: 'relative' }}>
                                <span className="eyebrow" style={{ fontSize: '0.75rem', marginBottom: '4px' }}>{p.product_id}</span>
                                <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{p.name}</h3>
                                <small style={{ color: '#4ade80', fontSize: '0.75rem', marginBottom: '8px' }}>Created: {formatDateTime(p.created_at)}</small>
                                <p style={{ fontSize: '0.85rem', color: '#a0a0a0', marginBottom: '16px', flex: 1 }}>{p.description}</p>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center', width: '100%', marginBottom: '16px' }}>
                                    {(viewMode === 'ALL' || viewMode === 'QR') && (
                                        <div style={{ background: '#fff', padding: '16px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
                                            <p style={{ fontSize: '0.7rem', color: '#666', fontWeight: 'bold', marginBottom: '8px' }}>2D QR CODE (GOOGLE LENS & CAMERA)</p>
                                            <QRCodeSVG id={`qr-${p.product_id}`} value={verifyUrl} size={160} includeMargin={true} />
                                        </div>
                                    )}

                                    {(viewMode === 'ALL' || viewMode === 'BARCODE') && (
                                        <div style={{ background: '#fff', padding: '16px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', width: '100%', maxWidth: '280px' }}>
                                            <p style={{ fontSize: '0.7rem', color: '#666', fontWeight: 'bold', marginBottom: '8px' }}>1D LINEAR BARCODE</p>
                                            <LinearBarcode value={p.product_id} width={230} height={50} />
                                        </div>
                                    )}
                                </div>

                                <p className="muted" style={{ fontSize: '0.75rem', wordBreak: 'break-all', marginBottom: '16px' }}>
                                    Target: <a href={verifyUrl} target="_blank" rel="noreferrer">{verifyUrl}</a>
                                </p>

                                <div style={{ marginTop: '12px', width: '100%', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '12px', marginBottom: '16px' }}>
                                    <p style={{ fontSize: '0.7rem', color: '#888', fontWeight: 'bold', marginBottom: '8px', letterSpacing: '0.5px' }}>
                                        VERIFIED SUPPLY CHAIN PIPELINE
                                    </p>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>🌿 COLLECTOR ✓</span>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>📦 AGGREGATOR ✓</span>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>🤝 TRADER ✓</span>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>🏭 PROCESSOR ✓</span>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>🧪 LAB REPORT ✓</span>
                                        <span style={{ background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '4px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold' }}>💊 MANUFACTURED ✓</span>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', gap: '8px', width: '100%' }}>
                                    <a href={verifyUrl} target="_blank" rel="noreferrer" className="button button-dark" style={{ flex: 1, fontSize: '0.8rem', padding: '10px', textAlign: 'center' }}>
                                        Open Traceability Journey →
                                    </a>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </Shell>
    );
}

