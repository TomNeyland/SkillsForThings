# Effective Infographics: Research-Based Decisions

Use this reference before drafting. It governs what the infographic says and proves; the parent skill governs the visual treatment.

## The core model

An infographic succeeds when a specific audience can perceive the intended relationship, understand why it matters, and retain or act on it. Visual polish is not the goal. Use this sequence:

`audience → task → takeaway → evidence → visual form → accessible equivalent → verification`

If any link is missing, stop before drawing.

## 1. Define the communication job

Write four lines:

1. **Audience:** Who encounters this, and what do they already know?
2. **Situation:** What question, failure, choice, or confusion brought them here?
3. **Takeaway:** What single sentence should they remember tomorrow?
4. **Action:** What should they do next? If no action is intended, what judgment should change?

The audience is not “everyone.” Public-feed readers are distracted, context-poor, and often on a phone. Give them the premise in the image; do not require the post title to make the image intelligible.

For a general programming or AI feed, assume the reader knows common software concepts but not the repository, product, framework names, or the author's private vocabulary. Translate internal labels before visualizing them. If a method needs several definitions, show one concrete input/output example instead of its full architecture.

One infographic should make one primary claim. Two or three subordinate concepts may support it. If the reader must learn five independent things, create a series or use prose.

## 2. Decide whether an infographic is the right form

| Information job | Best starting form |
|---|---|
| One conclusion with a visible relationship | Infographic |
| Exact values or lookup | Table |
| Long explanation, exceptions, or argument | Prose |
| Ordered actions | Numbered sequence |
| State or process change | Flow or before/after |
| Components and ownership | Labeled diagram |
| Quantitative comparison | Bar or dot plot |
| Change over time | Line chart |
| Distribution | Histogram, strip, or box plot |
| Exploration with user-selected questions | Interactive tool |

Do not turn reference material into a poster merely because a poster was requested. Distill the poster to the decision or relationship; put complete detail in adjacent Markdown.

## 3. Select the message before the graphic

Use a message title, not a topic label.

- Topic label: “Prompt caching”
- Message title: “One changing value can invalidate the repeated prefix.”

For a real struggling moment, lead with the lived problem. PAS (Problem → Agitate → Solve) and Jobs-to-be-Done are useful when the reader already feels a cost, delay, risk, or recurring frustration. The mechanism is the agitation: show why the apparently normal situation produces the bad result. The solution follows.

Do not force pain framing onto every subject. Choose the opener that matches the job:

| Situation | Opening strategy |
|---|---|
| Active frustration or costly failure | Lived problem → mechanism → fix |
| Wrong common assumption | Contrarian reframe → proof → better model |
| New capability | Desired transformation → path → evidence |
| Method or discipline | Quality gap → method → observable improvement |
| Comparison or migration | Decision criterion → decisive differences → recommendation |
| Curiosity or experience | Intriguing phenomenon → reveal → implication |
| Reference or taxonomy | Orientation question → organizing map → how to use it |

Product names and features are proof, not openers. People care first about what changes for them.

## 4. Reduce content without losing the argument

Keep content that performs one of four jobs:

- establishes the reader's situation;
- proves the mechanism or relationship;
- makes the consequence concrete;
- enables the next action.

Move implementation detail, caveats that do not change the main interpretation, long examples, citations, and exhaustive lists into the Markdown surrounding the image.

Prefer one annotated example over several shallow examples. Prefer direct labels over a legend. Prefer two simple visuals over one overloaded visual, but only when both are necessary to the same claim.

Numbers must earn their space. Explain what a number means, give its denominator and timeframe when relevant, and do the arithmetic the reader otherwise must perform. Keep denominators and scales consistent across comparisons.

## 5. Match visual encoding to the relationship

Position on a common scale is usually easier to compare than area, angle, color intensity, or pictogram counts. Use familiar encodings unless the audience is known to understand a specialized one.

### Quantitative integrity

- Start bars and filled areas at zero. A truncated line-chart axis may be justified when it reveals variation; label it clearly.
- Use the same scale for graphics meant to be compared.
- Avoid dual axes unless the relationship cannot be communicated another way.
- Do not add decorative 3D, perspective, or pictorial area that changes perceived magnitude.
- Distinguish observed values, estimates, forecasts, and targets.
- Do not imply causation from association.
- Cite the source and material transformations.

### Uncertainty

Show uncertainty when it could change the conclusion or decision. Use ranges, intervals, bands, or scenarios and state in plain language what the uncertainty changes. Do not add an uncertainty decoration the reader cannot interpret. Preserve full estimates in linked data or prose when the image must stay simple.

### Diagrams

A diagram must expose a relationship that prose alone hides: order, branching, amplification, divergence, ownership, feedback, or state change. Label the meaningful parts directly. Decorative icons do not make prose into a diagram.

## 6. Build hierarchy for scanning

