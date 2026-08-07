#!/usr/bin/env python3.11
import argparse, json, time, hashlib
def simulate(n=5):
    device=bytes(range(0xA0,0xB0)); session=bytes(range(0x10,0x20)); events=[]
    for seq in range(1,n+1):
        payload=device+session+seq.to_bytes(4,"little")
        events.append({"seq":seq,"ts_ms":int(time.time()*1000),"event_type":"pointer_move",
                       "confidence":0.9,"mac_sha256":hashlib.sha256(payload).hexdigest(),
                       "evidence_class":"SOFTWARE_SIMULATED"})
    return {"label":"development","board":"edge_io_ring_evt0","paired":True,"events":events}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--self-check",action="store_true"); ap.add_argument("--events",type=int,default=5)
    a=ap.parse_args(); out=simulate(a.events)
    if a.self_check:
        assert out["paired"] and len(out["events"])==a.events; print("host_sim_ok"); return
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
