"""Read-only Yousuu archive scanner. Standard library only; see references/yousuu.md."""
import argparse
import csv
import hashlib
import html
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path


def norm(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', value or '')).strip()


def clean(value):
    return norm(html.unescape(re.sub(r'<[^>]*>', ' ', value or '')))


def run(args):
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    clues = cfg['clues']
    ids = [x['id'] for x in clues]
    if not clues or len(ids) != len(set(ids)):
        raise ValueError('clues must be nonempty and have unique ids')
    patterns = {x['id']: [re.compile(p, re.I) for p in x['groups']] for x in clues}
    if any(not ps for ps in patterns.values()):
        raise ValueError('each clue needs at least one regex group')
    rules = cfg.get('candidate_when', [[x] for x in ids])
    if not rules or any(not r or set(r) - set(ids) for r in rules):
        raise ValueError('candidate_when must reference existing clue ids')
    weights = {x['id']: x.get('weight', 1) for x in clues}
    books, by_id, by_name, results = {}, {}, {}, {}
    counts = Counter()
    conflicts = []

    def add_book(source, bid, title, author, tags):
        title, author = norm(title), norm(author)
        match = by_id.get(bid)
        if match and books[match]['author'] != author:
            conflicts.append({'book_id': bid, 'source': source, 'title': title, 'author': author})
            match = None
        match = match or by_name.get((title, author))
        if not match:
            match = source + ':' + bid
            books[match] = {'title': title, 'author': author, 'source_metadata': []}
            by_name[(title, author)] = match
            by_id.setdefault(bid, match)
        books[match]['source_metadata'].append({'source': source, 'book_id': bid, 'tags_original': tags})
        scan(match, title + ' ' + tags, {'source': source, 'kind': 'metadata', 'book_id': bid})
        return match

    def scan(key, text, ref):
        text = clean(text)
        hits = [cid for cid, ps in patterns.items() if all(p.search(text) for p in ps)]
        if not hits:
            return
        record = results.setdefault(key, {'hits': set(), 'evidence': {}})
        record['hits'].update(hits)
        digest = hashlib.sha256(text.encode('utf8')).hexdigest()
        evidence = record['evidence'].get(digest)
        if evidence:
            if ref not in evidence['references']:
                evidence['references'].append(ref)
            counts['matched_duplicate_texts'] += 1
        else:
            snippets = {}
            for cid in hits:
                m = patterns[cid][0].search(text)
                start = max(0, m.start() - 80)
                snippets[cid] = text[start:start + 450]
            record['evidence'][digest] = {'clues': hits, 'snippets': snippets, 'references': [ref], 'normalized_text_sha256': digest}

    conn = None
    main_map, old_map = {}, {}
    try:
        if args.sqlite:
            conn = sqlite3.connect(Path(args.sqlite).resolve().as_uri() + '?mode=ro', uri=True)
            for bid, title, author, tags in conn.execute('SELECT bookId,title,author,tags FROM books'):
                counts['books_2024_raw'] += 1
                main_map[str(bid)] = add_book('2024', str(bid), title, author, tags or '')
        if args.old_dir:
            with (Path(args.old_dir) / 'book.csv').open(encoding='utf-8-sig', newline='') as f:
                for row in csv.DictReader(f):
                    counts['books_2019_raw'] += 1
                    m = re.search(r'/book/(\d+)', row['url'])
                    if not m:
                        raise ValueError('Unrecognized book URL: ' + row['url'])
                    bid = m.group(1)
                    old_map[bid] = add_book('2019', bid, row['name'], row['author'], row['category'])
        if conn:
            for bid, cid, content, date in conn.execute('SELECT bookId,_id,content,createdAt FROM comments'):
                counts['reviews_2024_raw'] += 1
                key = main_map.get(str(bid))
                if key is None:
                    counts['orphan_book_ids_2024'] += 1
                    key = add_book('2024', str(bid), '[书目缺失 ' + str(bid) + ']', '', '')
                    main_map[str(bid)] = key
                scan(key, content, {'source': '2024', 'kind': 'review', 'book_id': str(bid), 'comment_id': cid, 'date': date})
        if args.old_dir:
            with (Path(args.old_dir) / 'rating.csv').open(encoding='utf-8-sig', newline='') as f:
                for row in csv.DictReader(f):
                    counts['reviews_2019_raw'] += 1
                    bid = row['book_id']
                    key = old_map.get(bid)
                    if key is None:
                        counts['orphan_book_ids_2019'] += 1
                        key = add_book('2019', bid, '[书目缺失 ' + bid + ']', '', '')
                        old_map[bid] = key
                    scan(key, row['message'], {'source': '2019', 'kind': 'review', 'book_id': bid, 'comment_id': row['comment_id']})
    finally:
        if conn:
            conn.close()
    candidates = []
    for key, record in results.items():
        if not any(set(rule) <= record['hits'] for rule in rules):
            continue
        candidates.append({'key': key, **books[key], 'score': sum(weights[c] for c in record['hits']),
                           'clues': sorted(record['hits']), 'status': '机器命中，未核验',
                           'evidence': list(record['evidence'].values())})
    candidates.sort(key=lambda r: (-r['score'], r['title']))
    counts['merged_books'] = len(books)
    counts['candidates'] = len(candidates)
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding='utf8')
    (dest / 'coverage.json').write_text(json.dumps({'counts': counts, 'identity_conflicts': conflicts,
        'config': cfg, 'note': 'Raw counts include cross-source copies; evidence dedup uses normalized text within each merged book. Score counts each clue once; not confidence.'}, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(counts, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sqlite')
    parser.add_argument('--old-dir')
    parser.add_argument('--config', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    if not args.sqlite and not args.old_dir:
        parser.error('provide --sqlite and/or --old-dir')
    run(args)
