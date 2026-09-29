# Stream LiveCodeBench code_generation_lite jsonl files over HTTP and keep only question/metadata
# fields (drops public/private test cases). Nothing large is written to disk.
import os, sys, json, time, requests
FILES = sys.argv[1:] or ["test.jsonl","test2.jsonl","test3.jsonl","test4.jsonl","test5.jsonl","test6.jsonl"]
KEEP = ["question_title","question_content","platform","question_id","contest_id","contest_date","starter_code","difficulty","metadata"]
H = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
# optional LCB_OUT env var: write to a separate file (used for test5/test6 newest-window fetch)
out = open(os.environ.get("LCB_OUT", "/root/bench/jev_eval/raw/livecodebench/metadata_no_tests.jsonl"), "a")
for fn in FILES:
    t=time.time(); n=0
    url = f"https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/main/{fn}"
    with requests.get(url, headers=H, stream=True, timeout=60) as r:
        r.raise_for_status()
        for line in r.iter_lines(chunk_size=1<<20):
            if not line: continue
            d = json.loads(line)
            rec = {k: d.get(k) for k in KEEP}; rec["source_file"] = fn
            rec["n_public_chars"]=len(d.get("public_test_cases") or ""); rec["n_private_chars"]=len(d.get("private_test_cases") or "")
            out.write(json.dumps(rec, ensure_ascii=False)+"\n"); n+=1
    out.flush(); print(fn, n, "rows", round(time.time()-t), "s", flush=True)
