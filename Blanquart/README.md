# Transmission probability and viral load data from Rakai

On their way to analyze evolutionary tradeoffs in the virulence of HIV, Blanquart et al. explore the relationship between set point viral load (SPVL) and the probability of transmission between serodiscordant sexual partners. To quantify this relationship, the authors analyze data from the Rakai Community Cohort Suvery --- an open cohort, longitudinal study of people with HIV living in the Rakai District, Uganda. In particular, they use data from 817 serodiscordant heterosexual couples in the cohort where the viral load of the HIV positive partner was measured at least once. These authors made their data available in [a Dryad repository](https://doi.org/10.5061/dryad.7kr85). Below we discuss the relevant columns of this data in our reanalysis, and we discuss the steps we used to process the data for our purposes.

Relevant columns:
- `Couple #`: an integer identifying the serodiscordant couple.
- `male.index`: TRUE if the male partner was the index HIV case.
- `female.index`: TRUE if the female partner was the index HIV case.
- `spvl`: the set point (log 10) viral load for the index partner. Determined as the average of all (log 10) viral loads before ART but >6 months after inferred point of infection (mid point between last negative and first positive). When the viral load was undetectable in the index partner (below the detection limit of 400 copies/mL), a viral load of 200 copies/mL was used. (See Appendix 1).
- `spvl.ur`: the set point viral load excluding all measurements when the index partner had a viral load below the detection threshold.
- `n.vl`: number of measurements taken of the viral load of the index partner.
- `male.firstPosDate`: male date first HIV-positive test (if `female.index` is true then this column will have value `inf` unless seroconversion took place).
- `female.firstPosDate`: female date first HIV-positive test (if `male.index` is true then this column will have value `inf` unless seroconversion took place).
- `index.firstPosDate`: date of first HIV positive test for index case.
- `index.midpoint`: midpoint between last negative test for index and first positive test (0.0 if no negative tests were recorded before first positive).
- `partner.lastNegDate`: last HIV negative observation for recipient/partner (equal to the date of last observation if partner never seroconverted).
- `partner.firstPosDate`: first HIV positive observation for recipient/partner (equal to `inf` if partner never seroconverted).
- `index.first.art.date`: date that the index individual first began ART (determined by self-reports: see Appendix).

## Additional data to incorporate
- Instead of of a number of measurements (`n`) and their average (`spvl`), we want the value of each individual measurement (including measurements that recorded as "undetectable").
- Assay type. For each measurement: what quantitative assay was used to take the measurement.
- Any additional self-reported data about ART use/compliance. We would like any information about whether or not individuals are on ART. At the moment there's not a clear reason to use this data (because as long as we have each measurement of viral load, we can use those to estimate the instantaneous viral load even on ART), but it may be important in subsequent analyses.
- Data on male circumcision if available. This seems like an important cofactor based on some studies, and if we had it we could include it (or not, as desired).
- Extend viral load data to include all viral load measurements for all individuals regardless of participation in a serodiscordant couple. That additional data will help us estimate the rate of false negatives.

## Processing the data

- The data was exported from the RData file to a csv, which was munged in Python using `pandas`.
- 36 couples where the index case had 0 measurements of viral load (`n.vl` = 0) were dropped from the data leaving the 817 couples analyzed by Blanquart et al.
- The set point viral load (`spvl`) was transformed from log 10 viral load to copies/mL.
- An `partner.ever.seroconverted` column was developed by assigning `False` if the partner's date of first positive was `inf` and `True` otherwise. 279 seroconversions were recorded.
- A `partner.first.pos.after.art` column was developed with a value of `True` if the first positive test of a seroconverting recipient partner was recorded after the index partner reported initiating ART. 17 such couples were recorded.
- A `partner.seroconverted.before.art` column was added and set equal to `True` if the recipient partner seroconverted and had their first positive test before the index initiated ART. We treat couples where seroconversion may have taken place with the index on ART as if they were non-seroconverting with a duration that extended as long the recipient was known to be negative and the index had not yet initiated ART.
- A `number` column was developed to represent the number of couples observed with that precise viral load, and the value was set to 1 for all couples because couples were observed individually and data was not aggregated across couples.
- An `index.inferred.spvl.start.date` column was added which was set equal to `index.firstPosDate + 0.5`. The addition of 0.5 reflected the fact that in the first 6 months of infection, we cannot assume that the viral load is equal to the SPVL, and therefore we wish to ignore that period while fitting. Choosing to ignore a six month period after the first positive test is the most conservative choice --- we could have done 6 months after the midpoint between last negative and first positive for the index, when available --- but this choice does not introduce a bias, rather it only affects statistical power.
- A `partner.inferred.seroconversion.date` column was temporarily added. 
  - This was set equal to (`partner.firstPosDate` + `partner.lastNegDate`)/2 where `ever.seroconverted` was True and `inf` elsewhere. (The midpoint approximation was in keeping with the methods of the study. An alternative where we inferred a serconversion date equal to `partner.lastNegDate` was also considered. See later for more details.)
- An `infectious.contact.period.end` column was added which stored:
  - If `partner.seroconverted.before.art`: `min(index.first.art.date, partner.inferred.seroconversion.date)`.
  - Otherwise (partner never serconverted; or it might have taken place while index was on ART): `min(index.first.art.date, partner.lastNegDate)`.
  - By taking the `min` with respect to ART initiation, we cut from consideration any period after the index partner reported starting ART because the recorded SPVL could not be assumed to be accurate after that point.
- A `duration` column was added and set equal to `infectious.contact.period.end` - `index.inferred.spvl.start.date`.
- An `unprotected_coital_frequency` column was added with a fixed value of 9/month = 108/year. This value was chosen based on a previous study by Gray et al. (2001) for the same cohort that estimated frequency of sex via extensive interviews with both partners independently. The interviews also suggested very low condom use, so it was assumed that all sex was unprotected.

At this point, 58 couples were rejected based on the fact that the considered duration was less than or equal to 0.
- Four of these cases arose because the reported first initation of ART for the index partner came before their first positive test. In these cases, the methodology described by Blanquart et al. leaves it unclear what the reported SPVL means in reference to these index partners.

| Couple  | Description |
| ------- | ------------- |
| 703      | Reported initiation of ART was 2009.1. First index positive test was 2010.4. |
| 705      | Reported initiation of ART was 2005. First index positive test was 2008.5. |
| 921      | Reported initiation of ART was 2005.9. First index positive test was 2007.5. |
| 2604     | Reported initiation of ART was 2007.6. First index positive test was 2008.6. |
| 2860     | Reported initiation of ART was 2005.8. First index positive test was 2007.7. |

- For all the remaining couples we rejected, we rejected them because the couple was observed for fewer than 6 months after the first positive test for the index partner. We made the conservative choice to ignore the first 6 months after the first positive test as if the first positive test corresponded to the first day of infection. Some of these couples were observed longer but had a reported ART initiation by the index partner during the first 6 months.
  - The full list of all couples rejected for this reason is: 61,  219,  255,  279,  291,  316,  320,  392,  466,  514,  591,  629, 685,  722,  737,  741,  781,  847,  859,  866,  882,  899, 901, 1207, 1219, 1343, 1362, 1416, 1430, 1458, 1486, 1640, 1758, 1855, 1860, 1867, 1989, 2098, 2123, 2135, 2137, 2144, 2218, 2241, 2367, 2390, 2422, 2506, 2520, 2604, 2803, 2845, 2867, 2948.
- Below we consider a few representative examples:

| Couple  | Description | Duration |
| ------- | ------------- | ------ |
| 61       | First index positive test was 1996.7 => SPVL assumed valid after 1997.2. Last observation of partner (negative) was made in 1996.7. | -0.5 |
| 219      | First index positive test was 1995.7 => SPVL assumed valid after 1996.2. Partner tested negative for the last time in 1995.7 and postive for the first time in 1996.5. We inferred they converted in 1996.1 | -0.1 |
| 2506     | First index positive test was 2006.1 => SPVL assumed valid after 2006.6. Index reported ART initiation in 2006.5 | -0.1 |
| 2135     | First index positive test was 2003.7 => SPVL assumed valid after 2004.2. Index reported ART initiation in 2004.8. Recipient partner tested negative for the last time in 2003.8 and positive for the first time in 2005.2. Don't want to guess if the recipient seroconverted while the index was/was not on ART, so we try to use the last negative test, but it took place before SPVL was assumed valid. | -0.4 |

Of the 53 couples dropped for the above reason, the following statistics held:

| # dropped  | # partner ever seroconverted | # partner known positive before ART | # partner first positive after ART started for index |
| ------- | ------------- | ------ | -- |
| 53 | 26 | 23 | 3 |

3 rows where df['index.firstObsDate'].isna()

250 rows where (df['index.firstPosDate'] < df['index.firstObsDate'])
=> somehow have positivity of index before they enter into observation (either in study? or in cohort?)

0 rows where df['index.firstPosDate'].isna()

14 couples where seroconversion took place after the start of ART:
31, 128, 862, 1260, 1820, 1943, 1946, 2139, 2285, 2458, 2724, 2796, 3085, 3124


After excluding these couples, we were left with data for 807 serodiscordant couples.

## Confusions:

It's potentially misleading to use the midpoint between last negative and first positive as the date of seroconversion. Let's say you were following 10 couples and 5 of the donors had super high viral load and 5 had super low. You follow up 10 years later and you see 6 have seroconverted. You say that they all seroconverted after 5 years. But probably most of them seroconverted super early on! Can estimate the size of this potential problem by assuming seroconversion happens the day after the last negative test and seeing how much that changes results.

Couple 1317: male (index) is first observed in 1996.8. Female is first observed in 1995.1. Presumably we start the period of infectious contact in 1996.8 -- but the Blanquart methodology doesn't dicuss.

Couple 1341: looks malformed. index.firstPosDate = 1995.2 and index is male. But male.firstObsDate == male.lastObsDate == NA.

It feels a little weird to say that if you were entered into the cohort and testing HIV positive that you still have to have 6 months added to the time? This is fine (because of no bias), but is it necessary?

We should probably test a range of sex frequency to account for the fact that condom use maybe increased? Maybe do this only for couples after the Gray study (2001)?
Should we also infer ART begins the midpoint? Kinda hard because I'm not sure we have a list of every observation made

What to do with couple 16 (NA for first obs date for female)?
What to do with couples 76, 152, 211, 244, etc. where the first observation for the two partners aren't equal but are very close in time? (Assume that they were a couple at the first time? Or assume that they weren't?)

Couple 814 seems broken: last negative date for male is after last observation date?

# References

Blanquart, François et al. (2016). Data from: A transmission-virulence evolutionary trade-off explains attenuation of HIV-1 in Uganda \[Dataset\]. Dryad. https://doi.org/10.5061/dryad.7kr85

François Blanquart, Mary Kate Grabowski, Joshua Herbeck, Fred Nalugoda, David Serwadda, Michael A Eller, Merlin L Robb, Ronald Gray, Godfrey Kigozi, Oliver Laeyendecker, Katrina A Lythgoe, Gertrude Nakigozi, Thomas C Quinn, Steven J Reynolds, Maria J Wawer, Christophe Fraser (2016) A transmission-virulence evolutionary trade-off explains attenuation of HIV-1 in Uganda eLife 5:e20492. https://doi.org/10.7554/eLife.20492
