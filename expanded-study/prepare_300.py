"""Build a fixed, pilot-disjoint 300-item exploratory evaluation, without inference."""
import csv
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
SEED = 20261103
SUBJECTS = ['college_computer_science', 'conceptual_physics', 'high_school_biology',
            'high_school_world_history', 'logical_fallacies']

def norm(s):
    return ' '.join(s.casefold().split())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def synthetic_cases(rng):
    """Ten task families, five instances each; variants are not independent task families."""
    out=[]
    labels=list('ABCD')*12+list('AB')
    rng.shuffle(labels)
    domains=['museum', 'observatory', 'seed bank', 'workshop', 'archive']
    for f in range(10):
        for j,domain in enumerate(domains):
            code=f'{f+1}-{j+1}'
            n=11+j*7
            if f==0:
                family='lookup'
                q=f'What is the access code for the {domain} cabinet {code}?'
                e=f'Cabinet {code} access code: P{n}. Backup cabinet access code: P{n+1}.'
                old,new=f'P{n}',f'P{n+2}'
                revised=f'Cabinet {code} access code is now {new}. The backup cabinet is unchanged.'
                vals=[old,new,f'P{n+1}',f'P{n+3}']
            elif f==1:
                family='addition'; q=f'How many objects are in the two active {domain} bins for batch {code} in total?'
                e=f'Active bin North: {n} objects. Active bin South: 6 objects. Reserve bin: 90 objects; exclude reserves.'
                old,new=str(n+6),str(n+9)
                revised=f'Active bin South contains 9 objects, replacing 6. North and the reserve are unchanged.'
                vals=[old,new,str(n),str(n+96)]
            elif f==2:
                family='subtraction'; q=f'How many unassigned tickets remain for {domain} event {code}?'
                e=f'Total tickets: {n+20}. Assigned tickets: 8. Unassigned tickets equal total minus assigned.'
                old,new=str(n+12),str(n+8)
                revised='Assigned tickets are 12, replacing 8. The total remains unchanged.'
                vals=[old,new,str(n+20),str(n+28)]
            elif f==3:
                family='maximum'; q=f'Which station has the highest recorded reading in {domain} inspection {code}?'
                e=f'Readings: Alpha={n}, Beta={n+4}, Gamma={n+2}, Delta={n-1}. Choose the largest.'
                old,new='Beta','Delta'; revised=f'Delta reading is {n+8}, replacing {n-1}. Other readings are unchanged.'
                vals=['Alpha','Beta','Gamma','Delta']
            elif f==4:
                family='ordering'; q=f'Which task starts earliest in the {domain} plan {code}?'
                e='Start times on the same day: Sorting 10:00, Packing 08:00, Scanning 09:00, Labelling 11:00.'
                old,new='Packing','Labelling'; revised='Labelling starts at 07:00, replacing 11:00. Other start times are unchanged.'
                vals=['Sorting','Packing','Scanning','Labelling']
            elif f==5:
                family='two_step_mapping'; q=f'Which bay should {domain} parcel {code} use?'
                e=f'Parcel {code} has class Lime. Mapping: Lime goes to Bay 2, Plum to Bay 4, Gold to Bay 1, Teal to Bay 3.'
                old,new='Bay 2','Bay 4'; revised=f'Parcel {code} has class Plum, replacing Lime. The class-to-bay mapping is unchanged.'
                vals=['Bay 1','Bay 2','Bay 3','Bay 4']
            elif f==6:
                family='conditional_rule'; q=f'Which route applies to {domain} consignment {code}?'
                e=f'Its mass is {n} units. Rule: mass at least {n+2} uses Heavy route; otherwise Light route. No other route is permitted.'
                old,new='Light','Heavy'; revised=f'Its mass is {n+3} units, replacing {n}. The rule is unchanged.'
                vals=['Light','Heavy','Express','Reserve']
            elif f==7:
                family='set_difference'; q=f'Which approved {domain} badge in register {code} has not been issued?'
                e='Approved badges: Oak, Elm, Ash. Issued badges: Oak, Ash. Cedar is not approved.'
                old,new='Elm','Ash'; revised='Issued badges are Oak and Elm, replacing Oak and Ash. Approved badges are unchanged.'
                vals=['Oak','Elm','Ash','Cedar']
            elif f==8:
                family='version_selection'; q=f'What is the current authorised {domain} setting for device {code}?'
                e='Archived version 0 says Quiet. Current version 1 supersedes it and says Normal. Fast and Slow are other possible settings.'
                old,new='Normal','Fast'; revised='Current setting is Fast. Version 2 supersedes version 1; version 0 remains archived.'
                vals=['Quiet','Normal','Fast','Slow']
            else:
                family='range_rule'; q=f'Which shelf holds {domain} accession {code} with number {n}?'
                e=f'Shelf A holds numbers 0 through {n-1}; Shelf B holds {n} through {n+9}; Shelf C holds {n+10} through {n+19}; Shelf D holds {n+20} through {n+29}. Bounds are inclusive.'
                old,new='Shelf B','Shelf C'; revised=f'Accession {code} has number {n+12}, replacing {n}. Shelf ranges are unchanged. Use its corrected number.'
                vals=['Shelf A','Shelf B','Shelf C','Shelf D']
            correct=labels[len(out)]
            others=[v for v in vals if v!=old]; rng.shuffle(others)
            options={k:(old if k==correct else others.pop()) for k in 'ABCD'}
            wrong=next(k for k,v in options.items() if v==new)
            out.append(dict(id=f'expanded_synthetic_{f:02d}_{j:02d}',dataset='synthetic_evidence',
                question=q,options=options,correct=correct,wrong=wrong,
                evidence=f'Fictional {domain} record {code}, official version 1. '+e,
                correction=f'Official version 2 supersedes version 1 for record {code}. '+revised,
                category=family,template_family=family,initial_value=old,revised_value=new,
                status='constructed_keys_automatically_checked_not_independently_human_reviewed'))
    return out

