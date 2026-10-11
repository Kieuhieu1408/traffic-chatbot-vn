from __future__ import annotations

import asyncio
import json
import os
import re
from html import escape
from pathlib import Path

from markdown_it import MarkdownIt
from shiny import App, reactive, render, ui

from review.data import ROOT, LabelStore, load_runs
from review.langsmith_data import LangSmithReview
from evals.calibration import CalibrationStore, comparison, load_judge_batches

LOCAL_RUNS = load_runs()
JUDGE_BATCHES = load_judge_batches()
CALIBRATION = CalibrationStore(Path(os.getenv('RAG_CALIBRATION_DB', str(ROOT / 'evals/labels/calibration.sqlite3'))))
STORE = LabelStore(Path(os.getenv('RAG_REVIEW_DB', str(ROOT / 'evals/labels/human.sqlite3'))))
VERDICTS = {'pass': 'Pass', 'fail': 'Fail'}
CSS = '''
:root{--ink:#243c36;--green:#246b54;--border:#dce4de}body{background:#f5f6f2;color:var(--ink);font:14px/1.6 system-ui,sans-serif}.container-fluid{max-width:1900px;padding:22px 26px}h1{font-size:25px;font-weight:750;margin:0}h2{font-size:17px;font-weight:700;margin:0 0 16px}h3{font-size:15px;font-weight:700}.intro,.meta{color:#66786e;font-size:12px}.intro{margin:3px 0 18px}.meta{overflow-wrap:anywhere}.layout{display:grid;grid-template-columns:290px minmax(0,1fr) minmax(0,1fr);gap:18px;align-items:start}.panel{background:white;border:1px solid var(--border);border-radius:12px;padding:18px;min-width:0}.sidebar{position:sticky;top:16px}.sidebar .shiny-input-container{width:100%!important}.section-label{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#75857b;font-weight:750}.status-card{padding:13px;background:#edf3ed;border-radius:8px;margin:14px 0}.status-card #progress{font-size:12px}.status-card #save_status{font-size:12px;color:var(--green)}.question{font-size:17px;line-height:1.6;font-weight:650}.answer-markdown,.text{font-size:14px;line-height:1.8;overflow-wrap:anywhere}.text{white-space:pre-wrap}.answer-markdown p{margin-bottom:14px}.source{border:1px solid var(--border);border-radius:8px;padding:12px;margin:10px 0;scroll-margin-top:20px}.source summary{font-weight:600;cursor:pointer;overflow-wrap:anywhere}.source .text{margin-top:12px}.source .meta{margin:8px 0}.source.selected-source{outline:2px solid #cc9e35;background:#fffbed}.evidence-scroll{max-height:calc(100dvh - 220px);overflow:auto;padding:2px 5px}.conversation-scroll{max-height:calc(100dvh - 215px);overflow:auto;padding-right:6px}.cite{color:var(--green);font-weight:750}.history-turn{border-left:3px solid #dce6de;padding-left:14px;margin:15px 0}.history-turn .role{font-size:10px;font-weight:800;letter-spacing:.08em;color:#708477}.pill{display:inline-block;border-radius:20px;background:#edf3ed;padding:3px 9px;font-size:11px;margin:0 4px 7px 0}.btn{font-size:13px;border-radius:6px}.btn-primary{background:var(--green);border-color:var(--green)}.primary-action .btn{width:100%;padding:11px}.nav-actions{display:flex;gap:6px;margin:9px 0}.nav-actions .btn{flex:1}.rubric{font-size:12px;color:#66786e;line-height:1.6;margin-bottom:12px}.form-control,.form-select{font-size:13px}.shiny-input-container{margin-bottom:12px;width:100%!important}textarea{font-size:13px!important}.empty{padding:35px;color:#66786e}details summary{cursor:pointer}details.optional{border-top:1px solid var(--border);padding-top:12px;margin-top:12px}.link-out{font-size:12px;display:inline-block;margin:8px 0;color:var(--green)}.warning{padding:12px;background:#fff5da;color:#76551a;border-radius:8px;font-size:12px}.connection{margin-bottom:14px;font-size:12px;color:#617469}.header-actions{display:flex;gap:8px;margin:10px 0}.review-form{margin-top:18px;border-top:1px solid var(--border);padding-top:16px}.mobile-tabs{display:none}.error-text{background:#fff0ec;padding:12px;border-radius:8px}.panel-heading{display:flex;justify-content:space-between;align-items:start;gap:10px}.panel-heading h2{margin-bottom:8px}.sidebar label{font-size:12px}.review-form label{font-size:13px}#verdict .shiny-options-group{display:flex;gap:15px}.panel[hidden]{display:none!important}
@media(min-width:1250px){.sidebar{max-height:calc(100dvh - 40px);overflow:auto}}@media(max-width:1150px){.layout{grid-template-columns:250px minmax(0,1fr)}.evidence-panel{grid-column:2}.sidebar{grid-row:1/3}.conversation-scroll,.evidence-scroll{max-height:60vh}}@media(max-width:700px){.container-fluid{padding:12px}h1{font-size:21px}.layout{display:block}.sidebar{position:static;max-height:none}.mobile-tabs{display:flex;position:sticky;top:0;z-index:100;background:#f5f6f2;padding:8px 0;gap:6px}.mobile-tabs button{flex:1;border:1px solid var(--border);background:white;border-radius:6px;padding:9px}.mobile-tabs button.active{background:var(--green);color:white}.layout>.panel{display:none}.layout>.panel.mobile-active{display:block}.conversation-scroll,.evidence-scroll{max-height:none;overflow:visible}.source{scroll-margin-top:65px}.intro{margin-bottom:7px}}
'''
CSS += '''.queue-filters{margin:12px 0}.queue-filters summary{font-size:12px;font-weight:650}.queue-filters[open] summary{margin-bottom:12px}.header-actions .btn{padding:7px 8px;white-space:nowrap}.status-card{margin:10px 0}.review-form{margin-top:12px;padding-top:12px}.connection{font-size:11px}.sidebar .primary-action{position:sticky;bottom:0;background:white;padding-top:9px;z-index:5}'''
JS = '''
function showReviewTab(name){
 document.querySelectorAll('[data-panel]').forEach(p=>p.classList.toggle('mobile-active',p.dataset.panel===name));
 document.querySelectorAll('[data-tab]').forEach(b=>{b.classList.toggle('active',b.dataset.tab===name);b.setAttribute('aria-selected',String(b.dataset.tab===name));});
 $(document).trigger('shiny:visualchange');
}
$(document).on('shiny:connected',()=>{Shiny.addCustomMessageHandler('review-controls',data=>{['save','save_next','skip','previous'].forEach(id=>document.getElementById(id).disabled=data.busy||!data.active);document.getElementById('refresh').disabled=data.busy;document.querySelectorAll('#run,#case,#filter,#scenario,#search').forEach(el=>el.disabled=data.busy);document.querySelectorAll('#verdict input,#reason,#correction,#independent').forEach(el=>el.disabled=data.busy||data.locked);['save','save_next'].forEach(id=>document.getElementById(id).disabled=data.busy||!data.active||data.locked);document.getElementById('reveal_judge').disabled=data.busy||!data.locked;});});
document.addEventListener('click',e=>{
 const tab=e.target.closest('[data-tab]');if(tab)showReviewTab(tab.dataset.tab);
 const cite=e.target.closest('a.cite');if(cite){e.preventDefault();showReviewTab('evidence');
  requestAnimationFrame(()=>{const node=document.querySelector(cite.getAttribute('href'));if(!node)return;
   document.querySelectorAll('.selected-source').forEach(n=>n.classList.remove('selected-source'));
   node.open=true;node.classList.add('selected-source');node.scrollIntoView({block:'nearest',behavior:'smooth'});});}
});
'''
def citations(text, ranks):
    md = MarkdownIt("commonmark", {"html": False})
    def render_text(tokens, idx, options, env):
        value = escape(tokens[idx].content)
        def link(match):
            rank = int(match.group(1))
            if rank not in ranks:
                return match.group(0)
            return (f'<a class="cite" href="#source-{rank}" '
                    f'onclick="document.getElementById(&quot;source-{rank}&quot;).open=true">[{rank}]</a>')
        return re.sub(r'\[(\d+)\]', link, value)
    md.renderer.rules['text'] = render_text
    return ui.div(ui.HTML(md.render(text)), class_='answer-markdown')


