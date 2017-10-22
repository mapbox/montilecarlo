import logging
import time

import numpy as np
import scipy.ndimage as scimg


log = logging.getLogger(__name__)


def contig_mask(mask, thresh):
    """
    Given a mask, filter out contigous areas
    that are less than the provided threshold
    Paramters
    ----------
    mask: ndarray
        (rows, cols) mask
    thresh: int
        the threshold at which to filter out non-contigous areas
        (any contiguous areas of size below this threshold are filtered out)
    Returns
    --------
    mask: ndarray
        mask with areas below threshold filtered out
    """
    labels, ulabels = scimg.label(mask)
    masked_labels = np.unique(labels[mask])
    continous_mask_vals = [
        u for u in range(ulabels + 1) if u in masked_labels and
        np.sum(labels == u) > thresh]

    return np.in1d(labels.flatten(), continous_mask_vals).reshape(labels.shape)


def clear(img, cloud_thresh=225, cont_thresh=4096):
    """
    1.0 - clouds

    Given a (rows, cols, 3) ndarray, find the proportion of contiguous areas
    where all bands are greater than the cloud threshold

    Parameters
    -----------
    img: ndarray
        (rows, cols, 3) shape ndarray
    cloud_thresh: int
        the threshold at which to mark as possible cloud
    cont_thresh: int
        the threshold at which to filter out non-contigous areas
        (any contiguous areas of size below this threshold are filtered out)

    Returns
    --------
    cloud_proportion: float
        proportion of img areas where
        (a) all three bands are greater than the provided threshold
        (b) are larger than the provided contiguity threshold
    """
    c_mask = np.sum(np.dstack([
        img[:, :, i] > 200 for i in range(img.shape[-1])]), axis=2) == 3
    c_labels = contig_mask(c_mask, cont_thresh)
    return 1.0 - np.sum(c_labels) / c_mask.size
