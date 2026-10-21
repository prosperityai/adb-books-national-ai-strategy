<!-- Purpose: checklist to confirm a facility can host a GPU cluster before purchase.
     Book: National AI Strategy in Practice, Chapter 5. Licence: MIT. -->

# Data-Centre Readiness Checklist for GPU Hosting

Use this before ordering GPU servers, not after. Each "No" is a cost
or a delay that belongs in the plan.

Facility: ______________________  Location: ______________________
Operator: ______________________  Inspected by: __________________
Date of inspection: ____________

Planned load (from planner/compute_planner.py):

| Item | Value |
|---|---|
| GPU servers | ____ |
| IT load (kW) | ____ |
| Facility load at expected PUE (kW) | ____ |
| Racks needed at ____ kW per rack | ____ |

## 1. Power supply

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 1.1 | Utility capacity available at the site meets facility load plus 25% | [ ] | [ ] | ____ |
| 1.2 | Two independent utility feeds, or one feed plus on-site generation | [ ] | [ ] | ____ |
| 1.3 | Utility outage hours in the last 12 months recorded: ____ | [ ] | [ ] | ____ |
| 1.4 | Generators sized for full load, with ____ hours of fuel on site | [ ] | [ ] | ____ |
| 1.5 | UPS sized for full IT load with ____ minutes runtime | [ ] | [ ] | ____ |
| 1.6 | Power distribution can deliver ____ kW to each GPU rack | [ ] | [ ] | ____ |
| 1.7 | Electricity tariff for this load confirmed in writing: ____ per kWh | [ ] | [ ] | ____ |
| 1.8 | Power-factor and harmonics requirements checked with the utility | [ ] | [ ] | ____ |

## 2. Cooling

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 2.1 | Cooling capacity covers the full IT load at peak outdoor temperature (____ C) | [ ] | [ ] | ____ |
| 2.2 | Cooling designed for at least ____ kW per rack (air) | [ ] | [ ] | ____ |
| 2.3 | Liquid cooling available or plannable if racks exceed ~40 kW | [ ] | [ ] | ____ |
| 2.4 | Cooling plant has N+1 redundancy | [ ] | [ ] | ____ |
| 2.5 | Water supply for cooling secure in dry season (if evaporative) | [ ] | [ ] | ____ |
| 2.6 | Measured annual PUE: ____ (source of measurement: ________) | [ ] | [ ] | ____ |
| 2.7 | Hot/cold aisle containment in place | [ ] | [ ] | ____ |

## 3. Space and structure

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 3.1 | Floor rated for ____ kg per rack (8-GPU servers are heavy) | [ ] | [ ] | ____ |
| 3.2 | Space for ____ racks plus 30% growth | [ ] | [ ] | ____ |
| 3.3 | Loading bay, lifts and doors fit server crates | [ ] | [ ] | ____ |
| 3.4 | Fire suppression suitable for IT equipment | [ ] | [ ] | ____ |
| 3.5 | Site outside flood zone and away from other hazards | [ ] | [ ] | ____ |

## 4. Connectivity

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 4.1 | At least two fibre routes entering by separate paths | [ ] | [ ] | ____ |
| 4.2 | At least two carriers present | [ ] | [ ] | ____ |
| 4.3 | Direct connection to the national internet exchange point | [ ] | [ ] | ____ |
| 4.4 | Bandwidth of ____ Gbps available, upgradeable to ____ Gbps | [ ] | [ ] | ____ |
| 4.5 | Government network reachable without crossing the public internet | [ ] | [ ] | ____ |
| 4.6 | Service continues if one international cable is cut (tested on ____) | [ ] | [ ] | ____ |

## 5. Security and certification

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 5.1 | Tier or equivalent design/operations certification: ____ | [ ] | [ ] | ____ |
| 5.2 | Physical access control, CCTV and visitor log | [ ] | [ ] | ____ |
| 5.3 | Cage or suite dedicated to government equipment | [ ] | [ ] | ____ |
| 5.4 | Information security certification (e.g. ISO/IEC 27001): ____ | [ ] | [ ] | ____ |
| 5.5 | Staff security vetting meets government requirements | [ ] | [ ] | ____ |

## 6. Operations

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 6.1 | 24/7 on-site staff | [ ] | [ ] | ____ |
| 6.2 | Remote hands service with response time of ____ minutes | [ ] | [ ] | ____ |
| 6.3 | Spare parts store or vendor depot in-country | [ ] | [ ] | ____ |
| 6.4 | Customs clearance time for replacement parts: ____ days | [ ] | [ ] | ____ |
| 6.5 | Monthly power, cooling and incident reports provided | [ ] | [ ] | ____ |
| 6.6 | Maintenance windows agreed and notified ____ days ahead | [ ] | [ ] | ____ |

## 7. Commercial and legal

| # | Check | Yes | No | Notes |
|---|---|---|---|---|
| 7.1 | Price per kW per month (or per rack) quoted: ____ | [ ] | [ ] | ____ |
| 7.2 | Power billed at metered cost, not a flat estimate | [ ] | [ ] | ____ |
| 7.3 | Contract term and exit terms acceptable | [ ] | [ ] | ____ |
| 7.4 | Facility owned or controlled by a party acceptable for national data | [ ] | [ ] | ____ |
| 7.5 | Import duties and taxes on GPU servers confirmed: ____ | [ ] | [ ] | ____ |

## 8. Result

| Area | Ready | Ready with works | Not ready |
|---|---|---|---|
| Power | [ ] | [ ] | [ ] |
| Cooling | [ ] | [ ] | [ ] |
| Space and structure | [ ] | [ ] | [ ] |
| Connectivity | [ ] | [ ] | [ ] |
| Security | [ ] | [ ] | [ ] |
| Operations | [ ] | [ ] | [ ] |
| Commercial | [ ] | [ ] | [ ] |

Works required before delivery, with cost and time:

| Work | Cost (USD) | Weeks | Owner |
|---|---|---|---|
| ____________________ | ______ | ____ | ________ |
| ____________________ | ______ | ____ | ________ |
| ____________________ | ______ | ____ | ________ |

Recommendation: [ ] Proceed  [ ] Proceed after works  [ ] Find another site

Signed: ______________________  Date: ____________
