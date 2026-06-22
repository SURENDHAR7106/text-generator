import os
import gradio as gr
from utils import generate_text, process_modification

# Define custom CSS styling for a modern, glassmorphic dark theme
css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main Container Background and Font overrides */
.gradio-container {
    background: radial-gradient(circle at top left, #0e1118 0%, #141924 50%, #07090c 100%) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Apply Outfit font across all elements */
body, label, span, p, h1, h2, h3, button, select, input, textarea {
    font-family: 'Outfit', sans-serif !important;
}

/* Glassmorphic Panel Layout */
.glass-panel {
    background: rgba(21, 27, 38, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(16px) !important;
}

/* Custom Output Panel Spacing */
.output-panel {
    margin-top: 2rem !important;
    margin-bottom: 3rem !important;
}

/* Spacing between buttons in settings */
.btn-row {
    margin-top: 1rem !important;
}

/* Title Styling */
.title-gradient {
    background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    font-size: 2.8rem !important;
    text-align: center;
    margin-bottom: 0.2rem !important;
}

/* Subtitle Styling */
.subtitle {
    color: #94a3b8 !important;
    text-align: center;
    font-size: 1.1rem !important;
    margin-bottom: 2rem !important;
    font-weight: 300 !important;
}

/* Textarea Custom Design */
textarea {
    background-color: rgba(9, 11, 16, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #f1f5f9 !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
    transition: all 0.25s ease-in-out !important;
}
textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

/* Remove default background styling from form container */
.form {
    background: transparent !important;
    border: none !important;
}

/* Generate Button: Linear Gradient, Shadow, Hover Scaling */
.primary-btn {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    font-size: 1.05rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4) !important;
    cursor: pointer;
}
.primary-btn:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6) !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
}
.primary-btn:active {
    transform: translateY(0) scale(1.0) !important;
}

/* Clear Button: Alert Tone */
.clear-btn {
    background: rgba(239, 68, 68, 0.1) !important;
    color: #f87171 !important;
    border: 1px solid rgba(239, 68, 68, 0.25) !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    cursor: pointer;
}
.clear-btn:hover {
    background: rgba(239, 68, 68, 0.2) !important;
    border-color: rgba(239, 68, 68, 0.4) !important;
    color: #ef4444 !important;
    transform: translateY(-1px) !important;
}

/* Quick Action Buttons (Summarize, Expand, Rewrite, Continue) */
.action-btn {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer;
}
.action-btn:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}
"""

def create_app():
    # Construct blocks app using CSS layout
    with gr.Blocks(css=css, title="AI Text Generator") as demo:
        
        # Header Banner
        gr.HTML(
            '''
            <div style="margin-top: 1.5rem; margin-bottom: 1.5rem;">
                <h1 class="title-gradient">AI Text Generator</h1>
                <p class="subtitle">Write, refine, and transform text using Llama 3.3 on Groq Cloud</p>
            </div>
            '''
        )
        
        # Main Work Panel (split into Input on Left, Configs on Right)
        with gr.Row(elem_classes="glass-panel"):
            
            # LEFT: Input Area + Quick Modification Actions
            with gr.Column(scale=3):
                gr.HTML("<h3 style='color: #e2e8f0; margin-bottom: 0.5rem;'>Input Content</h3>")
                prompt_input = gr.Textbox(
                    label="Prompt / Text Input",
                    placeholder="Enter your prompt here (e.g. 'Write an email requesting leave.') or paste text to refine...",
                    lines=8,
                    show_label=False
                )
                
                # Modification utilities row
                with gr.Row():
                    summarize_btn = gr.Button("✨ Summarize Text", elem_classes="action-btn")
                    expand_btn = gr.Button("🚀 Expand Text", elem_classes="action-btn")
                    rewrite_btn = gr.Button("🔄 Rewrite Text", elem_classes="action-btn")
                    continue_btn = gr.Button("✍️ Continue Writing", elem_classes="action-btn")
                    
            # RIGHT: Configurations Panel
            with gr.Column(scale=2):
                gr.HTML("<h3 style='color: #e2e8f0; margin-bottom: 0.5rem;'>Settings</h3>")
                style_dropdown = gr.Dropdown(
                    label="Writing Style",
                    choices=["Formal", "Casual", "Creative", "Professional", "Story"],
                    value="Professional"
                )
                temp_slider = gr.Slider(
                    label="Temperature (Creativity)",
                    minimum=0.1,
                    maximum=1.0,
                    value=0.7,
                    step=0.05
                )
                tokens_slider = gr.Slider(
                    label="Maximum Tokens (Length)",
                    minimum=50,
                    maximum=500,
                    value=250,
                    step=10
                )
                
                # Bottom operation row
                with gr.Row(elem_classes="btn-row"):
                    clear_btn = gr.Button("🗑️ Clear", elem_classes="clear-btn")
                    generate_btn = gr.Button("🔮 Generate", elem_classes="primary-btn")
                    
        # Output Row
        with gr.Row(elem_classes="glass-panel output-panel"):
            with gr.Column():
                gr.HTML("<h3 style='color: #e2e8f0; margin-bottom: 0.5rem;'>Generated Output</h3>")
                output_textbox = gr.Textbox(
                    label="Output Content",
                    placeholder="Generated text will appear here.",
                    lines=10,
                    interactive=False,
                    show_label=False
                    # Note: show_copy_button was removed in Gradio 6.x
                    # Use a gr.Button to copy text instead if needed
                )

        # Wire Up Listeners

        # 1. Main text generation
        generate_btn.click(
            fn=generate_text,
            inputs=[prompt_input, style_dropdown, temp_slider, tokens_slider],
            outputs=output_textbox
        )
        
        # 2. Clear fields
        def clear_fields():
            return "", ""
        clear_btn.click(
            fn=clear_fields,
            inputs=[],
            outputs=[prompt_input, output_textbox]
        )
        
        # 3. Summarize function call
        summarize_btn.click(
            fn=lambda p, o, s, t, m: process_modification("summarize", p, o, s, t, m),
            inputs=[prompt_input, output_textbox, style_dropdown, temp_slider, tokens_slider],
            outputs=output_textbox
        )
        
        # 4. Expand function call
        expand_btn.click(
            fn=lambda p, o, s, t, m: process_modification("expand", p, o, s, t, m),
            inputs=[prompt_input, output_textbox, style_dropdown, temp_slider, tokens_slider],
            outputs=output_textbox
        )
        
        # 5. Rewrite function call
        rewrite_btn.click(
            fn=lambda p, o, s, t, m: process_modification("rewrite", p, o, s, t, m),
            inputs=[prompt_input, output_textbox, style_dropdown, temp_slider, tokens_slider],
            outputs=output_textbox
        )
        
        # 6. Continue writing function call
        continue_btn.click(
            fn=lambda p, o, s, t, m: process_modification("continue", p, o, s, t, m),
            inputs=[prompt_input, output_textbox, style_dropdown, temp_slider, tokens_slider],
            outputs=output_textbox
        )
        
    return demo

if __name__ == "__main__":
    demo = create_app()
    # Launch demo server (port and host will be assigned automatically by Gradio)
    demo.launch(share=False)
