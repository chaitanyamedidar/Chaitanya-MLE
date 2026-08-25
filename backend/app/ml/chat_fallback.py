from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.ml.insights import build_insights
from app.models.subscription import Subscription
from app.services.subscriptions import annotate, compute_metrics

_EXAMPLES: list[tuple[str, str]] = [
    ("what is my burn", "get_burn"),
    ("monthly burn rate", "get_burn"),
    ("how much do I spend", "get_burn"),
    ("total monthly cost", "get_burn"),
    ("what renews soon", "upcoming"),
    ("upcoming renewals", "upcoming"),
    ("renewing this week", "upcoming"),
    ("what should I pause", "pause_advice"),
    ("save money", "pause_advice"),
    ("which subscription to cancel", "pause_advice"),
    ("spend by category", "category"),
    ("where does my money go", "category"),
    ("redundant subscriptions", "overlaps"),
    ("overlapping streaming", "overlaps"),
    ("cash flow next months", "cashflow"),
    ("what will I be charged", "cashflow"),
    ("help", "help"),
    ("how do I add a subscription", "help"),
]

_CLF = Pipeline(
    [
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression(max_iter=300)),
    ]
)
_CLF.fit([text for text, _ in _EXAMPLES], [label for _, label in _EXAMPLES])


def intent_of(message: str) -> str:
    return str(_CLF.predict([message])[0])


def reply_from_data(message: str, subs: list[Subscription]) -> str:
    intent = intent_of(message)
    metrics = compute_metrics(subs)
    insights = build_insights(subs)
    rows = [annotate(sub) for sub in subs]

    if intent == "get_burn":
        return (
            f"Monthly burn is ₹{metrics.monthly_burn_rate:.2f} "
            f"across {metrics.active_count} active subscription(s). "
            f"Paused costs are excluded."
        )
    if intent == "upcoming":
        soon = [row.name for row in rows if row.renewing_soon]
        if not soon:
            return "Nothing renews in the next 7 days."
        return f"{metrics.upcoming_renewals_count} upcoming renewal(s): " + ", ".join(soon)
    if intent == "pause_advice":
        recs = insights["pause_recommendations"]
        if not recs:
            return "No pause recommendations yet. Add an active subscription first."
        bits = [f"{r['name']} (save ₹{r['savings_if_paused']:.2f}/mo)" for r in recs]
        return "Highest-impact pauses: " + "; ".join(bits)
    if intent == "category":
        cats = insights["categories"]
        if not cats:
            return "No active spend to categorize."
        bits = [f"{c['category']} ₹{c['monthly_spend']:.2f}" for c in cats]
        return "Spend by category: " + "; ".join(bits)
    if intent == "overlaps":
        overlaps = insights["overlaps"]
        if not overlaps:
            return "No overlapping categories detected."
        return " ".join(item["suggestion"] for item in overlaps)
    if intent == "cashflow":
        flow = insights["cashflow"]
        if not flow:
            return "No charges in the next 90 days."
        bits = [f"{c['month']} ₹{c['amount']:.2f}" for c in flow]
        return "Forward cash-flow: " + "; ".join(bits)
    return (
        "Add a service with the form (or upload a receipt). "
        "Ask me about burn, upcoming renewals, pause advice, categories, or cash-flow."
    )
