"""Runs bin/wf-status over fixture workflow dirs (journal and transcript shape copied from a real run) and checks its output."""
import datetime
import json
import os
import subprocess
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "wf-status")
PHRASINGS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "test", "fixtures", "budget-phrasings.txt")
NOW = time.time()
HEADER = "label\tbudget\tcalls\tidle\tinterrupted\tresults\n"


def iso(minutes_ago):
    stamp = datetime.datetime.fromtimestamp(NOW - minutes_ago * 60, datetime.timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def write_jsonl(path, records):
    with open(path, "w") as f:
        f.write("".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in records))


class Run:
    def __init__(self, home=None):
        self.dir = os.path.join(home or tempfile.mkdtemp(), "wf_abc")
        os.makedirs(self.dir)
        self.journal = [{"type": "launched"}]

    def agent(self, agent_id, label, prompt, calls, idle=1, result=True, interrupted=False):
        self.journal.append({"type": "started", "key": "k" + agent_id, "agentId": agent_id, "label": label, "phase": "P"})
        if result:
            self.journal.append({"type": "result", "key": "k" + agent_id, "agentId": agent_id, "result": {}})
        records = [{"type": "user", "agentId": agent_id, "timestamp": iso(idle + 1),
                    "message": {"role": "user", "content": prompt}}]
        records += [{"type": "assistant", "agentId": agent_id, "timestamp": iso(idle), "message": {"role": "assistant",
                     "content": [{"type": "tool_use", "id": f"t{i}", "name": "Bash", "input": {}}]}} for i in range(calls)]
        if interrupted:
            records.append({"type": "user", "agentId": agent_id, "timestamp": iso(idle),
                            "message": {"role": "user", "content": [{"type": "text", "text": "[Request interrupted by user]"}]}})
        write_jsonl(os.path.join(self.dir, f"agent-{agent_id}.jsonl"), records)

    def run(self, *args, journal_age=0, env=None):
        path = os.path.join(self.dir, "journal.jsonl")
        write_jsonl(path, self.journal)
        os.utime(path, (NOW - journal_age * 60,) * 2)
        return subprocess.run(["python3", SCRIPT, *(args or [self.dir])], capture_output=True, text=True, env=env)


class WfStatus(unittest.TestCase):
    def test_one_finished_agent_within_budget(self):
        run = Run()
        run.agent("a1", "build:own", "Do it. Hard budget: 10 tool calls.", 3)
        out = run.run()
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t10\t3\t1\tno\t1\n", 0))

    def test_agent_past_its_budget_exits_1(self):
        run = Run()
        run.agent("a1", "build:own", "Budget: about 4 tool calls.", 5)
        out = run.run()
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t4\t5\t1\tno\t1\n", 1))

    def test_transcript_ending_in_a_user_interrupt_exits_1(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 2, result=False, interrupted=True)
        out = run.run()
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t10\t2\t1\tyes\t0\n", 1))

    def test_twenty_minutes_with_an_agent_running_and_no_new_result_exits_1(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 2, result=False)
        self.assertEqual(run.run(journal_age=5).returncode, 0)
        out = run.run(journal_age=20)
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t10\t2\t1\tno\t0\n", 1))

    def test_retry_started_after_the_last_result_does_not_reset_the_stall_clock(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 2, idle=25)
        run.agent("a2", "build:two", "Hard budget: 10 tool calls.", 1, result=False)
        out = run.run(journal_age=0)
        self.assertEqual((out.stdout, out.returncode),
                         (HEADER + "build:own\t10\t2\t25\tno\t1\nbuild:two\t10\t1\t1\tno\t0\n", 1))

    def test_started_agent_without_a_transcript_yet_is_a_dash_row(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 2)
        run.journal.append({"type": "started", "key": "k2", "agentId": "a2", "label": "build:two", "phase": "P"})
        write_jsonl(os.path.join(run.dir, "agent-a3.jsonl"), [])
        run.journal.append({"type": "started", "key": "k3", "agentId": "a3", "label": "build:three", "phase": "P"})
        out = run.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode), (HEADER + "build:own\t10\t2\t1\tno\t1\n"
                         "build:two\t-\t-\t-\t-\t0\nbuild:three\t-\t-\t-\t-\t0\n", "", 0))

    def test_timestamp_without_fractional_seconds_is_read(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 3)
        path = os.path.join(run.dir, "agent-a1.jsonl")
        with open(path) as f:
            text = f.read().replace(".000Z", "Z")
        with open(path, "w") as f:
            f.write(text)
        out = run.run()
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t10\t3\t1\tno\t1\n", 0))

    def test_missing_argument_prints_usage(self):
        out = subprocess.run(["python3", SCRIPT], capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "usage: wf-status <workflow dir | wf_<id>>\n", 2))

    def test_missing_journal_exits_2_naming_the_path(self):
        run_dir = tempfile.mkdtemp()
        out = subprocess.run(["python3", SCRIPT, run_dir], capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("", f"error: no journal.jsonl at {run_dir}/journal.jsonl\n", 2))

    def test_malformed_line_is_skipped_and_the_rest_read(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 3)
        run.journal.insert(1, "{not json")
        out = run.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         (HEADER + "build:own\t10\t3\t1\tno\t1\n", f"skipped line 2 of {run.dir}/journal.jsonl\n", 0))

    def test_wf_id_resolves_under_the_session_dirs(self):
        home = tempfile.mkdtemp()
        run = Run(home=os.path.join(home, ".claude", "projects", "p", "s", "subagents", "workflows"))
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 3)
        out = run.run("wf_abc", env=dict(os.environ, HOME=home))
        self.assertEqual((out.stdout, out.returncode), (HEADER + "build:own\t10\t3\t1\tno\t1\n", 0))
        out = run.run("wf_none", env=dict(os.environ, HOME=home))
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: 0 runs match wf_none\n", 2))

    def test_budget_phrasings_shared_with_call_budget_hook(self):
        with open(PHRASINGS) as f:
            cases = [line.rstrip("\n").split("\t") for line in f]
        for phrase, n in cases:
            with self.subTest(phrase=phrase):
                run = Run()
                run.agent("a1", "x", phrase, 1)
                self.assertEqual(run.run().stdout, HEADER + f"x\t{n or '-'}\t1\t1\tno\t1\n")

    def test_finished_run_with_an_old_journal_exits_0(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 2)
        self.assertEqual(run.run(journal_age=60).returncode, 0)

    def test_results_counted_per_label_across_retries(self):
        run = Run()
        run.agent("a1", "build:own", "Hard budget: 10 tool calls.", 1)
        run.agent("a2", "build:own", "Hard budget: 10 tool calls.", 1)
        self.assertEqual(run.run().stdout, HEADER + "build:own\t10\t1\t1\tno\t2\n" * 2)

    def test_wf_id_matching_several_runs_exits_2_naming_the_count(self):
        home = tempfile.mkdtemp()
        for session in ("s1", "s2"):
            Run(home=os.path.join(home, ".claude", "projects", "p", session, "subagents", "workflows"))
        out = subprocess.run(["python3", SCRIPT, "wf_abc"], capture_output=True, text=True, env=dict(os.environ, HOME=home))
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: 2 runs match wf_abc\n", 2))
