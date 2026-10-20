# Alberta referendum dashboard: baseline sources by provincial ED

All CSVs are keyed by `ed_num`, the 2-digit ED number (01-87) on the "Provincial Electoral Division - Current 2019" boundaries (the 2023 election map). `ed_name` comes from /tmp/ed.geojson. ED 17 is named `Calgary-McCall` there (the current name is Calgary-Bhullar-McCall). Downloaded on 2026-10-20. Scripts are in `scripts/`, raw downloads are in one subfolder per source.

## 1. 2023 provincial general election (May 29, 2023)
- Files: `ab_2023_pge_results_by_ed.csv` (87 rows), `ab_2023_pge_candidates_by_ed.csv` (one row per candidate)
- Source: Elections Alberta, *2023 Provincial General Election Statement of Vote* (Excel). URL: https://www.elections.ab.ca/uploads/2023-Provincial-General-Election-Statement-of-Vote.xlsx (474 KB, one sheet per ED). Linked from https://www.elections.ab.ca/resources/reports/general-elections/
- Licence: the downloaded pages state no open licence (Elections Alberta website terms apply).
- Method: took the "Total (All Voting Options)" row from each sheet. Votes were summed by party code from the candidate column headers (format "Name\nPARTY").
- Checks: total ballots 1,777,315 (matches the official report), seats UCP 49 / NDP 38, valid votes equal the sum of candidate votes in every ED.
- Fields: ucp/ndp/other votes and %, valid_votes, margin_ucp_minus_ndp_pct, winner, names_on_list, declined, rejected, total_ballots, turnout_pct (Elections Alberta's own "Voter Turnout", which is total ballots / names on list), other_parties (party code=votes).
- Caveat: turnout is measured against names on the list, not eligible population.

## 2. By-elections since May 2023
- File: `ab_byelections_since_2023_candidates.csv` (one row per candidate)
- Source: Elections Alberta official results site, https://officialresults.elections.ab.ca/ . Event IDs: 109 = 2024-12-18 Lethbridge-West (ED 72); 114 = 2025-06-23 Edmonton-Ellerslie (31), Edmonton-Strathcona (44), Olds-Didsbury-Three Hills (76); 130 = 2026-09-14 Calgary-Shaw (ED 23). Pages used: `orResultsED.cfm?ED=<n>&EventId=<id>` and `orResultsED2026BE.cfm?EventId=130`. Totals were cross-checked against the "Download as Excel" provincial exports (`orResultsPGE.cfm?MODE=exProv&EventId=<id>`), all saved in `ea_officialresults/`.
- The site lists no other events after 2023-05-29. The "2026 By-election" page (`?page_id=17554`) now returns "Page Not Found". The 2026 by-election is Calgary-Shaw, Sept 14, 2026, and official results exist: NDP Kyle Campbell won with 46.66%, UCP 42.96%, TORY 6.11%.
- Fields: event_id, election_date, candidate, party, votes, pct, elected, valid_votes, names_on_list (named "Number of Electors" for event 130), spoiled, declined, rejected, turnout_pct.
- Party codes: AP Alberta Party, LIB Alberta Liberal, RPA Republican Party of Alberta, WLC Wildrose Loyalty Coalition, TORY Progressive Tory Party of Alberta, IND Independent.

## 3. 2025 federal election (April 28, 2025) transposed to provincial EDs
- File: `fed_2025_transposed_to_ab_ed.csv` (87 rows). Diagnostics: `fed2025_work/summary.txt` and `fed2025_work/poll_allocation_log.csv` (each poll with the ED shares it was assigned).
- Published transposition: none found. The Writ, daveberta and 338Canada cover the federal map only (The Writ "transposes" 2021 onto the new federal map). Elections Canada publishes no provincial-ED version.
- Sources (Elections Canada; boundary files are under the Open Government Licence - Canada per open.canada.ca dataset 97a2a33c-54cc-4f2e-82c1-047ad8212f05. The poll results licence was not checked separately, but earlier GEs are OGL-Canada):
  - Poll-by-poll results for Alberta, 45th GE: https://www.elections.ca/res/rep/off/ovrGE45/62/data_donnees/pollresults_resultatsbureau48.zip (375 KB, 37 CSVs). The national file `.../pollresults_resultatsbureauCanada.zip` is 3.6 MB.
  - Polling division boundaries 2025: https://www.elections.ca/res/cir/mapsCorner/vector/PollingDivisionBoundaries_2025_SHP.zip (95 MB zip, 175 MB .shp)
  - Advance polling district boundaries 2025: https://www.elections.ca/res/cir/mapsCorner/vector/AdvancePollingDistrictBoundaries_2025_SHP.zip (42 MB)
  - ED polygons: the full-resolution polygons in the Alberta census-profile shapefile (section 4, EPSG:3400). /tmp/ed.geojson was not used because it is simplified.
- Method:
  1. Election-day polls (1-499) and mobile polls (500s; these have small building polygons) were overlaid on ED polygons and split by intersected area. Split sub-polls (8A/8B) were matched on their numeric PD. A PD whose entire result was "combined with" another poll had its polygon added to the host poll.
  2. Advance polls (600s) were split across EDs in proportion to the registered electors of the ordinary PDs that make up each advance polling district, with each PD placed by area overlap.
  3. Special-voting-rules ballots (S/R 1 and S/R 2: mail, local special ballots, Canadians abroad, CAF), which are reported per riding only, were spread across EDs in proportion to that riding's geographically allocated votes. The same share was applied to every party.
- Coverage: 2,267,230 valid votes, all assigned, with the total preserved exactly.
  - Election-day/mobile votes: 1,247,207 (55.0%), assigned geographically. 0 geographic votes were left unmatched (the 525 unmatched polls are zero-vote combined polls).
  - Advance votes: 861,044 (38.0%), assigned by elector weighting.
  - Special ballots: 158,979 (7.01%), assigned pro rata. This is the share that could not be placed geographically.
- Fields: cpc/lpc/ndp/ppc/gpc/oth votes and %, valid_votes, winner, cpc_minus_lpc_pct; pct_votes_from_{ordinary,mobile,advance,special} (the composition of each ED's estimate); pct_votes_from_split_polls; federal_ridings_contributing (FED number:votes). The unmatched_* columns are all 0.
- Results: province-wide CPC 63.61 / LPC 27.87 / NDP 6.27. ED "winners" are CPC 79, LPC 5 (Calgary-Buffalo, Calgary-McCall, Calgary-Mountain View, Edmonton-City Centre, Edmonton-Glenora) and NDP 3 (Edmonton-Gold Bar, Edmonton-Highlands-Norwood, Edmonton-Strathcona).
- Caveats:
  - These are estimates. Vote counts are fractional and rounded.
  - Area weighting assumes even population within a PD. 3.2% of all votes come from polls that straddle an ED boundary, mostly large rural PDs.
  - 8.9% of votes are advance votes from advance districts spanning more than one ED. They were assigned assuming advance voters have the same party mix as the whole advance district.
  - Special ballots (7%) are assumed to follow each riding's geography and are not party-adjusted.
  - The ED polygons are StatCan-derived census polygons. Their edges may differ slightly from Elections Alberta's legal lines.
  - A centroid-only assignment gives election-day CPC% within 0.09 points of the area method on average (max 0.72 points).

## 4. 2021 Census profile by ED
- Files: `ab_census_2021_by_ed.csv` (87 rows, 54 columns) and `ab_census_2021_occupation_industry_by_ed.csv` (long table: all 10 NOC 2021 broad occupation groups and 20 NAICS 2017 sectors per ED, with counts and % of labour force)
- Primary source: Alberta Treasury Board and Finance, Office of Statistics and Information, *Alberta Census Profiles by Electoral Division - Current* (2021 Census; created 2023-02-14, published 2023-05-01). Open Government Licence - Alberta.
  - Shapefile and DBF (87 records, 104 fields, EPSG:3400): https://extranet.gov.ab.ca/srd/geodiscover/srd_pub/society/AlbertaCensusProfilesElectoralDivision_Current.zip (2.6 MB)
  - Metadata: https://geodiscover.alberta.ca/geoportal/rest/metadata/item/3908fa8bdd144194974b46fe0a178c3d/xml
  - The same data is served at https://geospatial.alberta.ca/titan/rest/services/census/census_profiles_by_electoral_division_2021/MapServer
- Supplementary source, used only for fields the DBF lacks: the 87 per-ED PDF profiles, "Alberta provincial electoral divisions : <ED>. Compiled from the 2021 Census of Canada" (open.alberta.ca, released 2023-04-12, same licence). URLs are in `ab_census_profiles/pdf_urls.txt`. The Alberta-total PDF is kept separately. Fields taken from the PDFs: avg_age, immigrants/recent immigrants, pop_25_64, bachelors_or_higher, labour_force, participation_rate, top occupation and industry groups, TNR.
- Dissemination-area (DA) route was tried first for the PDF fields but could not be used. The 2021 Census Profile comprehensive DA download (98-401-X2021006, `www12.statcan.gc.ca/.../download-telecharger/comp/getFile.cfm?...`), the download page itself, and the DA boundary file `lda_000b21a_e.zip` are all on www12.statcan.gc.ca. That host returned HTTP 403 with a Cloudflare JavaScript "Security Check" page from this environment (saved in `statcan_da_pages/comp.html`). open.canada.ca (dataset 750e6035-adf8-4426-966f-4c25b12a999e) only links back to the same www12 URLs. www150 data tables carry DA-level population counts but not the long-form education, immigration, occupation or industry variables. So no DA aggregation was done and the file size could not be checked. The PDF values are Statistics Canada tabulations made directly for each ED (block-face allocation), so they are not approximations. If a DA aggregation is done later, expect small differences: StatCan randomly rounds counts to multiples of 5 and suppresses some DA values.
- Field mapping (DBF field shown in brackets):
  - population_2021 [TotalPopul]; pct_age_* [PC0_4, PCY5_17, PCY18_24, PCY25_44, PCY45_64, PC65p]
  - median_household_income_2020 [MedTotIncH]; median_family_income_2020 [MedIncTotF]; median_total_income_15plus_2020 [MedIncTot2]
  - pct_immigrants [PC_Immigra]; pct_visible_minority [PC_VisMino]; pct_indigenous_identity [PC_IndID]
  - unemployment_rate [UnEmpRate]; employment_rate [EmpRate]
  - pct_postsecondary_cert_dip_degree_25_64 [PC_PSC_Dip]; pct_no_certificate_25_64 [PC_No_Cert]
  - pct_low_income_limat [LoInc_All]; pct_canadian_citizens_18plus [PC_Ctzn18p]; median_dwelling_value [MedVal]
  - vismin_group1-3: the three largest visible-minority groups, as % of the population base [from Arab ... MulVisMino counts / (TotVisMino+NotVisMino)]
  - From the PDFs: avg_age ("Average age (years)"); pct_recent_immigrants (immigrants who arrived 2016-2021 / total population by immigrant status, private households); pct_bachelors_or_higher_25_64 ("Bachelor's degree or higher", age 25-64); top1-3_occ and top1-3_ind (% of the total labour force 15+; occupation counts are men+ plus women+); tnr_short_form_pct and tnr_long_form_pct (non-response rates).
- Checks: Highwood DBF values match its PDF. Unemployment rates from the DBF and PDF agree for all 87 EDs. ED numbers and names match ed.geojson.
- Not available: median age (the source publishes average age only) and % rural vs urban (not in either source; would need StatCan population-centre overlays).
- Caveats:
  - 2021 Census labour figures (unemployment, participation, employment, occupation, industry) refer to the week of May 2-8, 2021, during COVID-19 restrictions, so unemployment is elevated (Calgary EDs 12-14%). Income is for 2020 and includes COVID benefits.
  - Long-form figures are 25% sample data, randomly rounded. On-reserve figures are affected by incompletely enumerated reserves (MapServer layer 39 lists them).
  - Data are tabulated from StatCan block-face points allocated to EDs.