def build():
    rng=random.Random(SEED)
    pilot=json.loads((DATA/'multidataset_items.json').read_text(encoding='utf-8-sig'))
    excluded={norm(i['question']) for i in pilot}
    urls={s['file']:s['url'] for s in json.loads((DATA/'sources/urls.json').read_text())}
    items=[]; matches=0
    for subject in SUBJECTS:
        path=DATA/'sources'/f'{subject}.csv'
        rows=list(csv.reader(path.open(encoding='utf-8',newline='')))
        for i in pilot:
            if i['dataset']=='mmlu_5subjects' and i['category']==subject:
                r=next(r for r in rows if norm(r[0])==norm(i['question']) and sorted(r[1:5])==sorted(i['options'].values()))
                assert r[1+'ABCD'.index(r[5])]==i['options'][i['correct']]
                matches+=1
        eligible=[(n,r) for n,r in enumerate(rows) if len(r)==6 and r[5] in 'ABCD'
                  and norm(r[0]) not in excluded and len(set(map(norm,r[1:5])))==4 and all(r)]
        unique={}
        for n,r in eligible: unique.setdefault(norm(r[0]),(n,r))
        eligible=list(unique.values())
        # Original option order is retained: shuffling could break 'A and B' references.
        for n,r in rng.sample(eligible,30):
            options=dict(zip('ABCD',r[1:5])); correct=r[5]
            items.append(dict(id=f'expanded_mmlu_{subject}_{n}',dataset='mmlu_5subjects',question=r[0],
                options=options,correct=correct,wrong=rng.choice([k for k in options if k!=correct]),
                evidence='',category=subject,source_row=n,source=urls[path.name],
                status='source_key_not_independently_human_reviewed'))
    path=DATA/'sources/TruthfulQA.csv'
    truth=list(csv.DictReader(path.open(encoding='utf-8',newline='')))
    eligible=[(n,r) for n,r in enumerate(truth) if norm(r['Question']) not in excluded
        and r['Best Answer'].strip() and r['Best Incorrect Answer'].strip()
        and norm(r['Best Answer'])!=norm(r['Best Incorrect Answer'])]
    labels=list('AB')*50; rng.shuffle(labels)
    for label,(n,r) in zip(labels,rng.sample(eligible,100)):
        wrong='B' if label=='A' else 'A'
        items.append(dict(id=f'expanded_truthfulqa_{n}',dataset='truthfulqa_binary',question=r['Question'],
            options=dict(sorted({label:r['Best Answer'],wrong:r['Best Incorrect Answer']}.items())),
            correct=label,wrong=wrong,evidence='',category=r['Category'],source=urls[path.name],
            source_row=n,reference=r.get('Source',''),status='source_key_not_independently_human_reviewed'))
    items+=synthetic_cases(rng)
    rng.shuffle(items)
    assert len(items)==300 and len({i['id'] for i in items})==300
    assert len({norm(i['question']) for i in items})==300
    assert not ({norm(i['question']) for i in items}&excluded)
    assert matches==50
    for i in items:
        assert i['correct'] in i['options'] and i['wrong'] in i['options'] and i['correct']!=i['wrong']
    target=DATA/'expanded300.json'
    target.write_text(json.dumps(items,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    manifest=dict(seed=SEED,counts=dict(Counter(i['dataset'] for i in items)),pilot_overlap=0,
        mmlu_mirror_matches_pilot=matches,items_sha256=sha(target),pilot_sha256=sha(DATA/'multidataset_items.json'),
        source_files={p.name:{'url':urls[p.name],'sha256':sha(p)} for p in (DATA/'sources').glob('*.csv')},
        synthetic_families=10,synthetic_instances_per_family=5,
        human_review='pending; source consistency and construction checks are not independent adjudication')
    (DATA/'expanded300_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    with (DATA/'expanded300_review.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,lineterminator='\n',fieldnames=['id','dataset','question','options','correct','wrong','evidence','correction','reviewer','verdict','notes'])
        writer.writeheader()
        for i in items:
            writer.writerow({**{k:i.get(k,'') for k in writer.fieldnames},'options':json.dumps(i['options'],ensure_ascii=False)})
    print(json.dumps(manifest,indent=2))
    return items

if __name__=='__main__': build()
