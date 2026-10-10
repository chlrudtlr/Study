'use strict';
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const labels = {RUNNING:'Running',PASS:'Pass',FAIL:'Fail',RETRYING:'Retrying',IDLE:'Idle',ENVIRONMENT:'환경성 불량',GENUINE:'Defect 의심',UNKNOWN:'판단 불가',NONE:'분석 없음',QUEUED:'대기',CHECKING:'상태 확인',PREPARING:'준비',LAUNCHING:'TC 시작',SUCCEEDED:'재투입 성공',FAILED:'재투입 실패'};
const badge = (key, label) => `<span class="badge ${String(key).toLowerCase()}">${escapeHtml(label || labels[key] || key)}</span>`;
const dateTime = (epoch) => epoch ? new Date(epoch * 1000).toLocaleString('ko-KR', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}) : '—';
const timeOnly = (epoch) => new Date(epoch * 1000).toLocaleTimeString('ko-KR',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
let state = null, activeView = 'overview', queueFilter = 'all', apiToken = '', fetching = false, toastTimer;
let detailPort = null, dirtyPolicy = false;

async function api(path, body) {
  const headers = body ? {'Content-Type':'application/json'} : {};
  if (apiToken) headers.Authorization = `Bearer ${apiToken}`;
  const response = await fetch(path, {method:body ? 'POST' : 'GET', headers, body:body ? JSON.stringify(body) : undefined, cache:'no-store'});
  const data = await response.json();
  if (response.status === 401) {
    if (!$('#login-dialog').open) $('#login-dialog').showModal();
    throw new Error(data.error);
  }
  if (!response.ok) throw new Error(data.error || '요청 처리 실패');
  return data;
}

function toast(message, error = false) {
  clearTimeout(toastTimer);
  $('#toast').textContent = message;
  $('#toast').classList.toggle('error', error);
  $('#toast').hidden = false;
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 4500);
}

async function refresh() {
  if (fetching) return;
  fetching = true;
  try {
    state = await api('/api/state');
    $('#loading').hidden = true;
    $('#error-banner').hidden = true;
    $('#connection').classList.remove('offline');
    $('#connection').innerHTML = '<i></i>서버 연결됨';
    $('#last-update').textContent = `업데이트 ${timeOnly(state.server_time)}`;
    render();
  } catch (error) {
    $('#error-banner').hidden = false;
    $('#error-banner').textContent = `업데이트 실패: ${error.message}. 표시된 데이터는 마지막 수신 상태입니다.`;
    $('#loading').hidden = true;
    $('#connection').classList.add('offline');
    $('#connection').innerHTML = '<i></i>연결 확인 필요';
  } finally { fetching = false; }
}

function queueGroup(port) {
  if (port.status === 'RETRYING') return 'active';
  if (!port.blockers.length) return 'ready';
  if (port.classification !== 'ENVIRONMENT' || !port.reviewed) return 'review';
  return 'blocked';
}
function queuePorts() {
  return state.ports.filter(p => ['FAIL','RETRYING'].includes(p.status)).sort((a,b) => {
    const order = {ready:0,active:1,review:2,blocked:3};
    return (order[queueGroup(a)] - order[queueGroup(b)]) || b.updated - a.updated;
  });
}
function eligibility(port) {
  if (port.status === 'RETRYING') return badge('RETRYING','재투입 중');
  const group = queueGroup(port);
  return badge(group, {ready:'재투입 가능',review:'검토 필요',blocked:'차단'}[group]);
}
function latestJob(portId) { return state.jobs.find(j => j.port_id === portId); }

function render() {
  $('#nav-count').textContent = queuePorts().length;
  $$('.view').forEach(v => { v.hidden = v.id !== `view-${activeView}`; });
  renderOverview();
  renderQueue();
  renderHistory();
  if (!dirtyPolicy) fillPolicy();
}

