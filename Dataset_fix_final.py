#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 15:38:29 2025

@author: huangjingkai
"""

"""
Fix FEval-TTC and repackage to a new zip, where the original dataset (ziped in api_responses) is from the paper "FEval-TTC: Fair Evaluation Protocol for Test-Time Compute" by Rumiantsev, Pavel and Pal, Soumyasundar and Zhang, Yingxue and Coates, Mark.

- metadata.cost   -> metadata.dollar_cost
- metadata.tokens -> metadata.token_cost   (missing -> 0)
- request.cost    -> request.dollar_cost
- request.tokens  -> request.token_cost    (missing -> 0)
"""

"""
Fix FEval-TTC old schema -> new schema while PRESERVING .txt filenames.
- only do replacement for .txt/.json which can be read through JSON or NDJSON:
    metadata.cost   -> metadata.dollar_cost
    metadata.tokens -> metadata.token_cost   
    request.cost    -> request.dollar_cost
    request.tokens  -> request.token_cost       

"""


import json, os, re, zipfile, argparse
from typing import Any, Dict

DEFAULT_IN  = "/Users/api_responses"
DEFAULT_OUT = "/Users/api_responses_fixed.zip"

def normalize_record(obj: Any, stats: Dict[str,int]) -> Any:
    if isinstance(obj, dict):
        for section in ("metadata","request"):
            if section in obj and isinstance(obj[section], dict):
                sec = obj[section]
                if "cost" in sec and "dollar_cost" not in sec:
                    sec["dollar_cost"] = sec.pop("cost"); stats["renamed_cost"] += 1
                if "tokens" in sec and "token_cost" not in sec:
                    val = sec.pop("tokens")
                    try: val = int(val)
                    except: 
                        try: val = int(float(val))
                        except: val = 0
                    sec["token_cost"] = val; stats["renamed_tokens"] += 1
                if "token_cost" not in sec:
                    sec["token_cost"] = 0; stats["filled_token_cost"] += 1
        for k,v in list(obj.items()):
            obj[k] = normalize_record(v, stats)
    elif isinstance(obj, list):
        for i,v in enumerate(obj): obj[i] = normalize_record(v, stats)
    return obj

def try_parse_json(text: str):
    text = text.strip()
    if not text: return False, None, None
    try: return True, "json", json.loads(text)
    except: pass
    items=[]
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        try: items.append(json.loads(s))
        except: return False, None, None
    if items: return True,"ndjson",items
    return False, None, None

def dump_as(mode: str, obj) -> str:
    if mode=="json": return json.dumps(obj, ensure_ascii=False)
    if mode=="ndjson": return "\n".join(json.dumps(x, ensure_ascii=False) for x in obj) + "\n"
    raise ValueError("unknown mode")

def run(input_dir: str, output_zip: str):
    input_dir  = os.path.abspath(input_dir)
    output_zip = os.path.abspath(output_zip)
    report_path = os.path.join(os.path.dirname(output_zip), "fix_report.txt")
    if not os.path.isdir(input_dir):
        raise SystemExit(f"[ERROR] Input directory not found: {input_dir}")

    stats: Dict[str,Any] = {
        "processed_json_like_files": 0,
        "raw_copied_files": 0,
        "renamed_cost": 0,
        "renamed_tokens": 0,
        "filled_token_cost": 0,
        "skipped_errors": [],
    }

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(input_dir):
            for fn in files:
                full = os.path.join(root, fn)
                rel  = os.path.relpath(full, input_dir)
                if os.path.abspath(full) in (output_zip, report_path): 
                    continue
                if fn.lower().endswith((".txt",".json")):
                    try:
                        raw = open(full,"r",encoding="utf-8").read()
                        ok, mode, obj = try_parse_json(raw)
                        if ok:
                            fixed = normalize_record(obj, stats)
                            zf.writestr(rel, dump_as(mode, fixed))
                            stats["processed_json_like_files"] += 1
                        else:
                            zf.writestr(rel, raw); stats["raw_copied_files"] += 1
                    except Exception as e:
                        data = open(full,"rb").read()
                        zf.writestr(rel, data)
                        stats["raw_copied_files"] += 1
                        stats["skipped_errors"].append(f"{rel}: {e}")
                else:
                    data = open(full,"rb").read()
                    zf.writestr(rel, data)
                    stats["raw_copied_files"] += 1

    with open(report_path,"w",encoding="utf-8") as rf:
        rf.write("FEval-TTC schema fixer (preserve .txt) report\n")
        rf.write(f"Input  : {input_dir}\nOutput : {output_zip}\n\n")
        rf.write(f"Processed JSON-like files : {stats['processed_json_like_files']}\n")
        rf.write(f"Raw-copied files         : {stats['raw_copied_files']}\n")
        rf.write(f"Renamed cost->dollar_cost: {stats['renamed_cost']}\n")
        rf.write(f"Renamed tokens->token_cost: {stats['renamed_tokens']}\n")
        rf.write(f"Filled missing token_cost: {stats['filled_token_cost']}\n")
        if stats["skipped_errors"]:
            rf.write("\nErrors:\n" + "\n".join(f" - {s}" for s in stats["skipped_errors"]))
    print("[DONE]")
    print(f"Output zip : {output_zip}")
    print(f"Report     : {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--in", dest="inp", default=DEFAULT_IN)
    parser.add_argument("--out", dest="outp", default=DEFAULT_OUT)
    args, _ = parser.parse_known_args()
    run(args.inp, args.outp)
    
    
    
    
    
    
    