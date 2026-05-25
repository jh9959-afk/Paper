# Project Overview

This repository contains the source code used to process the dataset and reproduce the main experimental results presented in our paper. 

## File Description

* **`Dataset_fix_final.py`**
  This script addresses read failures caused by missing entries in the original dataset from the paper *FEval-TTC: Fair Evaluation Protocol for Test-Time Compute*. It applies regularization procedures to the raw data and archives the cleaned dataset into a new file named `api_responses_fixed.zip`. All subsequent analyses in our paper rely on this processed file.

* **`LLM_known_prior_final.ipynb`**
  This notebook utilizes the processed real-world data (`api_responses_fixed.zip`) to reproduce the results presented in Section 5.3 Real-World Evaluation on FEVAL-TTC and Appendix.

* **`LLM_uncertain_prior_final.ipynb`**
  This notebook also utilizes the processed real-world data (`api_responses_fixed.zip`) to reproduce the results presented in in Section 5.3 Real-World Evaluation on FEVAL-TTC and Appendix.

## Usage Instructions

1. **Data Acquisition**: Download the original dataset provided by *FEval-TTC: Fair Evaluation Protocol for Test-Time Compute*.
2. **Data Processing**: Execute `Dataset_fix_final.py`. This script will process the raw data and automatically generate the required `api_responses_fixed.zip` file.
3. **Result Reproduction**: Run the cells within `LLM_known_prior_final.ipynb` and `LLM_uncertain_prior_final.ipynb` to generate the corresponding results.
