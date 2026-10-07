#!/usr/bin/env python3
"""Render the reading list and BibTeX from data/papers.json (standard library only)."""

from collections import Counter
from datetime import date
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = [
    'Foundations and overviews',
    'Self-teacher design',
    'Objectives, reliability, and diagnostics',
    'Unsupervised and self-generated supervision',
    'Agents, skills, and harness self-distillation',
    'Attention, representations, and latent context',
    'Context and domain extensions',
    'Related OPD and harness work',
]
DESCRIPTIONS = {
    'Foundations and overviews': 'The original OPSD formulation and a short orientation reference. Foundational work can predate the recent coverage window.',
    'Self-teacher design': 'Where does the teacher advantage come from: context, temperature, adaptation, extrapolation, or future optimization progress?',
    'Objectives, reliability, and diagnostics': 'Which teacher corrections transfer, how should they be weighted, and when does self-distillation damage reasoning or retention? Diagnostic findings are scoped to each paper\'s settings.',
    'Unsupervised and self-generated supervision': 'Consensus, retrieval, and the model\'s own attempts supply training signals. Self-generated does not always mean label-free: SSOPD still uses a correctness verifier.',
    'Agents, skills, and harness self-distillation': 'Training-time skills, reflection, harnesses, and environment feedback provide privileged guidance for student-generated interactions.',
    'Attention, representations, and latent context': 'Extensions that learn privileged context or transfer internal information beyond next-token probabilities.',
    'Context and domain extensions': 'Long context, evolving contexts, diffusion language models, and solver-informed applications. Scope labels distinguish broader context distillation.',
    'Related OPD and harness work': 'Useful comparisons that do not share the complete OPSD setup. This section includes external-teacher OPD, offline approximations, harness search, and harness-guided SFT.',
}


