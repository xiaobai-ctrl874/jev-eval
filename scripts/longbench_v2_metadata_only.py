# Fetch LongBench v2 question/metadata columns only (no `context`) via HF auto-converted parquet + range reads.
import os, time, pyarrow.parquet as pq
from huggingface_hub import HfFileSystem
fs = HfFileSystem(token=os.environ.get("HF_TOKEN"))
p = "datasets/zai-org/LongBench-v2@refs%2Fconvert%2Fparquet/default/train/0000.parquet"
t=time.time()
with fs.open(p, "rb", block_size=1<<20) as f:
    pf = pq.ParquetFile(f)
    print(pf.schema_arrow.names, pf.metadata.num_rows, pf.metadata.num_row_groups)
    cols=[c for c in pf.schema_arrow.names if c!="context"]
    tb = pf.read(columns=cols)
    print("rows", tb.num_rows, "secs", round(time.time()-t,1), "bytes fetched approx", getattr(f, "loc", None))
