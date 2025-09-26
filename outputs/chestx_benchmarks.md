| Paper & Year | Model Backbone | Input Resolution | Loss Function | Optimizer | Epochs | Reported AUC | Reported F1 | Interpretability | Notes |
|--------------|----------------|------------------|---------------|-----------|--------|--------------|-------------|------------------|-------|
| ConvNeXt for CXR (2025) | ConvNeXt-Base | 420x420 | Weighted BCE | AdamW | 40 | 0.905 | 0.64 | Grad-CAM++, Integrated Gradients | Strong mid-resolution baseline |
| Vision Transformers in Radiology (2024) | Swin-Transformer-T | 384x384 | Weighted BCE | AdamW | 25 | 0.90 | 0.62 | Attention rollout, Grad-CAM | Transfer learning from ImageNet-22K |
| Example 2023 | EfficientNet-B4 | 380x380 | Weighted BCE | AdamW | 30 | 0.89 | 0.61 | Grad-CAM++, Attention rollout | Used class reweighting |
| CheXNet (2017) | DenseNet-121 | 224x224 | BCE | Adam | 3 | 0.841 (avg) | – | Grad-CAM | First NIH baseline |
