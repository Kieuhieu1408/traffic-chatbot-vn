"""Summarize repeated judge outputs without treating abstention as a label."""
import argparse
import json
from pathlib import Path


def summarize(cases, results, repeats):
    expected = {c['case_id']: c['expected'] for c in cases}
    seen = set()
    reports = []
    labels = {key: [] for key in expected}
    for repeat in range(1, repeats + 1):
        counts = dict(tp=0, fp=0, fn=0, tn=0, abstain=0, error=0, missing=0)
        current = {}
        for row in results:
            if row['repeat'] != repeat:
                continue
            key = (repeat, row['case_id'])
            if key in seen or row['case_id'] not in expected:
                raise ValueError('Duplicate or unknown result')
            seen.add(key)
            current[row['case_id']] = row
        for id, target in expected.items():
            row = current.get(id)
            if row is None:
                counts['missing'] += 1; labels[id].append('missing'); continue
            if 'judgment' not in row:
                counts['error'] += 1; labels[id].append('error'); continue
            verdict = row['judgment']['verdict']
            labels[id].append(verdict)
            if verdict is None:
                counts['abstain'] += 1; continue
            if verdict not in ('pass', 'fail'):
                raise ValueError('Invalid verdict')
            key = ('tp' if verdict == 'fail' else 'fn') if target == 'fail' else ('fp' if verdict == 'fail' else 'tn')
            counts[key] += 1
        ratio = lambda a,b: a/b if b else None
        binary = sum(counts[k] for k in ('tp','fp','fn','tn'))
        reports.append(dict(repeat=repeat, **counts,
            precision=ratio(counts['tp'],counts['tp']+counts['fp']),
            recall_among_binary=ratio(counts['tp'],counts['tp']+counts['fn']),
            detected_fail_fraction=ratio(counts['tp'],sum(v=='fail' for v in expected.values())),
            coverage=ratio(binary,len(expected))))
    stable = sum(len(set(v)) == 1 and v[0] in ('pass','fail') for v in labels.values())
    return dict(positive_class='fail', reference='assistant', per_repeat=reports,
                stable_binary_cases=stable, unique_cases=len(cases), labels_by_case=labels)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    args = parser.parse_args(); p = args.experiment
    manifest = json.loads((p/'manifest.json').read_text())
    result = summarize(json.loads((p/'cases.json').read_text()),
        [json.loads(l) for l in (p/'results.jsonl').read_text().splitlines()], manifest['repeats'])
    (p/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
