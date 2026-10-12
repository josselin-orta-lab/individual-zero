"use strict";
const $ = s => document.querySelector(s);
const state = {page:"dashboard",runs:[],tests:[],selected:null,source:"lab_events",cursor:0,next:null,kind:"",step:"",q:"",selectedEvent:null,refresh:null,replayEpoch:0,replayRequestEpoch:0};
const escapeHTML = value => String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const display = value => value===null||value===undefined?"Indisponible":escapeHTML(value);
const pretty = x => JSON.stringify(x,null,2);
const formatBytes = n => n>=1048576?(n/1048576).toFixed(1)+" MiB":n>=1024?(n/1024).toFixed(1)+" KiB":n+" B";
const pill = s => `<span class="pill ${escapeHTML(s)}">${escapeHTML(s)}</span>`;
const intro = (tag,title,sub) => `<p class="heading-overline">${tag}</p><h1 class="page-title">${title}</h1><p class="subtitle">${sub}</p>`;
async function api(path,opts={}){let r=await fetch(path,{...opts,credentials:"same-origin",headers:{...(opts.body?{"Content-Type":"application/json"}:{}),...opts.headers}});if(r.status===401){showLogin();throw Error("Session expirée ou accès non autorisé")}let raw=await r.text();let data;try{data=raw?JSON.parse(raw):{}}catch{data={detail:raw}}if(!r.ok)throw Error(typeof data.detail==="string"?data.detail:`HTTP ${r.status}`);return data}
function showLogin(){clearInterval(state.refresh);state.refresh=null;$("#auth").classList.remove("hidden");$("#workspace").classList.add("hidden")}
function showApp(){$("#auth").classList.add("hidden");$("#workspace").classList.remove("hidden");navigate("dashboard")}
function renderError(error){$("#view").insertAdjacentHTML("afterbegin",`<p class="alert" role="alert">${escapeHTML(error.message||error)}</p>`)}
async function refreshRuns(){const r=await api("/api/runs?limit=200");state.runs=r.runs}
function setNav(){document.querySelectorAll("[data-page]").forEach(b=>b.classList.toggle("active",b.dataset.page===state.page));$("#page-name").textContent=state.page==="oracle"?"ORACLE EXPLORER":state.page.toUpperCase()}
async function navigate(page){state.replayEpoch++;state.replayRequestEpoch++;clearInterval(state.refresh);state.refresh=null;state.page=page;setNav();$("#view").innerHTML="<p class='muted'>Chargement des données originales…</p>";try{if(page==="tests")await pageTests();else if(page==="runs")await pageRuns();else if(page==="oracle")await pageOracle();else if(page==="replay")await pageReplay();else if(page==="downloads")await pageDownloads();else if(page==="settings")await pageSettings();else await pageDashboard()}catch(e){$("#view").innerHTML="";renderError(e)}}
function runTable(runs){return `<div class="table-wrap"><table><thead><tr><th>EXÉCUTION</th><th>TEST / SOURCE</th><th>HORODATAGE</th><th>STATUT</th><th>PAS PHYSIQUES</th></tr></thead><tbody>${runs.map(r=>`<tr data-run="${escapeHTML(r.id)}"><td class="mono">${escapeHTML(r.id.slice(0,19))}…</td><td>${display(r.test_id||"Archive importée")}</td><td>${display(r.created_at)}</td><td>${pill(r.status)}</td><td>${display(r.executed_steps)}</td></tr>`).join("")||`<tr><td colspan="5" class="empty">Aucune exécution enregistrée</td></tr>`}</tbody></table></div>`}
function bindRuns(){document.querySelectorAll("[data-run]").forEach(row=>row.addEventListener("click",()=>{state.selected=row.dataset.run;pageRunDetail(state.selected)}))}
async function pageDashboard(){await refreshRuns();const runs=state.runs;const active=runs.filter(r=>["PENDING","RUNNING"].includes(r.status)).length;const completed=runs.filter(r=>r.status==="SUCCESS").length;const anomalies=runs.filter(r=>["FAILED","INTERRUPTED"].includes(r.status)).length;$("#view").innerHTML=intro("SYSTEM OVERVIEW","Observation center","Un tableau de bord local pour comprendre les exécutions, sans modifier la vie ni les observations d'I0.")+`<div class="grid-stats"><div class="stat"><small>Exécutions</small><strong>${runs.length}</strong><span>locales et importées</span></div><div class="stat"><small>En cours</small><strong>${active}</strong><span>processus supervisés</span></div><div class="stat"><small>Succès techniques</small><strong>${completed}</strong><span>pas une validation scientifique</span></div><div class="stat"><small>Anomalies</small><strong>${anomalies}</strong><span>échecs et interruptions</span></div></div><div class="panel"><h2>Exécutions récentes</h2><p>Les campagnes importées ne sont jamais assimilées à des succès de tests.</p>${runTable(runs.slice(0,10))}</div><div class="provenance">Séparation stricte : la réussite technique et les assertions ne valident ni la conformité comportementale, ni la science, ni l'acceptation opérateur.</div>`;bindRuns()}
async function pageTests(){const data=await api("/api/tests");state.tests=data.tests;$("#view").innerHTML=intro("EXECUTION CONTROL","Test catalog","Commandes fixes et paramètres strictement bornés. Chaque test écrit dans un répertoire unique.")+`<div class="cards">${data.tests.map(t=>`<form class="catalog-item" data-test="${escapeHTML(t.id)}"><p class="heading-overline">AUTHORIZED RUNNER</p><h3>${escapeHTML(t.title)}</h3><p>${escapeHTML(t.description)}</p><div class="meta">Limite : ${t.timeout_seconds} s · Succès technique ≠ preuve scientifique</div><div class="field-row">${Object.entries(t.parameters).map(([k,v])=>`<label class="field">${escapeHTML(k)}<input name="${escapeHTML(k)}" type="number" required min="${v.min}" max="${v.max}" value="${v.default}"></label>`).join("")}<button class="primary" type="submit">▷ Lancer</button></div></form>`).join("")}</div><p class="note">Les résultats de l'Oracle ne sont pas injectés dans les tests. Un diagnostic 600 pas reste une hypothèse fonctionnelle préliminaire.</p>`;document.querySelectorAll("form[data-test]").forEach(f=>f.addEventListener("submit",async e=>{e.preventDefault();const p={test_id:f.dataset.test};for(const inp of f.querySelectorAll("input[name]"))p[inp.name]=Number(inp.value);const b=f.querySelector("button");b.disabled=true;try{const r=await api("/api/runs",{method:"POST",body:JSON.stringify(p)});state.selected=r.id;await pageRunDetail(r.id)}catch(err){renderError(err);b.disabled=false}}))}
async function pageRuns(){await refreshRuns();$("#view").innerHTML=intro("EXECUTION HISTORY","Run registry","Filtrez, consultez les diagnostics et examinez les fichiers de chaque exécution.")+`<div class="action-row"><input class="search-input" id="run-query" placeholder="Chercher un identifiant, test, état…"><select class="search-input" id="run-status"><option value="">Tous les statuts</option>${["PENDING","RUNNING","SUCCESS","FAILED","CANCELLED","INTERRUPTED","IMPORTED"].map(s=>`<option>${s}</option>`).join("")}</select><button class="secondary" id="refresh-runs">Actualiser</button></div><div id="runs-table">${runTable(state.runs)}</div>`;bindRuns();const filter=()=>{const q=$("#run-query").value.toLowerCase(),s=$("#run-status").value;$("#runs-table").innerHTML=runTable(state.runs.filter(r=>(!s||r.status===s)&&JSON.stringify(r).toLowerCase().includes(q)));bindRuns()};$("#run-query").addEventListener("input",filter);$("#run-status").addEventListener("change",filter);$("#refresh-runs").onclick=pageRuns}
async function pageRunDetail(id){clearInterval(state.refresh);state.refresh=null;state.selected=id;setNav();try{const r=await api(`/api/runs/${encodeURIComponent(id)}`);$("#view").innerHTML=intro("RUN DETAILS",`Run <span class="mono">${escapeHTML(id)}</span>`,`Source : ${r.kind==="imported"?"archive en lecture seule":"processus opérateur autorisé"}`)+`<div class="action-row">${pill(r.status)}<button class="secondary" id="back">← Historique</button>${["RUNNING","PENDING"].includes(r.status)?`<button class="secondary" id="cancel">Arrêt contrôlé</button>`:""}<button class="secondary" id="to-oracle">Explorer les événements</button><button class="secondary" id="to-download">Téléchargements</button></div>${r.anomaly?`<div class="alert">Anomalie : ${escapeHTML(r.anomaly)}</div>`:""}<div class="details-grid"><div class="panel"><h2>Exécution et vérification</h2><pre>${escapeHTML(pretty({source_commit:r.source_commit,source_dirty:r.source_dirty,parameters:r.parameters,requested_steps:r.requested_steps,executed_steps:r.executed_steps,technical_success:r.technical_success,assertions_passed:r.assertions_passed,behavior_conformance:r.behavior_conformance,scientific_validation:r.scientific_validation,operator_validation:r.operator_validation,exit_code:r.exit_code,started_at:r.started_at,ended_at:r.ended_at}))}</pre></div><div class="panel"><h2>Fichiers disponibles</h2><div class="downloads">${r.artifacts.map(a=>`<div class="download-row"><div><strong>${escapeHTML(a.alias)}</strong><small>${escapeHTML(a.category)} · ${formatBytes(a.bytes)}</small></div><button class="link-button" data-download="${escapeHTML(a.alias)}">⇩</button></div>`).join("")||"Aucun fichier publié"}</div></div></div><div class="panel"><h2>Logs du processus</h2><pre id="run-log" aria-live="polite">Chargement…</pre><button class="secondary" id="refresh-log">Rafraîchir les logs</button></div>`;$("#back").onclick=()=>navigate("runs");$("#to-oracle").onclick=()=>navigate("oracle");$("#to-download").onclick=()=>navigate("downloads");if($("#cancel"))$("#cancel").onclick=async()=>{try{await api(`/api/runs/${encodeURIComponent(id)}/cancel`,{method:"POST"});await pageRunDetail(id)}catch(e){renderError(e)}};document.querySelectorAll("[data-download]").forEach(b=>b.onclick=()=>download(id,b.dataset.download));const logs=async()=>{try{$("#run-log").textContent=(await api(`/api/runs/${encodeURIComponent(id)}/logs?limit=65536`)).text||"Aucun log"}catch(e){$("#run-log").textContent=e.message}};await logs();$("#refresh-log").onclick=logs;if(["RUNNING","PENDING"].includes(r.status))state.refresh=setInterval(()=>pageRunDetail(id),3500)}catch(e){renderError(e)}}
async function pageOracle(){await refreshRuns();const available=state.runs.filter(r=>r.id);if(!state.selected&&available.length)state.selected=available[0].id;$("#view").innerHTML=intro("CAUSAL EVIDENCE","Oracle Explorer","Exploration paginée des événements et archives effectivement présents. Aucun état caché n'est reconstruit.")+`<div class="panel"><div class="action-row"><label class="field">Exécution<select id="oracle-run" class="search-input">${available.map(r=>`<option value="${escapeHTML(r.id)}" ${r.id===state.selected?"selected":""}>${escapeHTML(r.id)} · ${escapeHTML(r.test_id||"archive")}</option>`).join("")}</select></label><label class="field">Source<select id="oracle-source" class="search-input"></select></label><label class="field">Type d'événement<input id="oracle-kind" placeholder="kind exact"></label><label class="field">Pas physique<input id="oracle-step" type="number" min="0" placeholder="Tous"></label><label class="field">Composant<input id="oracle-component" placeholder="Nom contient…"></label><label class="field">Instant exact<input id="oracle-time" placeholder="timestamp enregistré"></label><label class="field">Recherche<input id="oracle-query" placeholder="Texte contenu…"></label><button class="secondary" id="apply-events">Filtrer</button></div><div id="oracle-warning" class="provenance"></div></div><div class="event-layout"><div class="panel"><h2>Événements <span class="muted tiny">(max. 50 par page)</span></h2><div id="event-list" class="stack"></div><button class="secondary" id="next-events" disabled>Page suivante →</button></div><div class="panel"><h2>Événement brut</h2><pre id="event-payload">Sélectionnez un événement.</pre></div></div>`;$("#oracle-run").onchange=async e=>{state.selected=e.target.value;await sourceOptions()};$("#oracle-source").onchange=e=>{state.source=e.target.value;loadEvents(true)};$("#apply-events").onclick=()=>loadEvents(true);$("#next-events").onclick=()=>{state.cursor=state.next;loadEvents(false)};await sourceOptions()}
async function sourceOptions(){const run=state.selected;if(!run){$("#oracle-warning").textContent="Aucune exécution disponible.";return}const detail=await api(`/api/runs/${encodeURIComponent(run)}`);const avail=detail.artifacts.filter(x=>["journal","oracle","evaluation_trace","lab_events"].includes(x.alias));const labels={journal:"Journal causal I0",oracle:"Oracle (source déclarée)",evaluation_trace:"Trace du banc indépendant",lab_events:"Événements Lab"};$("#oracle-source").innerHTML=avail.map(a=>`<option value="${a.alias}">${labels[a.alias]}</option>`).join("");if(avail.length){state.source=avail.some(a=>a.alias===state.source)?state.source:avail[0].alias;$("#oracle-source").value=state.source;$("#oracle-warning").textContent=`Source : ${labels[state.source]}. Intégrité du fichier non vérifiée par la simple navigation. Les catégories de provenance restent distinctes.`;loadEvents(true)}else{$("#event-list").innerHTML="<p class='empty'>Aucun événement n'a été exporté pour cette exécution.</p>";$("#oracle-warning").textContent="Aucune source Lab/Oracle/journal disponible. Les données manquantes ne sont pas inventées."}}
async function loadEvents(reset){if(reset)state.cursor=0;const q=new URLSearchParams({source:state.source,cursor:state.cursor,limit:50,kind:$("#oracle-kind").value.trim(),component:$("#oracle-component").value.trim(),at:$("#oracle-time").value.trim(),q:$("#oracle-query").value.trim()});const step=$("#oracle-step").value;if(step!=="")q.set("step",step);try{const r=await api(`/api/runs/${encodeURIComponent(state.selected)}/events?${q}`);state.next=r.next_cursor;$("#event-list").innerHTML=r.items.map((e,i)=>`<div class="event-row" data-index="${i}"><small>#${e.line} · pas ${display(e.step)}</small><strong>${escapeHTML(e.kind||"Événement inconnu")}</strong><p>${escapeHTML(e.category)}${e.integrity_error?` · ⚠ ${escapeHTML(e.integrity_error)}`:""}</p></div>`).join("")||"<p class='empty'>Aucun événement correspondant aux filtres.</p>";$("#next-events").disabled=state.next===null;$("#event-payload").textContent="Sélectionnez un événement.";document.querySelectorAll("[data-index]").forEach(el=>el.onclick=()=>{$("#event-payload").textContent=pretty(r.items[Number(el.dataset.index)]);document.querySelectorAll(".event-row").forEach(x=>x.classList.remove("selected"));el.classList.add("selected")})}catch(e){renderError(e)}}
const FRAME_COLORS={obstacle:"#718096",water_source:"#38bdf8",creature:"#fda4af",danger_zone:"#fb923c",lethal_zone:"#f43f5e",shelter:"#a78bfa",placed_stones:"#d1d5db",resource_berry_a:"#4ade80",resource_berry_b:"#86efac",resource_wood:"#b48b61",resource_stone:"#f8fafc"};
function renderReplayGeometry(target,map,step){
  if(!map.available){target.textContent="Carte indisponible : "+String(map.reason||"aucune frame enregistrée");return}
  const width=Number(map.geometry.width),height=Number(map.geometry.height),pose=map.frame.individual_pose;
  const recorded=map.map_authorized===true && map.capture_integrity_verified===true;
  const category=recorded?"Capture directe du moteur vérifiée techniquement":"Archive importée non authentifiée";
  const dots=map.frame.entities.map(e=>{
    const kind=String(e.kind);
    const color=FRAME_COLORS[kind]||"#60a5fa";
    const x=Number(e.position.x),y=Number(e.position.y);
    return '<rect x="'+x+'" y="'+y+'" width="1" height="1" fill="'+color+'"><title>'+escapeHTML(kind)+'</title></rect>';
  }).join("");
  const grid='<defs><pattern id="observer-grid" width="1" height="1" patternUnits="userSpaceOnUse"><path d="M 1 0 L 0 0 0 1" fill="none" stroke="#94a3b8" stroke-opacity=".25" stroke-width=".035"/></pattern></defs>';
  const legend=Object.entries(FRAME_COLORS).map(entry=>'<span style="white-space:nowrap;display:inline-flex;gap:5px;align-items:center;margin-right:12px"><i aria-hidden="true" style="display:inline-block;width:10px;height:10px;background:'+entry[1]+'"></i>'+escapeHTML(entry[0])+'</span>').join("");
  target.innerHTML='<p><strong>'+escapeHTML(category)+'</strong> · pas '+step+' · I0 ('+pose.x+', '+pose.y+'). Vérité scientifique : non attestée.</p>'+
    '<svg role="img" aria-label="'+escapeHTML(category)+'" viewBox="0 0 '+width+' '+height+'" style="width:100%;max-width:600px;max-height:600px;background:#17212b;image-rendering:pixelated" xmlns="http://www.w3.org/2000/svg">'+grid+
    '<rect width="'+width+'" height="'+height+'" fill="url(#observer-grid)"/>'+dots+
    '<rect x="'+pose.x+'" y="'+pose.y+'" width="1" height="1" fill="#fde047" stroke="#000" stroke-width=".09"><title>Position physique enregistrée I0</title></rect></svg>'+
    '<p style="font-size:.8rem;line-height:2">I0 : <span style="color:#fde047">■</span> · '+legend+'</p>';
}
async function pageReplay(){
  const viewEpoch=++state.replayEpoch;
  await refreshRuns();
  if(state.page!=="replay"||viewEpoch!==state.replayEpoch)return;
  const isCurrent=runId=>state.page==="replay"&&state.replayEpoch===viewEpoch&&state.selected===runId;
  const choices=state.runs.filter(r=>r.id);
  if(!choices.length){$("#view").innerHTML=intro("HISTORICAL REPLAY","Replay historique","Aucune exécution disponible.");return}
  if(!choices.some(r=>r.id===state.selected))state.selected=choices[0].id;
  $("#view").innerHTML=intro("HISTORICAL REPLAY","Chronologie enregistrée","Navigation dans les événements historiques uniquement. Aucun état du monde, position ou vérité Oracle n'est déduit.")+
  `<div class="panel"><div class="action-row"><label class="field">Exécution<select id="replay-run" class="search-input">${choices.map(r=>`<option value="${escapeHTML(r.id)}" ${r.id===state.selected?"selected":""}>${escapeHTML(r.id)}</option>`).join("")}</select></label><label class="field">Source<select id="replay-source" class="search-input"></select></label><label class="field">Pas / cycle<input id="replay-step" type="number" min="0" max="2147483647" value="0"></label><button id="replay-prev" class="secondary">← Précédent</button><button id="replay-next" class="secondary">Suivant →</button><button id="replay-load" class="primary">Afficher</button></div><label class="field">Navigation temporelle<input id="replay-scrubber" type="range" min="0" max="600" step="1" value="0" style="width:100%"></label><p id="replay-warning" class="provenance">Reconstruction 2D indisponible sans géométrie vérifiée.</p></div><div class="panel"><h2>Carte 2D des captures locales vérifiées</h2><div id="replay-map" class="provenance">Aucune frame chargée.</div></div><div class="panel"><h2>Frontières temporelles enregistrées</h2><div id="step-diagnostic" class="provenance">Chargement…</div></div><div class="panel"><h2>Intégrité du journal causal</h2><div id="journal-diagnostic" class="provenance">Chargement…</div></div><div class="panel"><h2>Références externes de conservation</h2><p class="provenance">Saisir uniquement des références obtenues hors de cette archive. Leur concordance ne prouve pas la vérité physique et n'autorise pas la carte.</p><div class="action-row"><label class="field">SHA-256 archive 2D<input id="custody-frame" autocomplete="off" spellcheck="false" maxlength="64" placeholder="64 caractères hexadécimaux"></label><label class="field">Tête du journal<input id="custody-head" autocomplete="off" spellcheck="false" maxlength="64" placeholder="64 caractères hexadécimaux"></label><label class="field">Nombre d'événements<input id="custody-count" type="number" min="1" step="1" placeholder="Nombre indépendant"></label><button id="custody-check" class="secondary">Vérifier la concordance</button></div><p id="custody-result" class="provenance" role="status">Aucune vérification demandée. Carte désactivée.</p></div><div class="panel"><h2>Attestation détachée Ed25519</h2><p class="provenance">Utilisez une clé publique obtenue indépendamment de l'archive. Ne saisissez jamais de clé privée. Une signature valide n'établit pas la vérité physique.</p><div class="action-row"><label class="field">Clé publique Ed25519 (Base64)<input id="signed-key" autocomplete="off" spellcheck="false" maxlength="128" placeholder="Clé publique externe"></label><label class="field">Identifiant de clé attendu<input id="signed-key-id" autocomplete="off" spellcheck="false" maxlength="128" placeholder="Identifiant connu"></label><button id="signed-check" class="secondary">Vérifier la signature</button></div><p id="signed-result" class="provenance" role="status">Aucune attestation vérifiée. Carte désactivée.</p></div><div class="panel"><h2>Alignement frames / journal</h2><div id="frame-alignment" class="provenance">Chargement…</div></div><div class="panel"><h2>Diagnostic des archives 2D</h2><div id="frame-diagnostic" class="provenance">Chargement…</div></div><div class="panel"><h2>Événements historiques du pas</h2><div id="replay-results" class="stack"></div><pre id="replay-raw">Sélectionnez un événement pour voir son enregistrement brut.</pre></div>`;
  $("#custody-check").onclick=async()=>{
    const frame=$("#custody-frame").value.trim();
    const head=$("#custody-head").value.trim();
    const countText=$("#custody-count").value.trim();
    const count=Number(countText);
    const out=$("#custody-result");
    const runId=state.selected;
    const isActive=()=>isCurrent(runId)&&out.isConnected;
    out.textContent="Contrôle en cours…";
    if(!/^[0-9a-f]{64}$/.test(frame)||!/^[0-9a-f]{64}$/.test(head)||!countText||!Number.isSafeInteger(count)||count<1){
      out.textContent="Références invalides : deux empreintes SHA-256 minuscules et un nombre entier positif sont requis. Carte désactivée.";
      return;
    }
    try{
      const result=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/frames/custody",{
        method:"POST",
        headers:{"Origin":location.origin},
        body:JSON.stringify({trusted_frame_sha256:frame,trusted_journal_head:head,trusted_journal_count:count})
      });
      if(!isActive())return;
      out.textContent=`Empreintes saisies : ${result.operator_anchor_match?"concordantes":"NON concordantes"} · Origine des références authentifiée : NON · Déclarations : ${result.frame_claims_match?"concordantes":"NON concordantes"} · Pas enregistrés : ${result.recorded_step_alignment?"alignés":"NON alignés"} · Vérité physique : NON vérifiée · Carte autorisée : NON${result.error?" · "+result.error:""}.`;
    }catch(e){if(!isActive())return;out.textContent="Vérification impossible : "+e.message+" · Carte désactivée."}
  };
  $("#signed-check").onclick=async()=>{
    const key=$("#signed-key").value.trim();
    const keyId=$("#signed-key-id").value.trim();
    const out=$("#signed-result");
    const runId=state.selected;
    const isActive=()=>isCurrent(runId)&&out.isConnected;
    if(!/^[A-Za-z0-9+/]{43}=$/.test(key)||!keyId||keyId.length>128){
      out.textContent="Clé publique Base64 Ed25519 ou identifiant invalide. Carte désactivée.";
      return;
    }
    out.textContent="Vérification en cours…";
    try{
      const result=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/frames/signed-custody",{
        method:"POST",body:JSON.stringify({trusted_public_key_b64:key,expected_key_id:keyId})
      });
      if(!isActive())return;
      out.textContent=`Signature : ${result.signature.signature_valid?"valide":"INVALIDE"} · Empreinte frames : ${result.signature.frames_digest_matches?"concordante":"NON"} · Identité I0 : ${result.frame_identity_match?"concordante":"NON"} · Journal : ${result.journal_claim_match?"concordant":"NON"} · Pas fermés : ${result.recorded_step_alignment?"alignés":"NON"} · Vérité physique : NON vérifiée · Carte autorisée : NON${result.signature.error?" · "+result.signature.error:""}.`;
    }catch(e){if(!isActive())return;out.textContent="Vérification impossible : "+e.message+" · Carte désactivée."}
  };
  const loadSources=async()=>{
    const runId=state.selected;
    const detail=await api("/api/runs/"+encodeURIComponent(runId));
    if(!isCurrent(runId))return;
    $("#custody-result").textContent="Aucune vérification demandée pour cette exécution. Carte désactivée.";
    const maxSteps=Number(detail.executed_steps)||600;
    $("#replay-scrubber").max=maxSteps;
    $("#replay-scrubber").value=Math.max(0,Math.min(maxSteps,Number($("#replay-step").value)||1));
    $("#signed-result").textContent="Aucune attestation vérifiée pour cette exécution. Carte désactivée.";
    $("#custody-frame").value="";$("#custody-head").value="";$("#custody-count").value="";
    const sources=detail.artifacts.filter(a=>["journal","lab_events"].includes(a.alias));
    if(sources.some(a=>a.alias==="journal") && Number($("#replay-step").value)===0){
      $("#replay-step").value=1;
      $("#replay-scrubber").value=1;
    }
    $("#replay-source").innerHTML=sources.map(a=>`<option value="${a.alias}">${a.alias==="journal"?"Journal causal (t_monde)":"Lab telemetry (cycle non physique)"}</option>`).join("");
    const hasJournal=detail.artifacts.some(a=>a.alias==="journal");
    if(!hasJournal){
      $("#step-diagnostic").textContent="Journal absent : frontières temporelles non vérifiables.";
    }else{
      try{
        const boundaries=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/steps/diagnostic");
        if(!isCurrent(runId))return;
        $("#step-diagnostic").textContent=`Ouverture/fermeture des pas : ${boundaries.recorded_boundaries_valid?"cohérentes":"INCOMPLÈTES OU INVALIDES"} · Pas fermés : ${boundaries.closed_steps.length} · Décès terminal enregistré : ${boundaries.terminal_death_recorded?"oui":"non"} · Audit causal complet : NON · Carte autorisée : NON${boundaries.error?" · "+boundaries.error:""}.`;
      }catch(e){if(!isCurrent(runId))return;$("#step-diagnostic").textContent="Diagnostic impossible : "+e.message+" · Carte désactivée."}
    }
    if(!hasJournal){
      $("#journal-diagnostic").textContent="Aucun journal causal disponible. Chaîne et intégralité non vérifiées.";
    }else{
      $("#journal-diagnostic").textContent="Vérification cryptographique en cours…";
      try{
        const audit=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/journal/diagnostic");
        if(!isCurrent(runId))return;
        $("#journal-diagnostic").textContent=`Chaîne SHA-256 : ${audit.chain_valid?"cohérente":"INVALIDE"} · Événements : ${audit.occurrences} · Tête : ${audit.head_hash||"indisponible"} · Intégralité indépendante : ${audit.trusted_tail_verified?"confirmée":"NON"} · Audit causal complet : NON · Carte autorisée : NON${audit.error?" · Erreur : "+audit.error:""}.`;
      }catch(e){if(!isCurrent(runId))return;$("#journal-diagnostic").textContent="Vérification impossible : "+e.message+" · Carte désactivée."}
    }
    const hasFrames=detail.artifacts.some(a=>a.alias==="world_frames");
    if(!hasFrames || !hasJournal){
      $("#frame-alignment").textContent="Alignement indisponible : archive 2D et journal causal requis.";
    }else{
      try{
        const aligned=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/frames/alignment");
        if(!isCurrent(runId))return;
        $("#frame-alignment").textContent=`Frames sur des pas fermés : ${aligned.frame_step_alignment?"oui":"NON"} · Frames examinées : ${aligned.checked_frames} · Vérification indépendante : NON · Carte autorisée : NON${aligned.error?" · "+aligned.error:""}.`;
      }catch(e){if(!isCurrent(runId))return;$("#frame-alignment").textContent="Alignement impossible : "+e.message+" · Carte désactivée."}
    }
    if(!hasFrames){
      $("#frame-diagnostic").textContent="Aucune archive 2D déclarée. Carte désactivée : géométrie et attestation indépendante absentes.";
    }else{
      $("#frame-diagnostic").textContent="Analyse structurelle en cours…";
      try{
        const diagnostic=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/frames/diagnostic");
        if(!isCurrent(runId))return;
        const structural=diagnostic.structurally_valid?"Structure valide":"Structure invalide";
        const errors=(diagnostic.errors||[]).join(", ")||"aucune anomalie structurelle détectée";
        $("#frame-diagnostic").textContent=`${structural} · ${diagnostic.frame_count} frames · ${errors}. Vérification indépendante : NON. Carte autorisée : NON.`;
      }catch(e){if(!isCurrent(runId))return;$("#frame-diagnostic").textContent="Diagnostic impossible : "+e.message+" · Carte désactivée."}
    }
    if(!sources.length){$("#replay-results").textContent="Aucune source de replay enregistrée.";$("#replay-load").disabled=true;return}
    $("#replay-load").disabled=false;await load();
  };
  const load=async()=>{
    const requestEpoch=++state.replayRequestEpoch;
    const runId=state.selected;
    const source=$("#replay-source").value;
    const step=Number($("#replay-step").value);
    const isActive=()=>isCurrent(runId)&&state.replayRequestEpoch===requestEpoch&&$("#replay-source").value===source&&Number($("#replay-step").value)===step;
    if(!Number.isSafeInteger(step)||step<0){$("#replay-warning").textContent="Pas invalide.";$("#replay-map").textContent="Carte indisponible : pas invalide.";return}
    $("#replay-map").textContent="Vérification des données du pas sélectionné…";
    $("#replay-results").textContent="Chargement des événements…";
    $("#replay-scrubber").value=Math.max(0,Math.min(Number($("#replay-scrubber").max),step));
    try{
      const data=await api("/api/runs/"+encodeURIComponent(runId)+"/replay?"+new URLSearchParams({source:source,step:String(step),limit:"100"}));
      if(!isActive())return;
      $("#replay-warning").textContent=`Source : ${data.step_semantics}. ${data.matched_count} événements enregistrés, ${data.malformed_records} lignes malformées. ${data.truncated?"Résultat tronqué.":""} Carte visible uniquement si une capture physique locale est vérifiée; aucun état manquant inventé.`;
      if(source==="journal"){
        try{
          const map=await api("/api/runs/"+encodeURIComponent(runId)+"/replay/geometry?step="+encodeURIComponent(step));
          if(!isActive())return;
          renderReplayGeometry($("#replay-map"),map,step);
        }catch(e){if(isActive())$("#replay-map").textContent="Carte indisponible : "+e.message;}
      }else{
        $("#replay-map").textContent="Carte indisponible pour les cycles Lab : ils ne correspondent pas aux pas physiques t_monde.";
      }
      $("#replay-results").innerHTML=data.events.map((e,i)=>`<button class="secondary" data-replay-index="${i}">#${e.line} · ${escapeHTML(e.kind||"Type inconnu")}</button>`).join("")||"<p class='empty'>Aucun événement enregistré à ce pas.</p>";
      $("#replay-raw").textContent="Sélectionnez un événement.";
      document.querySelectorAll("[data-replay-index]").forEach(b=>b.onclick=()=>{$("#replay-raw").textContent=pretty(data.events[Number(b.dataset.replayIndex)].raw)});
    }catch(e){if(isActive()){$("#replay-results").textContent=e.message;$("#replay-map").textContent="Carte indisponible : récupération des événements impossible."}}
  };
  $("#replay-run").onchange=async e=>{state.selected=e.target.value;state.replayEpoch++;state.replayRequestEpoch++;$("#view").textContent="Chargement de la nouvelle exécution…";await pageReplay()};
  $("#replay-source").onchange=load;
  $("#replay-load").onclick=load;
  $("#replay-step").onchange=load;
  $("#replay-scrubber").onchange=e=>{$("#replay-step").value=e.target.value;load()};
  $("#replay-prev").onclick=()=>{$("#replay-step").value=Math.max(0,Number($("#replay-step").value)-1);load()};
  $("#replay-next").onclick=()=>{$("#replay-step").value=Math.min(2147483647,Number($("#replay-step").value)+1);load()};
  await loadSources();
}
async function pageDownloads(){await refreshRuns();if(!state.selected&&state.runs.length)state.selected=state.runs[0].id;$("#view").innerHTML=intro("EVIDENCE CUSTODY","Downloads","Fichiers natifs, manifestes et ZIP sans modification des originaux.")+`<div class="panel"><div class="action-row"><label class="field">Exécution<select id="download-run" class="search-input">${state.runs.map(r=>`<option value="${escapeHTML(r.id)}" ${r.id===state.selected?"selected":""}>${escapeHTML(r.id)}</option>`).join("")}</select></label><button class="secondary" id="zip">⇩ Archive ZIP</button></div><div id="files-list" class="downloads"></div></div><div class="provenance">Les SHA-256 vérifient des octets lorsqu'une empreinte de référence existe. Ils ne démontrent pas la vérité physique, ni la continuité après crash. Conservez les empreintes de confiance séparément.</div>`;$("#download-run").onchange=e=>{state.selected=e.target.value;renderFiles()};$("#zip").onclick=()=>downloadZip(state.selected);await renderFiles()}
async function renderFiles(){if(!state.selected){$("#files-list").textContent="Aucun run";return}let r=await api(`/api/runs/${encodeURIComponent(state.selected)}`);$("#files-list").innerHTML=r.artifacts.map(f=>`<div class="download-row"><div><strong>${escapeHTML(f.name)}</strong><small>${escapeHTML(f.category)} · ${formatBytes(f.bytes)}</small><small id="hash-${escapeHTML(f.alias)}"></small></div><div><button class="secondary" data-verify="${escapeHTML(f.alias)}">SHA-256</button> <button class="secondary" data-download="${escapeHTML(f.alias)}">⇩ Télécharger</button></div></div>`).join("")||"Aucun fichier";document.querySelectorAll("[data-verify]").forEach(b=>b.onclick=async()=>{try{const d=await api(`/api/runs/${encodeURIComponent(state.selected)}/integrity/${encodeURIComponent(b.dataset.verify)}`);document.getElementById("hash-"+b.dataset.verify).textContent=`SHA-256 ${d.sha256} · concordance ${d.matches_expected===null?"inconnue":d.matches_expected?"oui":"NON"}`}catch(e){renderError(e)}});document.querySelectorAll("[data-download]").forEach(b=>b.onclick=()=>download(state.selected,b.dataset.download))}
function triggerNativeDownload(path){const a=document.createElement("a");a.href=path;a.download="";document.body.append(a);a.click();a.remove()}
function download(id,alias){triggerNativeDownload(`/api/runs/${encodeURIComponent(id)}/file/${encodeURIComponent(alias)}`)}
function downloadZip(id){if(id)triggerNativeDownload(`/api/runs/${encodeURIComponent(id)}/archive.zip`)}
async function pageSettings(){const s=await api("/api/settings");$("#view").innerHTML=intro("LOCAL SECURITY","Settings","La configuration provient exclusivement du serveur local et de son environnement.")+`<div class="panel"><h2>Service et isolation</h2><pre>${escapeHTML(pretty(s))}</pre><p>Le navigateur n'exécute aucune commande. Le Core ne dépend pas de l'Observer. L'accès réseau externe nécessite un déploiement TLS et une revue de sécurité distincte.</p></div>`}
$("#login-form").addEventListener("submit",async e=>{e.preventDefault();$("#login-error").textContent="";try{await api("/api/session",{method:"POST",body:JSON.stringify({token:$("#token").value})});$("#token").value="";showApp()}catch(err){$("#login-error").textContent=err.message}});
document.querySelectorAll("[data-page]").forEach(b=>b.onclick=()=>navigate(b.dataset.page));
$("#logout").onclick=async()=>{try{await api("/api/session",{method:"DELETE"})}catch{}showLogin()};
api("/api/settings").then(showApp).catch(showLogin);
