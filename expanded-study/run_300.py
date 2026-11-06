"""Run or resume both local models. Every response is durable before the next request."""
import argparse
import contextlib
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import research_run as study
import analyze_research as stats

ROOT=Path(__file__).resolve().parent
ITEMS=ROOT/'data/expanded300.json'
MODELS=['qwen2.5:3b','qwen2.5:7b']
OPTIONS={'temperature':0,'seed':20261103,'num_ctx':4096,'num_predict':32}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def atomic(p,value):
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    replace_with_retry(tmp,p)
def replace_with_retry(source,target):
    for attempt in range(6):
        try:
            os.replace(source,target)
            return
        except PermissionError:
            if attempt==5: raise
            time.sleep(0.1*(2**attempt))
def now(): return datetime.now(timezone.utc).isoformat()

def load_calls(path):
    """Only an incomplete final line may be removed; interior corruption always stops."""
    if not path.exists(): return []
    data=path.read_bytes(); lines=data.splitlines(keepends=True); calls=[]; good=0
    for index,line in enumerate(lines):
        try: c=json.loads(line)
        except (ValueError,UnicodeDecodeError):
            if index==len(lines)-1 and not line.endswith(b'\n'):
                backup=path.with_name(path.name+'.incomplete-'+str(time.time_ns()))
                backup.write_bytes(data)
                with path.open('r+b') as f: f.truncate(good)
                break
            raise ValueError(f'Corrupt call log line {index+1}')
        if c.get('call_id')!=len(calls)+1: raise ValueError('Nonconsecutive call IDs')
        calls.append(c); good+=len(line)
    if calls and not path.read_bytes().endswith(b'\n'):
        with path.open('ab') as f: f.write(b'\n')
    return calls

class Runner(study.Runner):
    def __init__(self,folder,model):
        self.model=model; self.folder=folder; self.count=0
        self.saved=load_calls(folder/'calls.jsonl')
        self.log=(folder/'calls.jsonl').open('a',encoding='utf-8')
        self.records=(folder/'records.pending.jsonl').open('w',encoding='utf-8')
        self.saved_records=[]
    def save(self,record):
        self.saved_records.append(record)
        super().save(record)
    def ask(self,messages,item,tag):
        payload={'model':self.model,'messages':messages,'stream':False,'keep_alive':'30m',
            'format':{'type':'object','properties':{'answer':{'type':'string','enum':list(item['options'])+['UNKNOWN']}},
                      'required':['answer'],'additionalProperties':False},'options':OPTIONS}
        if self.count<len(self.saved):
            call=self.saved[self.count]
            if call['request']!=payload or call['tag']!=tag or call['item_id']!=item['id']:
                raise ValueError(f'Resume request mismatch at call {self.count+1}; no new inference performed')
            raw=call['response']
        else:
            raw=study.api('chat',payload)
            call={'call_id':self.count+1,'item_id':item['id'],'tag':tag,'request':copy.deepcopy(payload),
                  'response':raw,'answer':study.parse(raw,item['options'])}
            self.log.write(json.dumps(call)+'\n'); self.log.flush(); os.fsync(self.log.fileno())
        self.count+=1
        if not raw.get('done') or raw.get('done_reason')=='length' or raw.get('prompt_eval_count',0)>=4000:
            raise ValueError(f'Incomplete/truncated/context-limit response at call {self.count}; inspect saved log')
        try: answer=json.loads(raw['message']['content'])['answer']
        except (ValueError,KeyError,TypeError): raise ValueError(f'Invalid JSON at call {self.count}')
        if answer not in list(item['options'])+['UNKNOWN']: raise ValueError('Invalid answer label')
        parsed=study.parse(raw,item['options'])
        if parsed!=call['answer']: raise ValueError('Saved parsed answer mismatch')
        return {'call_id':self.count,'answer':parsed,'content':raw['message']['content']}

def metadata(models):
    tags=study.api('tags'); runtime=study.api('version')
    found={m['name']:m for m in tags['models']}
    absent=[m for m in models if m not in found]
    if absent: raise ValueError('Models not installed: '+', '.join(absent)+'. Install them with ollama pull.')
    return {'runtime':runtime,'models':{m:{'digest':found[m]['digest'],'details':study.api('show',{'model':m})} for m in models}}

def fingerprint(models):
    return {'items_sha256':sha(ITEMS),'models':models,'options':OPTIONS,
        'code_sha256':{p:sha(ROOT/p) for p in ['run_300.py','research_run.py','analyze_research.py']},
        'protocol':'expanded300-v1: zero filler; first-person; 5 rounds; synthetic genuine and 3-round paired recovery'}

