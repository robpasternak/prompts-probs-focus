# Datasets and results

This folder contains the datasets and results used for the evaluations presented in the paper. As per fn. 2, two slightly different versions of the dataset were tested. These datasets were identical for all categories other than ONLY and ADV\_QT. **The results reported in the paper were from Dataset 2.**

- **Dataset 1:** For this dataset, ONLY and ADV\_QT backgrounds both entailed the good sentence and **contradicted** the bad sentence. Example:
    - **Background:** Mary gave one book to the teacher, and another to her friend Paul. She did not give anybody anything else.
    - **Good sentence:** Mary only gave the teacher a BOOK.
    - **Bad sentence:** Mary only gave the TEACHER a book.
- **Dataset 2 (reported in the paper):** For this dataset, ONLY and ADV\_QT backgrounds entailed the good sentence and were **neutral** with respect to the bad sentence. Example:
    - **Background:** Mary gave the teacher a book. She did not give the teacher anything else.
    - **Good sentence:** Mary only gave the teacher a BOOK.
    - **Bad sentence:** Mary only gave the TEACHER a book.

**Note:** What is referred to in the paper as a _background_ is marked in the datasets and code as a _context_. We made the terminological switch to "background" because "context" could be ambiguous in an NLP environment.

In piloting, Dataset 1 performed significantly worse than Dataset 2. We hypothesize that this is because of the increased complexity of the backgrounds in Dataset 1.

## Structure

- `/data/datasets_1/`: Datasets generated from the Dataset 1 seed (as `.csv`).
- `/data/datasets_2/`: Datasets generated from the Dataset 2 seed (as `.csv`).
- `/data/datasets_seed/`: Seed datasets (as `.csv`).
- `/data/results/`: By-item results for all experiments.