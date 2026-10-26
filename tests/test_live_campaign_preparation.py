from __future__ import annotations
import json,subprocess,sys,unittest,tempfile
from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from scripts.run_live_campaign import CampaignError,grade_scenario,read_cases,read_json,summarize,validate_cases
ROOT=Path(__file__).resolve().parents[1]; CONFIG=read_json(ROOT/'evals/live-campaign.json'); MANIFEST=read_json(ROOT/CONFIG['dataset_manifest']); CASES=read_cases(ROOT/CONFIG['cases_path'],MANIFEST)

class CampaignPreparationTests(unittest.TestCase):
 def test_dataset_denominators_and_families(self):
  self.assertEqual(len(CASES),30); self.assertEqual(sum(x['split']=='development' for x in CASES),9); self.assertEqual(sum(x['split']=='holdout' for x in CASES),21); self.assertTrue(all(x['language']=='NOT_APPLICABLE' for x in CASES)); self.assertEqual({x['family'] for x in CASES},set(MANIFEST['families']))
 def test_dataset_rejects_cross_split_source(self):
  rows=[dict(x) for x in CASES]; rows[0]=dict(rows[0]); rows[0]['source_group']=rows[12]['source_group']
  with self.assertRaisesRegex(CampaignError,'crosses'): validate_cases(rows,MANIFEST)
 def test_trace_grader_rejects_correlation_mismatch(self):
  case=next(x for x in CASES if x['family']=='parent_child_correlation'); obs={'span_names':case['expected']['required_span_names'],'trace_ids':['abc','def'],'parent_edges':{'agent.run':'wrong'},'content_attributes':[]}
  errors=grade_scenario(case,obs); self.assertIn('trace correlation mismatch',errors); self.assertIn('parent-child span correlation mismatch',errors)
 def test_usage_and_identity_mismatches_fail(self):
  usage=next(x for x in CASES if x['family']=='usage_accounting'); obs={'response_usage':{'input_tokens':3,'output_tokens':2},'span_usage':{'input_tokens':3,'output_tokens':1},'metric_usage':{'input_tokens':3,'output_tokens':2},'content_attributes':[]}
  self.assertIn('provider usage accounting mismatch',grade_scenario(usage,obs))
  identity=next(x for x in CASES if x['family']=='provider_model_identity'); self.assertIn('provider/model identity mismatch',grade_scenario(identity,{'provider':'other','model':'fixture','content_attributes':[]}))
 def test_privacy_exporter_and_alert_fail_closed(self):
  privacy=next(x for x in CASES if x['family']=='content_exclusion'); self.assertIn('content-bearing attribute exported',grade_scenario(privacy,{'content_attributes':['supportops.llm.content']}))
  outage=next(x for x in CASES if x['family']=='exporter_outage_recovery'); errs=grade_scenario(outage,{'exporter_states':['failed'],'export_attempts':100,'pending_spans_after_recovery':9,'flush_success_after_recovery':False,'content_attributes':[]}); self.assertIn('exporter failure was unbounded',errs); self.assertIn('exporter outage did not recover',errs)
  alert=next(x for x in CASES if x['family']=='alert_fire_recovery'); self.assertIn('alert fire/recovery lifecycle mismatch',grade_scenario(alert,{'alert_states':['firing'],'content_attributes':[]}))
 def test_simulation_never_counts_as_live_evidence(self):
  case=CASES[0]; self.assertEqual(grade_scenario(case,{},provenance='offline_simulation'),['simulation/fixture is not live OTLP evidence'])
 def test_offline_dry_run_and_generation_block(self):
  result=subprocess.run([sys.executable,'-S',str(ROOT/'scripts/run_live_campaign.py'),'--stage','pilot','--dry-run'],cwd=ROOT,capture_output=True,text=True,check=False); self.assertEqual(result.returncode,0,result.stderr); report=json.loads(result.stdout); self.assertEqual((report['cases'],report['logical_trials'],report['max_provider_calls']),(6,6,6)); self.assertEqual(report['campaign_plan']['primary_campaign_max_calls'],90); self.assertEqual(report['campaign_plan']['confirmation_max_calls'],60); self.assertEqual(report['campaign_plan']['all_stages_max_calls_if_additive'],156); self.assertFalse(report['provider_accessed']); self.assertFalse(report['credentials_read']); self.assertFalse(report['network_accessed']); self.assertFalse(report['docker_mutated']); self.assertIn('budget.authorized_paid_spend_usd_zero',report['blockers'])
  dev=summarize('development',CASES,CONFIG,MANIFEST); hold=summarize('holdout',CASES,CONFIG,MANIFEST); self.assertEqual((dev['cases'],dev['logical_trials'],dev['max_provider_calls']),(9,27,27)); self.assertEqual((hold['cases'],hold['logical_trials'],hold['max_provider_calls']),(21,63,63))
  blocked=subprocess.run([sys.executable,str(ROOT/'scripts/run_live_campaign.py'),'--stage','pilot'],cwd=ROOT,capture_output=True,text=True,check=False); self.assertEqual(blocked.returncode,2); self.assertEqual(json.loads(blocked.stdout)['status'],'INCOMPLETE')
 def test_resume_inspection_is_read_only_and_rejects_unknown_campaign(self):
  from scripts import run_live_campaign
  from scripts.campaign_ledger import CampaignLedger
  with tempfile.TemporaryDirectory() as temporary:
   root=Path(temporary); ledger_path=root/'artifacts/evals/live/ledger.sqlite'; ledger=CampaignLedger(ledger_path,campaign_id='campaign-a'); empty=StringIO()
   with patch.object(run_live_campaign,'ROOT',root),redirect_stdout(empty): self.assertEqual(run_live_campaign.main(['--resume','unknown','--dry-run']),2)
   self.assertIn('campaign has no recorded attempts',empty.getvalue())
   ledger.reserve(case_id='case-1',trial=1,input_tokens=20,output_tokens=10,estimated_cost_usd=Decimal('0.02'),caps={'requests':1,'input_tokens':100,'output_tokens':100,'estimated_cost_usd':Decimal('0.10')})
   output=StringIO()
   with patch.object(run_live_campaign,'ROOT',root),redirect_stdout(output): self.assertEqual(run_live_campaign.main(['--resume','campaign-a','--dry-run']),0)
   report=json.loads(output.getvalue()); self.assertEqual(report['project'],'p03'); self.assertEqual(report['attempts'][0]['event'],'reserved'); self.assertEqual(report['cumulative_usage']['requests'],'1'); self.assertFalse(report['provider_accessed'])
if __name__=='__main__': unittest.main()