def source_card(source, *, gold=False):
    rank = source.get('rank')
    title = f"[{rank}] " if rank is not None else ''
    article = source['article']
    title += f"{source['document_id']} · {article[:100]}" + ('…' if len(article)>100 else '')
    return ui.tags.details(
        ui.tags.summary(title),
        ui.p(source['article'], class_='meta'),
        ui.p(f"{source['source_file']} · chunk {source['chunk_id']}" +
             (f" · score {source['score']:.4f}" if 'score' in source else ''), class_='meta'),
        ui.div(source['content'], class_='text'),
        id=f"gold-{source['chunk_id']}" if gold else f'source-{rank}', class_='source', open=gold,
    )


app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.style(CSS), ui.tags.script(ui.HTML(JS))),
    ui.h1('RAG Traffic VN · Data Review'),
    ui.p('Read the conversation. Check the evidence. Save a review on the original trace.', class_='intro'),
    ui.div(*[ui.tags.button(label, type='button', class_='active' if key=='conversation' else '',
                           **{'data-tab':key,'aria-selected':str(key=='conversation').lower()})
             for key,label in [('conversation','Conversation'),('evidence','Evidence'),('review','Review')]],
           class_='mobile-tabs', role='tablist'),
    ui.div(
        ui.div(
            ui.div('Review queue',class_='section-label'),
            ui.input_select('run','Data source',
                {k:'Blind review · '+k.removeprefix('judge:') for k in JUDGE_BATCHES} |
                {'cloud':'LangSmith'} | {k:'Local · '+k for k in LOCAL_RUNS}),
            ui.div(ui.input_action_button('refresh','Refresh traces'),
                   ui.download_button('export_labels','Export reviews'),class_='header-actions'),
            ui.output_text('connection',container=ui.div),
            ui.tags.details(ui.tags.summary('Filter queue'),
                ui.input_select('filter','Review status',{'all':'All','unlabeled':'Not reviewed','pass':'Pass','fail':'Fail'}),
                ui.input_select('scenario','Conversation type',{'all':'All','single':'Single turn','multi':'Multi-turn'}),
                ui.input_text('search','Search questions',placeholder='Keywords in the question…'),class_='queue-filters'),
            ui.input_select('case','Trace',{}),
            ui.div(ui.output_text('current_label'),ui.output_text('progress'),ui.output_text('save_status'),class_='status-card'),
            ui.output_ui('trace_link'),
            ui.div(
                ui.h2('Your review'),
                ui.p('Review the whole answer: correct, supported, complete, and scoped. Skip if unsure.',class_='rubric'),
                ui.panel_conditional("input.run && input.run.startsWith('judge:')",
                    ui.p('Blind review: previous labels and judge results are hidden. Your first saved review is locked.',class_='warning'),
                    ui.input_checkbox('independent','I have not seen earlier labels or critiques for this trace.',False)),
                ui.input_radio_buttons('verdict','Verdict',VERDICTS,selected='',inline=True),
                ui.input_text_area('reason','Reason · required for Fail',rows=4,
                                   placeholder='Which claim is wrong or unsupported? Cite the source.'),
                ui.tags.details(ui.tags.summary('Corrected answer · optional'),
                                ui.input_text_area('correction',None,rows=5),class_='optional'),
                ui.div(ui.input_action_button('save_next','Save & next',class_='btn-primary'),class_='primary-action'),
                ui.div(ui.input_action_button('previous','← Previous'),
                       ui.input_action_button('skip','Skip →'),class_='nav-actions'),
                ui.input_action_button('save','Save without moving',class_='btn-link'),
                ui.output_text('destination'),class_='review-form'),
            ui.panel_conditional("input.run && input.run.startsWith('judge:')",
                ui.input_action_button('reveal_judge','Reveal judge after saving'),
                ui.output_ui('judge_panel'),ui.output_ui('calibration_summary')),
            class_='panel sidebar',**{'data-panel':'review'}),
        ui.div(ui.h2('Conversation'),ui.output_ui('answer_panel'),
               class_='panel conversation-panel mobile-active',**{'data-panel':'conversation'}),
        ui.div(ui.h2('Evidence the model saw'),ui.output_ui('evidence_panel'),
               class_='panel evidence-panel',**{'data-panel':'evidence'}),
        class_='layout'),
    title='RAG Traffic VN · Data Review',lang='en',
)


