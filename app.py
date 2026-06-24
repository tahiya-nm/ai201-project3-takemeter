"""
app.py — TakeMeter Gradio Interface
Classifies r/DunderMifflin posts as analysis, hot_take, or reaction
using the fine-tuned DistilBERT model.

Run locally:
    pip install -r requirements.txt
    python app.py
"""

import torch
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = "./takemeter-model-final"
ECE        = 0.3662   # from evaluation_results.json — drives calibration warning
MAX_LENGTH = 256

# Label metadata — definitions shown in the UI
LABEL_INFO = {
    "analysis": {
        "emoji": "🔍",
        "color": "#2196F3",
        "definition": "A structured argument about the show using specific episodes "
                      "or scenes as load-bearing evidence to support a claim.",
    },
    "hot_take": {
        "emoji": "🔥",
        "color": "#F44336",
        "definition": "A bold opinion asserted without a real argument — references "
                      "to the show are decorative, not evidence.",
    },
    "reaction": {
        "emoji": "😮",
        "color": "#4CAF50",
        "definition": "An immediate emotional response to a rewatch or scene — "
                      "expressing a feeling rather than making a case.",
    },
}

# ── Load model ────────────────────────────────────────────────────────────────
print(f"Loading model from {MODEL_PATH}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Build id → label map from model config
ID_TO_LABEL = model.config.id2label   # {0: "analysis", 1: "hot_take", 2: "reaction"}
print(f"Model loaded. Labels: {ID_TO_LABEL}")


# ── Classifier ────────────────────────────────────────────────────────────────
def classify_post(text: str):
    """
    Tokenize input, run inference, return formatted Gradio outputs.
    Returns: label_display, confidence_display, all_probs_display, calibration_note
    """
    if not text or not text.strip():
        return (
            "⚠️ Please paste a post to classify.",
            "",
            "",
            ""
        )

    # Tokenize — truncate to model's max length
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True,
    )

    # Run inference without computing gradients
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probs      = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    pred_id    = probs.argmax().item()
    pred_label = ID_TO_LABEL[pred_id]
    confidence = probs[pred_id].item()

    # ── Format primary prediction ─────────────────────────────────────────────
    info   = LABEL_INFO[pred_label]
    label_display = (
        f"## {info['emoji']} `{pred_label}`\n\n"
        f"**{info['definition']}**"
    )

    # ── Confidence bar ────────────────────────────────────────────────────────
    bar_filled = int(confidence * 20)
    bar        = "█" * bar_filled + "░" * (20 - bar_filled)
    confidence_display = (
        f"**Confidence:** {confidence:.1%}\n\n"
        f"`{bar}`"
    )

    # ── All class probabilities ───────────────────────────────────────────────
    prob_lines = []
    sorted_labels = sorted(
        ID_TO_LABEL.items(),
        key=lambda x: probs[x[0]].item(),
        reverse=True
    )
    for label_id, label_name in sorted_labels:
        p     = probs[label_id].item()
        emoji = LABEL_INFO[label_name]["emoji"]
        bar_f = int(p * 20)
        bar_s = "█" * bar_f + "░" * (20 - bar_f)
        marker = " ◀ predicted" if label_id == pred_id else ""
        prob_lines.append(f"{emoji} **{label_name}** {p:.1%}  `{bar_s}`{marker}")

    all_probs_display = "\n\n".join(prob_lines)

    # ── Calibration warning ───────────────────────────────────────────────────
    # ECE = 0.37 >> 0.10 threshold — model is overconfident, warn user
    if ECE > 0.10:
        calib_note = (
            f"⚠️ **Calibration warning:** This model has an Expected Calibration "
            f"Error (ECE) of {ECE:.2f}, which means confidence scores are not "
            f"reliable. A prediction shown as {confidence:.0%} confident may only "
            f"be correct ~{max(33, int(confidence * 55))}% of the time. "
            f"Use the label as a suggestion, not a certainty."
        )
    else:
        calib_note = f"✅ Confidence scores are reasonably calibrated (ECE = {ECE:.2f})."

    return label_display, confidence_display, all_probs_display, calib_note


# ── Example posts for the demo ────────────────────────────────────────────────
EXAMPLES = [
    ["Michael's arc from S1 to S7 works because the writers kept his incompetence "
     "intact while slowly layering in emotional intelligence. His relationship with "
     "Dwight is the clearest evidence — it evolves from pure exploitation in Season 1 "
     "to something he'd never admit is real friendship by Goodbye Michael."],
    ["Toby is actually one of the best characters in the whole series and Michael's "
     "treatment of him is genuinely uncomfortable to watch on rewatch. "
     "It stopped being funny around Season 4."],
    ["Just rewatched Casino Night for the first time in years and completely forgot "
     "how that Jim and Pam moment at the end lands. I was not prepared at all."],
    ["Season 8 is underrated and the hate it gets is mostly people grieving Michael "
     "Scott. Ed Helms carries it."],
    ["The reason the Jim and Pam relationship stops working after Season 5 is that "
     "the writers gave them no more organic obstacles. Every conflict from S6 onward "
     "is manufactured external drama rather than the internal push-pull of two people "
     "figuring each other out."],
]


# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="TakeMeter — r/DunderMifflin Classifier",
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(
        """
        # 📊 TakeMeter
        ### Discourse Quality Classifier for r/DunderMifflin
        Paste any r/DunderMifflin post or comment to classify it as
        **analysis**, **hot_take**, or **reaction**.

        > Built with fine-tuned `distilbert-base-uncased` · AI201 Project 3
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Post or comment text",
                placeholder="Paste a r/DunderMifflin post here...",
                lines=6,
            )
            classify_btn = gr.Button("Classify", variant="primary", size="lg")

        with gr.Column(scale=3):
            label_out      = gr.Markdown(label="Predicted Label")
            confidence_out = gr.Markdown(label="Confidence")
            probs_out      = gr.Markdown(label="All Class Probabilities")
            calib_out      = gr.Markdown(label="Calibration Note")

    gr.Examples(
        examples=EXAMPLES,
        inputs=text_input,
        label="Example posts — click to load",
    )

    gr.Markdown(
        """
        ---
        **Label definitions:**
        - 🔍 **analysis** — Structured argument using specific episodes/scenes as load-bearing evidence
        - 🔥 **hot_take** — Bold opinion asserted without real argument; references are decorative
        - 😮 **reaction** — Immediate emotional response to a rewatch or scene; no argument structure

        **Note:** Model accuracy is 50% on the test set (vs. 45.7% zero-shot baseline).
        Confidence scores are poorly calibrated (ECE = 0.37) — treat them as rough signals only.
        """
    )

    classify_btn.click(
        fn=classify_post,
        inputs=text_input,
        outputs=[label_out, confidence_out, probs_out, calib_out],
    )

    # Also classify on Enter
    text_input.submit(
        fn=classify_post,
        inputs=text_input,
        outputs=[label_out, confidence_out, probs_out, calib_out],
    )


if __name__ == "__main__":
    demo.launch(share=False)