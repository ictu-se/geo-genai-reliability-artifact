# Journal Style Preflight

This ledger converts the current selected journal/Taylor & Francis submission route into local, reproducible checks. It is a preflight artifact, not a claim that the manuscript is final submission-ready.

- Automated checks passed: 13/14
- Manual gates retained: 3
- Checked route date: 2026-06-24

## Automated and Manual Checks

| Category | Check | Mode | Status | Evidence | Source |
|---|---|---|---|---|---|
| review_file | Blinded compact manuscript exists | automated | pass | 7394 words | local package |
| review_file | LaTeX submission package compiles to PDF | automated | pass | pdf_bytes=2004562 | local LaTeX compile |
| review_file | Double-anonymous review files have no obvious identity/path leaks | automated | pass | none detected | local anonymization scan |
| front_matter | Short abstract is in a journal-ready length band | automated | pass | 220 words | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| front_matter | Keyword field is populated | automated | pass | 10 keywords | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| statements | Acknowledgments section appears before References | automated | pass | Acknowledgments line=198; References line=214 | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| statements | Declaration of Interest Statement section appears before References | automated | pass | Declaration of Interest Statement line=202; References line=214 | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| statements | Data Availability Statement section appears before References | automated | pass | Data Availability Statement line=206; References line=214 | https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/ |
| statements | Software Availability Statement section appears before References | automated | pass | Software Availability Statement line=210; References line=214 | https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/ |
| statements | Full draft includes required end-matter sections | automated | pass | all present | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| references | Structured citations and resolver verification are current | automated | fail | metadata=39; verification=14; unresolved=0 | Crossref/arXiv/DOI resolver local audit |
| references | BibTeX export exists for final native reference-style conversion | automated | pass | submission/references.bib | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| target_route | Dated journal/special-issue source-confidence ledger exists | automated | pass | 2026-06-24 ledger with official and supporting-source confidence labels | https://think.taylorandfrancis.com/special_issues/critical-challenges-in-geoai/ |
| data_code | Data/code release plan and data-source manifest exist | automated | pass | release plan, data sources, and checksum manifest | https://authorservices.taylorandfrancis.com/data-sharing-policies/open-data/ |
| manual_gate | Final native Taylor & Francis/selected journal reference style conversion | manual | manual | Defer until final portal route and reference manager export are fixed. | https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/ |
| manual_gate | Final DOI/public repository and double-anonymous link treatment | manual | manual | Defer until public release DOI/URL exists and review-route policy is reconfirmed. | https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/ |
| manual_gate | Final Q1/quartile and route recheck | manual | manual | Quartile evidence is database/category/year dependent and must be reconfirmed immediately before portal upload. | https://www.tandfonline.com/journals/tgis20 |

## Official Sources to Reopen Before Submission

- manuscript_layout: https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/
- data_availability: https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/
- open_data_policy: https://authorservices.taylorandfrancis.com/data-sharing-policies/open-data/
- ijgis: https://www.tandfonline.com/journals/tgis20
- special_issue: https://think.taylorandfrancis.com/special_issues/critical-challenges-in-geoai/

## Interpretation

- `pass` means the local artifact satisfies the current automated preflight rule.
- `manual` means the item intentionally remains a final submission gate because it depends on the live portal, journal route, public DOI, or external database state.