function renderOverview() {
  const ports = state.ports;
  const count = status => ports.filter(p => p.status === status).length;
  const ready = ports.filter(p => p.status === 'FAIL' && !p.blockers.length).length;
  const success = state.job_totals.SUCCEEDED || 0, fail = state.job_totals.FAILED || 0;
  const stats = [
    ['전체 Port',ports.length,'개',`${ports.filter(p => p.online).length} Online · ${ports.filter(p => !p.online).length} Offline`,'server',''],
    ['평가 진행 중',count('RUNNING'),'개','Running · 정상 평가 진행','bolt','green'],
    ['Fail 감지',count('FAIL'),'개','검토 또는 재투입이 필요한 Port','alert','red'],
    ['재투입 가능',ready,'개',`${count('RETRYING')}개 조치 진행 중`,'repeat','blue'],
    ['재투입 성공률',success+fail ? Math.round(success/(success+fail)*100) : '—','%',`${success}건 시작 성공 / ${success+fail}건 조치 완료`,'check','green'],
  ];
  $('#stats').innerHTML = stats.map(([label,value,unit,foot,i,color]) => `<div class="stat-card ${color}"><div class="stat-label">${label}${icon(i)}</div><div class="stat-value">${value}<small>${unit}</small></div><div class="stat-foot">${foot}</div></div>`).join('');
  const config = state.config;
  $('#auto-toggle').setAttribute('aria-checked', String(config.auto_enabled));
  $('#auto-toggle').setAttribute('aria-label', config.auto_enabled ? '자동 재투입 끄기' : '자동 재투입 켜기');
  $('#auto-label').textContent = config.auto_enabled ? 'ON' : 'OFF';
  $('#auto-description').textContent = `검토 완료 + 장비 조건 충족 · 최대 ${config.max_retries}회 · 간격 ${config.cooldown_seconds}초 · 신뢰도 ${Math.round(config.min_confidence*100)}% 이상`;
  $('#auto-count').textContent = config.auto_enabled ? '허용된 대상 자동 등록 중' : '현재 수동 재투입 모드';
  $('#racks').innerHTML = ['A05C','A08B','A13B','LSB'].map(rack => {
    const items = ports.filter(p => p.rack === rack);
    return `<article class="rack-card"><div class="rack-heading"><div class="rack-name">${icon('server')}${rack} Rack</div><span class="rack-summary">${items.length} PORTS · ${items.filter(p => p.status === 'FAIL').length} FAIL</span></div>${items.map(p => `<button class="port-card" data-detail="${escapeHtml(p.id)}" aria-label="${escapeHtml(p.id)} ${escapeHtml(p.tc)} 상세"><div class="port-top"><div class="port-address">${escapeHtml(p.pc)}<span>P${p.port}</span></div>${badge(p.status)}</div><div class="port-tc">${escapeHtml(p.tc)}</div><div class="port-meta"><span>${escapeHtml(p.model)} · ${escapeHtml(p.fw)}</span><span class="${p.online?'':'port-offline'}">${p.online?'Online':'Offline'}</span></div></button>`).join('')}</article>`;
  }).join('');
  const queue = queuePorts();
  $('#overview-queue-count').textContent = queue.length;
  $('#overview-queue').innerHTML = queueTable(queue.slice(0,5), true);
  $('#activity').innerHTML = state.events.slice(0,5).map(e => `<div class="activity-row"><div class="activity-dot">${icon(['ERROR','FAIL','WARNING'].includes(e.kind)?'alert':e.kind==='RETRY'?'repeat':'check')}</div><div class="activity-text">${escapeHtml(e.message)}<small>${escapeHtml(e.port_id || 'SYSTEM')} · ${escapeHtml(e.kind)}</small></div><time>${timeOnly(e.time)}</time></div>`).join('') || '<div class="empty-state">아직 활동이 없습니다.</div>';
  const failPorts = ports.filter(p => p.status === 'FAIL');
  $('#distribution').innerHTML = ['ENVIRONMENT','GENUINE','UNKNOWN'].map(kind => {
    const n = failPorts.filter(p => p.classification === kind).length;
    return `<div class="dist-row ${kind.toLowerCase()}"><span>${labels[kind]}</span><progress max="${failPorts.length || 1}" value="${n}" aria-label="${labels[kind]} ${n}건"></progress><b>${n}건</b></div>`;
  }).join('');
}

