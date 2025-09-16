# fixed_streamlit_app.py
import streamlit as st
from PIL import Image
import io
import os
import subprocess
import json
import re
import logging
import warnings
from typing import Dict, Any, Optional

# Suppress warnings
warnings.filterwarnings("ignore")

class StreamlitImageAgent:
    def __init__(self, model_name="gemma:2b"):
        self.model_name = model_name
        self.available_backgrounds = self._scan_backgrounds()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _scan_backgrounds(self):
        """Scan available background images"""
        bg_dir = "backgrounds"
        if not os.path.exists(bg_dir):
            os.makedirs(bg_dir)
            return []
        
        backgrounds = []
        for file in os.listdir(bg_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                backgrounds.append(file)
        return backgrounds

    def _call_ollama(self, prompt: str) -> str:
        """Calls Ollama CLI with better error handling and debug logging"""
        try:
            cmd = ["ollama", "run", self.model_name]

            # Windows-specific subprocess configuration
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120,
                startupinfo=startupinfo
            )

            self.logger.info(f"Ollama return code: {result.returncode}")
            self.logger.info(f"Ollama stdout: {result.stdout}")
            self.logger.info(f"Ollama stderr: {result.stderr}")

            if result.returncode != 0:
                st.error(f"Ollama error: {result.stderr}")
                return ""

            response = result.stdout.strip()
            return response

        except subprocess.TimeoutExpired:
            st.error("Ollama call timed out")
            self.logger.error("Ollama call timed out")
            return ""
        except Exception as e:
            st.error(f"Error calling Ollama: {e}")
            self.logger.error(f"Error calling Ollama: {e}")
            return ""

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response"""
        if not text:
            return None
            
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try patterns
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            r'```(?:json)?\s*(\{.*?\})\s*```',
            r'\{.*\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        match = match[0]
                    if match.strip():
                        return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None

    # def _fallback_parse(self, instruction: str) -> Dict[str, Any]:
    #     """Fallback rule-based parsing"""
    #     instruction_lower = instruction.lower()
    #     actions = []
        
    #     remove_keywords = [
    #         'remove', 'cut out', 'transparent', 'detach', 'extract', 
    #         'isolate', 'separate', 'no background', 'without background'
    #     ]
        
    #     if any(keyword in instruction_lower for keyword in remove_keywords):
    #         actions.append({"type": "remove_background", "confidence": 0.9})
        
    #     set_bg_keywords= [
    #         'replace background', 'change background', 'set background','make background','embed background','modify background']
    #     ]
    #     if any(keyword in instruction_lower for keyword in set_bg_keywords):
    #         actions.append({"type": "replace_background", "confidence": 0.9})

    #     # Look for backgrounds
    #     for bg in self.available_backgrounds:
    #         bg_name = bg.lower().replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
    #         if bg_name in instruction_lower:
    #             actions.append({
    #                 "type": "replace_background", 
    #                 "params": {"source": bg}, 
    #                 "confidence": 0.8
    #             })
    #             break
        
    #     # Look for colors
    #     colors = ['white', 'black', 'red', 'green', 'blue', 'yellow', 'purple', 'brown']
    #     for color in colors:
    #         if color in instruction_lower:
    #             actions.append({
    #                 "type": "set_background_color",
    #                 "params": {"color": color},
    #                 "confidence": 0.7
    #             })
    #             break
        
    #     # Default
    #     if not actions and 'background' in instruction_lower:
    #         actions.append({"type": "remove_background", "confidence": 0.6})
        
    #     return {
    #         "actions": actions,
    #         "reasoning": "Rule-based parsing used",
    #         "warnings": []
    #     }

    def analyze_instruction(self, instruction: str) -> Dict[str, Any]:
        """Main analysis method"""
        prompt = f'''
You are an expert image editing assistant. You can find the exact intent even with twisted user queries. You can find different wordings and indirect mentioning. Some may mention colors in adjective form like greener, reddish. You are much expert and capable of finding and handling all that with the correct action. Analyze the following instruction and respond with ONLY valid JSON (no markdown, no extra text). IMPORTANT: The JSON must have exactly three top-level keys: "actions" (an array), "reasoning" (a string), and "warnings" (an array). Do NOT put "reasoning" or "warnings" inside the "actions" array or any other array. They must be top-level keys, not inside any array. If you do not follow this format exactly, your response will be rejected.

Instruction: "{instruction}"

When to use each action:
- Use 'remove_background' if the instruction asks to remove, erase, or make the background transparent. Do it first always.
- Use 'replace_background' only if the instruction mentions any file from backgrounds folder. Add a 'params' key with the background filename. If replace_background is chosen, set_background_color should not be chosen and vice versa.
- Use 'set_background_color' if the instruction asks to change the background to a specific color. Only use standard color names or hex codes for colors. **Before choosing set_background_color, always check if the word matches any file in the available backgrounds list. If it matches, use replace_background instead.** If set_background_color is chosen, replace_background should not be chosen and vice versa.

Response format examples: atmost any 2 actions type only will be chosen in which remove_background is for sure.
Remove background:
{{
  "actions": [
    {{"type": "remove_background", "confidence": 0.9}}
  ],
  "reasoning": "The instruction asks to remove the background.",
  "warnings": []
}}

Replace background:
{{
  "actions": [
    {{"type": "replace_background", "params": {{"source": "bg1.jpg"}}, "confidence": 0.85}}
  ],
  "reasoning": "The instruction asks to use a specific background image.",
  "warnings": []
}}

Set background color:
{{
  "actions": [
    {{"type": "set_background_color", "params": {{"color": "green"}}, "confidence": 0.8}}
  ],
  "reasoning": "The instruction asks to change the background color.",
  "warnings": []
}}

Available action types: remove_background, replace_background, set_background_color

dont perform replace_background unless a file name is mentioned from backgrounds folder
Available backgrounds: {', '.join(self.available_backgrounds) if self.available_backgrounds else 'none'}
'''
        self.logger.info(f"Prompt sent to LLM:\n{prompt}")
        with st.spinner("🤖 Agent is thinking..."):
            response = self._call_ollama(prompt)

        if not response:
            st.warning("Using rule-based fallback (LLM didn't respond)")
            return self._fallback_parse(instruction)

        parsed = self._extract_json(response)

        if not parsed:
            st.warning("Using rule-based fallback (couldn't parse JSON)")
            return self._fallback_parse(instruction)

        # Validate
        if 'actions' not in parsed:
            parsed['actions'] = []
        if 'reasoning' not in parsed:
            parsed['reasoning'] = 'No reasoning provided'
        if 'warnings' not in parsed:
            parsed['warnings'] = []

        return parsed

    def execute_plan(self, actions: list, image_bytes: bytes):
        """Execute the planned actions with detailed logging"""
        from editor_cli import remove_background, composite_with_background, parse_color
        import traceback

        current_image = image_bytes
        bg_path = None
        bg_color = None
        execution_log = []

        self.logger.info(f"Executing actions: {actions}")
        for idx, action in enumerate(actions):
            action_type = action.get('type', 'unknown')
            confidence = action.get('confidence', 0.5)
            self.logger.info(f"Action {idx+1}: {action}")
            try:
                if action_type == 'remove_background':
                    execution_log.append(f"✂️ Removing background (confidence: {confidence:.1%})")
                    current_image = remove_background(current_image)
                elif action_type == 'replace_background':
                    params = action.get('params', {})
                    bg_file = params.get('source')
                    if bg_file:
                        # Robust background file matching (ignore extension)
                        bg_name = os.path.splitext(bg_file)[0].lower()
                        matched_file = None
                        for candidate in self.available_backgrounds:
                            candidate_name = os.path.splitext(candidate)[0].lower()
                            if candidate_name == bg_name:
                                matched_file = candidate
                                break
                        if matched_file:
                            bg_path = os.path.join('backgrounds', matched_file)
                            execution_log.append(f"🖼️ Setting background to {matched_file} (confidence: {confidence:.1%})")
                        else:
                            execution_log.append(f"⚠️ Background {bg_file} not found (tried to match by name)")
                    else:
                        execution_log.append(f"⚠️ No background file specified for replace_background")
                elif action_type == 'set_background_color':
                    params = action.get('params', {})
                    color = params.get('color')
                    if color:
                        bg_color = parse_color(color)
                        execution_log.append(f"🎨 Setting background color to {color} (confidence: {confidence:.1%})")
                    else:
                        execution_log.append(f"⚠️ No color specified for set_background_color")
                else:
                    execution_log.append(f"⚠️ Unknown action type: {action_type}")
            except Exception as e:
                tb = traceback.format_exc()
                execution_log.append(f"❌ Error in {action_type}: {str(e)}\n{tb}")
                self.logger.error(f"Error in {action_type}: {str(e)}\n{tb}")

        # Final composition
        try:
            final_image = composite_with_background(current_image, bg_path=bg_path, bg_color=bg_color)
            execution_log.append("✅ Final composition completed")
            self.logger.info(f"Execution log: {execution_log}")
            return final_image, execution_log
        except Exception as e:
            tb = traceback.format_exc()
            execution_log.append(f"❌ Error in final composition: {str(e)}\n{tb}")
            self.logger.error(f"Error in final composition: {str(e)}\n{tb}")
            return None, execution_log


# Streamlit UI (vertical, no columns)
st.set_page_config(page_title="🤖 Agentic Image Editor", layout="wide")
st.title("🤖 Agentic Image Editor")

# Initialize agent
if 'agent' not in st.session_state:
    st.session_state.agent = StreamlitImageAgent()

st.subheader("📤 Input")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption="Preview: Uploaded Image", width=600)

instruction = st.text_area(
    "Enter your instruction:",
    placeholder="e.g., 'Remove the background', 'Make background blue', 'Replace with bg4'",
    height=100
)

if st.button("🚀 Process Image", type="primary"):
    if uploaded_file and instruction:
        img_bytes = uploaded_file.read()
        img = Image.open(io.BytesIO(img_bytes))
        st.session_state.original_image = img
        plan = st.session_state.agent.analyze_instruction(instruction)
        if plan['actions']:
            with st.spinner("🔄 Executing plan..."):
                result_image, execution_log = st.session_state.agent.execute_plan(plan['actions'], img_bytes)
            st.session_state.result = {
                'plan': plan,
                'result_image': result_image,
                'execution_log': execution_log,
                'success': result_image is not None
            }
        else:
            st.error("No actions planned. Try a different instruction.")
    else:
        st.error("Please upload an image and enter an instruction")

# Results section (vertical, only log and output image)
if hasattr(st.session_state, 'result') and st.session_state.result:
    result = st.session_state.result
    st.write("**Execution Log:**")
    for log_entry in result.get('execution_log', []):
        st.write(log_entry)
    if result['success'] and result['result_image']:
        st.image(result['result_image'], caption="Output", width=600)
    else:
        st.warning("No result image generated.")

# Sidebar
with st.sidebar:
    st.subheader("🤖 Agent Status")
    agent = st.session_state.agent
    st.metric("Available Backgrounds", len(agent.available_backgrounds))
    if agent.available_backgrounds:
        with st.expander("📁 Background Files"):
            for bg_file in agent._scan_backgrounds():
                st.write(bg_file)
    else:
        st.info("💡 Add images to the 'backgrounds' folder for background replacement")
    st.subheader("💡 Example Instructions")
    examples = [
        "Remove the background",
        "Make background gold", 
        "Replace with bg4 image in files",
        "Cut out the subject",
        "Detach the background"
    ]
    for example in examples:
        if st.button(f"'{example}'", key=f"ex_{hash(example)}"):
            st.session_state['example_instruction'] = example