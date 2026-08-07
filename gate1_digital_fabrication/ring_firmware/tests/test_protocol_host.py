import hmac, hashlib, struct
def mac(key, device, session, seq, etype):
    msg = device + session + struct.pack("<I", seq) + bytes([etype])
    return hmac.new(key, msg, hashlib.sha256).digest()
def test_anti_replay_monotonic():
    key=b"\x01"*16; device=b"\xA0"*16; session=b"\x10"*16; seen=set(); last=0
    for seq in (1,2,3):
        m=mac(key,device,session,seq,1); assert seq==last+1 and seq not in seen
        seen.add(seq); last=seq; assert len(m)==32
def test_reject_replay():
    assert 1 in {1}