function queueTable(ports, compact = false) {
  if (!ports.length) return '<div class="empty-state">조건에 맞는 재투입 대상이 없습니다.</div>';
  return `<div class="table-wrap"><table><thead><tr><th>RACK / PORT</th><th>TEST CASE</th><th>분석 결과 / 원인</th><th>재투입 상태</th>${compact?'':'<th>최신 조치</th>'}<th>조치</th></tr></thead><tbody>${ports.map(p => {
    const job = latestJob(p.id);
    const reason = p.status === 'RETRYING' ? '등록한 조치가 실행 중입니다.' : p.blockers[0] || '실행 전 필수 조건 충족';
    return `<tr><td><div class="cell-title">${escapeHtml(p.rack)} <span class="muted">/</span> P${p.port}</div><div class="cell-sub mono">${escapeHtml(p.pc)}</div></td><td><div class="mono cell-title">${escapeHtml(p.tc)}</div><div class="cell-sub">${escapeHtml(p.model)} · ${escapeHtml(p.owner)}</div></td><td class="cause">${badge(p.classification)}<div class="cell-sub">${escapeHtml(p.cause)}</div><div class="confidence"><progress max="1" value="${p.confidence}" aria-label="모의 분석 신뢰도 ${Math.round(p.confidence*100)}%"></progress>예시 ${Math.round(p.confidence*100)}%</div></td><td>${eligibility(p)}<div class="cell-sub">${escapeHtml(reason)}</div><div class="cell-sub">${p.attempts} / ${state.config.max_retries}회</div></td>${compact?'':`<td>${job?`${badge(job.status)}<div class="cell-sub">${dateTime(job.created)} · ${job.source==='AUTO'?'자동':'수동'}</div>`:'<span class="muted">조치 없음</span>'}</td>`}<td><div class="row-action"><button class="button compact ${p.blockers.length?'':'primary'}" data-retry="${escapeHtml(p.id)}" ${p.blockers.length?'disabled':''} title="${escapeHtml(p.blockers.join(' · '))}">${icon('repeat')}재투입</button><button class="text-button" data-detail="${escapeHtml(p.id)}">상세</button></div></td></tr>`;
  }).join('')}</tbody></table></div>`;
}

function renderQueue() {
  const rack = $('#rack-filter').value, text = $('#search').value.trim().toLowerCase();
  const queue = queuePorts();
  const filtered = queue.filter(p => (queueFilter === 'all' || queueGroup(p) === queueFilter) && (rack === 'all' || p.rack === rack) && `${p.pc} ${p.tc} ${p.cause} ${p.model}`.toLowerCase().includes(text));
  $('#queue-total').textContent = `전체 ${queue.length}건 · 표시 ${filtered.length}건`;
  $('#queue-table').innerHTML = queueTable(filtered);
}

function jobTable(jobs) {
  return `<div class="table-wrap"><table><thead><tr><th>시각 / TC</th><th>방식 / 횟수</th><th>결과</th><th>내용</th></tr></thead><tbody>${jobs.map(j => `<tr><td>${dateTime(j.created)}<div class="cell-sub mono">${escapeHtml(j.tc)}</div></td><td>${j.source==='AUTO'?'자동':'수동'} · ${j.attempt}회<div class="cell-sub mono">${escapeHtml(j.id.slice(0,8))}</div></td><td>${badge(j.status)}</td><td class="history-cell">${escapeHtml(j.message)}${j.stages.length?`<details><summary class="cell-sub">실행 단계 ${j.stages.length}개</summary>${j.stages.map(s=>`<div class="cell-sub">${timeOnly(s.time)} · ${escapeHtml(s.message)}</div>`).join('')}</details>`:''}</td></tr>`).join('')}</tbody></table></div>`;
}

