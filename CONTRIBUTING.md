# Contributing

Thanks for helping keep this list accurate.

## How the list is maintained

`incidents.yaml` is the **single source of truth**. `README.md` is generated
from it — do not hand-edit `README.md`, CI will reject it.

```bash
# 1. edit incidents.yaml (add or correct an entry)
# 2. regenerate the markdown
pip install pyyaml
python scripts/generate_readme.py
# 3. commit BOTH incidents.yaml and README.md
```

`python scripts/generate_readme.py --check` tells you whether the two are in
sync without writing anything.

## Entry format

S3 and ElasticSearch entries:

```yaml
- date: 2025-09              # YYYY-MM (YYYY alone is acceptable if the month is unknown)
  org: Example Corp          # organisation responsible for the bucket
  category: Finance          # sector — see the list below
  description: Short sentence naming the organisation and what happened
  url: https://example.com/article        # primary source
  records: 1.2M records / 340 GB          # scale; leave '' if the source doesn't say
  notes: What was exposed, how much, and who found it
```

Categories currently in use: Cross-industry, Data Broker, Defense, Education,
Finance, Gaming, Government, Healthcare, Media, Politics, Professional Services,
Research, Retail, Sports, Technology, Telecom, Transportation,
Travel & Hospitality. Reuse an existing one where it fits rather than coining a
near-duplicate.

Use `org` for the organisation whose bucket was exposed. When a vendor caused
the leak, name both — e.g. `Verizon (via NICE Systems)`. When there is no single
owner, use `Multiple (...)` with a short qualifier.

AWS IAM credential entries:

```yaml
- date: '2024-01'
  org_date: '<a href="https://example.com/article">Organisation (Month Year)</a>'
  root_cause: How the credential was exposed
  impact: What the exposure led to
  relevance: Why it matters for static keys / S3
```

Research entries use the same fields as S3 and ElasticSearch entries, under the
`research:` key. Use them for industry-wide studies of bucket exposure rather
than single-organisation incidents — put the researcher in `org`, the headline
scale in `records`, and set `category: Research`.

Entries are sorted newest-first and the IAM table is numbered automatically —
insert anywhere in the list and the generator takes care of ordering.

## Requirements for a new entry

1. **A working primary source.** Reporting from a security outlet or the
   researcher's own writeup. CI checks every link on each PR.
2. **It must be an AWS S3 / IAM credential exposure** — not a generic breach.
   This list is scoped to Amazon S3. Exposures from other object stores — Azure
   Blob Storage, Google Cloud Storage, Cloudflare R2, DigitalOcean Spaces — are
   out of scope no matter how large, and are closed rather than merged. The one
   exception is the research section below, where cross-provider scans are
   accepted because S3 is always a large share of the findings.
3. **No duplicates.** Check `incidents.yaml` for the organisation and URL first.
4. **Only what the source supports.** If a figure isn't in the source, leave it
   out rather than estimating.

## Automated checks

Every pull request runs:

| Check | What it enforces |
| --- | --- |
| `linkcheck` | Every URL still resolves (accepts 2xx, plus 403/429 from bot-protected sites) |
| `generate-check` | `README.md` matches what `incidents.yaml` generates |

`linkcheck` also runs weekly on a schedule and opens an issue if a previously
good link has rotted.

## Weekly discovery pass

A scheduled agent reviews recent reporting once a week and opens a pull request
proposing new incidents. It follows the same rules as any other contributor:
each candidate must be verified against its live source, deduplicated against
`incidents.yaml`, and added through the YAML file — never committed directly to
`master`. Proposals are reviewed by a maintainer like any other PR.
