import pandas as pd
import numpy as np
df = pd.read_csv('couples.unique.csv')
df = df.set_index('Couple')
df = df[~pd.isnull(df['spvl'])]

df['success'] = (df['male.index'] & (df['female.firstPosDate'] != np.inf)) | (df['female.index'] & (df['male.firstPosDate'] != np.inf))

# we assume our SPVL inference begins to apply 6 months after the midpoint
# (to account for uncertain early stage of infection) if midpoint is defined
# and immediately at the first positive date if no negative observation was ever made
df['index.inferred.spvl.start.date'] = np.where(
    df['index.midpoint'] > 0.0,
    df['index.midpoint'] + 0.5,
    df['index.firstPosDate']
)

df['partner.inferred.seroconversion.date'] = np.where(
    df['success'],
    (df['partner.firstPosDate'] + df['partner.lastNegDate'])/2,
    np.inf
)

# if seroconverted, then upper end of contact is date of seroconversion
# else, it is the min of last observation and ART start time
df['infectious.contact.period.inferred.end'] = np.where(
    df['partner.inferred.seroconversion.date'] < np.inf,
    df['partner.inferred.seroconversion.date'],
    df[['index.first.art.date', 'partner.lastNegDate']].min(axis=1)
)

df['duration'] = df['infectious.contact.period.inferred.end'] - df['index.inferred.spvl.start.date']

df_bad = df[df['duration'] <= 0]
df = df[df['duration'] > 0]

with open('couples.extra.columns.csv', 'w') as f:
    df.to_csv(f)

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
