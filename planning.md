# TakeMeter — planning.md
## AI201 · Project 3
**Author:** Tahiya Mahin  
**Community:** r/DunderMifflin  
**Last updated:** Before data collection began

---

## 1. Community

I chose **r/DunderMifflin**, a subreddit of ~1.7 million members dedicated to the US version of *The Office*. The community is a strong fit for a discourse quality classification task for several reasons.

First, the discourse is genuinely varied in substance. A significant portion of posts are low-effort memes and image reactions, but mixed in are thoughtful character analyses, contrarian hot takes about seasons or characters, and emotional rewatch reactions — all of which exist as meaningfully distinct registers of engagement. The community has strong shared norms about what constitutes a "real" take versus a lazy one, and debates about character rankings, season quality, and writing decisions are frequent and passionate.

Second, *The Office* has an unusually dedicated rewatch fanbase (driven in large part by its Netflix popularity), which creates a reliable stream of reaction-type posts from both long-time fans revisiting the show and new viewers discovering it. This makes `reaction` a stable and well-populated class rather than an afterthought.

Third, the show's long critical history — debates about the post-Michael Scott seasons, the British vs. American comparison, and individual character arcs — generates genuine analytical discourse that goes beyond surface-level fandom. This makes `analysis` achievable as a label without scraping only academic-style posts.

The distinctions I'm measuring matter to community regulars: people in r/DunderMifflin explicitly distinguish between someone who "has a take" and someone who "actually thought about it," making this taxonomy grounded in community norms rather than imposed from outside.

---

## 2. Label Taxonomy

### `analysis`
**Definition:** A post that constructs a structured argument about the show — covering character arcs, writing quality, thematic observations, or episode comparisons — and uses specific episodes, scenes, or character moments as *evidence* to support a claim rather than simply naming them.

**Example 1:**  
> "Michael's arc from S1 to S7 is a masterclass in slow character rehabilitation. The writers kept his incompetence intact throughout but layered in genuine emotional intelligence over time — the best evidence is how his relationship with Dwight evolves from pure exploitation in Season 1 to something he'd never admit is real friendship by the time of 'Goodbye Michael.' The show earns the emotional payoff because it never stops showing you his flaws."

**Example 2:**  
> "The reason the Jim/Pam relationship stops working after Season 5 isn't the actors — it's that the writers gave them no more obstacles that felt organic to who they are. Every conflict from S6 onward is manufactured external drama (Athlead, the baby, distance) rather than the internal push-pull of two people figuring each other out. Compare it to S2–3 where every scene between them has real tension because both of them are holding something back."

---

### `hot_take`
**Definition:** A bold, assertive opinion about the show, characters, or seasons stated without building a real argument — the post asserts or declares rather than reasons, and any references to the show are decorative rather than argumentative.

**Example 1:**  
> "Toby is actually one of the best characters in the whole series and Michael's treatment of him is genuinely uncomfortable to watch on rewatch. It stopped being funny around Season 4 and just becomes sad."

**Example 2:**  
> "Season 8 is underrated and the hate it gets is mostly just people grieving Michael Scott. Ed Helms absolutely carries it and the Sabre Florida arc is some of the best Andy content in the whole run."

---

### `reaction`
**Definition:** An immediate emotional response to a rewatch, first-time watch, or a specific scene or moment — the post is expressing a feeling in the moment rather than making a case for anything, and contains little to no argumentative structure.

**Example 1:**  
> "Just rewatched Casino Night for the first time in a few years and completely forgot how that final Jim/Pam moment lands. I was genuinely not prepared. Still one of the best scenes in the whole series."

**Example 2:**  
> "First time watching and I just finished Threat Level Midnight. I don't think I've ever laughed that hard at a TV show in my life. Michael's face when he watches himself on screen is everything."

---

## 3. Hard Edge Cases

### The Decorated Argument Problem

The hardest class boundary is between `analysis` and `hot_take`. The problem arises when a post cites specific episodes or characters but doesn't actually construct an argument from them — it's using specificity as a credibility signal rather than as genuine reasoning.

**Example ambiguous post:**
> "Season 8 is genuinely underrated — Ed Helms carries it and the Sabre Florida arc has some of the best Andy moments in the whole series."

This names specific content (Ed Helms, the Sabre Florida arc, Andy) but makes no argumentative move — it doesn't explain *why* those things support the claim, doesn't compare to other seasons, and doesn't engage with any counterargument. The specificity is decorative.

