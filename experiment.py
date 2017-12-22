import pandas as pd
import numpy as np


def calc_beta_OP(df):
    np_array = df.values
    m = np_array[:,0] # market returns are column zero from numpy array
    s = np_array[:,1] # stock returns are column one from numpy array
    covariance = np.cov(s,m) # Calculate covariance between stock and market
    beta = covariance[0,1]/covariance[1,1]
    return beta

def beta(df, market=None):
    if market is None:
        market = df['Market']
        df = df.drop('Market', axis=1)
    X = market.values.reshape(-1, 1)
    X = np.concatenate([np.ones_like(X), X], axis=1)
    b = np.linalg.pinv(X.T.dot(X)).dot(X.T).dot(df.values)
    return pd.Series(b[1], df.columns, name=df.index[-1])

def roll_SO(df, w):
    for i in range(df.shape[0] - w + 1):
        yield pd.DataFrame(df.values[i:i+w, :], df.index[i:i+w], df.columns)



def calc_betas(df):
    covariance = np.cov(df.values.T) # Calculate covariance between stock and market
    betas = covariance[1:,0]/covariance[0,0]
    return betas

def roll(df):
    for i in range(df.shape[0] - 1):
        yield pd.DataFrame(df[i:i+2])


m, n = 480, 2
dates = pd.date_range('1995-12-31', periods=m, freq='M', name='Date')
cols = ['Open', 'High', 'Low', 'Close']
dfs = {'s{:04d}'.format(i): pd.DataFrame(np.random.rand(m, 4), dates, cols) for i in range(n)}
market = pd.Series(np.random.rand(m), dates, name='Market')
df = pd.concat([market] + [dfs[k].Close.rename(k) for k in dfs.keys()], axis=1).sort_index(1)



betas_2 = pd.concat([beta(sdf) for sdf in roll_SO(df.pct_change().dropna(), 12)], axis=1).T


betas_set = [calc_betas(sub_frame) for sub_frame in roll(df)]
stacked = np.stack(betas_set)


np.concatenate()
columns = df.colums[1:]
frame = pd.DataFrame(stacked, columns=columns)

for c, col in betas.iteritems():
    dfs[c]['Beta'] = col

dfs['s0000'].head(20)

