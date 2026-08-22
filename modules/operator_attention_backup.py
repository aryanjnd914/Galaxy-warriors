import os
import cv2
import threading
import time

_lock = threading.Lock()
_status = {
    "attention_score": 100.0,
    "state": "NOMINAL",
    "face_detected": True,
    "eyes_visible": True,
    "manual_armed": True
}
_stop_event = threading.Event()

_face_cascade = None
_eye_cascade = None


def _load_cascades():
    global _face_cascade, _eye_cascade
    base_dir = os.path.dirname(os.path.abspath(__file__))
    face_path = os.path.join(base_dir, 'cascades', 'haarcascade_frontalface_default.xml')
    eye_path = os.path.join(base_dir, 'cascades', 'haarcascade_eye.xml')
    _face_cascade = cv2.CascadeClassifier(face_path)
    _eye_cascade = cv2.CascadeClassifier(eye_path)
    if _face_cascade.empty() or _eye_cascade.empty():
        raise RuntimeError(f"Could not load Haar cascade files from {face_path} / {eye_path}")


def _classify_state(score):
    if score >= 60:
        return "NOMINAL"
    elif score >= 40:
        return "WARNING"
    return "FAILSAFE"


def _state_color(state):
    if state == "NOMINAL":
        return (255, 200, 0)     # cyan-ish (BGR)
    elif state == "WARNING":
        return (0, 200, 255)     # amber (BGR)
    else:
        return (0, 0, 255)       # red (BGR)


def _tracker_loop(show_window=True):
    try:
        _load_cascades()
    except Exception as e:
        print(f"[operator_attention] Cascade load failed: {e} — staying NOMINAL")
        return

    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        if not cap.isOpened():
            print("[operator_attention] No camera found — staying NOMINAL")
            return
    except Exception as e:
        print(f"[operator_attention] Camera open failed: {e} — staying NOMINAL")
        return

    score = 100.0
    frame_count = 0
    DETECT_EVERY_N = 3          # only run face detection every 3rd frame
    last_face = None            # cached (x, y, w, h) from most recent detection

    try:
        while not _stop_event.is_set():
            try:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                run_full_detect = (frame_count % DETECT_EVERY_N == 0) or (last_face is None)

                face_detected = False
                eyes_visible = False

                if run_full_detect:
                    faces = _face_cascade.detectMultiScale(
                        gray, scaleFactor=1.3, minNeighbors=4, minSize=(60, 60)
                    )
                    if len(faces) > 0:
                        last_face = tuple(faces[0])
                    else:
                        last_face = None
                else:
                    # reuse last known face box — skip the expensive full-frame scan
                    pass

                if last_face is not None:
                    face_detected = True
                    (x, y, w, h) = last_face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 200, 0), 2)

                    roi_gray = gray[y:y + h, x:x + w]
                    roi_color = frame[y:y + h, x:x + w]

                    if run_full_detect:
                        eyes = _eye_cascade.detectMultiScale(
                            roi_gray, scaleFactor=1.1, minNeighbors=6, minSize=(15, 15)
                        )
                        eyes_visible = len(eyes) >= 1
                        for (ex, ey, ew, eh) in eyes[:2]:
                            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    else:
                        eyes_visible = _status["eyes_visible"]  # hold last known value

                    if eyes_visible:
                        score = min(100.0, score + 4.0)
                    else:
                        score = max(0.0, score - 3.0)
                else:
                    score = max(0.0, score - 8.0)

                state = _classify_state(score)

                with _lock:
                    _status["attention_score"] = round(score, 1)
                    _status["state"] = state
                    _status["face_detected"] = face_detected
                    _status["eyes_visible"] = eyes_visible
                    _status["manual_armed"] = state == "NOMINAL"

                if show_window:
                    color = _state_color(state)
                    cv2.putText(frame, f"ATTENTION: {score:.0f}%  [{state}]", (10, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    cv2.imshow("ORBIT-GUARD Operator Attention", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                frame_count += 1
                time.sleep(1 / 20)

            except Exception as frame_err:
                print(f"[operator_attention] Frame error (skipping): {frame_err}")
                time.sleep(0.1)

    except Exception as e:
        print(f"[operator_attention] Tracker loop failed: {e} — staying NOMINAL")
    finally:
        try:
            cap.release()
            if show_window:
                cv2.destroyAllWindows()
        except Exception:
            pass


def start_background_tracker(show_window=False):
    try:
        t = threading.Thread(target=_tracker_loop, args=(show_window,), daemon=True)
        t.start()
        print("[operator_attention] Background tracker thread started")
    except Exception as e:
        print(f"[operator_attention] Could not start tracker thread: {e}")


def get_status():
    with _lock:
        return dict(_status)