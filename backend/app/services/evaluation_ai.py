import random
from datetime import date


SCORE_BAND = [
    (8.5, "exceptional — consistently performing at the highest level"),
    (7.0, "strong — well above average with clear command of the fundamentals"),
    (5.5, "developing well — showing solid progress and good work ethic"),
    (4.0, "still building — the fundamentals are there but consistency is the key challenge"),
    (0.0, "needs significant focus — this area should be a priority in training"),
]

TREND_INTROS = {
    "improving": ["has shown clear improvement in", "is trending upward in", "has made meaningful progress in", "continues to develop in"],
    "stable":    ["maintains a consistent level in", "remains reliable in", "holds steady in", "is dependable in"],
    "declining": ["has slipped slightly in", "needs renewed attention in", "has shown some regression in", "requires a reset in"],
}

STRENGTH_OPENERS = [
    "Stands out for", "Particularly impressive is", "A clear strength is", "Excels in", "Shows real aptitude for",
]

IMPROVEMENT_OPENERS = [
    "The primary development area is", "The main focus going forward should be",
    "Still working to master", "Needs to sharpen", "Would benefit from more work on",
]

REC_TEMPLATES = {
    "Technical Skills":       ["Focus on repetition drills 3x/week to build muscle memory", "Film review sessions to identify technical gaps", "Deliberate practice with a specific technical focus each session"],
    "Tactical Awareness":     ["Introduce video analysis of game situations", "Positional drills that simulate match scenarios", "Shadow play exercises to improve pattern recognition"],
    "Physical Attributes":    ["Structured conditioning program 2x/week", "Agility ladder and speed work integrated into warm-ups", "Plyometric exercises to build explosive power"],
    "Mental Game":            ["Pre-training mindfulness routines (5 min)", "Pressure simulation drills during practice", "Goal-setting sessions with the athlete to build intrinsic motivation"],
    "Teamwork":               ["Small-sided games that require communication", "Leadership drills where athlete guides younger players", "Debrief sessions after training to discuss team dynamics"],
    "Ball Handling":          ["Ball mastery circuits daily", "Tight space dribbling challenges", "Two-ball juggling drills to improve coordination"],
    "Shooting":               ["Form shooting from 5 spots daily", "Game-speed shooting off screens", "Free throw routine development"],
    "Defense":                ["Defensive stance and footwork drills", "Help-side rotation pattern work", "Rebounding box-out competitions"],
    "Basketball IQ":          ["Film sessions reviewing decision-making moments", "Whiteboard walkthroughs of key plays", "Read-and-react offensive drills"],
    "Stroke Mechanics":       ["Video analysis of stroke mechanics", "Targeted stroke correction with coach shadow", "Wall practice for consistency at 50% pace"],
    "Court Awareness":        ["Point construction drills with pattern play", "Shot selection exercises with delayed decision trigger", "Match simulation focusing on court positioning"],
    "Match Play & Strategy":  ["Competitive match play with structured debrief", "Tactical pattern drilling (serve + 1, return + 1)", "Watch match footage of professional players at similar level"],
    "default":                ["Consistent focused repetition in this area", "One-on-one sessions targeting this skill", "Drill sets designed specifically for this development gap"],
}

PARENT_OPENERS = [
    "is making great strides",
    "is progressing really well",
    "is showing strong development",
    "continues to grow as an athlete",
]

PARENT_ENCOURAGERS = [
    "We're really proud of the effort and commitment being shown.",
    "The dedication in training is clearly paying off.",
    "Coach {coach} is very pleased with the attitude and work ethic.",
    "The improvement since the last evaluation is genuinely exciting to see.",
]


def _score_description(score: float) -> str:
    for threshold, desc in SCORE_BAND:
        if score >= threshold:
            return desc
    return SCORE_BAND[-1][1]


def _get_recommendations(category_name: str, n: int = 2) -> list[str]:
    pool = REC_TEMPLATES.get(category_name, REC_TEMPLATES["default"])
    return random.sample(pool, min(n, len(pool)))


