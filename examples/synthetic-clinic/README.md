# Check and document a sample dataset with DAIMS

This walkthrough takes you from a fictional clinic export to a reviewed dataset, data dictionary, and datasheet.

## 1. Run the initial checks

Download the [starter dataset](https://raw.githubusercontent.com/PERSIMUNE/DAIMS/main/examples/synthetic-clinic/starter-data.csv) and [starter data dictionary](https://raw.githubusercontent.com/PERSIMUNE/DAIMS/main/examples/synthetic-clinic/starter-dictionary.csv). Open the [DAIMS app](https://daims-app.streamlit.app/), upload the dataset in the first field and the dictionary in the second, then review the automated checklist.

| Check | What DAIMS flags | How the example was reviewed |
| --- | --- | --- |
| 8 · Missing entries | An `NA` value in `systolic_bp` | The fictional source record for visit `v08` supplies the omitted value of 132 mmHg. |
| 10 · Data dictionary | A missing unit for `systolic_bp` | The source record gives the unit as mmHg. Record it in the dictionary. |
| 12 · Categories | `rtne` is absent from the allowed values for `visit_type` | The source record for `v04` gives `routine`. Correct the export to match. |

The [fictional source notes](source-records.csv) support those edits. For your own data, check unexpected values against the source and document how you handled any unresolved entries.

## 2. Compare the reviewed files

Upload the [reviewed dataset](https://raw.githubusercontent.com/PERSIMUNE/DAIMS/main/examples/synthetic-clinic/reviewed-data.csv) and [reviewed dictionary](https://raw.githubusercontent.com/PERSIMUNE/DAIMS/main/examples/synthetic-clinic/reviewed-dictionary.csv). Checks 8, 10, and 12 should now pass. Work through the manual checks and use **Download Checklist** to save the results.

The [example datasheet](datasheet.md) records where the data came from, what changed, and what the data can be used for. Use the [full DAIMS template](../../DAIMS_DatasetName_DDMMYYYY.md) to document your own dataset.

## 3. Explore the next step with MAIT

For a runnable classification and SHAP example on a larger, different dataset, open the [MAIT quick demo on Kaggle](https://www.kaggle.com/code/remyz5/mait-explainable-ai-with-mixed-clinical-data). It shows how to compare models and explain predictions after data preparation.
