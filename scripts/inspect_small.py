import pandas as pd, json, collections
R="/root/bench/jev_eval/raw/"
for name in ["livebench_math","livebench_reasoning"]:
    df=pd.read_parquet(R+name+"/test.parquet")
    print("==",name,len(df),list(df.columns))
    print(df.groupby(["category","task"]).size())
    if "subtask" in df: print(df.groupby(["task","subtask"]).size())
    if "hardness" in df: print("hardness", df.hardness.describe().to_dict(), df.hardness.isna().sum())
    if "level" in df: print(df.groupby(["task","level"]).size())
    print("release dates", df.livebench_release_date.value_counts().sort_index().to_dict())
    print("removal", df.livebench_removal_date.value_counts().to_dict())
    print("multi-turn", (df.turns.apply(len)>1).sum())
    for t,g in df.groupby("task"):
        print("--",t, repr(g.iloc[0].turns[0][:300]))
rows=[json.loads(l) for l in open(R+"math500/test.jsonl")]
print("== math500",len(rows),list(rows[0].keys()))
print(collections.Counter(r["level"] for r in rows)); print(collections.Counter(r["subject"] for r in rows))
