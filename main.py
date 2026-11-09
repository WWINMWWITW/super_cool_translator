import gradio as gr
import requests
import json


css = """


.gradio-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding-top: 24px !important;
}

/* ---------- header ---------- */

#header, #header * , #subtitle, #subtitle * {
    overflow: visible !important;
}
#header { text-align: center; }
#header h1 {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 4px;
    color: #7c4a21;
}
.dark #header h1 { color: #f3d9b8; }

#subtitle { text-align: center; margin-bottom: 12px; }
#subtitle p {
    font-size: 16px;
    line-height: 1.6;
    color: #7a6a5c;
}
.dark #subtitle p { color: #c9b8a5; }

/* ---------- text areas ---------- */
textarea {
    font-size: 16px !important;
    line-height: 1.6 !important;
}

/* ---------- translate button ---------- */
#translate-btn {
    font-size: 18px;
    font-weight: 700;
    padding: 12px 0;
    max-width: 360px;
    margin: 8px auto 0 auto;
    box-shadow: 0 2px 6px rgba(124, 74, 33, 0.25);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
#translate-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(124, 74, 33, 0.3);
}
"""

theme = gr.themes.Soft(
    primary_hue="orange",
    neutral_hue="stone",
    radius_size="lg",
    font=[gr.themes.GoogleFont("Nunito"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    # page background
    body_background_fill="#fbf7f1",
    body_background_fill_dark="#1f1b17",
    # boxes
    block_background_fill="#fffdf9",
    block_background_fill_dark="#2a2420",
    block_border_color="#eadfce",
    block_border_color_dark="#3d342d",
    block_shadow="0 1px 3px rgba(124, 74, 33, 0.08)",
    # button
    button_primary_background_fill="#d97706",
    button_primary_background_fill_hover="#b45309",
    button_primary_text_color="white",
)



CHOICES = ['Ukrainian', 'Spanish', 'English']

def machine_translator(input_text, init_language, target_language, api):

    if not api or not api.strip():
        raise gr.Error("Please enter your OpenRouter API key.")
    if not input_text or not input_text.strip():
        raise gr.Error("Please enter some text to translate.")
    if not target_language:
        raise gr.Error("Please choose a target language.")


    if init_language and init_language != 'Auto select':
        source = f"The source language is {init_language}."
    else:
        source = "Detect the source language automatically."


    instructions = (
        "You are a professional translator. "
        f"{source} Translate the user's text into {target_language}. "
        "Output ONLY the translation: no introductions, no explanations, "
        "no quotes, no notes."
    )

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/responses",
            headers={"Authorization": f"Bearer {api.strip()}"},
            json={
                "model": "openrouter/free",
                "instructions": instructions,
                "input": f"<start_of_the_text>{input_text}<end_of_the_text>",
            },
            timeout=60,
        )
    except requests.RequestException as e:
        raise gr.Error(f"Network error: {e}")

    if response.status_code != 200:
        raise gr.Error(f"API error {response.status_code}: {response.text[:200]}")

    data = response.json()

    for item in data.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    text = part["text"]
                    text = text.replace("<start_of_the_text>", "").replace("<end_of_the_text>", "")
                    return text.strip()

    raise gr.Error("Could not parse the model response. Try again.")


with gr.Blocks() as main:
    gr.Markdown("# Super Cool Translator", elem_id="header")
    gr.Markdown(
        "Translate text between **Ukrainian, Spanish and English** using a free "
        "LLM from [OpenRouter](https://openrouter.ai/)."
        "Enter your API key, pick the languages, and get the translation.",
        elem_id="subtitle",
    )

    api = gr.Textbox(
        label="OpenRouter API key",
        type="password",
        placeholder="sk-or-v1-...",
    )

    with gr.Row():
        with gr.Column():
            init_language = gr.Dropdown(
                choices=['Auto select'] + CHOICES,
                value='Auto select',
                label='Initial language',
            )
            input_text = gr.Textbox(
                label="Input", lines=10, placeholder="Type or paste text here..."
            )

        with gr.Column():
            target_language = gr.Dropdown(
                choices=CHOICES, value='English', label='Target language'
            )
            output = gr.Textbox(label="Output", lines=10, interactive=False)

    translate_btn = gr.Button("Translate", variant="primary", elem_id="translate-btn")

    translate_btn.click(
        fn=machine_translator,
        inputs=[input_text, init_language, target_language, api],
        outputs=output,
        api_name="translate",
    )

main.launch(css=css, theme=theme)