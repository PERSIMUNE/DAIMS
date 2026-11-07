# Example datasheet for synthetic clinic visits

| DAIMS topic | Example entry |
| --- | --- |
| Motivation | Demonstrate how to check and document a tabular dataset before a classification analysis. |
| Composition | 12 fictional visits. Each row has a visit identifier, systolic blood pressure, a visit type, and a binary outcome indicating whether follow-up occurred within 30 days. |
| Collection | All records and source notes were constructed for this example. There are no patient records or clinical measurements. |
| Preprocessing | The starter export contains three seeded issues. The fictional source notes identify the intended visit category for `v04` and the omitted blood pressure for `v08`. The reviewed data restores those entries. The reviewed dictionary records systolic blood pressure in mmHg. |
| Uses and limitations | Use the files to practise data checks and documentation. The dataset is too small and deliberately constructed for drawing conclusions about model performance or clinical care. The example range in the dictionary is a demonstration setting. |
| Distribution and maintenance | The starter and reviewed files are maintained together in the DAIMS repository. Retain the starter files and source notes for comparison. |

For a real dataset, fill out the [full DAIMS datasheet](../../DAIMS_DatasetName_DDMMYYYY.md).
