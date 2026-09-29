import json, collections, pandas as pd
R="/root/bench/jev_eval/raw/longbench_v2/"
d=json.load(open(R+"data.json"))
print(len(d), list(d[0].keys()))
df=pd.DataFrame([{k:v for k,v in x.items() if k!="context"}|{"ctx_chars":len(x["context"])} for x in d])
print(df.groupby(["domain","sub_domain"]).size())
print(pd.crosstab(df.domain, df.difficulty)); print(pd.crosstab(df.domain, df.length))
print(df.difficulty.value_counts().to_dict(), df.length.value_counts().to_dict())
print(df.groupby("length").ctx_chars.describe())
# save metadata only (no context)
df.to_json(R+"metadata_no_context.jsonl",orient="records",lines=True,force_ascii=False)
for sd in ["Multi-News","Academic","Government","Legal","Financial","Table QA","Knowledge graph reasoning"]:
    for x in df[df.sub_domain==sd].head(3).itertuples():
        print(f"[{x.domain}/{x.sub_domain}/{x.difficulty}/{x.length}] {x.question[:220]!r}")
