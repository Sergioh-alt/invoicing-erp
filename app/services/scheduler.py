from PySide6 import QtCore
from datetime import datetime
from typing import Optional
import logging

from app.utils.datetime_helpers import now_local, parse_time_hhmm, is_due_date_trigger

logger = logging.getLogger("FacturasGanaTodo.scheduler")


class SchedulerThread(QtCore.QThread):
    alert_needed = QtCore.Signal(dict)

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        logger.info("Scheduler thread iniciado")
        while not self._stop:
            try:
                self._tick()
            except Exception as e:
                logger.exception(f"Error en scheduler tick: {e}")
            self.msleep(60_000)
        logger.info("Scheduler thread detenido")

    def _tick(self):
        now = now_local()
        facturas = self.db.list_facturas(status_filter="Pendiente")

        for f in facturas:
            try:
                due = datetime.fromisoformat(f["fecha_vencimiento"])
            except Exception:
                continue

            payload = dict(f)
            payload["now_iso"] = now.isoformat()

            # Snooze robusto
            su = f.get("snooze_until")
            if su:
                try:
                    snooze_until = datetime.fromisoformat(su)
                    if now < snooze_until:
                        continue
                    self.db.clear_snooze(int(f["id"]))
                    payload["alert_code"] = "SNZ"
                    self.alert_needed.emit(payload)
                    return
                except Exception:
                    try:
                        self.db.clear_snooze(int(f["id"]))
                    except Exception:
                        pass

            # Días antes: D5/D3/D1 (una vez cada uno)
            for code, d in [("D5", 5), ("D3", 3), ("D1", 1)]:
                if is_due_date_trigger(now, due, d):
                    if payload.get("ultimo_aviso_tipo") == code:
                        continue
                    payload["alert_code"] = code
                    self.alert_needed.emit(payload)
                    return

            # Día 0: H1/H2/H3 (una vez cada uno)
            if now.date() == due.date():
                slots = [
                    (1, f.get("hora_alerta_1"), f.get("aviso_h1_ts"), "H1"),
                    (2, f.get("hora_alerta_2"), f.get("aviso_h2_ts"), "H2"),
                    (3, f.get("hora_alerta_3"), f.get("aviso_h3_ts"), "H3"),
                ]
                for slot_id, hhmm, fired_ts, code in slots:
                    t = parse_time_hhmm(hhmm)
                    if not t:
                        continue
                    target_dt = datetime.combine(now.date(), t)
                    if now >= target_dt and not fired_ts:
                        payload["alert_code"] = code
                        payload["day0_slot"] = slot_id
                        self.alert_needed.emit(payload)
                        return
