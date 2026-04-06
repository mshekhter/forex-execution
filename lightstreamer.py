# =========================
# LIGHTSTREAMER (QUIET MODE, NON-BLOCKING)
# =========================

from datetime import datetime, timezone
from lightstreamer.client import LightstreamerClient, Subscription, SubscriptionListener

latest_tick = {
    "bid": None,
    "ask": None,
    "audit_id": None,
    "ts_utc": None,
}

class TickListener(SubscriptionListener):
    def onItemUpdate(self, update):
        bid = float(update.getValue("Bid"))
        ask = float(update.getValue("Offer"))
        audit_id = update.getValue("Row_Update_Version")
        ts = datetime.now(timezone.utc)
        
        latest_tick["bid"] = float(update.getValue("Bid"))
        latest_tick["ask"] = float(update.getValue("Offer"))
        latest_tick["audit_id"] = update.getValue("Row_Update_Version")
        latest_tick["ts_utc"] = datetime.now(timezone.utc)

        enqueue_tick_for_logging(bid=bid, ask=ask, audit_id=audit_id, ts_utc=ts)

ls_client = LightstreamerClient("https://push.cityindex.com", "STREAMINGALL")
ls_client.connectionDetails.setUser(USERNAME)
ls_client.connectionDetails.setPassword(session_trade)
ls_client.connect()

sub = Subscription(
    mode="MERGE",
    items=[f"ID.{market_id}"],
    fields=["Bid", "Offer", "Row_Update_Version"],
)
sub.setDataAdapter("PRICES")
sub.setRequestedSnapshot("yes")
sub.addListener(TickListener())

ls_client.subscribe(sub)
