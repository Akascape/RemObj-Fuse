# RemObj-Fuse

## 🎬 **Automatic Object Remover for DaVinci Resolve Fusion**  
Free and open-source plugin that integrates the power of [LaMa (Resolution-robust Large Mask Inpainting)](https://github.com/advimman/lama) into Fusion workflows for seamless object removal.


## ✨ Features

- 🔍 AI-powered object removal and inpainting using the LaMa model
- 🎞️ Designed for DaVinci Resolve Fusion workflows
- 🛠️ Lightweight, script-based implementation (Python + Fuse)
- 🧩 Easy to integrate, works with both Free and Studio version
- 🆓 100% Free and Open Source

## ⬇️ Download

### [<img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Akascape/RemObj-Fuse?&color=white&label=Download%20Source%20Code&logo=Python&logoColor=yellow&style=for-the-badge"  width="400">](https://github.com/Akascape/RemObj-Fuse/archive/refs/heads/main.zip)
<br> _Don't forget to leave a_ ⭐

## ⚙️ How to Install

1. First install the python3 from [www.python.org](https://www.python.org). Version Requirement: `python: >=3.11, <3.14`
2. Download/Clone the RemObj-Fuse Repo
3. Paste the `RemObj` folder in the fuse plugin directory of Resolve. [Know How](https://youtube.com/shorts/OFHyc48WOqc?feature=shared)
4. Follow the RemObj setup, either using `remobj_manager.py` or install manually.
5. Open the Fusion page in DaVinci Resolve
6. Search for the RemObj plugin in the node menu (_Shift+Spacebar_)
7. Connect the main footage to the main input (Orange/Yellow) and the mask to the secondary input (Green)
8. Let the plugin do its work
9. The output will be displayed through the media out (if connected)
    
### ⮞ Automatic Setup for beginners [[RemObj_Manager](https://github.com/Akascape/RemObj-Fuse/blob/main/RemObj/remobj_manager.py)]
An easy-to-use Python application has been developed to simplify the RemObj setup. Just open the `remobj_manager.py` file—either directly in Python or via the Fuse interface — and follow the installation steps.

<br> ![demo_remobj_manager](https://github.com/user-attachments/assets/a5de323e-6bf9-4823-ba59-fb7e29ddad65)

<details> 
<summary><span style="font-size:1.25em"><strong>Or Setup Manually</strong></span></summary>
   
<br> If you encounter any error or prefer to manually install the required libraries, follow the steps below:

* Install the required packages using pip/pip3 command

```
pip install onnxruntime opencv-python numpy pillow
```
<br> For CUDA support, use:
```
pip install onnxruntime-gpu opencv-python numpy pillow
```

* Make sure the LaMa model file `lama_fp32.onnx` is placed inside the `RemObj` folder.
<br> For fixing issues, check this page: [wiki](https://github.com/Akascape/RemObj-Fuse/wiki/Troubleshooting-Guide)
</details> 

## 📦 Available Models
| Model Name             | Description                                                         | Estimated Download Size      |
|------------------------|---------------------------------------------------------------------|------------------------------|
| lama_fp32.onnx         | Standard LaMa (Large Mask Inpainting) model for object removal      | 208 MB                       |

For more details, visit the LaMa repo: https://github.com/advimman/lama

## 🪄 Video Demo

[<img src="https://img.youtube.com/vi/Lv8DGq7qbx4/0.jpg" width=40% height=40%>](https://youtu.be/Lv8DGq7qbx4)

## 🌱 Overview

| Fuse Version                   | 0.1                           |
|:-------------------------------|:------------------------------|
| Script Version                 | 0.1                           |
| Setup Version                  | 1.0                           |
| DaVinci Resolve Requirement    | Free or Studio : 18+          |
| License                        | MIT                           |
| Copyright                      | 2026                          |
| Author                         | Akash Bora                    |

## 🐞 Debugging

To view plugin logs and troubleshoot issues, open the console through `Fusion page ⮞ Workspace ⮞ Console`. Make sure not to check the `Disable Logging` option in the fuse.
<br>📙 Here is full troubleshooting guide you can follow: [wiki](https://github.com/Akascape/RemOBJ-Fuse/wiki/Troubleshooting-Guide)

## 🚧 Planned Improvements
- Streamline Python Script Execution on Windows. Eliminate the disruptive console popup by implementing a cleaner method to trigger the processing script. Maybe consider using `comp:DoAction()` or `comp:Execute()` for a more integrated Fusion workflow.

- Optimize Model Reloading and improve overall performance during repeated operations.

- Refactor Image I/O Handling, replace the use of the `Clip()` method with direct image data passing. Maybe consider the `GetPixel()` method.
  
Whether you're fixing bugs, suggesting enhancements, or adding new features—your input is valued. Feel free to fork, improve, and submit pull requests to help evolve this tool.

**Get more Resolve plugins at [www.akascape.com](https://www.akascape.com) 👈**
## Thank You
