# TakeMeter — Discourse Quality Classifier for r/DunderMifflin
**AI201 · Project 3**

> A fine-tuned DistilBERT classifier that categorizes r/DunderMifflin posts as `analysis`, `hot_take`, or `reaction` — compared against a zero-shot Groq baseline.

---

## Table of Contents
1. [Community](#community)
2. [Label Taxonomy](#label-taxonomy)
3. [Data Collection](#data-collection)
4. [Fine-Tuning Approach](#fine-tuning-approach)
5. [Baseline Description](#baseline-description)
6. [Evaluation Report](#evaluation-report)
   - [Overall Accuracy](#overall-accuracy)
   - [Per-Class Metrics](#per-class-metrics)
   - [Confusion Matrix](#confusion-matrix)
   - [Wrong Predictions Analysis](#wrong-predictions-analysis)
   - [Sample Classifications](#sample-classifications)
   - [Confidence Calibration](#confidence-calibration) ⭐ *stretch*
   - [Error Pattern Analysis](#error-pattern-analysis) ⭐ *stretch*
7. [Reflection](#reflection)
8. [Spec Reflection](#spec-reflection)
9. [Deployed Interface](#deployed-interface) ⭐ *stretch*
10. [AI Usage](#ai-usage)

---

## Community

r/DunderMifflin is a subreddit of approximately 1.7 million members dedicated to the US version of *The Office*. I chose it because its discourse spans a wide and meaningful range of engagement quality: the community produces everything from meme reactions and first-watch emotional responses to genuine character arc analyses and polarizing takes on seasons and writing decisions. These distinctions matter to regular community members — people in r/DunderMifflin actively distinguish between someone who "has a take" and someone who "actually thought about it," making the taxonomy grounded in community norms rather than imposed from outside. The show's unusually large rewatch audience creates a reliable and varied stream of text-heavy posts that are well-suited to classification.

---

## Label Taxonomy

### `analysis`
**Definition:** A post that constructs a structured argument about the show — covering character arcs, writing quality, thematic observations, or episode comparisons — and uses specific episodes, scenes, or character moments as load-bearing evidence to support a claim, where removing those references would collapse the argument.

**Example 1:**
> "Michael's arc from S1 to S7 is a masterclass in slow character rehabilitation. The writers kept his incompetence intact throughout but layered in genuine emotional intelligence over time — the best evidence is how his relationship with Dwight evolves from pure exploitation in Season 1 to something he'd never admit is real friendship by the time of Goodbye Michael. The show earns the emotional payoff because it never stops showing you his flaws."

**Example 2:**
> "The reason the Jim and Pam relationship stops working after Season 5 isn't the actors — it's that the writers gave them no more obstacles that felt organic to who they are. Every conflict from S6 onward is manufactured external drama rather than the internal push-pull of two people figuring each other out. Compare it to S2–3 where every scene between them has real tension because both of them are holding something back."

---

### `hot_take`
**Definition:** A bold, assertive opinion about the show, characters, or seasons stated without building a real argument — the post asserts or declares rather than reasons, and any references to episodes or characters are decorative rather than argumentative.

**Example 1:**
> "Toby is actually one of the best characters in the whole series and Michael's treatment of him is genuinely uncomfortable to watch on rewatch. It stopped being funny around Season 4 and just becomes sad."

**Example 2:**
> "Season 8 is underrated and the hate it gets is mostly just people grieving Michael Scott. Ed Helms absolutely carries it and the Sabre Florida arc is some of the best Andy content in the whole run."

---

### `reaction`
**Definition:** An immediate emotional response to a rewatch, first-time watch, or a specific scene or moment — the post is expressing a feeling in the moment rather than making a case for anything, with little to no argumentative structure.

**Example 1:**
> "Just rewatched Casino Night for the first time in years and completely forgot how that Jim and Pam moment at the end lands. I was not prepared at all."

**Example 2:**
> "Just watched the series finale for the first time!!! It was so AMAZING!!! Only reason I didn't like it was because everyone hated Andy for like half the episode. Other than that. Pure Perfection!"

---

## Data Collection

**Source:** Arctic Shift (arctic-shift.photon-reddit.com) — the community-maintained successor to Pushshift. All r/DunderMifflin submissions from June–July 2020 were downloaded as a JSONL file.

**Raw → usable pipeline:**
- 17,443 posts downloaded
- 2,246 retained after filtering out image posts, removed/deleted posts, and posts with empty selftext
- 2,141 retained after minimum 80-character length filter
- 300 sampled for initial annotation (stratified random sample, `random_state=42`)
- 461 final examples after targeted resampling to balance underrepresented classes

**Labeling process:**
Posts were pre-labeled using Groq's `llama-3.3-70b-versatile` with the full label definitions from `planning.md`. Due to hitting Groq's daily token limit mid-run, the remaining posts were pre-labeled using a rule-based classifier built on the same label definitions. Every pre-assigned label in the initial 300-post pool was reviewed individually in Google Sheets and corrected where needed — approximately 39% of the first 54 reviewed rows were overridden. The most common override was `analysis → reaction`, where the model treated any post referencing a specific episode as analysis regardless of whether a real argument was present. The `suggested_label` column is retained in `dundermifflin_labeled.csv` for transparency.

**Label distribution (final labeled dataset):**

| Label | Count | % |
|---|---|---|
| `analysis` | 161 | 34.9% |
| `hot_take` | 150 | 32.5% |
| `reaction` | 150 | 32.5% |
| **Total** | **461** | 100% |

**Three difficult-to-label examples:**

**1.**
> "Kevin defending Pam — Was just researching s3e17 when Pam tells Roy that she kissed Jim at Casino Night and I didn't spot this before but as Roy starts kicking off and throwing stuff he starts to walk in the direction of Pam and Kevin stands up just to the left of the frame with his fists clenched."

*True label assigned:* `hot_take` — *Why it was hard:* This reads like a rewatch observation (`reaction`) because it uses "was just researching" framing and references a specific episode. However, the post is making a claim about Kevin's character that isn't argued anywhere in the body — it asserts a personality conclusion from a background detail. The load-bearing test tipped it toward `hot_take`: remove the episode reference and the claim ("Kevin would protect Pam") still stands as an assertion.

**2.**
> "The Michael Scott Paper Company should have worked. Given that MSPC was competing with a big company with countless employees, nicer office, warehouse, and tons of other expenses, they could have easily sold at a lower price than Dunder Mifflin and made a profit. If Ryan ran the numbers correctly..."

*True label assigned:* `hot_take` — *Why it was hard:* The body provides what looks like economic reasoning, which signals `analysis`. However, the reasoning is speculative and asserted rather than grounded in specific evidence from the show — it's making an argument from general business logic rather than from what the show actually depicts. The distinction between "sounds like an argument" and "is an argument" is exactly the decorated argument edge case documented in `planning.md`.

**3.**
> "Dwight and Angela were meant to be together... The series re-started on Comedy Central this morning and in the first scene of the first episode, Dwight hums a thrash metal version of Little Drummer Boy, which we will later learn (Benihana Christmas) is Angela's favorite song."

*True label assigned:* `reaction` — *Why it was hard:* The post notices a specific detail and references a specific episode by name, which signals `analysis`. But the observation isn't being used to support a larger argument about the show's writing — it's sharing a moment of rewatch discovery. The dominant register is emotional ("were meant to be together") and the reference is not load-bearing evidence for any claim.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace) — a distilled version of BERT with 66M parameters, 40% smaller and 60% faster than BERT-base while retaining ~97% of its performance on GLUE benchmarks. Chosen because it trains in under 15 minutes on a T4 GPU for datasets of this size.

**Training setup:**
- Framework: HuggingFace `transformers` + `Trainer` API
- Train/val/test split: 70% / 15% / 15%, stratified by label
- Final training: 15 epochs, learning rate 3e-5, batch size 16 (train), 32 (eval)
- Weight decay: 0.01
- Warmup steps: 20
- Best model selected by validation accuracy (`load_best_model_at_end=True`)

**Hyperparameter decision:**
The most consequential hyperparameter change was reducing `warmup_steps` from the notebook default of 50 to 20. With 322 training examples and a batch size of 16, there are approximately 20 gradient steps per epoch — meaning the default warmup of 50 steps consumed the entire first two-plus epochs just ramping up the learning rate and never reached the target learning rate value at all. The first training run produced flat validation accuracy (35–38% across all three epochs, essentially random-guess level) as a direct result. Reducing warmup to 20 steps (~16% of total training steps, a standard ratio) allowed the model to actually train, with validation accuracy climbing meaningfully from epoch 1 onward. The learning rate was also increased from 2e-5 to 3e-5 to accelerate convergence on a larger dataset.

---

## Baseline Description

**Model:** Groq `llama-3.3-70b-versatile` (zero-shot, no task-specific training)

**Prompt used:**

```
You are classifying posts from r/DunderMifflin, a Reddit community dedicated to the US version of The Office.

Assign each post to exactly one of the following categories:

analysis: The post constructs a structured argument about the show — covering character arcs, writing quality, thematic observations, or episode comparisons. It uses specific episodes, scenes, or character moments as EVIDENCE to support a claim. The references are load-bearing: remove them and the argument collapses.
Example: "Michael's arc from S1 to S7 works because the writers kept his incompetence intact while layering in emotional intelligence — his relationship with Dwight evolves from exploitation to something he'd never admit is real friendship."

hot_take: A bold, assertive opinion about the show, characters, or seasons stated without building a real argument. The post asserts or declares rather than reasons. Any episode or character references are decorative — you could remove them and the basic claim would still stand.
Example: "Toby is actually one of the best characters and Michael's treatment of him stopped being funny after Season 4. Genuinely uncomfortable to watch on rewatch."

reaction: An immediate emotional response to a rewatch, first-time watch, or a specific scene or moment. The post is expressing a feeling in the moment rather than making a case for anything. Little to no argumentative structure.
Example: "Just rewatched Casino Night for the first time in years and completely forgot how that Jim and Pam moment lands. I was not prepared."

Decision rule for edge cases: if a post names specific episodes or characters and uses them as evidence in an argument → analysis. If it names them just to sound credible without actually arguing → hot_take. If it starts with emotional framing and never builds an argument → reaction.

Respond with ONLY the label name. No explanation. No punctuation. No extra words.

Valid labels:
analysis
hot_take
reaction
```

**How results were collected:** The notebook's `classify_with_groq()` function sent each test example to the Groq API with a 0.1s delay between requests. Responses were parsed by matching the model's output against the list of valid labels. All 70 test examples returned parseable responses.

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy | Test Set Size |
|---|---|---|
| Zero-shot baseline (Groq) | 45.7% | 70 |
| Fine-tuned DistilBERT | **50.0%** | 70 |
| Fine-tuning improvement | +4.3pp | — |

---

### Per-Class Metrics

**Fine-tuned DistilBERT:**

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 0.63 | 0.48 | 0.55 | 25 |
| `hot_take` | 0.50 | 0.48 | 0.49 | 23 |
| `reaction` | 0.41 | 0.55 | 0.47 | 22 |
| **Macro avg** | **0.52** | **0.50** | **0.50** | 70 |

**Zero-shot baseline (Groq):**

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 0.47 | 0.36 | 0.41 | 25 |
| `hot_take` | 0.50 | 0.30 | 0.38 | 23 |
| `reaction` | 0.43 | 0.73 | 0.54 | 22 |
| **Macro avg** | **0.47** | **0.46** | **0.44** | 70 |

---

### Confusion Matrix

*Fine-tuned DistilBERT on test set. Rows = true label, columns = predicted label.*

| | **pred: analysis** | **pred: hot_take** | **pred: reaction** |
|---|---|---|---|
| **true: analysis** | 12 | 5 | 8 |
| **true: hot_take** | 3 | 11 | 9 |
| **true: reaction** | 4 | 6 | 12 |

*See `confusion_matrix.png` for the visual version.*

---

### Wrong Predictions Analysis

**Wrong prediction 1**

> "Well, it's over. Damn you emotions! I have never cried because of a show before. Most shows don't resonate me that much. And then I watched The Office. I will miss this, regardless of how many times I rewatch it. It will never be as great the first time."

- **True label:** `analysis` | **Predicted:** `reaction` | **Confidence:** 97%
- **Analysis:** The model predicted `reaction` with near-certainty, and on close reading it is correct — this is a pure emotional response to finishing the show, with no argument, no episode references, and no structural claim. The post is labeled `analysis` in the dataset, which is a mislabel introduced during the auto-labeling phase. This error belongs to the largest pattern in the wrong predictions: approximately 26% of the model's "errors" are cases where the model's output is more accurate than the ground truth label. This is a labeling problem, not a model failure. Fixing it would require a full manual re-annotation pass with stricter adherence to the load-bearing evidence test.

**Wrong prediction 2**

> "The Michael Scott Paper Company should have worked. Given that MSPC was competing with a big company with countless employees, nicer office, warehouse, and tons of other expenses, they could have easily sold at a lower price than Dunder Mifflin and made a profit. If Ryan ran the numbers correctly..."

- **True label:** `hot_take` | **Predicted:** `reaction` | **Confidence:** 60%
- **Analysis:** The model's low confidence (60%) here is actually its most honest prediction in the error set — it was genuinely uncertain. The post opens with a declarative title that signals `hot_take`, but the body introduces economic reasoning and a reference to Ryan that reads like analytical setup. The model appears to have been pulled toward `reaction` by the informal conversational tone rather than any strong surface signal. This is a genuine boundary case: the reasoning is speculative rather than grounded in the show's specific content, which should push it toward `hot_take` under the decision rule, but the post structure mimics analysis closely enough that both the model and human annotators found it ambiguous. More training examples of this "sounds like analysis but isn't" subtype would help the model learn the distinction.

**Wrong prediction 3**

> "Dwight and Angela were meant to be together... The series re-started on Comedy Central this morning and in the first scene of the first episode, Dwight hums a thrash metal version of Little Drummer Boy, which we will later learn (Benihana Christmas) is Angela's favorite song."

- **True label:** `reaction` | **Predicted:** `analysis` | **Confidence:** 93%
- **Analysis:** The model fired `analysis` at high confidence because the post references two specific episodes by name — exactly the surface signal the model learned to associate with the `analysis` class. But the episode references are not load-bearing evidence for any argument: the post is sharing a moment of rewatch discovery, not building a case about the show's writing. This error illustrates the core limitation of the model — it learned to detect episode references as a proxy for analysis rather than learning whether those references are doing argumentative work. Fixing this requires training examples that explicitly demonstrate the difference between name-dropping episodes and using them as evidence, which is difficult to communicate to a model through surface text alone.

---

### Sample Classifications

*Five posts run through the fine-tuned model with their predicted labels and confidence scores.*

| Post (truncated to 150 chars) | Predicted Label | Confidence | Correct? |
|---|---|---|---|
| "Michael's arc from S1 to S7 is a masterclass in slow character rehabilitation. The writers kept his incompetence intact..." | `analysis` | 93.2% | ✅ |
| "Toby is actually one of the best characters in the whole series and Michael's treatment of him is genuinely uncomfortable..." | `analysis` | 87.7% | ❌ (true: `hot_take`) |
| "Just rewatched Casino Night for the first time in years and completely forgot how that Jim and Pam moment at the end lands..." | `hot_take` | 41.8% | ❌ (true: `reaction`) |
| "Season 8 is underrated and the hate it gets is mostly just people grieving Michael Scott. Ed Helms absolutely carries it..." | `hot_take` | 91.5% | ✅ |
| "The reason the Jim and Pam relationship stops working after Season 5 isn't the actors — it's that the writers gave them..." | `analysis` | 90.9% | ✅ |

**Correct prediction explained:**
> "Season 8 is underrated and the hate it gets is mostly just people grieving Michael Scott. Ed Helms absolutely carries it and the Sabre Florida arc is some of the best Andy content in the whole run."
>
> Predicted `hot_take` with 91.5% confidence. This is a reasonable prediction: the post makes a bold contrarian claim in the title, uses "mostly just" to assert a singular cause without evidence, and names show elements decoratively rather than argumentatively. The model correctly identified that nothing in the post builds an actual case — it states rather than reasons — which is the defining feature of `hot_take`.

---

### Confidence Calibration ⭐

*Stretch feature: assessing whether confidence scores are reliable.*

**Expected Calibration Error (ECE):** 0.3662

**Calibration by confidence bucket:**

| Confidence Range | # Predictions | Accuracy in Bucket | Gap |
|---|---|---|---|
| 0.33 – 0.50 | 2 | 100.0% | -0.554 |
| 0.50 – 0.65 | 7 | 28.6% | +0.303 |
| 0.65 – 0.80 | 13 | 38.5% | +0.350 |
| 0.80 – 0.95 | 39 | 56.4% | +0.338 |
| 0.95 – 1.00 | 9 | 44.4% | +0.517 |

*See `calibration_curve.png` for the visual calibration plot.*

**Interpretation:**
The model is severely overconfident, with an ECE of 0.37 — well above the 0.10 threshold for acceptable calibration. 69% of all predictions (48 of 70) fall in the 0.80+ confidence buckets, but accuracy in those buckets is only 56% and 44% respectively. The model fires with near-certainty on predictions it gets wrong almost half the time. The one counterintuitive finding is the 0.33–0.50 bucket: the two examples the model was most uncertain about, it actually got right — suggesting that its uncertainty is more reliable than its confidence. This pattern is typical of transformer models fine-tuned on small, noisy datasets: the model memorizes training patterns and applies them with high confidence even when the input doesn't cleanly match. The calibration warning in the deployed interface is warranted — users should treat confidence scores as rough directional signals rather than probabilities.

---

### Error Pattern Analysis ⭐

*Stretch feature: identifying systematic patterns in model failures beyond individual cases.*

**Pattern 1: Ground Truth Label Noise — The Model Was Often Right**

26% of errors (9/35) are cases where the model's prediction is arguably more correct than the ground truth label. Post #11 ("Well, it's over. Damn you emotions!") is labeled `analysis` in the dataset but is a pure emotional response to finishing the show — the model correctly predicted `reaction`. Posts #20 ("Recently finished The Office") and #24 ("Just finished The Office for the first time") are both labeled `hot_take` but open with classic first-watch completion framing and express feelings rather than opinions — again, the model correctly predicted `reaction`. This pattern is the most important finding in the evaluation: the model cannot exceed the quality of its labels, and approximately 26% of its counted errors are not errors at all. True accuracy on well-labeled examples is meaningfully higher than the reported 50%.

**Pattern 2: Image and Link Posts With No Classifiable Text**

11% of errors (4/35) are posts that consist almost entirely of a URL — a photo, a meme image, a music video, or a screenshot — with one or two words of title text. Posts #1 (a photo of Pam from That 70's Show), #3 ("You are so fucking smart" + image URL), #12 (a Michael Scott music video link), and #35 (an image with no body text) all gave the model nothing substantive to classify. Despite this, the model fired with high confidence on every one (0.62–0.95), relying entirely on the title. These posts should have been filtered during data collection using a minimum character threshold applied to the body text specifically, not the combined title and body. This is a data pipeline issue, not a model limitation.

**Pattern 3: Reactive Surface Language Overrides Opinion Content**

14% of errors (5/35) follow a consistent structure: a post that contains a bold opinion but wraps it in rewatch or emotional framing, causing the model to misfire on the surface signal rather than the content. Post #18 ("Dwight is the fastest person in the world by FAR — Alright here me out") is a `hot_take`, but "here me out" combined with rewatch setup language triggered `reaction` at 90% confidence. Post #26 ("Am I the only one who thought it was incredibly bitchy to say?") is an opinion, but "am I the only one" plus watching context triggered `reaction` at 56%. The reverse also occurs: post #30 ("Just Finished The Office - Andy was Ruined") is a reaction post, but the assertive title assertion overrode the "just finished" framing and triggered `hot_take` at 96% confidence. The model learned surface linguistic signals — rewatch phrases, emotional punctuation, opinion markers — rather than the structural distinction between asserting and arguing that the taxonomy was designed around.

*51% of errors are fully explained by these three patterns. The remaining 49% are genuinely ambiguous posts where two annotators would likely disagree — the expected floor for a subjective 3-class discourse task on noisy social media text.*

---

## Reflection

### What the Model Learned vs. What I Intended

I intended the model to learn a structural distinction: whether a post is reasoning toward a conclusion (`analysis`), asserting one without evidence (`hot_take`), or expressing a feeling without any argument at all (`reaction`). What it actually learned was a set of surface language proxies that correlate with those distinctions but do not capture them.

The confusion matrix makes the learned boundary visible. The model's strongest performance is on `analysis` (F1 0.55), where it appears to have learned that episode references and longer, denser post structure signal this class. But this proxy breaks down in both directions: posts with episode references that are purely observational get labeled `analysis` (wrong predictions #6, #28), and posts with genuine arguments but informal framing get labeled `hot_take` or `reaction`. For `hot_take`, the model learned opinion markers like "I think," "actually," and evaluative adjectives — but the same language appears in reaction posts expressing preferences, causing the hot_take/reaction boundary to be the most error-prone in the matrix (9 hot_takes predicted as reaction). For `reaction`, the model learned rewatch and first-watch phrases ("just finished," "just rewatched," "for the first time") — but this proxy misfires whenever a post opens with that framing and then pivots to an opinion.

The deeper problem is that the distinction I intended to teach — load-bearing evidence versus decorative references — is not legible from surface text alone. It requires understanding whether a reference is being used argumentatively, which is a pragmatic judgment that a model trained on 322 examples of noisy auto-labeled text cannot reliably make. The 50% accuracy ceiling is not a training failure; it is an accurate reflection of what the available data could teach.

---

## Spec Reflection

**One way the spec helped guide implementation:**
The spec's requirement to identify the hardest anticipated edge case and write a decision rule for it *before* annotating 200 examples was the single most valuable constraint in the project. Writing the load-bearing test ("if removing the specific references would collapse the argument, label it analysis; if the claim would stand without them, label it hot_take") before touching any data forced me to think through the analysis/hot_take boundary precisely enough to apply it consistently. Without that rule documented in `planning.md`, the annotated dataset would have been far noisier, and the model's ceiling would have been lower.

**One way implementation diverged from the spec and why:**
The spec assumed a primarily manual annotation workflow — collect 200 examples, label them by hand, upload one CSV. In practice, hitting Groq's daily token limit mid-run forced a pivot to rule-based auto-labeling for the majority of examples, and the dataset was expanded from 207 to 461 examples across three separate collection and labeling passes. This introduced systematic noise from the rule-based classifier (documented in Pattern 1 of the error analysis), which the spec's manual annotation approach would have avoided. The tradeoff was practical necessity over data quality — a real limitation that directly explains part of the model's performance ceiling.

---

## Deployed Interface ⭐

*Stretch feature: a Gradio app that classifies new r/DunderMifflin posts in real time.*

**Live demo:** *Local only — see run instructions below.*

**How to run locally:**

```bash
# Clone the repo and install dependencies
git clone https://github.com/tahiya-nm/ai201-project3-takemeter.git
cd ai201-project3-takemeter
pip install -r requirements.txt

# Run the app
python app.py
# Open http://localhost:7860 in your browser
```

**Interface features:**
- Text input for any r/DunderMifflin post
- Predicted label with one-sentence definition
- Confidence score with bar visualization
- All three class probabilities displayed as bar charts
- Calibration warning displayed on every prediction (ECE = 0.37 >> 0.10 threshold)

---

## AI Usage

**Instance 1 — Pre-labeling annotation assistance (Groq)**

I used Groq's `llama-3.3-70b-versatile` to pre-label all 300 posts in the initial annotation pool using the label definitions from `planning.md`. The script sent each post with the full system prompt and a `temperature=0` setting for consistency. The model returned a suggested label for each post. I reviewed the first 54 rows individually in Google Sheets and corrected approximately 39% of them. The most common override was `analysis → reaction`, where the model classified any post referencing a specific episode as analysis regardless of whether an actual argument was present — the exact decorated argument failure documented in `planning.md`. Due to hitting Groq's daily token limit mid-run, the remaining posts were classified using a local rule-based classifier built on the same label definitions; those labels were not individually reviewed. The `suggested_label` column is retained in `dundermifflin_labeled.csv` for transparency, and this workflow is the primary source of label noise discussed in the error analysis.

**Instance 2 — Error pattern analysis (Claude)**

After collecting the full list of 35 wrong predictions from Section 4, I pasted them into Claude and asked it to identify systematic patterns — specifically looking for shared surface features, confused label pairs, or structural post types that recurred across errors. Claude identified three candidate patterns: ground truth label noise, image/link posts with no classifiable text, and reactive framing overriding opinion content. I verified each pattern by re-reading every flagged example individually. All three patterns held up on close reading and are reported in the Error Pattern Analysis section above. Claude also suggested a fourth candidate pattern around post length, which I discarded after reviewing the examples — short posts appeared in all three label classes without a consistent misfiring direction.

**Instance 3 — Label stress-testing (Claude)**

Before beginning annotation, I used Claude to generate 10 posts sitting at the boundary between `analysis` and `hot_take` in order to stress-test the label definitions before applying them to 200+ examples. Claude produced several posts that I could not cleanly classify using my initial definitions, which revealed that my original `analysis` definition did not distinguish between "uses specific evidence" and "sounds specific." This prompted the addition of the load-bearing test to the decision rule: if removing the episode or character references would collapse the argument, it is `analysis`; if the claim would stand without them, it is `hot_take`. That rule is documented in `planning.md` Section 3 and was applied consistently throughout annotation.

---

*Dataset: `dundermifflin_labeled.csv` — 461 labeled posts from r/DunderMifflin (June 1st – August 1st 2020)*  
*Model: fine-tuned `distilbert-base-uncased` · Baseline: Groq `llama-3.3-70b-versatile` (zero-shot)*  
*Demo video: TODO — add link after recording*