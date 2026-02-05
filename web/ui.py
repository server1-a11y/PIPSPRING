# web/ui.py

HTML_TEMPLATE = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PILEAKERS V10</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f0f12;
            --card-bg: #1a1a1d;
            --purple-primary: #8a2be2;
            --purple-glow: #b388ff;
            --text-main: #e0e0e0;
            --border-color: #2d2d30;
        }
        body { background-color: var(--bg-dark); color: var(--text-main); font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; }
        
        /* Navbar */
        .navbar { background-color: var(--card-bg) !important; border-bottom: 1px solid var(--purple-primary); }
        .navbar-brand { font-size: 1.5rem; letter-spacing: 2px; text-shadow: 0 0 10px var(--purple-primary); }

        /* Cards */
        .card { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .card-header { background-color: rgba(138, 43, 226, 0.1); border-bottom: 1px solid var(--border-color); font-weight: bold; color: var(--purple-glow); }
        
        /* Tabs */
        .nav-tabs { border-bottom: 1px solid var(--border-color); }
        .nav-tabs .nav-link { color: #888; border: none; font-weight: bold; transition: 0.3s; }
        .nav-tabs .nav-link:hover { color: var(--purple-glow); }
        .nav-tabs .nav-link.active { background-color: transparent; border-bottom: 3px solid var(--purple-primary); color: var(--purple-glow); }

        /* Inputs */
        .form-control, .form-control:focus { background-color: #0b0b0d; border: 1px solid #333; color: #fff; }
        .form-control:focus { border-color: var(--purple-primary); box-shadow: 0 0 8px rgba(138, 43, 226, 0.4); }
        label { color: #ccc; margin-bottom: 4px; font-size: 0.9rem; }

        /* Buttons */
        .btn-primary, .btn-success { background-color: var(--purple-primary); border: none; font-weight: bold; letter-spacing: 1px; }
        .btn-primary:hover, .btn-success:hover { background-color: #7b22d1; box-shadow: 0 0 15px var(--purple-primary); }
        .btn-outline-secondary { border-color: #444; color: #aaa; }
        .btn-outline-secondary:hover { background-color: #333; color: #fff; }

        /* Logs & Table */
        .log-box { height: 280px; overflow-y: scroll; background: #000; font-family: monospace; padding: 10px; border: 1px solid #333; border-left: 3px solid var(--purple-primary); }
        .table-dark { background-color: var(--card-bg); }
        .table-dark th { background-color: #252525; color: var(--purple-glow); border-bottom: 2px solid var(--purple-primary); }
        .table-dark td { border-color: #333; vertical-align: middle; }

        /* Text Colors */
        .log-default { color: #00ffcc; }
        .log-err { color: #ff4444; text-shadow: 0 0 5px #ff4444; }
        .log-ok { color: #00ff00; }
        .log-warn { color: #ffcc00; }
        .log-info { color: #00bfff; }
    </style>
</head>
<body>

{% if page == 'login' %}
<div class="container d-flex justify-content-center align-items-center" style="height: 100vh;">
    <div class="card p-5" style="width: 400px; border: 1px solid var(--purple-primary); box-shadow: 0 0 20px rgba(138,43,226,0.3);">
        <h2 class="text-center mb-4" style="color: var(--purple-glow); text-shadow: 0 0 10px var(--purple-primary);">PILEAKERS V10</h2>
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="mb-4">
                <input type="password" name="password" class="form-control form-control-lg text-center" placeholder="ENTER PASSWORD">
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2">ACCESS SYSTEM</button>
        </form>
    </div>
</div>
{% else %}

<nav class="navbar navbar-dark mb-4 py-3">
    <div class="container-fluid px-4">
        <a class="navbar-brand fw-bold" href="#">PILEAKERS <span style="color: var(--purple-glow)">V10</span></a>
        <a href="/logout" class="btn btn-outline-light btn-sm px-3">LOGOUT</a>
    </div>
</nav>

<div class="container-fluid px-4">
    <div class="row">
        <!-- LEFT COLUMN: CONFIG TABS -->
        <div class="col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-header bg-transparent">
                    <ul class="nav nav-tabs card-header-tabs" id="configTabs" role="tablist">
                        <li class="nav-item">
                            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-net" type="button">🌐 Network</button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-target" type="button">🎯 Target</button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-strat" type="button">⚡ Strategy</button>
                        </li>
                    </ul>
                </div>
                
                <div class="card-body">
                    <div class="tab-content" id="configTabsContent">
                        
                        <!-- TAB 1: NETWORK & FEE -->
                        <div class="tab-pane fade show active" id="tab-net" role="tabpanel">
                            <label>Servers:</label>
                            <div class="input-group mb-3">
                                <textarea id="servers" class="form-control" rows="3">{{ config.get('servers', 'https://api.mainnet.minepi.com') }}</textarea>
                                <button class="btn btn-outline-secondary" onclick="saveField('servers')">💾</button>
                                <button class="btn btn-outline-danger" onclick="clearField('servers')">🗑️</button>
                            </div>

                            <label>Fee Payer List (Mnemonics):</label>
                            <div class="input-group mb-3">
                                <textarea id="fee_file" class="form-control" rows="3" placeholder="Paste phrase...">{{ config.get('fee_file', '') }}</textarea>
                                <button class="btn btn-outline-secondary" onclick="saveField('fee_file')">💾</button>
                                <button class="btn btn-outline-danger" onclick="clearField('fee_file')">🗑️</button>
                            </div>

                            <div class="row g-2">
                                <div class="col-6">
                                    <label>Base Fee:</label>
                                    <input type="number" id="base_fee" class="form-control" value="{{ config.get('base_fee', '4000000') }}">
                                </div>
                                <div class="col-6 d-flex align-items-end pb-2">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="auto_fee" {% if config.get('auto_fee', True) %}checked{% endif %}>
                                        <label class="form-check-label">Auto Fee</label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- TAB 2: TARGET -->
                        <div class="tab-pane fade" id="tab-target" role="tabpanel">
                            <label>Master Seed (Topup/Sweep):</label>
                            <div class="input-group mb-3">
                                <input type="password" id="master_seed" class="form-control" value="{{ config.get('master_seed', '') }}">
                                <button class="btn btn-outline-secondary" onclick="saveField('master_seed')">💾</button>
                                <button class="btn btn-outline-danger" onclick="clearField('master_seed')">🗑️</button>
                            </div>

                            <label>Destination Address:</label>
                            <input type="text" id="dest_addr" class="form-control mb-3" value="{{ config.get('dest_addr', 'GD7W6X7AOTMKM2C57UPNRLUOVTZ4P66FG5TOHW2DAOCNKQFF377YPFUX') }}">

                            <label>Memo:</label>
                            <input type="text" id="memo" class="form-control" value="{{ config.get('memo', 'bad9b9d83d') }}">
                        </div>

                        <!-- TAB 3: STRATEGY -->
                        <div class="tab-pane fade" id="tab-strat" role="tabpanel">
                            <div class="p-3 border border-secondary rounded mb-3 bg-dark">
                                <label class="text-warning mb-2">Scheduling Mode:</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="schedMode" id="mode_auto" checked onchange="toggleSched()">
                                    <label class="form-check-label">Auto Detect (Claimable)</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="schedMode" id="mode_manual" onchange="toggleSched()">
                                    <label class="form-check-label">Manual Time</label>
                                </div>
                                
                                <div id="manual_inputs" class="row g-1 mt-2 d-none">
                                    <div class="col-2"><input type="text" id="s_day" class="form-control form-control-sm text-center" placeholder="DD"></div>
                                    <div class="col-2"><input type="text" id="s_mon" class="form-control form-control-sm text-center" placeholder="MM"></div>
                                    <div class="col-3"><input type="text" id="s_year" class="form-control form-control-sm text-center" placeholder="YYYY"></div>
                                    <div class="col-5"><input type="text" id="s_hour" class="form-control form-control-sm text-center" placeholder="HH"></div>
                                    <div class="col-4"><input type="text" id="s_min" class="form-control form-control-sm text-center" placeholder="MM"></div>
                                    <div class="col-4"><input type="text" id="s_sec" class="form-control form-control-sm text-center" placeholder="SS"></div>
                                </div>
                            </div>

                            <div class="row g-2 mb-2">
                                <div class="col-6">
                                    <label>Workers:</label>
                                    <input type="number" id="workers" class="form-control" value="{{ config.get('workers', '1000') }}">
                                </div>
                                <div class="col-6">
                                    <label>Timeout (s):</label>
                                    <input type="number" id="timeout" class="form-control" value="{{ config.get('timeout', '30') }}">
                                </div>
                            </div>
                            
                            <label class="mt-2 text-primary">Auto Topup Settings:</label>
                            <div class="row g-2">
                                <div class="col-6">
                                    <label>Min Gas:</label>
                                    <input type="text" id="min_gas" class="form-control" value="{{ config.get('min_gas', '1.1') }}">
                                </div>
                                <div class="col-6">
                                    <label>Amount:</label>
                                    <input type="text" id="topup_amt" class="form-control" value="{{ config.get('topup_amt', '1.1') }}">
                                </div>
                            </div>
                            
                            <input type="hidden" id="call_before" value="{{ config.get('call_before', '1.7') }}">
                            <input type="hidden" id="latency" value="{{ config.get('latency', '1.7') }}">
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <!-- RIGHT COLUMN: EXECUTION & MONITOR -->
        <div class="col-lg-8">
            <!-- INPUT AREA -->
            <div class="card mb-3">
                <div class="card-header">🚀 TARGET WALLETS</div>
                <div class="card-body">
                    <textarea id="mnemonics" class="form-control mb-3" rows="3" placeholder="Paste target mnemonics here (one per line)...">{{ config.get('mnemonics', '') }}</textarea>
                    <div class="d-flex justify-content-end gap-3">
                         <button onclick="stopTasks()" class="btn btn-outline-danger px-4">STOP / CLEAR</button>
                         <button onclick="startTasks()" class="btn btn-success px-5 py-2">START ENGINE</button>
                    </div>
                </div>
            </div>

            <!-- LOGS -->
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between">
                    <span>💻 SYSTEM LOGS</span>
                    <span class="badge bg-secondary" id="log-count">0</span>
                </div>
                <div id="log-box" class="log-box"></div>
            </div>

            <!-- TABLE -->
            <div class="card">
                <div class="card-header">📊 LIVE STATUS</div>
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0">
                        <thead>
                            <tr>
                                <th width="35%">WALLET</th>
                                <th width="15%">ASSET</th>
                                <th width="15%">AMOUNT</th>
                                <th width="20%">UNLOCK TIME</th>
                                <th width="15%">STATUS</th>
                            </tr>
                        </thead>
                        <tbody id="task-body"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    function toggleSched() {
        const manualBox = document.getElementById('manual_inputs');
        const isManual = document.getElementById('mode_manual').checked;
        manualBox.classList.toggle('d-none', !isManual);
    }

    function saveField(fieldId) {
        const val = document.getElementById(fieldId).value;
        fetch('/api/field/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: fieldId, value: val})
        }).then(r=>r.json()).then(d=>alert(d.msg));
    }

    function clearField(fieldId) {
        if(confirm("Clear this field permanently?")) {
            document.getElementById(fieldId).value = "";
            fetch('/api/field/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: fieldId})
            }).then(r=>r.json());
        }
    }

    function startTasks() {
        const isManual = document.getElementById('mode_manual').checked;
        const payload = {
            servers: document.getElementById('servers').value,
            fee_file: document.getElementById('fee_file').value,
            base_fee: document.getElementById('base_fee').value,
            auto_fee: document.getElementById('auto_fee').checked,
            master_seed: document.getElementById('master_seed').value,
            dest_addr: document.getElementById('dest_addr').value,
            memo: document.getElementById('memo').value,
            workers: document.getElementById('workers').value,
            timeout: document.getElementById('timeout').value,
            call_before: document.getElementById('call_before').value,
            latency: document.getElementById('latency').value,
            min_gas: document.getElementById('min_gas').value,
            topup_amt: document.getElementById('topup_amt').value,
            mnemonics: document.getElementById('mnemonics').value,
            manual_mode: isManual,
            d: document.getElementById('s_day').value,
            m: document.getElementById('s_mon').value,
            y: document.getElementById('s_year').value,
            H: document.getElementById('s_hour').value,
            M: document.getElementById('s_min').value,
            S: document.getElementById('s_sec').value
        };

        fetch('/api/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(d => {
            if(d.status === 'ok') alert(d.msg);
            else alert("Error: " + d.msg);
        });
    }

    function stopTasks() {
        if(confirm("Stop all tracking?")) {
            fetch('/api/stop', {method: 'POST'}).then(r=>r.json()).then(d=>location.reload());
        }
    }

    function pollData() {
        fetch('/api/stream')
        .then(r => r.json())
        .then(data => {
            const logBox = document.getElementById('log-box');
            let newLogsHtml = "";
            let shouldScroll = (logBox.scrollTop + logBox.clientHeight >= logBox.scrollHeight - 50);

            data.logs.forEach(l => {
                newLogsHtml += `<div class="log-${l.type}">[${l.ts}] ${l.msg}</div>`;
            });
            logBox.innerHTML = newLogsHtml;
            if(shouldScroll) logBox.scrollTop = logBox.scrollHeight;
            
            document.getElementById('log-count').innerText = data.logs.length;

            const tbody = document.getElementById('task-body');
            tbody.innerHTML = "";
            data.tasks.forEach(t => {
                let color = "text-white";
                if(t.status.includes("Success")) color = "text-success fw-bold";
                else if(t.status.includes("Fail")) color = "text-danger fw-bold";
                else if(t.status.includes("Fir")) color = "text-warning fw-bold";

                tbody.innerHTML += `
                    <tr>
                        <td class="text-truncate" style="max-width: 150px; font-family:monospace; color:#aaa;">${t.wallet}</td>
                        <td class="text-info">${t.asset}</td>
                        <td class="text-white fw-bold">${t.amount}</td>
                        <td style="color:var(--purple-glow)">${t.schedule}</td>
                        <td class="${color}">${t.status}</td>
                    </tr>
                `;
            });
        });
    }

    setInterval(pollData, 1000);
</script>

{% endif %}
</body>
</html>
"""
