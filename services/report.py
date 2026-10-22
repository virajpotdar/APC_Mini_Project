from datetime import datetime
import os
from services.file_manager import REPORT_DIR


def generate_report(trip, settlements):
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, "trip_report.txt")
    lines = [
        f"TripSplit Report - {trip.name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Budget: {trip.budget:.2f}",
        f"Total Expense: {trip.total_expense():.2f}",
        f"Remaining Budget: {trip.remaining_budget():.2f}",
        "",
        "Members"
    ]
    for m in trip.members.values():
        lines.append(f"{m.name} | Paid: {m.paid:.2f} | Balance: {m.balance:.2f}")
    lines += ["", "Settlements"]
    for s in settlements:
        lines.append(f"{s['from']} -> {s['to']} : {s['amount']:.2f}")
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
    return path