**Decision rule:**  
> If removing the specific references (episode names, character moments) would collapse the argument — i.e., the claim can't stand without them — label it `analysis`. If the post would still make the same basic assertion even without those references ("Season 8 is underrated"), label it `hot_take`. The test is whether the specifics are *load-bearing*.

### The Reactive Analysis Problem

A second edge case is a post that starts as a reaction ("just rewatched X and was struck by Y") but then pivots into genuine analysis of why Y works. 

**Decision rule:**  
> Label by the dominant register. If more than half the post is argument and reasoning, label it `analysis`. If the analytical content is brief and the emotional framing dominates, label it `reaction`. When it's genuinely 50/50, default to `analysis` — it's the rarer class and the analytical content is meaningful even if it's embedded in a reaction.

---

## 4. Data Collection Plan

**Source:** Arctic Shift (arctic-shift.photon-reddit.com/download-tool), the community-maintained successor to Pushshift. Downloaded all r/DunderMifflin submissions from June–July 2020 (post-Netflix peak period, high activity, rich discourse variety).

**Raw volume:** 17,443 posts downloaded. After filtering for non-empty, non-removed selftext and a minimum combined length of 80 characters, 2,141 usable posts remained. A stratified random sample of 300 posts was drawn for annotation.

**Target distribution per label:**

| Label | Target | Minimum |
|---|---|---|
| `reaction` | 80 | 60 |
| `hot_take` | 75 | 60 |
| `analysis` | 65 | 50 |

`reaction` is expected to be the most naturally abundant in r/DunderMifflin given its large rewatch community. `analysis` is the rarest and may require deliberate effort to surface — if underrepresented after 150 annotations, I will filter the remaining pool by `score > 50` to surface more upvoted, substantive posts, which tend to skew toward analysis.

**If a label remains underrepresented after 200 total examples:**  
Re-sample from the 2,141-post filtered pool using a higher score threshold (top 25% by upvotes) to surface more substantive posts for `analysis`, or search explicitly for post titles containing phrases like "why," "the reason," "breakdown," or "analysis" to find candidates.

**Annotation workflow:**  
Posts were pre-labeled using Groq's `llama-3.3-70b-versatile` with the label definitions from this document. Every pre-assigned label was reviewed and corrected by me. The final `label` column reflects human judgment; `suggested_label` reflects the model's suggestion and is retained for transparency.

---

## 5. Evaluation Metrics

Accuracy alone is insufficient for this task for two reasons: (1) with three classes, a model that always predicts `reaction` could achieve ~40% accuracy if that class is overrepresented, and (2) the cost of different errors is not symmetric — misclassifying `analysis` as `hot_take` is a more meaningful failure than misclassifying `reaction` as `hot_take`, because the analysis/hot_take boundary is the one the classifier is actually being asked to learn.

**Metrics I will use:**

**Per-class F1 score** — the harmonic mean of precision and recall for each label. This is the primary metric because it captures both false positives (precision) and false negatives (recall) for each class. A model that learns `analysis` well but can't distinguish `hot_take` from `reaction` will show that clearly in per-class F1.

**Macro-averaged F1** — the unweighted average of per-class F1 scores. This treats each class equally regardless of size, which is appropriate here because all three labels are meaningful targets — a model that ignores `analysis` entirely is not acceptable even if its overall accuracy looks reasonable.

**Overall accuracy** — reported for direct comparison with the zero-shot Groq baseline, but not used as the primary success criterion.

**Confusion matrix** — to identify which specific label pairs the model confuses. Given my label design, I expect the dominant error to be on the analysis/hot_take boundary, and the confusion matrix will confirm or refute this hypothesis.

**Why not precision or recall individually?**  
Reporting only precision or only recall allows a model to game one direction (e.g., predict `analysis` very conservatively to maximize precision, while missing most real analysis posts). F1 prevents this by penalizing both types of errors simultaneously.

---

## 6. Definition of Success

**Minimum bar for a "working" classifier:**
- Fine-tuned model accuracy exceeds the zero-shot Groq baseline on the same test set
- Per-class F1 ≥ 0.55 for all three labels (no class is completely unlearned)
- Macro F1 ≥ 0.60

