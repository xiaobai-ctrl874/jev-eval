import os, json, sys
from huggingface_hub import HfApi
api = HfApi(token=os.environ.get("HF_TOKEN"))
for rid in sys.argv[1:]:
    info = api.dataset_info(rid, files_metadata=True)
    tot = sum((s.size or 0) for s in info.siblings)
    print("==", rid, "gated=", info.gated, "private=", info.private, "total_bytes=", tot)
    card = info.card_data.to_dict() if info.card_data else {}
    print("  license:", card.get("license"), "| lastModified:", info.last_modified)
    for s in info.siblings:
        print("   ", s.rfilename, s.size)