function renderHistory() {
  const open = new Set($$('#history details[open]').map(d => d.dataset.port));
  const grouped = new Map();
  for (const job of state.jobs) {
    if (!grouped.has(job.port_id)) grouped.set(job.port_id, []);
    grouped.get(job.port_id).push(job);
  }
  $('#history').innerHTML = [...grouped].map(([portId,jobs]) => {
    const latest = jobs[0];
    return `<details class="history-item" data-port="${escapeHtml(portId)}" ${open.has(portId)?'open':''}><summary><div class="history-main"><span class="history-arrow">›</span><div><strong class="mono">${escapeHtml(portId)}</strong><div class="cell-sub mono">${escapeHtml(latest.tc)} · ${dateTime(latest.created)}</div></div>${badge(latest.status)}</div><div class="history-summary-meta small muted">${latest.source==='AUTO'?'자동':'수동'} · ${latest.attempt}회차 · 이력 ${jobs.length}건 <span class="counter">펼치기</span></div></summary><div class="history-extra">${jobTable(jobs)}</div></details>`;
  }).join('') || '<div class="empty-state">아직 재투입 이력이 없습니다. 대기 목록에서 재투입을 실행해보세요.</div>';
}

function fillPolicy() {
  const f = $('#policy-form');
  f.elements.max_retries.value = state.config.max_retries;
  f.elements.cooldown_seconds.value = state.config.cooldown_seconds;
  f.elements.min_confidence.value = Math.round(state.config.min_confidence * 100);
}

async function showDetail(portId) {
  try {
    const detail = await api(`/api/ports/${encodeURIComponent(portId)}`);
    detailPort = portId;
    const p = detail.port;
    $('#detail-title').textContent = `${p.pc} / Port ${p.port}`;
    const info = [['Test Case',p.tc],['Device / FW',`${p.model} / ${p.fw}`],['담당자',p.owner],['PC / SSD',`${p.online?'Online':'Offline'} / ${p.device_present?'인식':'미인식'}`],['예약 / 점유',`${p.reservation_ok?'예약 확인':'예약 필요'} / ${p.busy?'사용 중':'비어 있음'}`],['재투입 횟수',`${p.attempts} / ${state.config.max_retries}회`]];
    $('#detail-content').innerHTML = `<div class="detail-body"><div class="detail-badges">${badge(p.status)}${badge(p.classification)}${p.status==='FAIL'?eligibility(p):''}</div><dl class="detail-info">${info.map(([k,v])=>`<div><dt>${k}</dt><dd>${escapeHtml(v)}</dd></div>`).join('')}</dl>${p.issue_id?`<section class="detail-section"><h3>분석 근거 <span class="badge demo">예시 분석 ${Math.round(p.confidence*100)}%</span></h3><div class="evidence">${escapeHtml(p.evidence)}</div><p class="field-help">실제 AI가 분석한 결과가 아닌 데모용 분류와 신뢰도입니다.</p><div class="cell-sub mono">Fail ID: ${escapeHtml(p.issue_id)}</div><div class="cell-sub mono">Log: ${escapeHtml(p.log_path)}</div><div class="cell-sub mono">Dump: ${escapeHtml(p.dump_path)}</div><p class="field-help">경로와 보존 상태는 모의 데이터입니다. 이 데모에는 실제 Log / Dump 파일이 없습니다.</p></section>`:''}${p.status==='FAIL'?`<section class="detail-section"><h3>재투입 조건</h3>${p.blockers.length?`<ul class="blockers-list">${p.blockers.map(r=>`<li>• ${escapeHtml(r)}</li>`).join('')}</ul>`:'<div class="ready-note">모든 필수 조건을 충족했습니다. 수동 재투입이 가능합니다.</div>'}<div class="field-help">자동 실행 조건: ${p.auto_blockers.length?escapeHtml(p.auto_blockers.join(' · ')):'충족'}</div>${p.review_note?`<div class="cell-sub">최근 검토 근거: ${escapeHtml(p.review_note)}</div>`:''}<div class="detail-actions"><button class="button primary" data-retry="${escapeHtml(p.id)}" ${p.blockers.length?'disabled':''}>${icon('repeat')}수동 재투입</button></div></section><form id="review-form" class="dialog-form review-form"><h3>담당자 검토</h3><label>최종 분류<select name="classification">${['ENVIRONMENT','GENUINE','UNKNOWN'].map(k=>`<option value="${k}" ${k===p.classification?'selected':''}>${labels[k]}</option>`).join('')}</select></label><label>검토 근거<textarea name="note" minlength="3" maxlength="1000" required placeholder="환경 상태와 원본 Log를 확인한 근거를 입력하세요.">${escapeHtml(p.review_note || '')}</textarea></label><label class="inline-label"><input type="checkbox" name="auto_allowed" ${p.auto_allowed?'checked':''}>이 Fail의 자동 재투입 허용 (환경성 분류에만 적용)</label><button class="button" type="submit">검토 저장</button></form>`:''}<section class="detail-section"><h3>재투입 이력 <span class="counter">${detail.jobs.length}</span></h3>${detail.jobs.length?jobTable(detail.jobs):'<p class="field-help">아직 재투입 이력이 없습니다.</p>'}</section><section class="detail-section"><h3>원본 Fail 기록 <span class="counter">${detail.failures.length}</span></h3>${detail.failures.map(f=>`<details class="original-failure"><summary>${dateTime(f.updated)} · ${escapeHtml(f.issue_id)} · ${escapeHtml(f.cause)}</summary><pre class="evidence">${escapeHtml(f.evidence)}</pre><div class="field-help">최초 분류: ${labels[f.classification]} · 원본 스냅샷 유지</div></details>`).join('') || '<p class="field-help">Fail 기록이 없습니다.</p>'}</section></div>`;
    if (!$('#detail-dialog').open) $('#detail-dialog').showModal();
    $('#review-form')?.addEventListener('submit', async e => {
      e.preventDefault();
      const f = e.target;
      await mutate('/api/review', {port_id:portId,classification:f.elements.classification.value,note:f.elements.note.value,auto_allowed:f.elements.auto_allowed.checked}, '담당자 검토를 저장했습니다.', f.querySelector('button[type=submit]'));
      await showDetail(portId);
    });
  } catch (error) { toast(error.message, true); }
}

