import serial
import serial.tools.list_ports
import threading
import time

_ser = None
_lock = threading.Lock()
_current_signal = 'G'
_blink_stop = threading.Event()

def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'Arduino' in p.description or 'CH340' in p.description or 'USB Serial' in p.description:
            return p.device
    if ports:
        return ports[0].device
    return None

def connect():
    global _ser
    try:
        port = find_arduino_port()
        if not port:
            print("[arduino] No Arduino found — LED alerts disabled")
            return False
        _ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)
        print(f"[arduino] Connected on {port}")
        return True
    except Exception as e:
        print(f"[arduino] Connection failed: {e}")
        return False

def send_signal(level):
    global _current_signal
    char_map = {
        'CRITICAL': b'R',
        'HIGH':     b'Y',
        'MEDIUM':   b'G',
        'LOW':      b'G'
    }
    char = char_map.get(level, b'G')
    _current_signal = char.decode()
    with _lock:
        if _ser and _ser.is_open:
            try:
                _ser.write(char)
            except Exception as e:
                print(f"[arduino] Send failed: {e}")

def send_event(event):
    char_map = {
        'critical_detected':   b'C',
        'mission_capture':     b'M',
        'conjunction_warning': b'J',
        'proximity_lock':      b'P',
        'idle_heartbeat':      b'H'
    }
    char = char_map.get(event)
    if not char:
        return
    with _lock:
        if _ser and _ser.is_open:
            try:
                _ser.write(char)
                print(f"[arduino] Event: {event} -> {char.decode()}")
            except Exception as e:
                print(f"[arduino] Send failed: {e}")

def update_from_debris(scored_debris):
    if not scored_debris:
        return
    levels = [d.get('risk_level', 'LOW') for d in scored_debris]
    if 'CRITICAL' in levels:
        send_signal('CRITICAL')
    elif 'HIGH' in levels:
        send_signal('HIGH')
    elif 'MEDIUM' in levels:
        send_signal('MEDIUM')
    else:
        send_signal('LOW')

def start_background_updater(get_debris_func, interval=30):
    def loop():
        cycle = 0  # counts blink cycles

        while not _blink_stop.is_set():
            try:
                debris = get_debris_func()
                levels = [d.get('risk_level', 'LOW') for d in debris] if debris else []

                if 'CRITICAL' in levels:

                    # Every 8 cycles (~10s) — YELLOW conjunction interrupt
                    if cycle % 8 == 0 and cycle != 0:
                        print("[arduino] YELLOW interrupt — conjunction warning")
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'J')  # YELLOW flash x2
                        time.sleep(1.2)
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'R')  # back to RED
                        time.sleep(0.3)

                    # Every 25 cycles (~30s) — GREEN data refresh flash
                    elif cycle % 25 == 0 and cycle != 0:
                        print("[arduino] GREEN flash — live data refresh")
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'M')  # GREEN double flash
                        time.sleep(0.8)
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'R')  # back to RED
                        time.sleep(0.3)

                    else:
                        # Normal RED blink
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'R')
                        time.sleep(0.8)
                        with _lock:
                            if _ser and _ser.is_open:
                                _ser.write(b'G')
                        time.sleep(0.4)

                    cycle += 1
                    if cycle > 1000:
                        cycle = 1  # reset but skip 0

                elif 'HIGH' in levels:
                    # YELLOW slow blink
                    with _lock:
                        if _ser and _ser.is_open:
                            _ser.write(b'Y')
                    time.sleep(1.5)
                    with _lock:
                        if _ser and _ser.is_open:
                            _ser.write(b'G')
                    time.sleep(0.5)

                else:
                    # GREEN heartbeat every 5s
                    with _lock:
                        if _ser and _ser.is_open:
                            _ser.write(b'H')
                    time.sleep(5)
                    cycle = 0

            except Exception as e:
                print(f"[arduino] Background update error: {e}")
                time.sleep(2)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print("[arduino] Background LED updater started")


def send_safety_signal(state):
    char_map = {
        'NOMINAL':  b'H',   # reuse existing green heartbeat pulse
        'WARNING':  b'W',   # NEW: amber fast blink
        'FAILSAFE': b'F',   # NEW: red rapid strobe
    }
    char = char_map.get(state, b'H')
    with _lock:
        if _ser and _ser.is_open:
            try:
                _ser.write(char)
            except Exception as e:
                print(f"[arduino] Safety send failed: {e}")