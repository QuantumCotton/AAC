import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime


def _normalize_name(name: str) -> str:
    name = (name or '').strip()
    name = re.sub(r'\s+', ' ', name)
    return name


def _strip_parenthetical(name: str) -> str:
    return re.sub(r'\s*\([^)]*\)\s*', ' ', name).strip()


def _wikidata_search(query: str, lang: str = 'en', limit: int = 8, timeout_s: int = 20):
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': lang,
        'uselang': lang,
        'type': 'item',
        'search': query,
        'limit': str(limit),
    }
    url = 'https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'liora-animal-learning-audit/1.0'})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        payload = resp.read().decode('utf-8')
    data = json.loads(payload)
    return data.get('search', [])


def _classify_match(original_name: str, results):
    name = _normalize_name(original_name)
    stripped = _strip_parenthetical(name)

    positive_terms = (
        'species', 'subspecies', 'genus', 'animal', 'mammal', 'bird', 'fish', 'reptile', 'amphibian',
        'insect', 'arthropod', 'crustacean', 'mollusk', 'mollusc', 'cnidarian', 'worm', 'cephalopod',
        'shark', 'ray', 'dolphin', 'whale', 'seal', 'penguin', 'lizard', 'snake', 'frog', 'toad',
        'spider', 'jellyfish', 'octopus', 'squid', 'starfish', 'echinoderm'
    )
    negative_terms = (
        'fictional', 'character', 'video game', 'myth', 'mythical', 'legendary', 'cryptid', 'monster',
        'pokémon', 'pokemon', 'comic', 'tv series', 'film', 'novel'
    )

    def score_item(item):
        label = (item.get('label') or '').strip()
        desc = (item.get('description') or '').strip().lower()
        label_n = _normalize_name(label).lower()
        exact = label_n == name.lower() or label_n == stripped.lower()
        has_positive = any(t in desc for t in positive_terms)
        has_negative = any(t in desc for t in negative_terms)
        return {
            'id': item.get('id'),
            'label': label,
            'description': item.get('description') or '',
            'url': item.get('concepturi') or '',
            'exact': exact,
            'has_positive': has_positive,
            'has_negative': has_negative,
        }

    scored = [score_item(it) for it in results]

    verified_exact = [s for s in scored if s['exact'] and s['has_positive'] and not s['has_negative']]
    if verified_exact:
        return 'verified', verified_exact[0]

    verified_loose = [s for s in scored if s['has_positive'] and not s['has_negative']]
    if verified_loose:
        return 'maybe', verified_loose[0]

    exact_any = [s for s in scored if s['exact']]
    if exact_any:
        return 'unsure', exact_any[0]

    if scored:
        return 'no_match', scored[0]

    return 'no_match', None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--animals', default=os.path.join('src', 'data', 'animals.json'))
    ap.add_argument('--out', default=os.path.join('scripts', 'wikidata_animal_audit_report.json'))
    ap.add_argument('--lang', default='en')
    ap.add_argument('--limit', type=int, default=8)
    ap.add_argument('--sleep-ms', type=int, default=150)
    ap.add_argument('--max', type=int, default=0)
    args = ap.parse_args()

    with open(args.animals, 'r', encoding='utf-8') as f:
        animals = json.load(f)

    names = []
    for a in animals:
        n = a.get('name') or a.get('id') or ''
        n = _normalize_name(n)
        if n:
            names.append(n)

    if args.max and args.max > 0:
        names = names[: args.max]

    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'source_file': args.animals,
        'total': len(names),
        'counts': {'verified': 0, 'maybe': 0, 'unsure': 0, 'no_match': 0},
        'items': [],
    }

    for idx, name in enumerate(names, start=1):
        try:
            results = _wikidata_search(name, lang=args.lang, limit=args.limit)
            status, best = _classify_match(name, results)
            report['counts'][status] += 1
            report['items'].append(
                {
                    'name': name,
                    'status': status,
                    'best': best,
                    'results_count': len(results),
                }
            )
        except Exception as e:
            report['counts']['no_match'] += 1
            report['items'].append(
                {
                    'name': name,
                    'status': 'no_match',
                    'best': None,
                    'results_count': 0,
                    'error': str(e),
                }
            )

        if idx % 25 == 0 or idx == len(names):
            print(f"[{idx}/{len(names)}] verified={report['counts']['verified']} maybe={report['counts']['maybe']} unsure={report['counts']['unsure']} no_match={report['counts']['no_match']}")

        time.sleep(max(0, args.sleep_ms) / 1000.0)

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    suspicious = [it for it in report['items'] if it['status'] in ('no_match', 'unsure')]
    print('\n=== SUMMARY ===')
    print(json.dumps(report['counts'], indent=2))
    print(f"Report written to: {args.out}")

    if suspicious:
        print('\n=== SUSPICIOUS (first 30) ===')
        for it in suspicious[:30]:
            best = it.get('best') or {}
            label = best.get('label') or ''
            desc = best.get('description') or ''
            qid = best.get('id') or ''
            print(f"- {it['name']} -> {it['status']} | best={label} {qid} | {desc}")


if __name__ == '__main__':
    main()
