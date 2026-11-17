# Bibliography verification
Status: **VERIFIED** = checked against the publisher page or arXiv in this session. **AS IN REVIEW** = copied from the author's review and not re-checked. **[TO VERIFY]** = check before submission.

| Key | Use in paper | Status | Notes |
|---|---|---|---|
| joshi2026review | the author's review | — | unpublished course manuscript |
| hua2025flaw [R6] | RQ2 framing | VERIFIED | EMNLP 2025, pp. 19889–19899, DOI 10.18653/v1/2025.emnlp-main.1006. Setting (7 LLMs, 6 benchmarks, 12 templates) and finding (heuristic scoring inflates sensitivity; an LLM judge reduces it) checked |
| errica2025sensitivity [R5] | metric definitions | VERIFIED | NAACL 2025, DOI 10.18653/v1/2025.naacl-long.73. Sensitivity = entropy across rephrasings, no labels needed; consistency = class-wise agreement |
| zhuo2024prosa [R17] | related work | VERIFIED | Findings EMNLP 2024. DOI 10.18653/v1/2024.findings-emnlp.108 **added** (missing in the review). Pages 1950–1976 as in the review |
| chatterjee2024posix [R3] | related work | VERIFIED | Findings EMNLP 2024, DOI …findings-emnlp.852 |
| habba2025dove | related work | VERIFIED | Findings ACL 2025, pp. 11744–11763, DOI 10.18653/v1/2025.findings-acl.611; authors checked on the ACL Anthology |
| hariprasad2026clinical | data source | VERIFIED | arXiv:2603.00917 (v1 1 Mar 2026; v3 16 Mar 2026, retitled "…in Small Open-Source Language Models for Clinical Question Answering: An Empirical Evaluation…"). Author: Shravani Hariprasad, independent researcher. CC BY 4.0. **[TO VERIFY]** which arXiv version title the course prefers |
| jin2019pubmedqa | dataset | VERIFIED | EMNLP-IJCNLP 2019, pp. 2567–2577, DOI 10.18653/v1/D19-1259. The context excludes the conclusion section |
| liu2024lost [R10] | not cited in this paper | CORRECTED | The review lists "Kehan Lin" and "A. Paranjape"; the TACL paper's authors are **Kevin Lin** and **Ashwin Paranjape**. Fix this in the review if it is resubmitted |
| chen2026stability [R4], liu2026understanding [R11], si2025ideas [R12], wang2024guideline [R13], zheng2023judge [R16], wang2023selfconsistency [R14] | context citations | AS IN REVIEW | [TO VERIFY] pages and DOI of liu2026understanding (ACL 2026), which was not checked here |
| bommasani2021foundation, brown2020gpt3, ji2023hallucination, kojima2022zeroshot, lin2022truthfulqa, wei2022cot | in .bib, not cited | AS IN REVIEW | kept for completeness; BibTeX prints only cited entries |

**Open issue carried over from the gap analysis.** The review attributes the finding "few-shot examples reduce sensitivity" to ProSA [17] in Table 5 and to POSIX [3] in Table 6. ProSA's abstract and DOVE both report that few-shot examples reduce sensitivity, and POSIX reports a related few-shot effect. Attributing it to [17] (and optionally DOVE) is the safer choice. This paper does not rely on the claim.
