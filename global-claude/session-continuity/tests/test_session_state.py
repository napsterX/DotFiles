#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).parents[1]/"bin/session_state.py"
class T(unittest.TestCase):
 def setUp(self):
  self.t=Path(tempfile.mkdtemp(prefix="handoff contract ")); self.repo=self.t/"repo with spaces"; self.repo.mkdir(); self.env={**os.environ,"CLAUDE_SESSION_HANDOFFS":str(self.t/"handoffs")}
  subprocess.run(["git","init","-b","develop",str(self.repo)],check=True,capture_output=True); subprocess.run(["git","-C",str(self.repo),"config","user.email","t@example.com"],check=True); subprocess.run(["git","-C",str(self.repo),"config","user.name","T"],check=True); (self.repo/"a.txt").write_text("a\n"); subprocess.run(["git","-C",str(self.repo),"add","a.txt"],check=True); subprocess.run(["git","-C",str(self.repo),"commit","-m","init"],check=True,capture_output=True)
 def cmd(self,*args,check=True): return subprocess.run([sys.executable,str(SCRIPT),*args],text=True,capture_output=True,env=self.env,check=check)
 def draft(self):
  p=Path(self.cmd("draft-path","--cwd",str(self.repo)).stdout.strip()); p.write_text("# Claude Code Operational Handoff\n\n## Handoff Metadata\n- Schema version: 2\n\n## Active Objective\nX\n\n## Definition of Done\nY\n\n## Next Exact Action\nZ\n"); return p
 def test_immediate_publish_then_locate(self):
  p=self.draft(); pub=json.loads(self.cmd("publish","--source",str(p),"--cwd",str(self.repo),"--session-id","s1").stdout); loc=json.loads(self.cmd("locate","--cwd",str(self.repo)).stdout); self.assertEqual(pub["handoff_id"],loc["handoff_id"]); self.assertEqual("CURRENT",loc["freshness"])
 def test_new_publish_replaces_old_current(self):
  a=json.loads(self.cmd("publish","--source",str(self.draft()),"--cwd",str(self.repo)).stdout); (self.repo/"a.txt").write_text("b\n"); subprocess.run(["git","-C",str(self.repo),"commit","-am","next"],check=True,capture_output=True); b=json.loads(self.cmd("publish","--source",str(self.draft()),"--cwd",str(self.repo)).stdout); loc=json.loads(self.cmd("locate","--cwd",str(self.repo)).stdout); self.assertNotEqual(a["handoff_id"],b["handoff_id"]); self.assertEqual(b["handoff_id"],loc["handoff_id"])
 def test_hash_mismatch_blocks(self):
  pub=json.loads(self.cmd("publish","--source",str(self.draft()),"--cwd",str(self.repo)).stdout); Path(pub["current_path"]).write_text("tampered"); r=self.cmd("locate","--cwd",str(self.repo),check=False); self.assertEqual(2,r.returncode)
 def test_realpath_alias_safe(self):
  loc=Path(os.path.realpath(self.repo)); c=json.loads(self.cmd("collect","--cwd",str(loc)).stdout); self.assertTrue(os.path.samefile(c["worktree_root"],self.repo))
 def test_linked_worktree_family_locates_latest(self):
  wt=self.t/"linked"; subprocess.run(["git","-C",str(self.repo),"worktree","add","-b","task",str(wt)],check=True,capture_output=True); pub=json.loads(self.cmd("publish","--source",str(self.draft()),"--cwd",str(wt)).stdout); loc=json.loads(self.cmd("locate","--cwd",str(self.repo)).stdout); self.assertEqual(pub["handoff_id"],loc["handoff_id"]); self.assertEqual(str(Path(os.path.realpath(wt))),loc["active_worktree"])
if __name__=="__main__": unittest.main()