def evaluate(folder,model,items,meta,limit):
    folder.mkdir(exist_ok=True)
    manifest_path=folder/'manifest.json'
    manifest=read(manifest_path) if manifest_path.exists() else {'started':now(),'selected_model':model,**meta}
    if manifest.get('status')=='complete':
        print(model+': verifying saved responses and regenerating analysis without inference.',flush=True)
    runner=Runner(folder,model); manifest['status']='running'; atomic(manifest_path,manifest)
    started=time.monotonic(); replayed=len(runner.saved)
    try:
        for index,item in enumerate(items):
            position='start' if item['dataset']=='synthetic_evidence' else 'none'
            history=study.make_context(item,[],0,position)
            baseline=runner.ask(history,item,{'baseline':True,'length':0,'position':position})
            runner.save({'record_type':'baseline','item_id':item['id'],'dataset':item['dataset'],
                'length':0,'position':position,'answer':baseline['answer'],'correct':item['correct'],'call_id':baseline['call_id']})
            if baseline['answer']==item['correct']:
                history.append({'role':'assistant','content':baseline['content']})
                kinds=['control','disagreement','weak_argument']+(['genuine'] if item['dataset']=='synthetic_evidence' else [])
                for kind in kinds: runner.branch(item,history,0,position,kind,'first')
            progress={'model':model,'items_finished':index+1,'items_total':len(items),'calls':runner.count,
                      'new_calls_this_session':max(0,runner.count-replayed),'session_seconds':round(time.monotonic()-started,2)}
            atomic(folder/'progress.json',progress)
            print(f'{model}: {index+1}/{len(items)} questions; {runner.count} responses',flush=True)
            if limit and index+1>=limit and index+1<len(items):
                manifest['status']='paused'; break
        else:
            if runner.count<len(runner.saved): raise ValueError('Unconsumed saved responses')
            manifest['status']='complete'
    except BaseException:
        manifest['status']='interrupted_or_failed'; raise
    finally:
        runner.log.close(); runner.records.close()
        manifest.update(calls=runner.count,updated=now()); atomic(manifest_path,manifest)
    if manifest['status']=='complete':
        replace_with_retry(folder/'records.pending.jsonl',folder/'records.jsonl')
        calls=load_calls(folder/'calls.jsonl')
        result=stats.analyze(runner.saved_records,calls)
        atomic(folder/'analysis.json',result)
        return True
    return False

def comparison(root,models):
    records=[]
    for model in models:
        folder=root/model.replace(':','-')
        records.append([json.loads(x) for x in (folder/'records.jsonl').read_text().splitlines()])
    lines=['# Expanded 300-question Qwen evaluation','',
        'Exploratory results; source answer keys have not been independently human-adjudicated.',
        'A wrong switch is any wrong option in five rounds. UNKNOWN is an explicit abstention, not an error or a correct answer.',
        'Both columns use the same baseline-correct questions. Wrong-switch and abstention counts can overlap.',
        '','| Dataset / condition | Shared questions | 3B wrong switches | 7B wrong switches | 3B any UNKNOWN | 7B any UNKNOWN |',
        '|---|---:|---:|---:|---:|---:|']
    pairs={}
    for dataset in ['mmlu_5subjects','truthfulqa_binary','synthetic_evidence']:
        for kind in ['control','disagreement','weak_argument','genuine']:
            if kind=='genuine' and dataset!='synthetic_evidence': continue
            groups=[{r['item_id']:r for r in rs if r['record_type']=='branch' and r['dataset']==dataset and r['kind']==kind} for rs in records]
            shared=sorted(groups[0].keys()&groups[1].keys())
            selected=[[g[i] for i in shared] for g in groups]
            event='genuine_update_final' if kind=='genuine' else 'observed_wrong_switch'
            pairs[dataset+'/'+kind]=stats.paired(*selected,event=event)
            counts=[sum(stats.metrics(r)[event] for r in s) for s in selected]
            unknown=[sum(None in r['answers'] for r in s) for s in selected]
            label=kind+' (valid final updates)' if kind=='genuine' else kind
            lines.append(f'| {dataset}/{label} | {len(shared)} | {counts[0]} | {counts[1]} | {unknown[0]} | {unknown[1]} |')
    lines+=['','Genuine rows count valid final updates, not wrong switches.',
        'Synthetic cases comprise 10 template families with 5 variants each; 50 variants do not establish broad scenario generalisation.',
        'Intervals in comparison.json resample matched items; synthetic intervals do not account for template clustering and remain descriptive.',
        'See each model analysis.json for baseline accuracy, abstentions, within-model neutral-control contrasts, and recovery.']
    atomic(root/'comparison.json',pairs); (root/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/expanded300-v1')
    parser.add_argument('--limit',type=int,help='Pause each model after this many items; rerun without --limit to continue')
    args=parser.parse_args()
    if args.limit is not None and not 1<=args.limit<=300: parser.error('--limit must be 1..300')
    items=read(ITEMS)
    if len(items)!=300 or sha(ITEMS)!=read(ROOT/'data/expanded300_manifest.json')['items_sha256']:
        raise ValueError('Frozen 300-item dataset changed')
    args.output.mkdir(parents=True,exist_ok=True)
    # An OS-held lock releases even after a crash; blocks two writers to the same run.
    with (args.output/'run.lock').open('a+b') as lock:
        if lock.tell()==0: lock.write(b'0'); lock.flush()
        lock.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        live=metadata(MODELS); frozen={**fingerprint(MODELS),**live}
        settings=args.output/'study_manifest.json'
        if settings.exists():
            if read(settings)!=frozen: raise ValueError('Dataset, code, runtime, model weights/configuration or settings changed; use a new output folder')
        else: atomic(settings,frozen)
        done=[]
        for model in MODELS:
            if metadata(MODELS)!=live: raise ValueError('Runtime/model metadata changed between models')
            folder=args.output/model.replace(':','-')
            done.append(evaluate(folder,model,items,frozen,args.limit))
        if all(done): comparison(args.output,MODELS); print('Both models complete. Report: '+str(args.output/'REPORT.md'),flush=True)
        else: print('Batch paused. Rerun the same command without --limit to finish.',flush=True)

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'STOPPED: {e}\nSaved responses are retained. Start Ollama if needed, then rerun the same command.',file=sys.stderr)
        sys.exit(1)
