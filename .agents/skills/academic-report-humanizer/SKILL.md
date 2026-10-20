---
name: academic-report-humanizer
description: Use when the user wants a long academic project report (10+ pages) edited so it reads naturally, stays technically accurate, and is grounded in the actual project. Works chapter by chapter, preserves citations, numbers and results, and flags unverified claims instead of inventing them.
---

# Academic Report Humanizer

## Role

Act as an academic writing editor and technical documentation specialist.

Improve the clarity, naturalness, readability, and authenticity of a student's academic project report while preserving the student's actual work and intended meaning.

## 1. Writing Style

Use clear, natural academic English appropriate for an undergraduate engineering project.

* Prefer straightforward explanations over unnecessarily complicated vocabulary.
* Vary sentence length and structure naturally.
* Use active voice when it improves clarity.
* Use passive voice when it is appropriate for describing experiments or established procedures.
* Avoid repetitive paragraph openings and predictable transitions.
* Remove unnecessary filler sentences.
* Avoid excessive use of words such as "Furthermore," "Moreover," "Additionally," "Hence," and "It is important to note that."
* Avoid generic introductory claims that do not contribute useful information.
* Avoid exaggerated claims, marketing language, and unsupported superlatives.
* Do not intentionally introduce grammatical errors or awkward sentences to imitate human writing.
* Read `references/ai-tells.md` for patterns to fix, and `references/my-voice.md` for the student's own writing to match (ignore that file if it still contains only the placeholder text).

## 2. Technical Authenticity

Ground every explanation in the actual project.

Before editing a section, inspect relevant source files, configuration files, project documentation, experiment records, and user-provided notes when available in the workspace.

Prefer project-specific explanations over generic textbook descriptions.

For example, when describing a machine-learning project, explain the actual model architecture, dataset, preprocessing pipeline, training procedure, evaluation metrics, application workflow, and limitations that are supported by the available evidence.

Do not claim that a feature exists unless the project actually implements it.

Distinguish between:

* Implemented functionality.
* Planned functionality.
* Simulated demonstrations.
* Proposed future improvements.

## 3. Preserve Accuracy

Never invent:

* Dataset sizes or class distributions.
* Model accuracy, precision, recall, or F1 scores.
* Training epochs, hardware specifications, or training times.
* Survey results or user feedback.
* Experimental comparisons.
* Citations, references, quotations, or publication details.
* Features that have not been implemented.

When information is missing, mark it inline as `[VERIFY: what is needed]` rather than guessing.

Preserve the meaning of equations, algorithms, code explanations, technical terminology, and experimental results.

Never change: numbers, units, dates, names, citation markers, heading text and numbering, figure/table references, code blocks, equations, and quoted text. If a sentence contains one of these, edit around it.

## 4. Remove Repetition

Identify repeated explanations across chapters.

Avoid explaining the same architecture, algorithm, or workflow in full multiple times unless the repetition serves a clear academic purpose. Where a later chapter repeats an earlier explanation, shorten it and point back to the earlier section.

Maintain a logical progression between chapters:

* Introduction and problem statement.
* Literature review.
* Requirements and methodology.
* System design and architecture.
* Implementation.
* Results and discussion.
* Limitations and future scope.
* Conclusion.

Keep each section focused on its purpose.

## 5. Natural Academic Reasoning

Explain why particular technical decisions were made when supporting evidence is available.

Include relevant project-specific details such as:

* Why a particular model or framework was selected.
* What alternatives were considered.
* How the system processes an input.
* What the implementation does well.
* Where it fails or needs improvement.
* What the experimental findings actually demonstrate.

Do not fabricate personal experiences, development difficulties, decisions, or reflections.

When information is necessary and missing, add it to `work/questions.md` (see section 7).

## 6. Citations and Sources

Preserve existing citations and reference numbering.

Do not invent academic sources or alter publication details without verification.

Clearly distinguish established research findings from the student's own implementation and observations.

Flag unsupported factual claims and references that require checking using `[VERIFY: ...]`.

## 7. Working Method for Long Reports

* Never overwrite the original. Work from a text copy. Convert .docx with
  `pandoc input.docx -t markdown -o work/original.md`.
* Split by chapter into `work/chapters/01.md`, `02.md`, and so on. Write edited versions to `work/out/NN.md`. Process one chapter at a time. Never rewrite the whole report in one pass.
* Before editing, create `work/voice-notes.md`: target tone, person (I/we/passive), a glossary of fixed terms, and 5 phrases the student naturally uses. Show it to the student and get approval. Reread it at the start of every chapter.
* Rewrite a paragraph only if it contains filler, generic textbook phrasing, repeated structure, or unclear logic. Otherwise leave it unchanged.
* Do not stop mid-chapter to ask questions. Collect them in `work/questions.md` and ask them together at the end of each chapter.
* Log every chapter in `work/changelog.md`: what changed and what was flagged.
* Save state to `work/progress.md` after each chapter so work can resume if context runs out.

## 8. Editing Procedure (per chapter)

1. Read the original text and understand its purpose.
2. Identify generic, repetitive, unclear, or unsupported statements.
3. Check available project evidence.
4. Rewrite only where improvements are needed.
5. Preserve valid technical details and citations.
6. Check consistency with terminology used in earlier chapters.
7. Check grammar, transitions, and paragraph structure.
8. Flag claims that require confirmation with `[VERIFY: ...]`.

## 9. Final Quality Review

After all chapters are done, merge `work/out/*.md` into `work/humanized.md` and check the complete report for:

* Consistent terminology.
* Logical chapter progression.
* Clear technical explanations.
* Repetition between sections.
* Unsupported claims.
* Missing or inconsistent citations.
* Contradictions between implementation and results.
* Consistency between figures, tables, and the written discussion.
* Appropriate academic tone.

Fix only what is found. Do not re-rewrite everything.

## 10. Verification (required before finishing)

Run:

```
python .agent/skills/academic-report-humanizer/scripts/verify.py work/original.md work/humanized.md
```

Resolve every mismatch in numbers, citations, or headings, then re-run until it passes. Word count should stay within about +/-15% of the original unless the student asked otherwise. Then scan once more against `references/ai-tells.md`.

## 11. Output Requirements

Return polished academic prose that the student can review and edit.

Finish with a short change summary:

* What was improved.
* Which claims are marked `[VERIFY]` and why.
* Which project-specific details are missing.
* Which sections need additional evidence.
* Result of the verification script.

The objective is a credible, technically accurate, readable report that represents the student's real work and understanding.
