import numpy as np
import pandas as pd

# def _roll(collection, window):
#     for i in range(collection.shape[0] - window + 1):
#         yield pd.DataFrame(collection.values[i:i+window, :], collection.index[i:i+window], collection.columns)
#
# def _beta(slide):
#     market = slide['MKT']
#     X = market.values.reshape(-1,1)
#     X = np.concatenate([np.ones_like(X), X], axis=1)
#     b = np.linalg.pinv(X.T.dot(X)).dot(X.T).dot(slide.values)
#     return pd.Series(b[1], slide.columns, name=slide.index[-1])
#
# def calculate(collection):
#     betas = pd.concat([_beta(slide) for slide in _roll(collection.pct_change().dropna(), 1)], axis=1).T
#     return betas




def calc_betas(df):
    covariance = np.cov(df.values.T) # Calculate covariance between stock and market
    betas = covariance[1:,0]/covariance[0,0]
    return betas

def roll(df, window):
    for i in range(df.shape[0] - window):
        yield pd.DataFrame(df[i:i+window+1])

def calculate(collection, window):
    collection = collection.pct_change().dropna()
    betas_set = [calc_betas(sub_frame) for sub_frame in roll(collection, window)]

    stacked = np.stack(betas_set)
    columns = collection.columns[1:]
    return pd.DataFrame(stacked, columns=columns, index = collection.index[window:]).sort_index()


