"""
PR #1 — Bulk Purchase Feature (CORRECTED)
==========================================
Fixes applied:
  1. Filter query to is_purchased=False so already-purchased items are not overwritten.
  2. Return count is now correct automatically (len of newly purchased items only).
  3. Route validates user_id before calling the service.

To test:
    python try_prs.py
then use the curl examples in pr1_description.md.
"""

# ---------------------------------------------------------------------------
# Addition to services/list_service.py
# ---------------------------------------------------------------------------

def purchase_all_items(list_id: str, user_id: str) -> int:
    """
    Mark all unpurchased items in a list as purchased.

    Args:
        list_id: ID of the grocery list.
        user_id: ID of the user performing the bulk purchase.

    Returns:
        The number of items newly marked as purchased (excludes already-purchased items).
    """
    items = Item.query.filter_by(list_id=list_id, is_purchased=False).all()
    for item in items:
        item.is_purchased = True
        item.purchased_by = user_id
        item.purchased_at = datetime.now(timezone.utc)
    db.session.commit()
    return len(items)


# ---------------------------------------------------------------------------
# Addition to routes/lists.py
# ---------------------------------------------------------------------------

@lists_bp.route("/<list_id>/purchase-all", methods=["POST"])
def purchase_all(list_id):
    """
    Mark all unpurchased items in a list as purchased at once.

    Expected JSON body:
        user_id (str, required) — the user doing the shopping
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    count = list_service.purchase_all_items(list_id, user_id)
    return jsonify({"purchased": count}), 200