def server(input, output, session):
    runs = dict(LOCAL_RUNS) | dict(JUDGE_BATCHES)
    gateway = None
    current = reactive.value(None)
    revision = reactive.value(0)
    baseline = reactive.value(('', '', ''))
    status = reactive.value('')
    connection_status = reactive.value('Connecting to LangSmith…')
    busy = reactive.value(False)
    pending = reactive.value(None)
    link = reactive.value('')
    expected_case = reactive.value(None)
    revealed = reactive.value(None)
    baseline_independent = reactive.value(False)

    def form(): return (input.verdict() or '', input.reason(), input.correction())
    def dirty():
        key=current.get()
        return bool(key and (form()!=baseline.get() or
            (key[0].startswith('judge:') and input.independent()!=baseline_independent.get())))
    def row_for(key): return next(r for r in runs[key[0]]['rows'] if r['case_id']==key[1])
    def label_for(key):
        if key[0].startswith('judge:'):
            return CALIBRATION.get(key[0],row_for(key),runs[key[0]]['manifest']['rubric_hash'])
        if key[0]=='cloud': return gateway.get(key[1]) if gateway else None
        return STORE.get(*key,row_for(key)['trace_hash'])

    async def refresh_data():
        nonlocal gateway
        busy.set(True)
        connection_status.set('Refreshing…')
        try:
            if input.run()=='cloud':
                candidate = LangSmithReview()
                batch = await candidate.load()
                gateway = candidate
                runs['cloud'] = batch
                connection_status.set(f"LangSmith · {candidate.settings.langsmith_project} · up to 100 recent completed traces")
            elif input.run().startswith('judge:'):
                runs.update(load_judge_batches())
                connection_status.set('Frozen judge pilot · no earlier reviews shown · local human labels')
            else:
                runs.update(load_runs())
                connection_status.set('Local eval runs · reviews stay in SQLite')
            current.set(None)
            baseline.set(('', '', ''))
            revision.set(revision.get()+1)
        except Exception as exc:
            # Do not expose transport errors that might include request credentials.
            message = str(exc) if isinstance(exc, ValueError) else 'Could not refresh. Check the connection, LangSmith key, project and workspace; then retry.'
            connection_status.set(message)
            ui.notification_show(message,type='error',duration=8)
        finally:
            busy.set(False)

    async def activate(key):
        current.set(key)
        revealed.set(None)
        expected_case.set(key)
        ui.update_select('case',selected=key[1])
        item = label_for(key)
        values = (item.get('verdict',''),item.get('reason',''),item.get('correction','')) if item else ('','','')
        if values[0] not in VERDICTS: values=('',values[1],values[2])
        baseline.set(values)
        ui.update_radio_buttons('verdict',choices=VERDICTS,selected=values[0])
        ui.update_text_area('reason',value=values[1])
        ui.update_text_area('correction',value=values[2])
        ui.update_checkbox('independent',value=bool(item.get('independent')) if item else False)
        baseline_independent.set(bool(item.get('independent')) if item else False)
        status.set('Saved review · '+item.get('reviewer','human') if item and values[0] else 'Not reviewed')
        link.set('')
        if key[0]=='cloud':
            try:
                url=await gateway.url(key[1])
                if current.get()==key: link.set(url)
            except Exception:
                pass

    def confirm(action):
        pending.set(action)
        ui.modal_show(ui.modal('Your edits have not been saved. Stay to save them, or discard them to continue.',
                              title='Unsaved review',easy_close=False,
                              footer=ui.TagList(ui.input_action_button('stay','Keep editing'),
                                                ui.input_action_button('discard','Discard & continue'))))

    @reactive.effect
    @reactive.event(input.refresh)
    async def refresh_click():
        if busy.get(): return
        if dirty(): confirm(('refresh',None))
        else: await refresh_data()

    @reactive.effect
    @reactive.event(input.run)
    async def source_changed():
        key=current.get()
        if key and key[0]==input.run():return
        if dirty():
            confirm(('refresh',None))
        else: await refresh_data()

    @reactive.effect
    @reactive.event(input.stay)
    def stay():
        pending.set(None); ui.modal_remove()
        key=current.get()
        if key:
            ui.update_select('filter',selected='all');ui.update_select('scenario',selected='all')
            ui.update_text('search',value='')
            ui.update_select('run',selected=key[0]);ui.update_select('case',selected=key[1])

    @reactive.effect
    @reactive.event(input.discard)
    async def discard():
        action=pending.get();pending.set(None);ui.modal_remove()
        if not action:return
        if action[0]=='refresh': await refresh_data()
        else: await activate(action[1])

    @reactive.calc
    def filtered_ids():
        revision.get()
        batch=runs.get(input.run(),{})
        ids=[]
        for row in batch.get('rows',[]):
            label=label_for((input.run(),row['case_id']))
            state=label['verdict'] if label and label['verdict'] in VERDICTS else 'unlabeled'
            scenario='multi' if row.get('history') else 'single'
            if input.filter() not in ('all',state):continue
            if input.scenario() not in ('all',scenario):continue
            if input.search().strip().casefold() not in row['query'].casefold():continue
            ids.append(row['case_id'])
        return ids

    @reactive.effect
    def choices():
        ids=filtered_ids()
        with reactive.isolate():
            key=current.get()
            selected=key[1] if key and key[0]==input.run() and key[1] in ids else ids[0] if ids else ''
        choices={rid:f"{index+1:02d} · {row_for((input.run(),rid))['query'][:65]}" for index,rid in enumerate(ids)}
        ui.update_select('case',choices=choices,selected=selected)

    @reactive.effect
    @reactive.event(input.case,revision)
    async def select_case():
        key=(input.run(),input.case())
        expected=expected_case.get()
        if expected and expected[0]==input.run() and expected[1] in filtered_ids():
            if key!=expected:return
            expected_case.set(None)
        elif expected:
            expected_case.set(None)
        if key==current.get() or key[1] not in filtered_ids(): return
        if dirty(): confirm(('navigate',key))
        else: await activate(key)

    def active():
        key=current.get()
        return bool(key and key[0]==input.run() and key[1] in filtered_ids())

    @reactive.effect
    async def controls():
        revision.get()
        key=current.get()
        locked=bool(active() and key[0].startswith('judge:') and label_for(key))
        await session.send_custom_message('review-controls',{'busy':busy.get(),'active':active(),'locked':locked})

    async def step(delta):
        ids=filtered_ids();key=current.get()
        if not active():return
        index=ids.index(key[1])+delta
        if not 0<=index<len(ids):
            ui.notification_show('You have reached the end of this queue.',duration=3);return
        target=(input.run(),ids[index])
        if dirty(): confirm(('navigate',target))
        else: await activate(target);ui.update_select('case',selected=target[1])

    @reactive.effect
    @reactive.event(input.previous)
    async def previous():
        if not busy.get():await step(-1)

    @reactive.effect
    @reactive.event(input.skip)
    async def skip():
        if not busy.get():await step(1)

    async def save_current(advance):
        if busy.get() or not active():return
        key=current.get();values=form();row=row_for(key)
        if values[0] not in VERDICTS or (values[0]=='fail' and not values[1].strip()):
            ui.notification_show('Choose Pass or Fail. A failure needs a source-based reason.',type='warning');return
        ids=filtered_ids();index=ids.index(key[1]);target=ids[index+1] if index+1<len(ids) else None
        busy.set(True);status.set('Saving and verifying…')
        try:
            if key[0].startswith('judge:'):
                CALIBRATION.save(key[0],row,runs[key[0]]['manifest']['rubric_hash'],*values,input.independent())
            elif key[0]=='cloud':
                await asyncio.to_thread(gateway.save,key[1],row['trace_hash'],*values)
            else:
                prior=label_for(key)
                errors=json.loads(prior.get('errors','[]')) if prior else []
                STORE.save(*key,row['trace_hash'],values[0],values[1],errors,values[2])
            baseline.set(values);status.set('Saved to LangSmith' if key[0]=='cloud' else 'Saved locally')
            baseline_independent.set(input.independent())
            if advance and target:
                await activate((key[0],target));ui.update_select('case',selected=target)
            elif advance:status.set('Saved · last trace in this queue')
            revision.set(revision.get()+1)
        except Exception as exc:
            message=str(exc) if isinstance(exc,ValueError) else 'Save could not be verified. Your edits are kept; a partial cloud write is possible. Copy your edits before refreshing.'
            status.set('Not confirmed saved')
            ui.notification_show(message,type='error',duration=None)
        finally:busy.set(False)

    @reactive.effect
    @reactive.event(input.save_next)
    async def save_next(): await save_current(True)

    @reactive.effect
    @reactive.event(input.save)
    async def save(): await save_current(False)

    @render.text
    def connection():return connection_status.get()

    @render.text
    def destination():
        if input.run().startswith('judge:'):return 'Saves a separate, locked human review locally. Existing LangSmith labels are untouched.'
        return 'Saves answer_pass and review_reason on LangSmith.' if input.run()=='cloud' else 'Saves to the local review database.'

    @render.text
    def current_label():
        ids=filtered_ids()
        return f'Trace {ids.index(current.get()[1])+1} of {len(ids)}' if active() else 'No matching trace'

    @render.text
    def progress():
        revision.get()
        rows=runs.get(input.run(),{}).get('rows',[])
        labels=[label_for((input.run(),r['case_id'])) for r in rows]
        count=sum(bool(x and x['verdict'] in VERDICTS) for x in labels)
        return f'{count}/{len(rows)} reviewed · {len(filtered_ids())} in this queue'

    @render.text
    def save_status():
        if busy.get():return status.get() or 'Loading…'
        return 'Unsaved edits' if dirty() else status.get()

    @render.ui
    def trace_link():
        if active() and link.get():
            return ui.tags.a('Open trace in LangSmith ↗',href=link.get(),target='_blank',rel='noopener noreferrer',class_='link-out')
        return None

    @reactive.effect
    @reactive.event(input.reveal_judge)
    def reveal_judge():
        if not active() or not current.get()[0].startswith('judge:'):return
        key=current.get();row=row_for(key)
        try:CALIBRATION.reveal(key[0],row,runs[key[0]]['manifest']['rubric_hash'])
        except ValueError as exc:
            ui.notification_show(str(exc),type='warning');return
        revealed.set(key)

    @output(suspend_when_hidden=False)
    @render.ui
    def judge_panel():
        if not active() or not current.get()[0].startswith('judge:'):return None
        key=current.get()
        if revealed.get()!=key:return ui.p('Judge feedback is withheld until you save and explicitly reveal it.',class_='meta')
        result=runs[key[0]]['judgments'][key[1]]
        if result['status']!='ok':return ui.p('Judge error · no quality label assigned.',class_='warning')
        judgment=result['judgment'];human=label_for(key)
        verdict=judgment['verdict']
        agreement='Needs specialist review' if verdict is None else 'Agrees with your review' if verdict==human['verdict'] else 'Disagrees with your review'
        return ui.div(ui.h3('Judge: '+(VERDICTS[verdict] if verdict else 'Needs review')),
            ui.p(agreement,class_='pill'),ui.p(judgment['reason']),
            *[ui.div(ui.tags.blockquote(issue['claim']),ui.p(issue['explanation']),
                     ui.p('Sources: '+', '.join(map(str,issue['source_ranks'])),class_='meta')) for issue in judgment['issues']],
            ui.p('Uncalibrated pilot · '+runs[key[0]]['manifest']['model'],class_='meta'))

    @render.ui
    def calibration_summary():
        revision.get()
        if not input.run().startswith('judge:') or input.run() not in runs:return None
        batch=runs[input.run()]
        # Do not disclose aggregate judge outcomes while the queue is being reviewed.
        labels=[CALIBRATION.get(input.run(),r,batch['manifest']['rubric_hash']) for r in batch['rows']]
        count=sum(bool(x) for x in labels)
        if count!=len(labels):return ui.p(f'Human reviews saved: {count}/{len(labels)}. Comparison metrics stay hidden until the queue is complete.',class_='meta')
        report=comparison(input.run(),batch,CALIBRATION)
        return ui.div(ui.h3('Pilot comparison'),
            ui.p(f"Eligible paired reviews: {report['matched_binary_reviews']} · excluded as previously exposed: {report['excluded_nonindependent']}"),
            ui.p(f"Judge abstentions: {report['judge_abstentions']} · judge errors: {report['judge_errors']}"),
            ui.p(f"Failure precision: {report['precision'] if report['precision'] is not None else 'N/A'} · recall: {report['recall'] if report['recall'] is not None else 'N/A'}"),
            ui.p('Self-reported independence. Not a held-out or expert-validated estimate.',class_='meta'))

    @output(suspend_when_hidden=False)
    @render.ui
    def answer_panel():
        if not active():return ui.div('Refresh traces or adjust the filters to start reviewing.',class_='empty')
        row=row_for(current.get());meta=runs[current.get()[0]]['manifest'];history=row.get('history',[])
        history_ui=ui.tags.details(ui.tags.summary(f'Conversation history · {len(history)} previous turns'),
            *[ui.div(ui.div('USER',class_='role'),ui.p(turn[0]),ui.div('ASSISTANT',class_='role'),
                      citations(turn[1],set()),class_='history-turn') for turn in history]) if history else ui.p('First turn · no previous conversation',class_='meta')
        return ui.div(
            ui.div(ui.span('Multi-turn' if history else 'Single turn',class_='pill'),
                   ui.span(row.get('mode','unknown'),class_='pill'),
                   ui.span('Blind review' if current.get()[0].startswith('judge:') else 'LangSmith' if current.get()[0]=='cloud' else 'Local eval',class_='pill')),
            ui.p(row['query'],class_='question'),
            ui.p(f"{row.get('model',meta.get('model','?'))} · {row.get('start_time','')} · latency {row.get('generation_seconds','?')} s",class_='meta'),
            history_ui,ui.hr(),ui.h3('Current answer'),
            ui.div(row['error'],class_='error-text') if row.get('error') else None,
            citations(row.get('answer',''),{s['rank'] for s in row['results']}),class_='conversation-scroll')

    @output(suspend_when_hidden=False)
    @render.ui
    def evidence_panel():
        if not active():return ui.div('No trace selected.',class_='empty')
        row=row_for(current.get());batch=runs[current.get()[0]];case=batch['cases'].get(row['case_id'])
        return ui.div(ui.p(f"{len(row['results'])} retrieved sources · click a citation in the answer to open its source.",class_='meta'),
                      *[source_card(s) for s in row['results']],
                      ui.p('No sources were retrieved.',class_='warning') if not row['results'] else None,
                      ui.tags.details(ui.tags.summary('Proposed reference evidence · local eval'),
                         ui.p('Assistant-proposed references, not independently validated.',class_='meta'),
                         *[source_card(s,gold=True) for s in case['gold_evidence']]) if case else None,
                      class_='evidence-scroll')

    @render.download_button(filename='trace-reviews.jsonl')
    def export_labels():
        if input.run().startswith('judge:') and input.run() in runs:
            batch=runs[input.run()]
            rows=[label for r in batch['rows'] if (label:=CALIBRATION.get(input.run(),r,batch['manifest']['rubric_hash']))]
        elif input.run()=='cloud' and gateway:
            rows=[]
            for rid,row in gateway.rows.items():
                label=gateway.get(rid)
                if label:rows.append({'run_id':rid,'trace_hash':row['trace_hash'],'project_id':gateway.project_id,**label})
        else: rows=STORE.export()
        yield ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)


app=App(app_ui,server)
