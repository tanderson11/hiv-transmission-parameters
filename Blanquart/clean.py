import pandas as pd
import numpy as np
df = pd.read_csv('couples.unique.csv')
df = df.set_index('Couple')
df = df[~pd.isnull(df['spvl'])]
og_df = df.copy()

df['success'] = (df['partner.firstPosDate'] != np.inf)

df['index.firstObsDate'] = np.where(df['male.index'], df['male.firstObsDate'], df['female.firstObsDate'])

# we assume our SPVL inference begins to apply 6 months after first positive
# this is the maximally conservative estimate
# to account for uncertain period of early infection
df['index.inferred.spvl.start.date'] = df['index.firstPosDate'] + 0.5

df['partner.inferred.seroconversion.date'] = np.where(
    df['success'],
    (df['partner.firstPosDate'] + df['partner.lastNegDate'])/2,
    np.inf
)

# if seroconverted, then upper end of contact is date of seroconversion
# else, it is the min of last observation and ART start time
df['infectious.contact.period.inferred.end'] = np.where(
    df['success'],
    df['partner.inferred.seroconversion.date'],
    df[['index.first.art.date', 'partner.lastNegDate']].min(axis=1)
)

df['duration'] = df['infectious.contact.period.inferred.end'] - df['index.inferred.spvl.start.date']

df_bad = df[df['duration'] <= 0]
df = df[df['duration'] > 0]

with open('couples.extra.columns.csv', 'w') as f:
    df.to_csv(f)

"""
df = pd.DataFrame({
    'couple': df.index,
    'dose': 10**df.spvl,
    'number': 1,
    'success': df['success'],
    'duration': df['duration'],
    'dose_frequency': 9.
    },
)

df['success'] = df['success'].astype(int)
df = df.set_index('couple')

with open('blanquart.couples.for.fitting.csv', 'w') as f:
    df.to_csv(f)
"""