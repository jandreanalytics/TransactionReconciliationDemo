
# Gift Card Transaction Reconciliation System

![Project Status](https://img.shields.io/badge/status-in_development-yellow)

## Project Overview

This system identifies and analyzes discrepancies between point-of-sale and payment processor gift card transaction data. It demonstrates automated reconciliation techniques, error detection algorithms, and data quality visualization - core capabilities for ensuring financial data integrity in payment systems.

## Key Features

- 🔄 Multi-source transaction reconciliation with 25,000+ transaction volume
- 🔍 Advanced discrepancy detection algorithms across systems
- 📊 Interactive visualization dashboard for error pattern analysis
- 📋 Comprehensive error classification and reporting
- ⚙️ Configurable data quality rules engine

## Dataset Highlights

- **Synthetic Dataset**: Created to simulate both POS and processor sides of transactions (typically not available in a single dataset - especially not in a public context)
- **Transaction Volume**: 25,500 POS / 23,750 processor records (25,984 total after merge)
- **Discrepancy Analysis**:
  - Missing Transactions: 6.8% (1,729 records)
  - Amount Discrepancies: 6.2% (1,592 records)
  - Decimal Shift Errors: 1.8% (464 records)
- **Status**: Successfully processed and reconciled using both local and cloud-based approaches
- **Data Processing**: Implemented with pandas DataFrame operations and proper indexing for performance
- **Quality Control**: Includes automatic error detection and classification with configurable thresholds

## Technical Implementation

### Data Generation

- Synthetic gift card transaction data with industry-standard formats
- 1,000+ unique gift cards with realistic patterns and activation timelines
- Multiple card number formats based on retail industry standards
- POS-to-processor transaction pairing with controlled error scenarios

### Database Implementation

- Separate SQLite databases for POS and processor systems using DB Browser for SQLite:
  - **POS Database**: Contains gift card data (1,000+ records) and transaction data (25,500 records)
  - **Processor Database**: Contains matched processor transactions (23,750 records)
- Optimized with strategic indexes on reconciliation-critical fields:
  - Card ID indexes for relationship tracking
  - Timestamp indexes for temporal analysis
  - Batch ID and reference ID indexes for transaction pairing
- Structured to simulate real-world separation between systems
- SQL query access for advanced reconciliation analysis

### Reconciliation Implementation

- **Python-based reconciliation engine** rather than notebook-based approach for better production readiness
- **Direct AWS S3 data access** using boto3 for cloud-based reconciliation:
  - Reads SQLite databases directly from S3 bucket
  - Avoids local file dependencies for cloud-native operation
- Multi-stage discrepancy detection:
  - Reference-based transaction matching across systems
  - Amount comparison with tolerance thresholds
  - Decimal shift detection algorithms
  - Missing transaction identification
- Results exported as structured CSV for further analysis
- Visual summary charts generated for quick pattern identification

### AWS Integration

- SQLite databases stored in S3 for cloud-based access
- AWS credential management through environment variables
- Cloud-ready architecture demonstrating:
  - S3 for data storage
  - Secure credential handling
  - Cross-system data access patterns
- Production-ready design aligned with AWS best practices
  - Scalable to Redshift implementation
  - Compatible with AWS Glue ETL processes
  - Structured for QuickSight visualization integration

The reconciliation system demonstrates both local processing capabilities and cloud integration patterns that would be implemented in a production environment.

### Error Detection

- Missing transaction identification
- Decimal shift detection
- Timing mismatch analysis
- Double-charge detection
- Amount discrepancy classification

## Project Structure

```
transaction-reconciliation/
├── data/
│   ├── raw/              # Transaction CSVs
│   └── db/               # SQLite databases
├── src/
│   ├── data_generation/  # Data simulation
│   ├── reconciliation/   # Core logic
│   └── visualization/    # Reporting dashboards
└── dashboards/           # Tableau workbooks
```

## Development Approach

This project was developed using a research-based approach:

1. **Research**: Analyzed real gift card formats, transaction patterns, and reconciliation challenges from industry documentation and retail examples
2. **Design**: Created data models that reflect actual financial system structures
3. **Implementation**: Built synthetic data generation with realistic error patterns
4. **Validation**: Ensured accuracy of financial calculations and reconciliation logic

### Development Methodology & Data Privacy

This project leverages modern development tools while focusing on core data quality principles:

- **Tool-assisted data generation**: GitHub Copilot was used to accelerate generation of synthetic test data and random patterns - areas outside the core focus of data reconciliation but necessary for demonstration purposes
- **Manual implementation of core logic**: The reconciliation algorithms, error detection patterns, and quality control mechanisms were manually implemented to ensure proper understanding of financial data integrity principles
- **Industry-focused approach**: The data generation serves only as a means to demonstrate the reconciliation capabilities, which are the true focus of this project and more aligned with real-world data quality analysis

All data is completely synthetic and programmatically generated. No transaction data of any kind was ever shared with AI tools - AI assistance was strictly limited to code implementation patterns while maintaining strict data privacy standards.

## License

MIT License

---

*This project demonstrates payment reconciliation and data quality techniques for financial transaction systems.*