def generate_narrative(
    athlete_name: str,
    coach_name: str,
    sport_type: str,
    categories: list[dict],  # [{category_name, score, previous_score, trend, notes}]
    overall_score: float,
    evaluation_type: str = "monthly",
) -> dict:
    """
    generates a full evaluation narrative from category scores.
    returns: {summary, strengths, areas_for_improvement, recommendations, parent_friendly_summary}
    """
    first_name = athlete_name.split()[0]

    # sort by score descending for strengths, ascending for improvement areas
    sorted_cats = sorted(categories, key=lambda c: c["score"], reverse=True)
    strong_cats = [c for c in sorted_cats if c["score"] >= 7.0]
    weak_cats   = [c for c in sorted_cats if c["score"] < 5.5]
    mid_cats    = [c for c in sorted_cats if 5.5 <= c["score"] < 7.0]
    improving_cats = [c for c in categories if c.get("trend") == "improving"]
    declining_cats = [c for c in categories if c.get("trend") == "declining"]

    # coach summary
    paras = []

    # paragraph 1: overall impression + top strength
    overall_desc = _score_description(overall_score)
    p1_parts = [f"{first_name}'s overall performance this {evaluation_type} evaluation reflects a {overall_desc}."]
    if strong_cats:
        top = strong_cats[0]
        trend_phrase = random.choice(TREND_INTROS[top.get("trend", "stable")])
        p1_parts.append(f"{first_name.capitalize()} {trend_phrase} {top['category_name']}, consistently demonstrating {_score_description(top['score'])} in this area.")
    if improving_cats:
        imp = improving_cats[0]
        p1_parts.append(f"Particular credit goes to the progress made in {imp['category_name']} — the upward trend here is encouraging.")
    paras.append(" ".join(p1_parts))

    # paragraph 2: middle-ground and specific observations
    p2_parts = []
    if mid_cats:
        mid = mid_cats[0]
        trend_phrase = random.choice(TREND_INTROS[mid.get("trend", "stable")])
        p2_parts.append(f"In terms of {mid['category_name']}, {first_name} {trend_phrase} this area, with room to push toward the next level.")
    if len(strong_cats) > 1:
        p2_parts.append(f"The breadth of competence across {strong_cats[1]['category_name']} is also worth highlighting.")
    if not p2_parts:
        p2_parts.append(f"Across the board, {first_name} demonstrates the foundation needed to keep progressing in {sport_type}.")
    paras.append(" ".join(p2_parts))

    # paragraph 3: areas for development + forward look
    p3_parts = []
    if weak_cats:
        w = weak_cats[0]
        trend_phrase = random.choice(TREND_INTROS[w.get("trend", "stable")])
        p3_parts.append(f"The area requiring the most attention right now is {w['category_name']}. {first_name.capitalize()} {trend_phrase} this skill, and we have a specific plan to address it in upcoming sessions.")
    if declining_cats:
        d = declining_cats[0]
        p3_parts.append(f"We'll also be keeping a close eye on {d['category_name']}, where a slight dip was noted — nothing alarming, but worth monitoring.")
    p3_parts.append(f"Overall, {first_name} is on a positive development trajectory and the coaching team is optimistic about the next evaluation period.")
    paras.append(" ".join(p3_parts))

    summary = "\n\n".join(paras)

    # strengths
    strengths = []
    for cat in strong_cats[:3]:
        opener = random.choice(STRENGTH_OPENERS)
        strengths.append(f"{opener} {cat['category_name']} ({cat['score']:.1f}/10)")
    if improving_cats and len(strengths) < 3:
        imp = improving_cats[0]
        strengths.append(f"Consistent upward trend in {imp['category_name']}")
    if not strengths:
        strengths.append(f"Solid effort and positive attitude throughout the evaluation period")

    # areas for improvement
    areas = []
    for cat in weak_cats[:3]:
        opener = random.choice(IMPROVEMENT_OPENERS)
        areas.append(f"{opener} {cat['category_name']} — currently at {cat['score']:.1f}/10")
    if declining_cats and len(areas) < 2:
        d = declining_cats[0]
        areas.append(f"Arresting the slight decline in {d['category_name']}")
    if not areas:
        areas.append("Continue pushing for consistency across all categories")

    # recommendations
    recs = []
    priority_cats = (weak_cats + declining_cats)[:2]
    for cat in priority_cats:
        rec_texts = _get_recommendations(cat["category_name"], 1)
        recs.extend(rec_texts)
    if len(recs) < 2 and mid_cats:
        rec_texts = _get_recommendations(mid_cats[0]["category_name"], 1)
        recs.extend(rec_texts)
    if not recs:
        recs = _get_recommendations("default", 2)

    # parent-friendly summary
    opener = random.choice(PARENT_OPENERS)
    encourager = random.choice(PARENT_ENCOURAGERS).replace("{coach}", coach_name.split()[0])
    focus_area = weak_cats[0]["category_name"] if weak_cats else (mid_cats[0]["category_name"] if mid_cats else "all areas")
    parent_summary = (
        f"{first_name} {opener} this {evaluation_type}! "
        f"{encourager} "
        f"The main focus for the coming weeks will be building {focus_area} — "
        f"Coach {coach_name.split()[-1]} has a clear plan to help {first_name} level up in this area. "
        f"Overall, {first_name} is moving in a really positive direction and we're excited for what's ahead."
    )

    return {
        "summary": summary,
        "strengths": strengths,
        "areas_for_improvement": areas,
        "recommendations": recs,
        "parent_friendly_summary": parent_summary,
    }