**Bar for "genuinely useful" deployment in a real community tool:**
- Per-class F1 ≥ 0.70 for all three labels
- Macro F1 ≥ 0.72
- The analysis/hot_take confusion rate (off-diagonal cells in the confusion matrix) is below 20% of all analysis examples — i.e., the model isn't just collapsing the two hardest-to-distinguish classes

**Why these thresholds?**  
A TakeMeter tool deployed in a community context would be labeling posts automatically for features like "show me only analysis-type posts" or "flag hot takes for discussion." At F1 < 0.55, the model is making enough errors to actively mislead community members. At F1 ≥ 0.70, the error rate is low enough that most users would trust the label without needing to verify it manually.

A fine-tuned model that underperforms the Groq zero-shot baseline would be a finding worth investigating (likely indicating annotation inconsistency or label leakage) rather than a result to paper over.

---

## 7. AI Tool Plan

### Label Stress-Testing
Before beginning annotation, I will use Claude to stress-test my label definitions by asking it to generate 10 posts that sit at the boundary between `analysis` and `hot_take`. If Claude produces posts that I cannot classify cleanly using my own definitions, I will tighten the decision rule before annotating 200 examples. The edge case decision rule in Section 3 above was developed through this process.

### Annotation Assistance
I will use Groq's `llama-3.3-70b-versatile` to pre-label all 300 posts in the annotation pool using the label definitions from Section 2 of this document. The pre-labeling script sends each post with the full system prompt and retrieves a single label. I will then review every suggested label individually in Google Sheets, correcting any I disagree with and documenting disagreements in the `notes` column. I will not skim — every label in the final CSV reflects a deliberate human judgment. The `suggested_label` column will be retained in the final CSV for transparency, and this workflow is disclosed in the README AI usage section.

### Failure Analysis
After running the fine-tuned model on the test set, I will paste the full list of misclassified examples into Claude and ask it to identify systematic patterns — e.g., whether errors cluster around short posts, sarcastic tone, posts without explicit episode references, or a specific label pair. I will then verify any identified patterns myself by re-reading the examples before including them in the evaluation report. If Claude's suggested patterns don't hold up on closer inspection, I will discard them and report what I actually find in the data.

---

## 8. Stretch Features

**Inter-annotator reliability** — Skipped. Would require recruiting another annotator and coordinating 30+ shared examples before the submission deadline. The time is better spent on the three features below, which produce more directly useful outputs for the evaluation report and demo.

---

### Stretch 1: Confidence Calibration

**Goal:** Determine whether the fine-tuned model's confidence scores are meaningful — i.e., whether a prediction at 90% confidence is actually correct more often than one at 60%.

**Plan:**

After running inference on the test set in Section 4 of the notebook, I will add a calibration analysis cell that:

1. Extracts the max softmax probability for each prediction as the confidence score
2. Bins predictions into confidence buckets: [0.33–0.50), [0.50–0.65), [0.65–0.80), [0.80–0.95), [0.95–1.00]
3. Computes accuracy within each bucket
4. Plots a calibration curve (confidence on x-axis, actual accuracy on y-axis) with a perfect-calibration diagonal for reference
5. Reports the Expected Calibration Error (ECE) — the weighted average gap between confidence and accuracy across all buckets

**What I'm looking for:**

- A well-calibrated model tracks the diagonal closely — 80% confidence → ~80% accuracy
- An overconfident model clusters high confidence but has lower actual accuracy — common with fine-tuned transformers on small datasets
- An underconfident model stays in the 0.5–0.7 range even on easy examples

**How this informs the evaluation report:**

If the model is poorly calibrated, that limits its usefulness in a deployed tool — a confidence score the user can't trust is worse than no confidence score at all. I will note calibration quality explicitly in the README and in the deployed interface (e.g., displaying a calibration warning if ECE > 0.10).

**Output:** A `calibration_curve.png` saved from Colab and committed to the repo, plus an ECE value reported in `evaluation_results.json` and the README.

---

### Stretch 2: Error Pattern Analysis

**Goal:** Identify *systematic* patterns in the model's failures — not just listing wrong predictions, but finding a structural explanation for why a category of examples fails.

**Plan:**

After collecting all wrong predictions from Section 4, I will run the following analysis:

1. Export the full list of misclassified examples (text, true label, predicted label, confidence) to a structured format
2. Paste them into Claude with the prompt: *"Here are posts a text classifier got wrong. Each includes the true label and the predicted label. Identify 2–3 systematic patterns in the errors — look for shared surface features like post length, use of sarcasm or irony, absence of episode references, a specific confused label pair, or anything else that appears more than once. Be specific."*
3. Verify every suggested pattern myself by re-reading the flagged examples
4. Discard any pattern that doesn't hold up on close reading
5. Write up only verified patterns in the evaluation report