async function mutate(path, body, message, button) {
  if (button) button.disabled = true;
  try {
    await api(path,body);
    toast(message);
    await refresh();
    return true;
  } catch (error) { toast(error.message,true); return false; }
  finally { if (button?.isConnected) button.disabled = false; }
}

function navigate(view) {
  if (!['overview','queue','history','policy'].includes(view)) return;
  activeView = view;
  history.replaceState(null,'',`#${view}`);
  const titles = {overview:['Smart Rack Dashboard','원격 평가 현황부터 재투입까지, 하나의 흐름으로 관리하세요.','Dashboard'],queue:['재투입 관리','실패 원인과 실행 조건을 확인하고, 필요한 평가를 다시 시작하세요.','재투입 관리'],history:['실행 이력','Port별 최신 조치와 이전 재투입 과정을 추적하세요.','실행 이력'],policy:['자동화 정책','재투입 허용 조건과 실행 제한을 한곳에서 관리하세요.','자동화 정책']};
  const [title,description,crumb] = titles[view];
  $('#page-title').textContent = title;
  $('#page-description').textContent = description;
  $('#breadcrumb').textContent = crumb;
  $$('.nav-item').forEach(b => { b.classList.toggle('active', b.dataset.view===view); if(b.dataset.view===view) b.setAttribute('aria-current','page'); else b.removeAttribute('aria-current'); });
  if (state) render();
}

