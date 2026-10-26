"""Offline preparation and reservation dry-run for P03 telemetry evaluation."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
from typing import Any
try:
 from .campaign_ledger import CampaignLedger
except ImportError:
 from campaign_ledger import CampaignLedger
ROOT=Path(__file__).resolve().parents[1]
FAMILIES={'parent_child_correlation','usage_accounting','provider_model_identity','content_exclusion','exporter_outage_recovery','alert_fire_recovery'}
CONTENT_TERMS=('prompt','response','content','argument','message')
class CampaignError(ValueError): pass

def read_json(path: Path) -> dict[str,Any]:
 try: value=json.loads(path.read_text(encoding='utf-8-sig'))
 except (OSError,json.JSONDecodeError) as exc: raise CampaignError(f'cannot read valid JSON: {path.name}') from exc
 if not isinstance(value,dict): raise CampaignError(f'expected JSON object: {path.name}')
 return value

def validate_cases(rows: list[dict[str,Any]], manifest: dict[str,Any]) -> None:
 if len(rows)!=30 or len({r.get('id') for r in rows})!=30: raise CampaignError('dataset must have 30 unique scenario IDs')
 if {s:sum(r.get('split')==s for r in rows) for s in ('development','holdout')}!={'development':9,'holdout':21}: raise CampaignError('dataset split must be 9/21')
 if any(r.get('language')!='NOT_APPLICABLE' for r in rows): raise CampaignError('operational scenario language must be NOT_APPLICABLE')
 if {r.get('family') for r in rows}!=FAMILIES or any(sum(r.get('family')==f for r in rows)<3 for f in FAMILIES): raise CampaignError('family set or minimum coverage invalid')
 groups={}
 for row in rows:
  groups.setdefault(row.get('source_group'),set()).add(row.get('split'))
  if (not isinstance(row.get('preconditions'),str) or not row['preconditions'] or not isinstance(row.get('expected'),dict)
      or not isinstance(row.get('forbidden_content_attributes'),list) or not row['forbidden_content_attributes']
      or not isinstance(row.get('limits'),dict) or row['limits']!={'provider_calls':1,'input_tokens':4096,'output_tokens':512,'scenario_timeout_seconds':45}):
   raise CampaignError(f'case contract invalid: {row.get("id","unknown")}')
 if any(len(splits)>1 for splits in groups.values()): raise CampaignError('source group crosses development/holdout splits')
 if len(groups)!=len(rows): raise CampaignError('scenario source groups must be unique')
 if manifest.get('case_count')!=30 or set(manifest.get('families',[]))!=FAMILIES: raise CampaignError('manifest denominators or families mismatch')

def read_cases(path:Path, manifest:dict[str,Any])->list[dict[str,Any]]:
 try: raw=path.read_bytes()
 except OSError as exc: raise CampaignError('dataset is unavailable') from exc
 if hashlib.sha256(raw).hexdigest()!=manifest.get('sha256_cases_jsonl'): raise CampaignError('dataset SHA-256 mismatch')
 try: rows=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
 except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise CampaignError('dataset must be UTF-8 JSONL') from exc
 validate_cases(rows,manifest); return rows

def validate_config(config:dict[str,Any])->None:
 if config.get('trials_per_case')!=3 or config.get('pilot_trials_per_case')!=1: raise CampaignError('trial configuration invalid')
 if config.get('per_case_caps')!={'provider_calls_per_trial':1,'input_tokens_per_trial':4096,'output_tokens_per_trial':512,'scenario_timeout_seconds':45}: raise CampaignError('per-case caps invalid')
 planned=config.get('planned_reservations',{})
 if planned.get('primary_campaign_max_calls')!=90 or planned.get('confirmation_max_calls')!=60 or planned.get('all_stages_max_calls_if_additive')!=156: raise CampaignError('planned reservation totals invalid')
 if config.get('generation_enabled') is not False or config.get('offline_simulation_counts_as_live_evidence') is not False: raise CampaignError('generation/provenance must fail closed')
 if config.get('cumulative_caps',{}).get('authorized_paid_spend_usd')!=0: raise CampaignError('paid campaign spend must remain zero')

def grade_scenario(case:dict[str,Any], observation:Any, *, provenance:str='live')->list[str]:
 if provenance not in {'live','offline_simulation','fixture'}: return ['invalid provenance']
 if provenance!='live': return ['simulation/fixture is not live OTLP evidence']
 if not isinstance(observation,dict): return ['observation schema invalid']
 errors=[]; expected=case['expected']; family=case['family']
 attrs=observation.get('content_attributes',[])
 if not isinstance(attrs,list): errors.append('content attribute inventory invalid')
 elif any(any(term in str(name).casefold() for term in CONTENT_TERMS) for name in attrs): errors.append('content-bearing attribute exported')
 if family=='parent_child_correlation':
  names=observation.get('span_names',[]); traces=observation.get('trace_ids',[]); parents=observation.get('parent_edges',{})
  if not set(expected['required_span_names']).issubset(names): errors.append('required span missing')
  if not traces or len(set(traces))!=1: errors.append('trace correlation mismatch')
  for parent,child in expected.get('parent_edges',[]):
   if not isinstance(parents,dict) or parents.get(child)!=parent: errors.append('parent-child span correlation mismatch'); break
 elif family=='usage_accounting':
  response=observation.get('response_usage'); span=observation.get('span_usage'); metric=observation.get('metric_usage')
  if not isinstance(response,dict) or response!=span or response!=metric: errors.append('provider usage accounting mismatch')
  if not isinstance(response,dict) or any(not isinstance(response.get(k),int) or response[k]<0 for k in ('input_tokens','output_tokens')): errors.append('usage values invalid')
 elif family=='provider_model_identity':
  if observation.get('provider')!='groq' or observation.get('model')!='openai/gpt-oss-20b': errors.append('provider/model identity mismatch')
 elif family=='exporter_outage_recovery':
  if observation.get('exporter_states')!=['failed','recovered']: errors.append('exporter outage did not recover')
  if not isinstance(observation.get('export_attempts'),int) or observation['export_attempts']>3: errors.append('exporter failure was unbounded')
  if observation.get('pending_spans_after_recovery')!=0 or observation.get('flush_success_after_recovery') is not True: errors.append('exporter recovery incomplete')
 elif family=='alert_fire_recovery':
  if observation.get('alert_states')!=['firing','inactive']: errors.append('alert fire/recovery lifecycle mismatch')
 return errors

def summarize(stage:str,rows:list[dict[str,Any]],config:dict[str,Any],manifest:dict[str,Any])->dict[str,Any]:
 if stage=='pilot': selected=[r for r in rows if r['split']=='development'][:6]
 elif stage in {'development','holdout'}: selected=[r for r in rows if r['split']==stage]
 else: raise CampaignError('unknown stage')
 trials=len(selected)*(config['pilot_trials_per_case'] if stage=='pilot' else config['trials_per_case']); caps=config['per_case_caps']; calls=trials*caps['provider_calls_per_trial']; planned=config['planned_reservations']
 blockers=['budget.authorized_paid_spend_usd_zero','approval.expanded_campaign_approval','approval.independent_dataset_and_rubric_review','approval.clean_context_phase_verification','cumulative_caps.requests','cumulative_caps.input_tokens','cumulative_caps.output_tokens','cumulative_caps.provider_account_quota','cumulative_caps.confirmation_funding','execution.min_seconds_between_calls','execution.max_wall_clock_minutes','execution.persistent_cumulative_ledger','execution.serialized_campaign_lease','provider.authenticated_model_catalog_preflight']
 return {'status':'DRY_RUN','stage':stage,'dataset_sha256':manifest['sha256_cases_jsonl'],'cases':len(selected),'logical_trials':trials,'max_provider_calls':calls,'max_input_tokens':trials*caps['input_tokens_per_trial'],'max_output_tokens':trials*caps['output_tokens_per_trial'],'strata':{'family':{f:sum(r['family']==f for r in selected) for f in sorted(FAMILIES)},'split':{s:sum(r['split']==s for r in selected) for s in ('development','holdout')}},'campaign_plan':{k:planned[k] for k in ('primary_campaign_max_calls','primary_campaign_max_input_tokens','primary_campaign_max_output_tokens','confirmation_fresh_cases','confirmation_max_calls','confirmation_max_input_tokens','confirmation_max_output_tokens','all_stages_max_calls_if_additive','all_stages_max_input_tokens_if_additive','all_stages_max_output_tokens_if_additive')},'authorized_paid_spend_usd':0,'blockers':blockers,'generation_authorized':False,'provider_accessed':False,'credentials_read':False,'network_accessed':False,'docker_mutated':False}

def main(argv:list[str]|None=None)->int:
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--config',type=Path,default=ROOT/'evals/live-campaign.json'); command=parser.add_mutually_exclusive_group(required=True); command.add_argument('--stage',choices=('pilot','development','holdout')); command.add_argument('--resume',metavar='CAMPAIGN_ID'); parser.add_argument('--dry-run',action='store_true'); args=parser.parse_args(argv)
 try:
  if args.resume is not None:
   if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}',args.resume): raise CampaignError('invalid campaign ID')
   ledger_path=ROOT/'artifacts/evals/live/ledger.sqlite'
   if not ledger_path.is_file(): raise CampaignError('campaign ledger does not exist')
   ledger=CampaignLedger(ledger_path,campaign_id=args.resume,read_only=True); attempts=ledger.reserved_trials()
   if not attempts: raise CampaignError('campaign has no recorded attempts')
   report={'project':'p03','campaign_id':args.resume,'mode':'read-only-resume-inspection','attempts':attempts,'cumulative_usage':{k:str(v) for k,v in ledger.totals().items()},'provider_accessed':False}
   if args.dry_run: print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)); return 0
   print(json.dumps({**report,'status':'INCOMPLETE'},sort_keys=True)); return 2
  cfg=read_json(args.config if args.config.is_absolute() else ROOT/args.config); manifest=read_json(ROOT/cfg['dataset_manifest']); rows=read_cases(ROOT/cfg['cases_path'],manifest); validate_config(cfg); report=summarize(args.stage,rows,cfg,manifest)
 except (CampaignError,KeyError,TypeError) as exc: print(json.dumps({'status':'INCOMPLETE','error':str(exc)},sort_keys=True)); return 2
 if args.dry_run: print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)); return 0
 print(json.dumps({**report,'status':'INCOMPLETE','reason':'generation is disabled during campaign preparation'},sort_keys=True)); return 2
if __name__=='__main__': sys.exit(main())
