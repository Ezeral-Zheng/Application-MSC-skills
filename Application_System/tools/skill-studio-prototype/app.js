/* PROTOTYPE: compare canvas, rule-sheet, and guided workflow design with shared state. */
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const directions={general:'通用申请',business:'商科 / 管理',engineering:'理工 / 技术',transfer:'跨专业申请'};
const variantLabels={A:'A · 节点画布',B:'B · 规则工作表',C:'C · 分步向导'};
const conditions={always:'每次运行',empty:'个性化素材不足时',others:'存在其他目标 PS 时',word:'需要 Word 交付时'};
const icons={'准备':'▤','规划':'◇','写作':'✎','审查':'✓','修改':'↺','交付':'↗','组合流程':'▦'};
let catalog=[],byId=new Map(),counter=0;
let state={schemaVersion:1,prototype:true,name:'先给学生看叙事方案',direction:'general',student:'',target:'',template:'matrix',nodes:[],selected:null};
let variant=new URLSearchParams(location.search).get('variant')||'A';
if(!variantLabels[variant])variant='A';
let toastTimer,dragged,simulation;
const node=(skill,extra={})=>({uid:`node-${++counter}`,skill,condition:'always',rules:{general:'',business:'',engineering:'',transfer:''},...extra});
const builtin={id:'controller-publish',title:'发布与交付',category:'交付',input:'通过适用门禁的最终候选稿',output:'唯一正式 Vn 与任务看板更新',summary:'由总控预留版本、发布最终产物；矩阵只执行其自身事实与格式检查。',path:'AGENTS.md · 总控发布职责',source:'这是总控动作，不是独立 skill。正式文书发布前完成全部适用门禁；同一任务只发布一个新 Vn。原始附件与已有正式稿保留。学生版矩阵完成时不标记为 PS 正文完成。',controller:true};
function skill(n){return byId.get(typeof n==='string'?n:n.skill)||builtin}
function title(n){return n.label||skill(n).title}
function selected(){return state.nodes.find(n=>n.uid===state.selected)}
function chooseTemplate(key){
 state.template=key;
 const templates={matrix:()=>[node('student-material-normalizer'),node('ps-narrative-matrix'),node('controller-publish')],ps:()=>[node('student-material-normalizer'),node('personalization-material-importer',{condition:'empty'}),node('ps-narrative-matrix'),node('personal-statement-writer'),node('application-review'),node('external-application-review',{mode:'single-draft',label:'独立单篇审稿'}),node('external-application-review',{mode:'portfolio-differentiation',label:'组合差异审稿',condition:'others'}),node('controller-publish'),node('student-style-memory'),node('ps-word-export',{condition:'word'})],resume:()=>[node('resume-application-pipeline'),node('controller-publish')],blank:()=>[]};
 state.nodes=templates[key]();state.selected=state.nodes[1]?.uid||state.nodes[0]?.uid||null;
 state.name={matrix:'先给学生看叙事方案',ps:'PS 写作与独立审稿',resume:'按目标专业生成简历',blank:'我的申请工作流'}[key];
 $('#flowName').value=state.name;render();
}
function baseRule(n){
 const s=skill(n);
 if(n.skill==='ps-narrative-matrix')return '六列组合总览 + 十一字段项目卡。新增专业保留原有条目。同校不同专业拉开核心问题与证据用途，跨校同方向允许适度复用。学生版不包含内部过程。';
 if(n.skill==='external-application-review')return n.mode==='portfolio-differentiation'?'全新隔离审稿人。四层矩阵审计 + 第八维 ≥ 8.5；P1–P5 独立计数。组合修改后重新事实审查并进行 S1–S5 单篇复核，再继续下一轮 P。':'全新隔离审稿人。前七维平均 ≥ 8.5，无 P0/P1；初始 C1–C5。Revise 由另一隔离修改者处理并重新事实审查。';
 if(n.skill==='personal-statement-writer')return '英文在前、中文在后。默认英文 700–1000 words，约 800；官方字数要求可覆盖。先读取矩阵与资料，历史事实有来源，未来规划使用未来语气。';
 return s.summary;
}
function directionRule(n){
 if(state.direction==='general')return '依据目标项目选择相关事实与能力，保持自然、具体的表达。';
 if(['审查','修改','交付'].includes(skill(n).category))return '按本申请方向判断匹配度；事实边界、隔离审稿与正式版本规则继续生效。';
 return {business:'优先连接真实商业判断、用户或市场问题与管理能力；说明选择依据及实践边界。',engineering:'优先说明真实技术问题、方法选择、个人贡献与可核验结果；学习需求连接目标培养方向。',transfer:'从已有可迁移能力连接新领域问题；区分学习意向与已掌握技能，不虚构长期兴趣或历史转向事件。'}[state.direction];
}
function effective(n){return n.rules[state.direction]||directionRule(n)}
function lockNote(n){
 if(n.skill==='external-application-review')return '保留隔离审稿、8.5 门槛、P0/P1 与 C / S / P 独立上限。';
 if(n.skill==='resume-application-pipeline')return '组合节点内部包括事实与质量门禁、修改与可选导出，不能当成一次裸写作调用。';
 return '方向规则作为叠加层；事实依据、资料保留与正式版本规则仍来自原有流程。';
}
function badge(n){return `<span class="tag ${n.condition==='always'?'green':'orange'}">${esc(conditions[n.condition])}</span>`}
function nodeTools(n){return `<div class="node-tools"><button data-action="up" data-uid="${n.uid}" title="上移">↑</button><button data-action="down" data-uid="${n.uid}" title="下移">↓</button><button data-action="remove" data-uid="${n.uid}" title="移除">×</button></div>`}
function libraryMarkup(extraClass='library'){
 return `<aside class="${extraClass}"><div class="section-title">节点库 <small>${catalog.length} 个 skills</small></div><input id="searchSkills" placeholder="搜索写作、审查、矩阵…" aria-label="搜索 skills"><div id="libraryItems">${libraryItems('')}</div></aside>`;
}
function libraryItems(query){
 let group='';return [...catalog,builtin].filter(s=>[s.title,s.id,s.category,s.summary].join(' ').toLowerCase().includes(query.toLowerCase())).map(s=>{
 let h='';if(s.category!==group){group=s.category;h=`<div class="group-label">${esc(group)}</div>`;}
 return h+`<div class="skill-item"><span class="category-icon">${icons[s.category]||'◈'}</span><div><div class="skill-name">${esc(s.title)}</div><small>${s.controller?'总控动作':esc(s.id)}</small></div><button data-action="add" data-skill="${esc(s.id)}" aria-label="添加${esc(s.title)}">+</button></div>`;
 }).join('');
}
function inspectorMarkup(){
 const n=selected();if(!n)return `<aside class="inspector"><div class="section-title">节点配置</div><p>从节点库添加一个节点，再设置它的规则。</p></aside>`;
 const s=skill(n);
 return `<aside class="inspector"><div class="section-title">节点配置 <small>${state.nodes.indexOf(n)+1} / ${state.nodes.length}</small></div><span class="category-icon">${icons[s.category]||'◇'}</span><h2>${esc(title(n))}</h2><div class="skill-code">${esc(s.id)}</div><p>${esc(s.summary)}</p><div class="info-row"><small>读取什么</small>${esc(s.input)}</div><div class="info-row"><small>产出什么</small>${esc(s.output)}</div><h4>规则与调用条件</h4><label>调用条件</label><select data-condition="${n.uid}">${Object.entries(conditions).map(([k,v])=>`<option value="${k}" ${n.condition===k?'selected':''}>${esc(v)}</option>`).join('')}</select>${n.skill==='external-application-review'?`<label>审稿模式</label><select data-mode="${n.uid}"><option value="single-draft" ${n.mode!=='portfolio-differentiation'?'selected':''}>单篇质量</option><option value="portfolio-differentiation" ${n.mode==='portfolio-differentiation'?'selected':''}>组合差异</option></select>`:''}<label>继承的基础规则</label><div class="rule-base">${esc(baseRule(n))}</div><label>${esc(directions[state.direction])} · 可调整规则</label><textarea data-rule="${n.uid}" placeholder="${esc(directionRule(n))}" aria-label="方向规则">${esc(n.rules[state.direction])}</textarea><div class="lock-note">${esc(lockNote(n))}</div><button class="full-width small-btn" data-action="resetRule" data-uid="${n.uid}">恢复此方向的默认规则</button><button class="full-width small-btn" data-action="source" data-uid="${n.uid}">查看原始 Skill</button></aside>`;
}
function canvasMarkup(){
 return `${libraryMarkup()}<section class="stage-work"><div class="canvas-heading"><div><h2>你的申请工作流</h2><p>拖动排序 · 点击配置 · 条件与返回路径由原流程约束</p></div><span class="count">${state.nodes.length} 个节点</span></div><div class="canvas">${state.nodes.length?state.nodes.map((n,i)=>`${i?'<div class="connector"><span>↓</span></div>':''}<article class="node ${n.uid===state.selected?'selected':''}" data-select="${n.uid}" draggable="true" data-drag="${n.uid}"><div class="node-head"><span class="category-icon">${icons[skill(n).category]||'◇'}</span><div><h3>${String(i+1).padStart(2,'0')} &nbsp; ${esc(title(n))}</h3><small>${esc(skill(n).category)}${n.mode?' / '+esc(n.mode):''}</small></div>${badge(n)}</div><p class="node-desc">${esc(skill(n).summary)}</p><div class="io-mini"><span>产出 &nbsp;<b>${esc(skill(n).output)}</b></span></div>${nodeTools(n)}</article>`).join(''):'<div class="empty">从左侧添加节点，开始拼接流程。</div>'}<button class="add-step" data-action="focusLibrary">＋ 添加下一步</button><div class="flow-end">◉ &nbsp; 输出由任务类型决定</div></div><div class="hint-panel"><strong>方向配置独立于基础 Skill</strong>切换申请方向，可以配置另一套规则。所有原始 Skill 都可查看；修改保存在当前方案，导出后可以继续编辑。</div></section>${inspectorMarkup()}`;
}
function tableMarkup(){
 return `<section class="table-main"><div class="table-toolbar"><div><h2>把规则放在同一张表上比较</h2><span class="check-caption">每一行是一个节点，当前方向：${esc(directions[state.direction])}</span></div><select id="tableAdd" aria-label="添加节点"><option value="">＋ 添加节点</option>${[...catalog,builtin].map(s=>`<option value="${s.id}">${esc(s.title)}</option>`).join('')}</select></div><div class="table-sheet"><table><thead><tr><th>顺序与节点</th><th>输入 → 产物</th><th>调用条件</th><th>本方向规则</th><th>调整</th></tr></thead><tbody>${state.nodes.map((n,i)=>`<tr class="${n.uid===state.selected?'chosen':''}" data-select="${n.uid}"><td><strong>${i+1}. ${esc(title(n))}</strong><div class="caption">${esc(skill(n).category)}</div></td><td>${esc(skill(n).input)}<div class="caption">↓ ${esc(skill(n).output)}</div></td><td>${badge(n)}</td><td><textarea data-rule="${n.uid}" placeholder="${esc(directionRule(n))}" aria-label="${esc(title(n))}方向规则">${esc(n.rules[state.direction])}</textarea></td><td><div class="row-action"><button data-action="up" data-uid="${n.uid}">↑</button><button data-action="down" data-uid="${n.uid}">↓</button><button data-action="remove" data-uid="${n.uid}">×</button></div></td></tr>`).join('')}</tbody></table>${!state.nodes.length?'<div class="empty">从右上角添加节点。</div>':''}</div><h3 style="font-size:13px;margin-top:27px">可组合的节点</h3><div class="catalog-grid">${catalog.map(s=>`<article class="catalog-card" data-action="add" data-skill="${s.id}"><span class="tag">${esc(s.category)}</span><h3>${esc(s.title)} <span style="float:right;color:var(--purple)">＋</span></h3><p>${esc(s.summary)}</p></article>`).join('')}</div></section>${inspectorMarkup()}`;
}
function guideMarkup(){
 const n=selected();let i=n?state.nodes.indexOf(n):0;
 return `<div class="guide-shell"><aside class="guide-map"><span class="eyebrow" style="color:#b7afda">YOUR RECIPE</span><h2>${esc(state.name)}</h2><p>一次只决定一个步骤。</p>${state.nodes.map((x,j)=>`<div class="guide-stop ${x.uid===state.selected?'active':''}" data-select="${x.uid}"><small>STEP ${String(j+1).padStart(2,'0')}</small><strong>${esc(title(x))}</strong></div>`).join('')}</aside><section class="guide-detail">${n?`<span class="number">STEP ${String(i+1).padStart(2,'0')} / ${state.nodes.length}</span><h2>这一步，${esc(title(n))}</h2><p>${esc(skill(n).summary)}</p><div class="io"><div><small>开始前需要</small>${esc(skill(n).input)}</div><div><small>完成后获得</small>${esc(skill(n).output)}</div></div><h3>基础规则</h3><div class="rule-base">${esc(baseRule(n))}</div><h3>为${esc(directions[state.direction])}调整这一步</h3><textarea data-rule="${n.uid}" placeholder="${esc(directionRule(n))}" aria-label="向导方向规则">${esc(n.rules[state.direction])}</textarea><p class="check-caption">${esc(lockNote(n))}</p><label class="check-caption">什么时候调用？</label><select data-condition="${n.uid}">${Object.entries(conditions).map(([k,v])=>`<option value="${k}" ${n.condition===k?'selected':''}>${v}</option>`).join('')}</select><div class="guide-buttons"><button data-action="selectPrevious" ${i===0?'disabled':''}>← 上一步</button><button data-action="source" data-uid="${n.uid}">看完整规则</button><button class="primary" data-action="selectNext">${i===state.nodes.length-1?'检查方案':'配置下一步 →'}</button></div>`:'<h2>先添加一个步骤</h2><p>从右侧选择一个 Skill，把它加进你的流程。</p>'}</section>${libraryMarkup('guide-library')}</div>`;
}
function render(){
 const main=$('#workspace');main.className=variant==='B'?'table-view':variant==='C'?'guide-view':'';
 main.innerHTML=variant==='B'?tableMarkup():variant==='C'?guideMarkup():canvasMarkup();
 $('#variantName').textContent=variantLabels[variant];
 document.querySelectorAll('[data-template]').forEach(b=>b.classList.toggle('active',b.dataset.template===state.template));
 $('#bottomState').innerHTML=`<span>${state.nodes.length} 个节点 · ${esc(directions[state.direction])} · ${state.nodes.filter(n=>n.rules[state.direction]).length} 项方向规则已自定义</span><span>配置可导出 · 基础 Skill 保留 · 原型未连接任务执行</span>`;
}
function showToast(s){$('#toast').textContent=s;$('#toast').style.opacity='1';clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').style.opacity='0',2800)}
function setVariant(v){variant=v;const url=new URL(location);url.searchParams.set('variant',v);history.replaceState({},'',url);render()}
function cycle(dir){const keys=['A','B','C'];setVariant(keys[(keys.indexOf(variant)+dir+3)%3])}
function mutate(action,uid,id){
 const n=state.nodes.find(n=>n.uid===uid),i=state.nodes.indexOf(n);
 if(action==='add'){
  const newNode=node(id,id==='external-application-review'?{mode:'single-draft'}:{});
  const insertAt=state.nodes.findIndex(x=>x.uid===state.selected);
  state.nodes.splice(insertAt<0?state.nodes.length:insertAt+1,0,newNode);state.selected=newNode.uid;state.template='custom';render();showToast('已添加节点，可以在右侧配置');
 }else if(action==='remove'&&n){state.nodes.splice(i,1);state.selected=state.nodes[Math.min(i,state.nodes.length-1)]?.uid||null;state.template='custom';render()}
 else if(action==='up'&&i>0){[state.nodes[i-1],state.nodes[i]]=[state.nodes[i],state.nodes[i-1]];state.template='custom';render()}
 else if(action==='down'&&i>=0&&i<state.nodes.length-1){[state.nodes[i+1],state.nodes[i]]=[state.nodes[i],state.nodes[i+1]];state.template='custom';render()}
 else if(action==='resetRule'&&n){n.rules[state.direction]='';render();showToast('已恢复此方向的默认规则')}
 else if(action==='source'&&n){openDialog('原始 Skill · '+title(n),`<p class="check-caption">${esc(skill(n).path)}</p><pre>${esc(skill(n).source)}</pre>`)}
 else if(action==='focusLibrary'){$('#searchSkills')?.focus()}
 else if(action==='selectPrevious'){state.selected=state.nodes[Math.max(0,state.nodes.indexOf(selected())-1)]?.uid;render()}
 else if(action==='selectNext'){let idx=state.nodes.indexOf(selected());if(idx<state.nodes.length-1){state.selected=state.nodes[idx+1].uid;render()}else showChecks()}
}
function issues(){
 const out=[];const find=id=>state.nodes.findIndex(n=>n.skill===id);const exists=id=>find(id)>=0;
 const ps=exists('personal-statement-writer'),resume=exists('resume-application-pipeline');
 if(!state.nodes.length)out.push({title:'流程还没有节点',text:'从节点库添加节点，或选用一个模板。'});
 if(!state.student.trim()||!state.target.trim())out.push({title:'实际执行前补齐学生与目标',text:'设计方案可以先导出；实际任务需要明确学生和目标学校 / 专业。',draft:true});
 const publish=find('controller-publish');
 if(ps){
  for(const [id,name] of [['student-material-normalizer','资料标准化'],['ps-narrative-matrix','叙事矩阵'],['application-review','事实审查']]){
   if(!exists(id))out.push({title:'PS 缺少'+name,text:'在当前设计中加入这一阶段，或明确由组合流程内部承接。'});
  }
  const writer=find('personal-statement-writer'),fact=find('application-review');
  if(exists('student-material-normalizer')&&find('student-material-normalizer')>writer)out.push({title:'准备步骤顺序需要调整',text:'资料标准化应在 PS 写作之前。'});
  if(exists('ps-narrative-matrix')&&find('ps-narrative-matrix')>writer)out.push({title:'矩阵应在写作前',text:'先决定申请叙事，再生成正文。'});
  if(fact>=0&&fact<writer)out.push({title:'事实审查需要当前候选稿',text:'把事实审查移到写作之后。'});
  const single=state.nodes.findIndex(n=>n.skill==='external-application-review'&&n.mode!=='portfolio-differentiation');
  const portfolio=state.nodes.findIndex(n=>n.skill==='external-application-review'&&n.mode==='portfolio-differentiation');
  if(single<0)out.push({title:'PS 缺少独立单篇审稿',text:'加入独立审稿节点并设置单篇模式；原写作者不能代替隔离审稿人。'});
  if(single>=0&&fact>=0&&single<fact)out.push({title:'独立内容审稿应在事实审查之后',text:'先通过事实与格式门禁，再评价单篇内容。'});
  if(portfolio<0)out.push({title:'需要预留组合审稿分支',text:'有其他目标 PS 时还需要组合差异审稿。可以添加条件节点，而不是要求每个任务都运行。'});
  if(portfolio>=0&&single>=0&&portfolio<single)out.push({title:'组合审稿应在单篇通过之后',text:'先完成单篇门禁，再进入独立 P 轮组合门禁。'});
  if(publish>=0&&(publish<fact||publish<single||publish<portfolio))out.push({title:'发布步骤过早',text:'正式 Vn 只能在全部适用门禁通过后发布。'});
  for(const id of ['student-material-normalizer','ps-narrative-matrix','personal-statement-writer','application-review']){
   const n=state.nodes.find(n=>n.skill===id);if(n&&n.condition!=='always')out.push({title:skill(n).title+'不能作为随意跳过的阶段',text:'默认每次运行；已有产物可复用时由总控核验，不以不相关条件跳过。'});
  }
  const sn=state.nodes[single];if(sn&&sn.condition!=='always')out.push({title:'PS 单篇门禁需要每次检查',text:'单篇审稿不能设置为仅在需要 Word 或有其他目标时调用。'});
 }
 if(state.nodes.some(n=>['resume-writer','targeted-one-page-resume-writer','resume-word-generator'].includes(n.skill))&&!resume)out.push({title:'简历任务应从完整流程进入',text:'加入 resume-application-pipeline。写作与导出是内部阶段，不能替代其两道门禁。'});
 if(exists('ps-word-export')){
  const n=state.nodes.find(n=>n.skill==='ps-word-export');
  if(!ps)out.push({title:'PS 导出需要已通过审查的正式 Markdown',text:'仅导出任务可以成立，但需另外指定已有正式 PS 和通过记录；当前原型未提供这个输入。'});
  if(publish<0||find('ps-word-export')<publish)out.push({title:'导出应在正式发布之后',text:'先形成唯一正式 Markdown Vn，再执行英文部分 Word 导出。'});
  if(n.condition!=='word')out.push({title:'明确 Word 交付意向',text:'建议把 PS 导出设为“需要 Word 交付时”。',draft:true});
 }
 for(const n of state.nodes){if(n.skill==='external-application-review'&&n.mode==='portfolio-differentiation'&&!ps)out.push({title:'组合审稿需要 PS 组合输入',text:'此模式读取当前候选稿、其他目标最新正式 PS、矩阵与相似度报告。'})}
 if(resume&&publish>=0&&publish<find('resume-application-pipeline'))out.push({title:'简历发布应在完整流程之后',text:'组合流程内部完成写作、事实与质量门禁。'});
 return out;
}
function checksMarkup(){const all=issues();return `<p class="check-caption">这是对流程顺序和关键阶段的静态检查，不能替代资料核验、真实审稿或完整执行验收。</p>${all.length?all.map(x=>`<div class="issue"><b>${esc(x.title)}${x.draft?' · 执行前补充':''}</b><p>${esc(x.text)}</p></div>`).join(''):'<div class="issue good"><b>当前设计未发现关键阶段或顺序缺失</b><p>实际任务仍由 Agent 检查资料、隔离环境、事实与全部适用门禁。</p></div>'}<div class="issue good"><b>基础规则继承</b><p>保留真实事实、全新隔离审稿、唯一正式版本与资料保留。每次内容修改仍重新经过适用门禁。</p></div>`}
function showChecks(){openDialog('流程检查',checksMarkup())}
function openDialog(title,body,buttons=''){$('#dialogTitle').textContent=title;$('#dialogBody').innerHTML=body;$('#dialogActions').innerHTML=buttons;$('#modal').showModal()}
function download(text,name,type){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function exportData(){return {...state,nodes:state.nodes.map(n=>({...n,skillPath:skill(n).path})),exportedAt:new Date().toISOString(),executionConnected:false}}
function promptText(){
 const warnings=issues();
 return `# ${state.name}\n\n学生：${state.student||'[执行前填写学生]'}\n目标：${state.target||'[执行前填写学校与专业]'}\n申请方向：${directions[state.direction]}\n\n请在 Application-MSC Vault 中按已授权范围处理本任务。以下是流程设计，不能作为绕过 AGENTS.md 或 skill 内置门禁的执行器。组合 skill 的内置步骤与显式节点按职责去重，不重复启动整套管线。\n\n## 设计的阶段\n\n${state.nodes.map((n,i)=>`### ${i+1}. ${title(n)}\n\n- 入口：${skill(n).path}\n- 条件：${conditions[n.condition]}${n.mode?'\n- 模式：'+n.mode:''}\n- 输入：${skill(n).input}\n- 预期产物：${skill(n).output}\n- 基础要求：${baseRule(n)}\n- ${directions[state.direction]}方向规则：${effective(n)}\n`).join('\n')}\n## 运行与返回要求\n\n读取当前原始 skill 与用户最新明确输入。过去事实必须有来源，不伪造经历或数字。仅矩阵任务不执行 PS 字数与评分门禁。PS 初始 C、组合 P、补充 S 独立计数，每类最多 5 轮；每轮审稿与修改分别使用全新隔离 worker。Revise 先净化问题单，再隔离修改、事实审查与相应复核；Blocked 停止依赖阶段并报告缺失。正式文书通过全部适用门禁后只发布本次唯一 Vn。方向叠加规则与基础流程冲突时先指出冲突，不悄悄降低质量要求。\n${warnings.length?'\n## 执行前需处理的设计问题\n\n'+warnings.map(x=>'- '+x.title+'：'+x.text).join('\n'):'\n静态流程检查未发现关键阶段缺失；这不是实际任务通过记录。'}\n`;
}
function preview(){const text=promptText();openDialog('执行提示预览',`<p class="check-caption">可以复制到 Codex 继续任务。此页没有执行学生任务；导出的方向规则也没有改写原 Skill。</p><pre id="promptPreview">${esc(text)}</pre>`,`<button id="downloadPrompt">下载 Markdown</button><button class="primary" id="copyPrompt">复制到 Codex</button>`);$('#downloadPrompt').onclick=()=>download(text,'申请工作流-执行提示.md','text/markdown;charset=utf-8');$('#copyPrompt').onclick=async()=>{try{await navigator.clipboard.writeText(text);showToast('已复制，可以粘贴到 Codex')}catch(e){showToast('浏览器未允许复制，可下载 Markdown')}}}
function beginSimulation(){simulation={index:0,log:[],done:false};showSimulation()}
function showSimulation(){
 const n=state.nodes[simulation.index];
 if(!n||simulation.done){openDialog('流程演练结束',`<p class="simulation-label">模拟状态 · 未调用模型或生成文书</p>${simulation.log.map(l=>`<div class="sim-log">${esc(l)}</div>`).join('')}<div class="issue good"><b>已到达设计终点</b><p>这里验证节点顺序；实际产物与审查结论必须由 Agent 执行生成。</p></div>`);return;}
 const review=['application-review','external-application-review','resume-quality-review'].includes(n.skill);
 openDialog('步骤演练',`<p class="simulation-label">仅演练状态转换 · ${simulation.index+1} / ${state.nodes.length}</p>${simulation.log.map(l=>`<div class="sim-log">${esc(l)}</div>`).join('')}<div class="sim-stage"><span class="tag">${esc(conditions[n.condition])}</span><h3>${esc(title(n))}</h3><p>${esc(skill(n).input)} → ${esc(skill(n).output)}</p><p class="check-caption">${review?'选择一个模拟结果，观察后续路径。不会产生真实审稿得分。':'选择推进或模拟输入缺失。条件节点可以模拟本次不适用。'}</p></div>`,`<button data-sim="blocked">模拟输入缺失</button>${n.condition!=='always'?'<button data-sim="skip">本次不适用</button>':''}${review?'<button data-sim="revise">模拟返修</button>':''}<button class="primary" data-sim="pass">${review?'模拟通过':'模拟完成 →'}</button>`);
}
function simulationAction(action){
 const n=state.nodes[simulation.index];
 if(action==='blocked'){openDialog('演练停在 Blocked',`<div class="issue"><b>${esc(title(n))} · 输入不足</b><p>依赖阶段停止，补充资料后才继续。不会跳过节点或发布正式版本。</p></div><p class="check-caption">模拟状态，没有修改任何学生资料。</p>`);return}
 if(action==='revise'){
  openDialog('演练：返修路径',`<div class="issue"><b>Revise → 净化问题 → 隔离修改 → 事实复查</b><p>修改者只接收当前稿、净化问题单与最小事实包。新审稿人不继承上一轮分数。</p></div><div class="issue good"><b>${n.mode==='portfolio-differentiation'?'组合返修先经过 S 单篇复核，达标后再进入下一 P 轮':'单篇返修继续下一轮 C；达到 C5 仍不合格则停止发布'}</b><p>各组计数独立。真实运行需要支持隔离 worker 的 Agent 执行环境。</p></div>`,`<button class="primary" id="backSimulation">返回当前审查节点</button>`);$('#backSimulation').onclick=showSimulation;return;
 }
 simulation.log.push(`${simulation.index+1}. ${title(n)} · ${action==='skip'?'条件不适用，模拟跳过':'模拟完成'}`);simulation.index++;$('#modal').close();showSimulation();
}
document.addEventListener('click',e=>{
 const action=e.target.closest('[data-action]');if(action){mutate(action.dataset.action,action.dataset.uid,action.dataset.skill);return}
 const t=e.target.closest('[data-template]');if(t){chooseTemplate(t.dataset.template);return}
 const sim=e.target.closest('[data-sim]');if(sim){$('#modal').close();simulationAction(sim.dataset.sim);return}
 const select=e.target.closest('[data-select]');if(select&&!e.target.matches('textarea,input,select,button')){state.selected=select.dataset.select;render()}
});
document.addEventListener('input',e=>{
 if(e.target.dataset.rule){const n=state.nodes.find(n=>n.uid===e.target.dataset.rule);if(n)n.rules[state.direction]=e.target.value;$('#bottomState').textContent=`${state.nodes.length} 个节点 · ${directions[state.direction]} · 规则已更新，导出配置可保留修改`;}
 if(e.target.id==='searchSkills')$('#libraryItems').innerHTML=libraryItems(e.target.value);
});
document.addEventListener('change',e=>{
 if(e.target.dataset.condition){const n=state.nodes.find(n=>n.uid===e.target.dataset.condition);if(n)n.condition=e.target.value;render()}
 if(e.target.dataset.mode){const n=state.nodes.find(n=>n.uid===e.target.dataset.mode);n.mode=e.target.value;n.label=n.mode==='single-draft'?'独立单篇审稿':'组合差异审稿';render()}
 if(e.target.id==='tableAdd'&&e.target.value)mutate('add',null,e.target.value);
});
document.addEventListener('dragstart',e=>{const el=e.target.closest('[data-drag]');if(el){dragged=el.dataset.drag;e.dataTransfer.setData('text/plain',dragged)}});
document.addEventListener('dragover',e=>{if(e.target.closest('[data-drag]'))e.preventDefault()});
document.addEventListener('drop',e=>{
 const target=e.target.closest('[data-drag]');if(!target||!dragged||dragged===target.dataset.drag)return;e.preventDefault();
 const item=state.nodes.find(n=>n.uid===dragged);state.nodes=state.nodes.filter(n=>n.uid!==dragged);const at=state.nodes.findIndex(n=>n.uid===target.dataset.drag);state.nodes.splice(at,0,item);state.template='custom';state.selected=item.uid;dragged=null;render();
});
$('#flowName').oninput=e=>state.name=e.target.value;
$('#student').oninput=e=>state.student=e.target.value;
$('#target').oninput=e=>state.target=e.target.value;
$('#direction').onchange=e=>{state.direction=e.target.value;render();showToast('已切换方向，节点顺序保持不变')};
$('#prevVariant').onclick=()=>cycle(-1);$('#nextVariant').onclick=()=>cycle(1);
document.addEventListener('keydown',e=>{if(e.target.closest('input,textarea,select,[contenteditable]')||$('#modal').open)return;if(e.key==='ArrowLeft')cycle(-1);if(e.key==='ArrowRight')cycle(1)});
$('#closeDialog').onclick=()=>$('#modal').close();$('#checkBtn').onclick=showChecks;$('#previewBtn').onclick=preview;$('#simulateBtn').onclick=beginSimulation;
$('#jsonBtn').onclick=()=>{download(JSON.stringify(exportData(),null,2),'申请工作流-配置.json','application/json');showToast('已导出节点顺序与四套方向配置')};
$('#importBtn').onclick=()=>$('#importFile').click();
$('#importFile').onchange=async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  const data=JSON.parse(await file.text());
  if(data.schemaVersion!==1||!Array.isArray(data.nodes)||!directions[data.direction])throw Error('不是本原型支持的方案');
  const nodes=data.nodes.map(n=>{if(!byId.has(n.skill)&&n.skill!==builtin.id)throw Error('无法识别节点 '+n.skill);if(!conditions[n.condition])throw Error('无法识别调用条件');return node(n.skill,{condition:n.condition,mode:n.mode,label:typeof n.label==='string'?n.label:undefined,rules:Object.fromEntries(Object.keys(directions).map(k=>[k,typeof n.rules?.[k]==='string'?n.rules[k]:'']))})});
  state={...state,name:String(data.name||'导入方案'),direction:data.direction,student:String(data.student||''),target:String(data.target||''),template:'custom',nodes,selected:nodes[0]?.uid||null};
  for(const key of ['student','target','direction'])$('#'+key).value=state[key];$('#flowName').value=state.name;render();showToast('已恢复方案与方向规则');
 }catch(err){showToast('导入失败：'+err.message)}finally{e.target.value=''}
};
fetch('catalog.json').then(r=>{if(!r.ok)throw Error('catalogue unavailable');return r.json()}).then(data=>{const order=['准备','规划','写作','组合流程','审查','修改','交付','其他'];catalog=data.sort((a,b)=>order.indexOf(a.category)-order.indexOf(b.category));byId=new Map(catalog.map(s=>[s.id,s]));byId.set(builtin.id,builtin);chooseTemplate('matrix')}).catch(()=>{$('#workspace').innerHTML='<div class="empty">节点库未加载。请用 python3 serve.py 启动原型后访问本地页面。</div>'});
