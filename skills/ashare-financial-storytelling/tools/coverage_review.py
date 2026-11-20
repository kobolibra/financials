"""Immutable unmapped-row anchors and targeted editorial blockers."""
import hashlib
import json


def unmapped_review_items(unmapped, source_sha256):
    """Make every unrecognized amount row independently reviewable, never auto-clear it.

    The ID is bound to the original PDF bytes and physical row, not to which canonical
    key happened to precede it; mapping-rule changes must not silently erase a review.
    """
    items = []
    for u in unmapped:
        anchor = [source_sha256, u['statement'], u['page'], round(float(u['y']), 2),
                  u['label'], u.get('current'), u.get('prior')]
        stable_id = hashlib.sha256(json.dumps(anchor, ensure_ascii=False,
                                              separators=(',', ':')).encode('utf-8')).hexdigest()[:24]
        items.append({'id': stable_id, 'statement': u['statement'], 'physical_page': u['page'],
                      'position_y': round(float(u['y']), 2), 'printed_label': u['label'],
                      'printed_current': u.get('current'), 'printed_comparative': u.get('prior'),
                      'preceding_canonical_key': u.get('after'),
                      'classification': 'NOT_CHECKED', 'materiality': 'NOT_CHECKED',
                      'review_evidence': None})
    return items


def check_dependencies(ledger, keys):
    """A material unresolved source row blocks only the cited dependent metrics."""
    review = ledger.get('unmapped_review', {})
    if not review:
        return
    if review['source_sha256'] != ledger['source']['original_bytes_sha256']:
        raise ValueError('UNMAPPED_REVIEW_SOURCE_DRIFT')
    keys = {key.removesuffix('_prior') for key in keys}
    for item in review['items']:
        evidence = item.get('review_evidence') or {}
        affected = set(evidence.get('affected_keys', []))
        if item['classification'] in ('MATERIAL_OMISSION', 'PENDING') and affected & keys:
            raise ValueError('UNMAPPED_DEPENDENCY_BLOCKED ' + item['id'] + ' ' + ','.join(sorted(affected & keys)))
