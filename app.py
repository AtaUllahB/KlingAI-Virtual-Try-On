import os
import cv2
import gradio as gr
import numpy as np
import random
import base64
import requests
import json
import time
import jwt
import logging
from typing import Optional, Dict, Any, Union, Tuple

class KlingAIClient:
    def __init__(self, access_key: str, secret_key: str, base_url: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for API authentication"""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800,  # Current time + 30 minutes
            "nbf": int(time.time()) - 5      # Current time - 5 seconds
        }
        return jwt.encode(payload, self.secret_key, headers=headers)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self._generate_jwt_token()}"
        }
    
    def try_on(self, person_img: np.ndarray, garment_img: np.ndarray, seed: int) -> Tuple[np.ndarray, str]:
        if person_img is None or garment_img is None:
            raise ValueError("Empty image")
            
        # Encode images
        encoded_person = cv2.imencode('.jpg', cv2.cvtColor(person_img, cv2.COLOR_RGB2BGR))[1]
        encoded_person = base64.b64encode(encoded_person.tobytes()).decode('utf-8')
        
        encoded_garment = cv2.imencode('.jpg', cv2.cvtColor(garment_img, cv2.COLOR_RGB2BGR))[1]
        encoded_garment = base64.b64encode(encoded_garment.tobytes()).decode('utf-8')

        # Submit task
        url = f"{self.base_url}/v1/images/kolors-virtual-try-on"
        data = {
            "model_name": "kolors-virtual-try-on-v1",
            "cloth_image": encoded_garment,
            "human_image": encoded_person,
            "seed": seed
        }

        try:
            response = requests.post(
                url, 
                headers=self._get_headers(),
                json=data,
                timeout=50
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result['data']['task_id']
            
            # Wait for result
            time.sleep(9)  # Initial wait
            
            for attempt in range(12):  # Max 12 retries
                try:
                    url = f"{self.base_url}/v1/images/kolors-virtual-try-on/{task_id}"
                    response = requests.get(url, headers=self._get_headers(), timeout=20)
                    response.raise_for_status()
                    
                    result = response.json()
                    status = result['data']['task_status']
                    
                    if status == "succeed":
                        # Get output image URL and download it
                        output_url = result['data']['task_result']['images'][0]['url']
                        img_response = requests.get(output_url)
                        img_response.raise_for_status()
                        
                        # Convert to numpy array
                        nparr = np.frombuffer(img_response.content, np.uint8)
                        result_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
                        return result_img, "Success"
                    elif status == "failed":
                        return None, f"Error: {result['data']['task_status_msg']}"
                        
                except requests.exceptions.ReadTimeout:
                    if attempt == 11:  # Last attempt
                        return None, "Request timed out"
                        
                time.sleep(1)
                
            return None, "Processing took too long"
            
        except Exception as e:
            self.logger.error(f"Error in try_on: {str(e)}")
            return None, f"Error: {str(e)}"

def process_try_on(person_img: np.ndarray, garment_img: np.ndarray, 
                  seed: int, randomize_seed: bool) -> Tuple[np.ndarray, int, str]:
    """Main processing function for Gradio interface"""
    if person_img is None or garment_img is None:
        return None, None, "Empty image"
        
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
        
    client = KlingAIClient(
        access_key="",
        secret_key="",
        base_url="https://api.klingai.com"
    )
    
    try:
        result_img, status = client.try_on(person_img, garment_img, seed)
        return result_img, seed, status
    except Exception as e:
        return None, seed, f"Error: {str(e)}"

# Constants
MAX_SEED = 999999

# Load example images
example_path = os.path.join(os.path.dirname(__file__), 'assets')
garm_list = os.listdir(os.path.join(example_path, "cloth"))
garm_list_path = [os.path.join(example_path, "cloth", garm) for garm in garm_list]
human_list = os.listdir(os.path.join(example_path, "human"))
human_list_path = [os.path.join(example_path, "human", human) for human in human_list]

# CSS styling
css = """
#col-left { margin: 0 auto; max-width: 430px; }
#col-mid { margin: 0 auto; max-width: 430px; }
#col-right { margin: 0 auto; max-width: 430px; }
#col-showcase { margin: 0 auto; max-width: 1100px; }
#button { color: blue; }
"""

def load_description(fp: str) -> str:
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()

# Create Gradio interface
with gr.Blocks(css=css) as Tryon:
    gr.HTML(load_description("assets/title.md"))
    
    with gr.Row():
        with gr.Column(elem_id="col-left"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>Step 1. Upload a person image ⬇️</div>
            </div>
            """)
            
        with gr.Column(elem_id="col-mid"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>Step 2. Upload a garment image ⬇️</div>
            </div>
            """)
            
        with gr.Column(elem_id="col-right"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>Step 3. Press "Run" to get try-on results</div>
            </div>
            """)
            
    with gr.Row():
        with gr.Column(elem_id="col-left"):
            person_img = gr.Image(label="Person image", sources='upload', type="numpy")
            # person_examples = gr.Examples(
            #     inputs=person_img,
            #     examples=human_list_path,
            #     examples_per_page=12
            # )
            
        with gr.Column(elem_id="col-mid"):
            garment_img = gr.Image(label="Garment image", sources='upload', type="numpy")
            # garment_examples = gr.Examples(
            #     inputs=garment_img,
            #     examples=garm_list_path,
            #     examples_per_page=12
            # )
            
        with gr.Column(elem_id="col-right"):
            output_img = gr.Image(label="Result", show_share_button=False)
            
            with gr.Row():
                seed = gr.Slider(
                    label="Seed",
                    minimum=0,
                    maximum=MAX_SEED,
                    step=1,
                    value=0
                )
                randomize_seed = gr.Checkbox(label="Random seed", value=True)
                
            with gr.Row():
                seed_used = gr.Number(label="Seed used")
                result_info = gr.Text(label="Response")
                
            run_button = gr.Button(value="Run", elem_id="button")
            
    with gr.Column(elem_id="col-showcase"):
        gr.HTML("""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
        </div>
        """)
        
        # showcase = gr.Examples(
        #     examples=[
        #         ["assets/examples/model2.png", "assets/examples/garment2.png", "assets/examples/result2.png"],
        #         ["assets/examples/model3.png", "assets/examples/garment3.png", "assets/examples/result3.png"],
        #         ["assets/examples/model1.png", "assets/examples/garment1.png", "assets/examples/result1.png"]
        #     ],
        #     inputs=[person_img, garment_img, output_img],
        #     label=None
        # )
    
    run_button.click(
        fn=process_try_on,
        inputs=[person_img, garment_img, seed, randomize_seed],
        outputs=[output_img, seed_used, result_info],
        api_name=False,
        concurrency_limit=45
    )

if __name__ == "__main__":
    Tryon.queue(api_open=False).launch(show_api=False)