def anchor(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')


def clean(text):
    return text.replace('$\\neq$', '≠').replace('$\\beta$', 'β').replace('|', '\\|').replace('\n', ' ')


def main():
    data = json.loads((ROOT / 'data/papers.json').read_text())
    papers = data['papers']
    by_id = {p['id']: p for p in papers}
    if len(by_id) != len(papers):
        raise ValueError('Duplicate arXiv IDs')
    for p in papers:
        date.fromisoformat(p['first_submitted'])
        assert p['category'] in CATEGORIES, p['category']
        assert p['url'] == f'https://arxiv.org/abs/{p["id"]}'
        assert p['pdf_url'] == f'https://arxiv.org/pdf/{p["id"]}'
        assert all(i in by_id for i in p['related_ids'])
        assert not p['code_url'] or p['code_url'].startswith('https://github.com/')
    count = len(papers)
    code_count = sum(bool(p['code_url']) for p in papers)
    recent = sum(data['recent_window']['start'] <= p['first_submitted'] <= data['recent_window']['end'] for p in papers)
    counts = Counter(p['category'] for p in papers)

    def paper_link(ident):
        p = by_id[ident]
        return f'[{p["label"]}]({p["url"]})'

    lines = [
        '# Awesome OPSD',
        '',
        '**A curated reading list of on-policy self-distillation for language models and agents.**',
        '',
        f'![Papers](https://img.shields.io/badge/papers-{count}-087b74) '
        f'![Code](https://img.shields.io/badge/linked_code_repositories-{code_count}-376ba0) '
        f'![Updated](https://img.shields.io/badge/updated-{data["updated"].replace("-", "--")}-555)',
        '',
        'Papers, code, and concise method annotations covering self-teacher construction, privileged context, '
        'reasoning stability, label-free learning, and multi-turn agents. Related OPD and harness work is labeled separately.',
        '',
        f'**Current coverage:** {count} papers, including {recent} first submitted from '
        f'**{data["recent_window"]["start"]} through {data["recent_window"]["end"]}**, plus '
        'foundational papers as earlier background. Dates refer to the **first arXiv submission**, not the latest revision or conference appearance.',
        '',
        '[Paper data](data/papers.json) · [BibTeX](papers.bib) · [Contributing](CONTRIBUTING.md)',
        '',
        '## What is OPSD?',
        '',
        'In on-policy self-distillation, a student generates training trajectories and a teacher derived from '
        'the same model supervises those trajectories. The teacher often receives additional context, such as '
        'a solution, feedback, or a skill, while the student learns to act without that context. The teacher can '
        'be frozen, synchronized, averaged, or separately adapted; “self” does not require identical live weights '
        'at every update. See the [original formulation](https://arxiv.org/abs/2601.18734).',
        '',
        '```mermaid',
        'flowchart LR',
        '    Q[Task] --> S[Student policy]',
        '    S --> R[Student-generated trajectory]',
        '    R --> T[Self-teacher scores visited prefixes]',
        '    P[Training-only context or teacher advantage] --> T',
        '    R --> L[Distillation objective]',
        '    T --> L',
        '    L --> U[Update student]',
        '    U --> S',
        '```',
        '',
        'This diagram describes the common privileged-context recipe. Some listed methods also use RL rewards, '
        'intervene in trajectory generation, or align hidden states and attention. Their annotations state those differences.',
        '',
        '## Contents',
        '',
        '- [Suggested reading paths](#suggested-reading-paths)',
        *[f'- [{c}](#{anchor(c)}) ({counts[c]})' for c in CATEGORIES],
        '- [Curation notes](#curation-notes)',
        '',
        '## Suggested reading paths',
        '',
        '| Question | Reading path |',
        '| --- | --- |',
        '| How does OPSD work, and what does privilege add? | '+ ' → '.join(paper_link(i) for i in ['2601.18734','2608.09228','2609.20612'])+' |',
        '| Can it learn from demonstrations while retaining prior skills? | '+' → '.join(paper_link(i) for i in ['2601.19897','2607.01763'])+' |',
        '| How can rubrics guide on-policy learning? | '+' → '.join(paper_link(i) for i in ['2606.12507','2606.19327','2605.07396','2608.14684'])+' |',
        '| Why can reasoning degrade? | '+' → '.join(paper_link(i) for i in ['2607.05184','2607.02234','2606.11709','2609.36742'])+' |',
        '| Can it work without gold answers? | '+' → '.join(paper_link(i) for i in ['2608.06296','2608.08764','2608.27448'])+' |',
        '| Can the teacher improve with the student? | '+' → '.join(paper_link(i) for i in ['2608.26019','2609.37132','2609.05295','2609.30652'])+' |',
        '| How does it extend to agents? | '+' → '.join(paper_link(i) for i in ['2604.10674','2606.26790','2606.11559','2608.05987','2609.20784'])+' |',
        '| What can be transferred besides token probabilities? | '+' → '.join(paper_link(i) for i in ['2608.13040','2609.36642','2609.33200'])+' |',
        '',
        'Reading order is a navigation aid, not a benchmark ranking. In the tables, a dash in the code column means '
        'no reachable author-associated repository was identified during curation; it does not establish that no implementation exists.',
    ]
    for category in CATEGORIES:
        lines.extend(['', f'## {category}', '', DESCRIPTIONS[category], '', '| First submitted | Paper | Method / connection | Code |', '| --- | --- | --- | --- |'])
        for p in sorted((p for p in papers if p['category'] == category), key=lambda p: (p['first_submitted'], p['id']), reverse=True):
            title = clean(p['title'])
            code = f'[Code]({p["code_url"]})' if p['code_url'] else '—'
            lines.append(f'| {p["first_submitted"]} | **{clean(p["label"])}**<br>[{title}]({p["url"]}) · [PDF]({p["pdf_url"]}) | {clean(p["summary"])} | {code} |')
    lines.extend([
        '', '## Curation notes', '',
        '- **Primary sources:** titles and dates are checked against arXiv records. Paper links lead to the source and version history.',
        '- **Scope:** direct OPSD methods, diagnostics, and useful adjacent methods are distinguished. Harness optimization, external-teacher OPD, and supervised trajectory imitation are not treated as equivalent to OPSD.',
        '- **Supervision:** “self-generated” and “unsupervised” are different claims. Verifiers, environment feedback, solver outputs, and training-stage teacher construction can supply additional information.',
        '- **Evidence:** annotations summarize the papers rather than independently reproduced results. Model family, reasoning mode, training budget, and evaluation protocol can change conclusions. This is a curated reading list, not an exhaustive systematic review.',
        '- **Reading coverage:** `coverage` in [the data](data/papers.json) distinguishes targeted full-text reading from abstract screening. Neither label implies a complete proof audit or experimental reproduction.',
        f'- **Code links:** {code_count} author-associated public repositories are linked. Links are checked when added; implementations were not all executed or audited.',
        '- **Maintenance:** edit `data/papers.json`, then run `python3 scripts/build_readme.py` to regenerate this README and the bibliography.',
        '', '## Acknowledgment', '',
        'Inspired by the organization of [thinkwee/AwesomeOPD](https://github.com/thinkwee/AwesomeOPD). '
        'This list focuses on self-distillation and uses its own annotations. All paper and implementation credit belongs to the respective authors.',
        '', 'Suggestions and corrections are welcome through issues or pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md).', '',
    ])
    (ROOT / 'README.md').write_text('\n'.join(lines))
    bibliography=[]
    for p in sorted(papers, key=lambda p:p['id']):
        bibliography.append('@misc{arxiv'+p['id'].replace('.','')+',\n  title = {'+p['title']+'},\n  author = {'+' and '.join(p['authors'])+'},\n  year = {'+p['first_submitted'][:4]+'},\n  eprint = {'+p['id']+'},\n  archivePrefix = {arXiv},\n  url = {'+p['url']+'},\n  note = {First submitted '+p['first_submitted']+'}\n}\n')
    (ROOT / 'papers.bib').write_text('\n'.join(bibliography))
    print(f'Rendered {count} papers in {len(CATEGORIES)} categories; {recent} in the recent window; {code_count} code links.')


if __name__ == '__main__':
    main()
