from pathlib import Path

import numpy as np
import pandas as pd

from npt.datasets.base import BaseDataset
from npt.utils.data_loading_utils import download


class NewsClassificationDataset(BaseDataset):
    def __init__(self, c):
        super(NewsClassificationDataset, self).__init__(
            fixed_test_set_index=None)
        self.c = c

    def load(self):
        (self.data_table, self.N, self.D, self.cat_features, self.num_features,
            self.missing_matrix) = load_and_preprocess_News_dataset(
            self.c)

        # For breast cancer, target index is the first column
        self.num_target_cols = []
        self.cat_target_cols = [self.D - 1]

        self.is_data_loaded = True
        self.tmp_file_or_dir_names = ['wdbc.data']

        # overwrite missing
        if (p := self.c.exp_artificial_missing) > 0:
            self.missing_matrix = self.make_missing(p)
            # this is not strictly necessary with our code, but safeguards
            # against bugs
            # TODO: maybe replace with np.nan
            self.data_table[self.missing_matrix] = 0


def load_and_preprocess_News_dataset(c):
    """Class imbalance is [357, 212]."""
    if c.imp == "mean":
        path = Path("/data/lsw/data/data/" + c.data_set + "/" + c.missingtype + c.data_set + "_" + str(
            c.missingrate) + ".csv")
    else:
        path = Path("/data/lsw/data/data/" + c.data_set + "/" + c.missingtype + c.data_set + "_" + str(
            c.missingrate) + c.imp + ".csv")

    file = path

    # Read dataset
    data_table = pd.read_csv(file, header=0)
    data_table = np.array(data_table)
    new_values = np.nanmean(data_table, axis=0)
    nan_masks = np.isnan(data_table)
    num_nan_indices = np.where(nan_masks)
    data_table[num_nan_indices] = np.take(new_values, num_nan_indices[1])
    data_table = pd.DataFrame(data_table)
    # Drop id col

    N = data_table.shape[0]
    D = data_table.shape[1]
    types = data_table.dtypes
    nunique = data_table.nunique()
    categorical_indicator = list(np.zeros(data_table.shape[1]).astype(bool))
    missing_matrix = np.zeros((N, D))
    missing_matrix = missing_matrix.astype(dtype=np.bool_)
    for col in data_table.columns:
        if types[col] == 'object' or nunique[col] < 100:
            categorical_indicator[data_table.columns.get_loc(col)] = True
    categorical_columns = data_table.columns[list(np.where(np.array(categorical_indicator) == True)[0])].tolist()
    cont_columns = list(set(data_table.columns.tolist()) - set(categorical_columns))

    cat_idxs = list(np.where(np.array(categorical_indicator) == True)[0])
    cat_idxs = [int(idx) for idx in cat_idxs]
    con_idxs = list(set(range(len(data_table.columns))) - set(cat_idxs))
    return data_table.to_numpy(), N, D, cat_idxs, con_idxs, missing_matrix

