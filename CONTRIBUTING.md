# Contributing

Suggest a paper or correction by opening an issue or pull request.

For a new paper, include:

- The full title and primary paper URL.
- The first submission date and, when relevant, the version reviewed.
- A short explanation of its connection to on-policy self-distillation.
- An author-associated code repository, if one is publicly available.
- Whether it uses a self-teacher, external teacher, verifier, environment feedback, or another supervision source.

Prefer recent work while retaining useful foundational references. Clearly mark adjacent work instead of treating every use of “distillation” or “self-improvement” as OPSD.

The source of truth is [data/papers.json](data/papers.json). Add a record in the closest existing category, use its arXiv identifier for deduplication, and keep related-paper references valid. Describe results within their evaluated setting; avoid unqualified superiority claims.

Use `targeted-full-text` when relevant method or analysis passages were read, or `abstract-screened` when inclusion rests on the abstract and metadata. Neither label means the experiments were reproduced.

Regenerate the README and bibliography with Python 3:

```bash
python3 scripts/build_readme.py
```

Check the generated links and table placement before submitting. Link to author-hosted papers and code rather than adding PDF files, model weights, or datasets to this repository.