Public-feed viewing happens in layers:

1. **One-second scan:** headline communicates the problem or conclusion.
2. **Five-second scan:** diagram reveals the relationship.
3. **Thirty-second read:** consequence and actions complete the argument.
4. **Deep follow-up:** Markdown supplies detail, citations, installation, and edge cases.

Use size, weight, alignment, and whitespace before color. Keep related text close to the mark it explains. Avoid remote legends, rotated labels, and ornamental dividers.

The plain technical-document style works because it spends visual emphasis only on meaning. Bordered card grids create multiple competing entry points and make a poster feel like a dashboard. Dark code panels pull attention toward implementation rather than consequence. Tiny code is neither readable nor explanatory.

## 7. Design for the delivery context

For Reddit and similar mobile feeds:

- Use 4:5 at 1600×2000.
- Keep essential content inside the centered square `y=200..1800`; feed treatments may crop or resize.
- Keep 120 px side margins.
- Test at full resolution and at roughly 400×500.
- Keep body text at least 28 px on the source canvas for this style.
- Make the image understandable without relying on the post title.
- Put expendable metadata or attribution in the outer top/bottom bands.

The 1:1 safe core is a robustness measure, not permission to duplicate the whole image in a square. Preserve the 4:5 composition.

## 8. Accessibility is part of authorship

WCAG provides the delivery floor; accessible communication goes further.

- Do not use color as the only carrier of meaning. Add labels, position, shape, or line style.
- Maintain at least 4.5:1 contrast for normal text and 3:1 for large text and meaningful graphical objects.
- Use direct labels.
- Keep the SVG's `<title>` and `<desc>` accurate.
- In Markdown, provide concise alt text stating the takeaway and essential relationship.
- When exact values or a complex structure matter, provide a visible text explanation or table outside the image. A giant alt attribute is not a substitute for structured content.
- For PDF output, tagged PDF/PDF-UA addresses structure but does not replace WCAG color, contrast, or content requirements.

Social platforms make the infographic an image of text. The surrounding post or Markdown must therefore carry an equivalent textual takeaway.

## 9. Provenance, ethics, and trust

- Identify the source, author/organization, and relevant date when claims depend on external evidence.
- Disclose exclusions, transformations, assumptions, missing data, and uncertainty when they affect interpretation.
- Do not cherry-pick a comparison or visual scale to strengthen the claim.
- Avoid stereotype-coded colors, icons, and category order when depicting people or groups.
- Correct substantive errors in both the image and its accompanying text.

Let the reader trace any claim back to its source, and don't bury the main message under disclaimers — a chart that needs heavy hedging to stand up usually has a weak source, not too few caveats.

## 10. Verification rubric

Score the rendered artifact, not the SVG source:

| Question | Pass condition |
|---|---|
| Can a new reader state the takeaway after five seconds? | Their sentence matches the intended takeaway |
| Can they name the situation, method, and changed behavior without a caption? | All three match the brief in ordinary language |
| Does the visual prove a relationship? | Removing it would make the mechanism harder to understand |
| Is every element necessary? | Each element supports situation, proof, consequence, or action |
| Is the claim honest? | Scale, denominator, timeframe, uncertainty, and causality are accurate |
| Is it readable in-feed? | Headline, diagram labels, and actions work at preview size |
| Are text blocks geometrically separate? | No line crosses its column bound or collides with adjacent labels |
| Is meaning independent of color? | Labels/position/shape preserve it in grayscale |
| Is equivalent text present? | Alt text or adjacent prose states the takeaway and relationship |
| Is provenance recoverable? | Claims trace to named sources or repository material |
| Is the raster faithful? | No clipping, substitution, overlap, or stale render |

If the answer to any row is no, revise before publishing.

## Primary sources behind these rules

- W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- W3C WAI, [Complex Images Tutorial](https://www.w3.org/WAI/tutorials/images/complex/)
- UK Office for National Statistics, [Data Visualisation Service Manual](https://service-manual.ons.gov.uk/data-visualisation)
- UK Government Analysis Function, [Charts: a checklist](https://analysisfunction.civilservice.gov.uk/policy-store/charts-a-checklist/)
- U.S. Web Design System, [Data Visualizations](https://designsystem.digital.gov/components/data-visualizations/)
- Statistics Canada, [Data Visualization: Best Practices](https://www150.statcan.gc.ca/n1/pub/89-26-0005/892600052022001-eng.htm)
- U.S. Census Bureau, [Statistical Quality Standard E2](https://www.census.gov/about/policies/quality/standards/standarde2.html)
- CDC, [Clear Communication Index](https://www.cdc.gov/ccindex/)
- American Statistical Association, [Ethical Guidelines for Statistical Practice](https://www.amstat.org/your-career/ethical-guidelines-for-statistical-practice)
- ISO, [PDF/UA-2 overview](https://www.iso.org/standard/82278.html)
