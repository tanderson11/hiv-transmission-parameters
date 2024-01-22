# Transmission probability and viral load data from Rakai

On their way to analyze evolutionary tradeoffs in the virulence of HIV, Blanquart et al. explore the relationship between set point viral load (SPVL) and the probability of transmission between serodiscordant sexual partners. To quantify this relationship, the authors analyze data from the Rakai Community Cohort Suvery --- an open cohort, longitudinal study of people with HIV living in the Rakai District, Uganda. In particular, they use data from 817 serodiscordant heterosexual couples in the cohort where the viral load of the HIV positive partner was measured at least once. These authors made their data available in [a Dryad repository](https://doi.org/10.5061/dryad.7kr85). Below we discuss the relevant columns of this data in our reanalysis, and we discuss the steps we used to process the data for our purposes.

Relevant columns:
- `Couple #`: an integer identifying the serodiscordant couple.
- `male.index`: TRUE if the male partner was the index HIV case.
- `female.index`: TRUE if the female partner was the index HIV case.
- `spvl`: the set point (log 10) viral load for the index partner. Determined as the average of all (log 10) viral loads before ART but >6 months after mid-point. When the viral load was undetectable in the index partner (below the detection limit of 400 copies/mL), a viral load of 200 copies/mL was used. (See Appendix 1).
- `spvl.ur`: the set point viral load excluding all measurements when the index partner had a viral load below the detection threshold.
- `n.vl`: number of measurements taken of the viral load of the index partner.
- `male.firstPosDate`: male date first HIV-positive (if `female.index` is true then this column will have value `inf` unless seroconversion took place).
- `female.firstPosDate`: female date first HIV-positive (if `male.index` is true then this column will have value `inf` unless seroconversion took place).
- `index.firstPosDate`: date of first HIV positive test for index case.
- `index.midpoint`: midpoint between last negative test for index and first positive test (0.0 if no negative tests were recorded before first positive).
- `partner.lastNegDate`: last HIV negative observation for partner (equal to the date of last observation if partner never seroconverted).
- `partner.firstPosDate`: first HIV positive observation for partner (equal to `inf` if partner never seroconverted).
- `index.first.art.date`: date that the index individual first began ART.

## Processing the data

- The data was exported from the RData file to a csv, which was munged in Python using `pandas`.
- 36 couples where the index case had 0 measurements of viral load (`n.vl` = 0) were dropped from the data leaving the 817 couples analyzed by Blanquart et al.
- The set point viral load (`spvl`) was transformed from log 10 viral load to copies/mL.
- A `success` column (TRUE if partner seroconverted) was developed by assigning FALSE if the partner's date of first positive was `inf` and TRUE otherwise. 277 seroconversions were recorded.
- A `number` column was developed to represent the number of couples observed with that precise viral load, and the value was set to 1 for all couples because couples were observed individually and data was not aggregated across couples.
- A `duration` column was developed according the following steps:
  - An `index.inferred.spvl.start.date` column was temporarily added which was set equal to `index.midpoint` + 0.5 if `index.midpoint` was nonzero and set to `index.firstPosDate` == `index.firstObsDate` if no negative observations were made of the index partner. The addition of 0.5 reflected the fact that in the first 6 months of infection, we cannot assume that the viral load is equal to the SPVL, and therefore we wish to ignore that period while fitting.
  - A `partner.inferred.seroconversion.date` column was temporarily added. This was set equal to `inf` if partner never seroconverted and (`partner.firstPosDate` + `partner.lastNegDate`)/2 otherwise.
  - An `infectious.contact.period.inferred.end` column was temporarily added which stored:
      - `min(index.first.art.date, partner.lastNegDate)` if partner never seroconverted. This encoded the assumption that after beginning ART, index partners successfully suppressed their viral load. Some credence was lent to this assumption by the observation that 0 recorded seroconversions took place after the index partner began ART.
      - `partner.inferred.seroconversion.date` if partner seroconverted.
  - `duration` was finally set equal to `infectious.contact.period.inferred.end` - `index.inferred.spvl.start.date`.
- A `unprotected_coital_frequency` column was added with a fixed value of 9/month = 108/year. This value was chosen based on a previous study by Gray et al. (2001) for the same cohort that estimated frequency of sex via extensive interviews with both partners independently. The interviews also suggested very low condom use, so it was assumed that all sex was unprotected.

The validity of the `duration` column was verified by checking the following representative couples:

| Couple  | Description | Duration |
| ------- | ------------- | ------ |
| 1       | Index is positive at first observation on 1994.9. Partner seroconverts before 2002.1 and after 2000.8. | 6.55 |
| 7       | Index is positive at first observation on 1994.9. Partner never seroconverts. Last observation is 1995.7 | 0.8 |
| 814     | Index is first positive in 2005.1. Index first ART reported on 2008.6. Partner never seroconverts. Last observation is  | 3.5 |
| 914     | Index is first positive on 2009.2 after being first observed on 2007.5. Partner never seroconverts. Last observation is 2010.7. | 1.9 |

After tracking the supposed duration of observed potentially infectious contact, we excluded the 10 couples with a duration of <=0 years. These are individually discussed below:

| Couple  | Description | Duration |
| ------- | ------------- | ------ |
| 61       | `index.midpoint` was 1996.2<sup>*</sup>. Last observation of partner (negative) was made on 1996.7. 1996.2 + 0.5 == 1996.7 | 0.0 |
| 741      | `index.midpoint` was 1997.2. Last observation of partner (negative) was made on 1997.7. 1997.2 + 0.5 == 1997.7 | 0.0 |
| 1416     | `index.midpoint` was 1997.7. Last observation of partner (negative) was made on 1998.2. 1997.7 + 0.5 == 1998.2 | 0.0 |
| 2098     | `index.midpoint` was 2000.9. Last observation of partner (negative) was made on 2001.4. 2000.9 + 0.5 == 2001.4 | 0.0 |
| 591      | `index.midpoint` was 1999.9. Last observation of partner (negative) was made on 2000.3. 2000.3 < 1999.9 + 0.5 | -0.1 |
| 2218      | `index.midpoint` was 2000.2. Last observation of partner (negative) was made on 2000.5. 2000.5 < 2000.2 + 0.5 | -0.2 |
| 703      | Reported initiation of ART was 2009.1. First index positive test was 2010.4. | -1.3 |
| 921      | Reported initiation of ART was 2005.9. First index positive test was 2007.5. | -1.6 |
| 2860      | Reported initiation of ART was 2005.8. First index positive test was 2007.7. | -1.9 |
| 705      | Reported initiation of ART was 2005. First index positive test was 2008.5. | -3.5 |

<sup>*</sup> Note that the implied midpoint based on last negative and first positive would be 1996.25, but we preferred to use the reported midpoint when available because it was presumably calculated with reference to the true dates of observations rather than the coarse dates of observations provided for anonymization.

We can see that there were two kinds of couples for which we recorded no duration of transmission:
- Couples where the starting point for the validity of SPVL measurements (6 months after inferred date of infection) was on or after the date of the last observation.
- Couples where the index case reported first initiation on ART before they first recorded a positive test in the study. These could be examples of index partners who ceased ART or experienced ART failure. Since we could not distinguish between ART failure and interruption and because ART interruption dates were not reported, it is challenging to estimate the duration of potentially infectious contact. Since there were only 4 couples affected, we decided simply to exclude them from the data used for fitting.

After excluding these couples, we were left with data for 807 serodiscordant couples.

## Confusions:

We should probably test a range of sex frequency to account for the fact that condom use maybe increased? Maybe do this only for couples after the Gray study (2001)?
Should we also infer ART begins the midpoint? Kinda hard because I'm not sure we have a list of every observation made

What to do with couple 16 (NA for first obs date for female)?
What to do with couples 76, 152, 211, 244, etc. where the first observation for the two partners aren't equal but are very close in time? (Assume that they were a couple at the first time? Or assume that they weren't?)

Couple 814 seems broken: last negative date for male is after last observation date?

# References

Blanquart, François et al. (2016). Data from: A transmission-virulence evolutionary trade-off explains attenuation of HIV-1 in Uganda \[Dataset\]. Dryad. https://doi.org/10.5061/dryad.7kr85

François Blanquart, Mary Kate Grabowski, Joshua Herbeck, Fred Nalugoda, David Serwadda, Michael A Eller, Merlin L Robb, Ronald Gray, Godfrey Kigozi, Oliver Laeyendecker, Katrina A Lythgoe, Gertrude Nakigozi, Thomas C Quinn, Steven J Reynolds, Maria J Wawer, Christophe Fraser (2016) A transmission-virulence evolutionary trade-off explains attenuation of HIV-1 in Uganda eLife 5:e20492. https://doi.org/10.7554/eLife.20492