**Hypotheses to test going in** (to check whether Claude's analysis confirms or refutes them):

- The model confuses `analysis` and `hot_take` on posts that name specific episodes without building an argument (the "decorated argument" edge case from Section 3)
- The model over-predicts `reaction` on short posts regardless of content, because short length correlates with emotional register in training data
- The model struggles with sarcastic `hot_take` posts that read as neutral in tone

**Output:** A dedicated "Error Pattern Analysis" subsection in the README evaluation report with 2–3 verified patterns, each supported by 2+ specific examples from the test set.

---

### Stretch 3: Deployed Interface

**Goal:** Build a working Gradio app that accepts a new r/DunderMifflin post, runs it through the fine-tuned DistilBERT classifier, and displays the predicted label and confidence score.

**Plan:**

1. **Save the model from Colab:** After fine-tuning completes, save the model and tokenizer using `trainer.save_model("takemeter-model")` and download the folder from Colab's file panel
2. **Build the Gradio interface locally:** A single-file `app.py` that loads the saved model and tokenizer, accepts a text input, runs inference, and returns the label and confidence with a brief definition of what that label means
3. **Calibration-aware display:** If ECE from Stretch 1 is above 0.10, display a note in the UI that confidence scores may not be well-calibrated on this model
4. **Deploy to Hugging Face Spaces** (free): Push the model and `app.py` to a public HF Space so it's accessible via URL for the demo video without needing to run locally

**Interface design:**

- Text area: "Paste a post from r/DunderMifflin"
- Output: Label name + confidence bar + one-sentence definition of the predicted label
- Optional: show all three class probabilities as a small bar chart

**Files committed to repo:**

- `app.py` — the Gradio interface
- `requirements.txt` — `transformers`, `torch`, `gradio`
- README section documenting how to run locally: `pip install -r requirements.txt && python app.py`

**What counts as done:** The app runs locally, classifies a new post correctly on at least the 3–5 demo examples used in the video, and is documented in the README with run instructions.

---

## 9. Project Roadmap

This section maps every remaining deliverable to a concrete step, including where each stretch feature slots in relative to the required work.

---

### Phase 1 — Annotation (In Progress)
**Goal:** Produce a clean, balanced, human-verified labeled CSV with 210+ examples.

- [x] Download r/DunderMifflin posts via Arctic Shift (17,443 raw → 2,141 filtered → 300 sampled)
- [x] Write pre-labeling script using Groq
- [ ] Run pre-labeling script — produces `dundermifflin_prelabeled.csv`
- [ ] Review every suggested label in Google Sheets; correct and document disagreements in `notes`
- [ ] Check label distribution — target: no label above 70%, all labels ≥ 50 examples
- [ ] Export final labeled file as `dundermifflin_labeled.csv` and commit to repo

**Watch for during annotation:**
- `reaction` dominating — if it exceeds 45% after 150 examples, start skipping clear reaction posts
- `analysis` falling short — filter remaining pool by `score > 50` to surface more substantive posts
- Document at least 3 edge cases with notes for planning.md Section 3 and README

---

### Phase 2 — Notebook: Baseline (Milestone 4)
**Goal:** Establish zero-shot Groq baseline on the locked test set before touching training data.

- [ ] Open Colab notebook, set runtime to T4 GPU
- [ ] Run Section 1: define `LABEL_MAP`, upload `dundermifflin_labeled.csv`
- [ ] Run Section 2: verify 70/15/15 split sizes and label distribution
- [ ] Write `SYSTEM_PROMPT` for Groq baseline in Section 5 (use label definitions from Section 2 of this document)
- [ ] Run Section 5: collect baseline accuracy + per-class metrics
- [ ] Record baseline numbers — do not look at fine-tuned results yet

**SYSTEM_PROMPT checklist:**
- Names r/DunderMifflin and the classification task
- Defines all three labels in plain language
- Gives one example post per label
- Instructs model to output ONLY the label name

---

### Phase 3 — Notebook: Fine-Tuning + Required Evaluation (Milestone 5)
**Goal:** Fine-tune DistilBERT, evaluate on test set, produce confusion matrix.

- [ ] Run Section 3: fine-tune `distilbert-base-uncased` (3 epochs, lr=2e-5, batch=16)
  - Note any hyperparameter changes and reasoning in README
- [ ] Run Section 4: inference on test set → per-class metrics + confusion matrix
- [ ] Review wrong predictions list — identify candidates for error analysis
- [ ] Run Section 6: side-by-side comparison + export `evaluation_results.json`
- [ ] Download `evaluation_results.json` and `confusion_matrix.png` from Colab → commit to repo

---

### Phase 4 — Stretch 1: Confidence Calibration
**Goal:** Determine whether confidence scores are meaningful; compute ECE.
**Slot:** Immediately after Section 4 runs, before closing the Colab session.

- [ ] Add calibration analysis cell to Colab notebook after Section 4:
  - Bucket test predictions by max softmax probability
  - Compute accuracy per bucket
  - Plot calibration curve with perfect-calibration diagonal
  - Compute ECE (weighted mean |confidence − accuracy| across buckets)
- [ ] Save `calibration_curve.png` → download and commit to repo
- [ ] Add ECE to `evaluation_results.json`
- [ ] Note calibration quality in README and factor into deployed interface design

---

### Phase 5 — Stretch 2: Error Pattern Analysis
**Goal:** Identify 2–3 verified systematic patterns in the model's failures.
**Slot:** After Phase 3 evaluation, using the wrong predictions list from Section 4.

- [ ] Export misclassified examples (text, true label, predicted label, confidence)
- [ ] Run Claude analysis prompt on the full error list
- [ ] Re-read every example Claude flags for a suggested pattern — verify or discard
- [ ] Write up 2–3 confirmed patterns with supporting examples
- [ ] Include in README "Error Pattern Analysis" subsection with specific examples

---

### Phase 6 — Stretch 3: Deployed Interface
**Goal:** Working Gradio app running the fine-tuned model, deployed to Hugging Face Spaces.
**Slot:** After Phases 3–5 are complete (model is saved and evaluated).

- [ ] Save fine-tuned model and tokenizer from Colab:
  ```python
  trainer.save_model("takemeter-model")
  tokenizer.save_pretrained("takemeter-model")
  ```
  Download the `takemeter-model/` folder from Colab Files panel
- [ ] Write `app.py` — Gradio interface with:
  - Text input for post
  - Predicted label + confidence bar
  - One-sentence label definition
  - All three class probabilities as bar chart
  - Calibration warning if ECE > 0.10
- [ ] Write `requirements.txt`
- [ ] Test locally: `pip install -r requirements.txt && python app.py`
- [ ] Deploy to Hugging Face Spaces (free tier)
- [ ] Commit `app.py` and `requirements.txt` to repo
- [ ] Add "How to run" section to README

---

### Phase 7 — Documentation + Demo (Milestone 6)
**Goal:** Complete README, write all analysis sections, record demo video.

- [ ] Fill in all README sections (skeleton drafted separately)
- [ ] Write confusion matrix as a markdown table in README
- [ ] Write 3 analyzed wrong predictions (use error pattern analysis output)
- [ ] Write 3–5 sample classifications table with predicted label + confidence
- [ ] Write reflection: what model learned vs. what was intended
- [ ] Write spec reflection
- [ ] Write AI usage section (at least 2 specific instances)
- [ ] Record 3–5 min demo video showing:
  - 3–5 posts classified by fine-tuned model with label + confidence visible (use Gradio app)
  - One correct prediction narrated
  - One incorrect prediction narrated
  - Brief walkthrough of evaluation report
- [ ] Final repo check: planning.md, README, CSV, evaluation_results.json, confusion_matrix.png, calibration_curve.png, app.py, requirements.txt all committed

---

### Deliverables Checklist

| File | Status |
|---|---|
| `planning.md` | ✅ Written |
| `dundermifflin_labeled.csv` | 🔄 In progress |
| `dundermifflin_to_annotate.csv` | ✅ Generated |
| `dundermifflin_prelabeled.csv` | 🔄 Script running |
| `README.md` | 🔄 Skeleton drafted |
| `evaluation_results.json` | ⏳ Post-training |
| `confusion_matrix.png` | ⏳ Post-training |
| `calibration_curve.png` | ⏳ Stretch 1 |
| `app.py` | ⏳ Stretch 3 |
| `requirements.txt` | ⏳ Stretch 3 |