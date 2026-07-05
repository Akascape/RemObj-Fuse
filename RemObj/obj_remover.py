"""
obj_remover.py
=================
Author: Akascape
License: MIT License
Script Version: 0.1

Object Remover Script for DaVinci Resolve Fusion using LaMa ONNX model.
"""

import sys
import os

# Handle pythonw.exe environment where stdout and stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import time
import cv2
import numpy as np
import onnxruntime as ort

# Set UTF-8 encoding for better compatibility
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class LaMaInpainter:
    def __init__(self, model_path):
        self.log("="*50)
        self.log(f"Loading LaMa model from: {model_path}")
        
        # Check GPU availability and configure providers
        self._check_and_configure_gpu()
        
        # Session options for optimizations
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        so.enable_mem_pattern = True
        so.enable_cpu_mem_arena = True
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        t0 = time.perf_counter()
        try:
            self.session = ort.InferenceSession(
                model_path,
                sess_options=so,
                providers=self.providers
            )
            self.log("[SUCCESS] LaMa model loaded successfully!")
            self.log(f"[INFO] Active providers: {self.session.get_providers()}")
            
            # Cache input/output information for IOBinding
            self.input_names = [i.name for i in self.session.get_inputs()]
            self.output_name = self.session.get_outputs()[0].name
            
            # Warmup loop to prepare the execution engine
            self.log("[INFO] Warming up the model...")
            dummy_img = np.zeros((1, 3, 512, 512), np.float32)
            dummy_mask = np.zeros((1, 1, 512, 512), np.float32)
            
            for _ in range(5):
                self.session.run(
                    None,
                    {
                        self.input_names[0]: dummy_img,
                        self.input_names[1]: dummy_mask,
                    },
                )
            
            self.log(f"[SUCCESS] Load and warmup completed in {(time.perf_counter()-t0)*1000:.2f} ms")
        except Exception as e:
            self.log(f"[CRITICAL] Critical error loading LaMa model: {e}")
            raise e
            
    def _check_and_configure_gpu(self):
        """Check GPU availability and configure ONNX Runtime providers"""
        try:
            available_providers = ort.get_available_providers()
            self.log(f"[INFO] Available ONNX providers: {available_providers}")
            
            self.providers = []
            gpu_found = False
            
            if 'CUDAExecutionProvider' in available_providers:
                # Include provider options to avoid warnings or execution issues
                self.providers.append((
                    "CUDAExecutionProvider",
                    {
                        "device_id": 0,
                        "arena_extend_strategy": "kNextPowerOfTwo",
                        "gpu_mem_limit": 4 * 1024 * 1024 * 1024,
                        "cudnn_conv_algo_search": "EXHAUSTIVE",
                        "cudnn_conv_use_max_workspace": "1",
                        "do_copy_in_default_stream": "1",
                    }
                ))
                self.log("[INFO] GPU detected: NVIDIA CUDA will be used with optimizations")
                gpu_found = True
            elif 'ROCMExecutionProvider' in available_providers:
                self.providers.append('ROCMExecutionProvider')
                self.log("[INFO] GPU detected: AMD ROCm will be used")
                gpu_found = True
                
            # Always add CPU as fallback
            self.providers.append('CPUExecutionProvider')
            
            if not gpu_found:
                self.log("[WARNING] No GPU detected! Using CPU only (slow)")
                
        except Exception as e:
            self.log(f"[WARNING] GPU configuration error: {e}")
            self.providers = ['CPUExecutionProvider']

    def log(self, message):
        """Print log message with timestamp and flush immediately."""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        try:
            print(f"[{timestamp}] {message}")
            sys.stdout.flush()  
        except UnicodeEncodeError:
            print(f"[{timestamp}] {message.encode('ascii', 'ignore').decode('ascii')}")
            sys.stdout.flush()

    def remove(self, image_path, mask_path, output_path):
        try:
            self.log("-"*50)
            self.log(f"[INPUT] Image path: {image_path}")
            self.log(f"[INPUT] Mask path: {mask_path}")
            self.log(f"[OUTPUT] Output path: {output_path}")

            if not os.path.exists(image_path):
                self.log(f"[ERROR] Input image file does not exist: {image_path}")
                return False
            if not os.path.exists(mask_path):
                self.log(f"[ERROR] Input mask file does not exist: {mask_path}")
                return False

            self.log("[STEP 1/4] Loading image and mask...")
            image = cv2.imread(image_path)
            mask = cv2.imread(mask_path)

            if image is None:
                self.log(f"[ERROR] Failed to load image from {image_path}")
                return False
            if mask is None:
                self.log(f"[ERROR] Failed to load mask from {mask_path}")
                return False

            h, w = image.shape[:2]
            self.log(f"Dimensions: {w}x{h} pixels")

            # Resize to model input size (512x512)
            self.log("[STEP 2/4] Preprocessing inputs...")
            img = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
            msk = cv2.resize(mask, (512, 512), interpolation=cv2.INTER_NEAREST)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))[None]

            if len(msk.shape) == 3:
                msk = cv2.cvtColor(msk, cv2.COLOR_BGR2GRAY)

            msk = (msk > 127).astype(np.float32)
            msk = msk[None, None]

            self.log("[STEP 3/4] Running LaMa inpainting model with IOBinding...")
            start_time = time.time()

            io = self.session.io_binding()
            io.bind_cpu_input(self.input_names[0], img)
            io.bind_cpu_input(self.input_names[1], msk)
            io.bind_output(self.output_name)

            self.session.run_with_iobinding(io)
            output = io.copy_outputs_to_cpu()[0]

            processing_time = time.time() - start_time
            self.log(f"[SUCCESS] Inpainting completed in {processing_time:.2f} seconds")

            self.log("[STEP 4/4] Postprocessing and saving output...")
            output = output[0].transpose(1, 2, 0).astype(np.uint8)
            output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            output = cv2.resize(output, (w, h), interpolation=cv2.INTER_CUBIC)

            # Save the result
            cv2.imwrite(output_path, output)
            self.log(f"[SUCCESS] Saved inpainted output to: {output_path}")

            if not os.path.exists(output_path):
                self.log("[ERROR] Output file was not created!")
                return False

            self.log("-"*50)
            return True

        except Exception as e:
            self.log(f"[ERROR] Exception during processing: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False

def main():
    def log_main(message):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{timestamp}] MAIN: {message}")
        sys.stdout.flush()

    log_main("[START] REMOBJ Script Started")

    if len(sys.argv) < 4:
        log_main("[ERROR] Usage: python obj_remover.py <image_path> <mask_path> <output_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    mask_path = sys.argv[2]
    output_path = sys.argv[3]

    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "lama_sim_fp32.onnx")

    if not os.path.exists(model_path):
        log_main(f"[ERROR] Model file not found at: {model_path}")
        sys.exit(1)

    try:
        log_main("[INIT] Initializing LaMa Inpainter...")
        inpainter = LaMaInpainter(model_path)
        
        success = inpainter.remove(image_path, mask_path, output_path)
        if success:
            log_main("[COMPLETE] Object removal completed successfully!")
            sys.exit(0)
        else:
            log_main("[FAILED] Object removal failed!")
            sys.exit(1)
            
    except Exception as e:
        log_main(f"[FATAL] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
