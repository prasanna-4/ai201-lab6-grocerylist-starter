"""
PR #2 — List Stats Feature (CORRECTED)
========================================
Fixes applied:
  1. by_category counts only unpurchased (remaining) items, matching the
     frontend team's request: "break down what's remaining by category."
  2. Returns 404 if the list_id does not exist, consistent with the rest of the API.

To test:
    python try_prs.py
then use the curl examples in pr2_description.md.
"""

# ---------------------------------------------------------------------------
# Addition to services/list_service.py
# ---------------------------------------------------------------------------

def get_list_stats(list_id: str) -> dict:
    """
    Compute summary statistics for a grocery list.

    Returns a dict with:
        list_id      — the list ID
        total_items  — total number of items on the list
        purchased    — number of items marked as purchased
        remaining    — number of items not yet purchased
        by_category  — remaining item counts grouped by category

    Raises:
        ValueError: If the list does not exist.
    """
    grocery_list = db.session.get(GroceryList, list_id)
    if not grocery_list:
        raise ValueError(f"List {list_id!r} not found")

    items = Item.query.filter_by(list_id=list_id).all()

    total = len(items)
    purchased = sum(1 for item in items if item.is_purchased)
    remaining = total - purchased

    by_category = {}
    for item in items:
        if not item.is_purchased:
            cat = item.category or "uncategorized"
            by_category[cat] = by_category.get(cat, 0) + 1

    return {
        "list_id": list_id,
        "total_items": total,
        "purchased": purchased,
        "remaining": remaining,
        "by_category": by_category,
    }


# ---------------------------------------------------------------------------
# Addition to routes/lists.py
# ---------------------------------------------------------------------------

@lists_bp.route("/<list_id>/stats", methods=["GET"])
def list_stats(list_id):
    """Return summary statistics for a grocery list."""
    try:
        stats = list_service.get_list_stats(list_id)
        return jsonify(stats), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