document.addEventListener('click', async event => {
  const target = event.target.closest('button');
  if (!target) return;
  if (target.dataset.view) navigate(target.dataset.view);
  if (target.dataset.detail) await showDetail(target.dataset.detail);
  if (target.dataset.retry) {
    const ok = await mutate('/api/retry',{port_id:target.dataset.retry},'재투입을 등록했습니다. 실행 이력에서 진행 상황을 확인하세요.',target);
    if (ok && $('#detail-dialog').open) await showDetail(target.dataset.retry);
  }
  if (target.dataset.filter) {
    queueFilter = target.dataset.filter;
    $$('#queue-tabs button').forEach(b=>b.classList.toggle('active', b===target));
    renderQueue();
  }
  if (target.classList.contains('close-dialog')) target.closest('dialog').close();
});
$('#refresh').addEventListener('click', refresh);
$('#detail-refresh').addEventListener('click', ()=> detailPort && showDetail(detailPort));
$('#search').addEventListener('input', ()=>state && renderQueue());
$('#rack-filter').addEventListener('change', ()=>state && renderQueue());
$('#auto-toggle').addEventListener('click', async e => {
  if (state) await mutate('/api/settings',{auto_enabled:!state.config.auto_enabled},state.config.auto_enabled?'자동 신규 등록을 중지했습니다.':'자동 재투입을 켰습니다. 조건을 충족한 대상이 등록됩니다.',e.currentTarget);
});
$('#policy-form').addEventListener('input', ()=>{dirtyPolicy=true;});
$('#policy-form').addEventListener('submit', async e=>{
  e.preventDefault();
  const f=e.target;
  const ok = await mutate('/api/settings',{max_retries:Number(f.elements.max_retries.value),cooldown_seconds:Number(f.elements.cooldown_seconds.value),min_confidence:Number(f.elements.min_confidence.value)/100},'재투입 정책을 저장했습니다.',f.querySelector('button'));
  if (ok) { dirtyPolicy=false; fillPolicy(); }
});
$('#demo-button').addEventListener('click', ()=>{
  if (!state) return toast('서버 연결을 먼저 확인하세요.',true);
  const ports = state.ports.filter(p=>['RUNNING','PASS','IDLE'].includes(p.status));
  if (!ports.length) return toast('Fail을 생성할 수 있는 Port가 없습니다.',true);
  $('#demo-port').innerHTML=ports.map(p=>`<option value="${escapeHtml(p.id)}">${escapeHtml(p.id)} · ${escapeHtml(p.tc)} (${labels[p.status]})</option>`).join('');
  $('#demo-dialog').showModal();
});
$('#demo-form').addEventListener('submit', async e=>{
  e.preventDefault();
  const f=e.target;
  const portId=f.elements.port_id.value;
  if(await mutate('/api/demo/failure',{port_id:portId,scenario:f.elements.scenario.value},'모의 Fail을 생성했습니다. 담당자 검토 후 재투입할 수 있습니다.',f.querySelector('button'))){$('#demo-dialog').close();await showDetail(portId);}
});
$('#login-form').addEventListener('submit',async e=>{
  e.preventDefault();apiToken=e.target.elements.token.value;e.target.reset();$('#login-dialog').close();await refresh();
});
$('#export-history').addEventListener('click',()=>{
  if(!state) return;
  // Quote all fields and neutralize Excel formula interpretation.
  const csvCell = value => '"'+String(value??'').replace(/^[=+@\-\t\r]/,'\'$&').replace(/"/g,'""')+'"';
  const rows=[['Job ID','Port','TC','Source','Attempt','Status','Created','Finished','Message'],...state.jobs.map(j=>[j.id,j.port_id,j.tc,j.source,j.attempt,j.status,dateTime(j.created),dateTime(j.finished),j.message])];
  const blob=new Blob(['\uFEFF'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='smart-rack-retry-history.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  toast('최근 100건의 실행 이력을 다운로드했습니다. 전체 기록은 SQLite에 보존됩니다.');
});
function tickClock() { $('#clock').textContent=new Date().toLocaleString('ko-KR',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}); }
tickClock();setInterval(tickClock,30000);
navigate(location.hash.slice(1) || 'overview');
refresh();setInterval(refresh,3000);
window.addEventListener('hashchange',()=>navigate(location.hash.slice(1)));
