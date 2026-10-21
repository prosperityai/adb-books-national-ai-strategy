## Compute plan: Example Republic, mid-size: 60k civil servants

ILLUSTRATIVE. Fictional country used throughout the book.

### Demand

| Stream | Interactions/day | Avg output tok/s | Peak output tok/s |
|---|---|---|---|
| Civil-service assistant | 360,000 | 5,000 | 15,000 |
| Citizen services (web, SMS, voice) | 150,000 | 651 | 1,953 |

### Capacity

| Pool | Peak tok/s | Tok/s per GPU | Raw GPUs | GPUs + headroom | Servers (N+1) | Installed GPUs |
|---|---|---|---|---|---|---|
| 30B-class | 13,953 | 1,500 | 9.3 | 13 | 3 | 24 |
| 120B-class | 3,000 | 700 | 4.3 | 6 | 2 | 16 |
| Research and fine-tuning | - | - | 27.4 | 28 | 4 | 32 |
| **Total** |  |  |  | 47 | 9 | 72 |

### Power

| Measure | Value |
|---|---|
| IT load (kW) | 101 |
| Facility load at PUE 1.5 (kW) | 151 |
| Annual energy (MWh) | 1,062 |

### Cost and 5-year TCO (USD)

| Item | Amount |
|---|---|
| Capex: GPU servers | $3.60M |
| Capex: Networking | $540,000 |
| Capex: Storage | $150,000 |
| Capex: Facility fit-out | $1.01M |
| **Total capex** | **$5.30M** |
| Opex per year: Electricity | $127,380 |
| Opex per year: Maintenance and spares | $343,200 |
| Opex per year: Software licences | $0 |
| Opex per year: Engineering staff | $360,000 |
| Opex per year: Connectivity | $120,000 |
| **Total opex per year** | **$950,580** |
| **5-year TCO** | **$10.05M** |

### Build versus rent at 60% utilisation

| Option | List $/GPU-h | 5-year cost | $ per useful GPU-h | Owning wins above |
|---|---|---|---|---|
| Own (this plan) | - | $10.05M | $5.31 | - |
| Neocloud on-demand | $4.00 | $7.57M | $4.00 | 80% |
| Hyperscaler on-demand | $6.88 | $13.02M | $6.88 | 46% |

### Talent

| Measure | Value |
|---|---|
| Installed GPUs | 72 |
| Engineers needed to operate | 6 |

### Sensitivity to GPU throughput

| Throughput x | Inference GPUs | Installed GPUs | Capex | 5-year TCO |
|---|---|---|---|---|
| 0.5 | 64 | 96 | $7.02M | $12.53M |
| 1 | 40 | 72 | $5.30M | $10.05M |
| 2 | 32 | 64 | $4.73M | $9.23M |
| 6 | 32 | 64 | $4.73M | $9.23M |

## Compute plan: Regional research hub

ILLUSTRATIVE. A hub serving universities and agencies in several countries.

### Demand

| Stream | Interactions/day | Avg output tok/s | Peak output tok/s |
|---|---|---|---|
| University and agency assistant | 200,000 | 2,315 | 5,787 |
| Partner-country API (startups and agencies) | 500,000 | 2,894 | 5,787 |

### Capacity

| Pool | Peak tok/s | Tok/s per GPU | Raw GPUs | GPUs + headroom | Servers (N+1) | Installed GPUs |
|---|---|---|---|---|---|---|
| 30B-class | 7,523 | 1,500 | 5.0 | 7 | 2 | 16 |
| 120B-class | 4,051 | 700 | 5.8 | 8 | 2 | 16 |
| Research and fine-tuning | - | - | 440.3 | 441 | 56 | 448 |
| **Total** |  |  |  | 456 | 60 | 480 |

### Power

| Measure | Value |
|---|---|
| IT load (kW) | 673 |
| Facility load at PUE 1.35 (kW) | 909 |
| Annual energy (MWh) | 6,369 |

### Cost and 5-year TCO (USD)

| Item | Amount |
|---|---|
| Capex: GPU servers | $24.00M |
| Capex: Networking | $3.60M |
| Capex: Storage | $1.20M |
| Capex: Facility fit-out | $6.73M |
| **Total capex** | **$35.53M** |
| Opex per year: Electricity | $764,281 |
| Opex per year: Maintenance and spares | $2.30M |
| Opex per year: Software licences | $0 |
| Opex per year: Engineering staff | $2.10M |
| Opex per year: Connectivity | $400,000 |
| **Total opex per year** | **$5.57M** |
| **5-year TCO** | **$63.37M** |

### Build versus rent at 60% utilisation

| Option | List $/GPU-h | 5-year cost | $ per useful GPU-h | Owning wins above |
|---|---|---|---|---|
| Own (this plan) | - | $63.37M | $5.02 | - |
| Neocloud on-demand | $4.00 | $50.46M | $4.00 | 75% |
| Hyperscaler on-demand | $6.88 | $86.79M | $6.88 | 44% |

### Talent

| Measure | Value |
|---|---|
| Installed GPUs | 480 |
| Engineers needed to operate | 15 |

### Sensitivity to GPU throughput

| Throughput x | Inference GPUs | Installed GPUs | Capex | 5-year TCO |
|---|---|---|---|---|
| 0.5 | 48 | 496 | $36.68M | $65.71M |
| 1 | 32 | 480 | $35.53M | $63.37M |
| 2 | 32 | 480 | $35.53M | $63.37M |
| 6 | 32 | 480 | $35.53M | $63.37M |
