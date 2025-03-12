
# Gift Card Transaction Reconciliation System

![Project Status](https://img.shields.io/badge/status-in_development-yellow)

## Project Overview

This system identifies and analyzes discrepancies between point-of-sale and payment processor gift card transaction data. It demonstrates automated reconciliation techniques, error detection algorithms, and data quality visualization - core capabilities for ensuring financial data integrity in payment systems.

## Case Study Context

This project demonstrates my approach to financial data quality and reconciliation, developed as part of a technical interview process. It showcases my ability to:

- Design and implement data quality controls
- Build effective data visualization dashboards
- Handle complex financial reconciliation scenarios
- Work with AWS cloud architecture

## Key Results

- Successfully processed 25,984 transactions
- Achieved 81.81% automated match rate
- Identified $4,807.16 in net discrepancies
- Reduced analysis time through pattern detection
- Built scalable Python reconciliation engine

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

## Technical Stack

- **Python**: Core reconciliation engine
- **Pandas**: Data processing and analysis
- **SQLite**: Local database simulation
- **AWS S3**: Cloud storage integration
- **Tableau**: Data visualization
- **Git**: Version control

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

### AWS Implementation Notes

This project demonstrates AWS integration concepts through S3 connectivity while simulating more advanced AWS services that would be cost-prohibitive in a demonstration context:

- **Implemented**: Direct S3 integration for data storage and retrieval
- **Simulated**: Redshift data warehousing using SQLite with similar schema design
- **Simulated**: QuickSight visualizations using Tableau/local visualization tools
- **Designed for**: Easy migration to full AWS stack in a production environment

The reconciliation system is architected to seamlessly transition to enterprise AWS services while avoiding unnecessary costs during development.

### Error Detection

- Missing transaction identification
- Decimal shift detection
- Timing mismatch analysis
- Double-charge detection
- Amount discrepancy classification

### Operational Details

- **Local/Cloud Flexibility**: System operates with both local SQLite files and AWS S3 storage:

  - Local mode for development and testing
  - S3 integration for cloud deployment readiness
  - Automatic fallback if cloud access is unavailable
- **Performance Metrics**:

  - Successfully processed 25,984 total records
  - Average processing time: < 5 seconds
  - Memory efficient with batched processing
  - Pandas operations optimized for large datasets
- **Reconciliation Results**:

  - Successfully matched 86% of transactions across systems
  - Identified 1,729 missing processor records (6.8%)
  - Detected 1,592 amount discrepancies (6.2%)
  - Found 464 decimal shift errors (1.8%)
  - Net financial difference: $3,345.59

### Next Development Phase

- Tableau dashboard development
- Trend analysis implementation
- Automated testing suite
- Advanced error pattern detection

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

All data is completely synthetic and programmatically generated. No transaction data of any kind was ever shared with AI tools - AI assistance was strictly limited to helping format SQL and Python queries, with all generated code being rigorously reviewed and validated before implementation. Even though the data was synthetic, maintaining proper data handling practices was a key priority.

## Dashboard Implementation

### Dashboard 1: Executive Overview

Primary audience: Leadership and daily monitoring

KPI Cards:

- **Match Rate**: 81.81%

  * Below target threshold (85%)
  * Requires immediate attention
- **Net Difference**: -$4,807.16

  * Daily average: -$155
  * Processor showing more money than POS
- **Transaction Volume**: 25,984

  * Up 16.07% from last week
  * Strong volume increase
- **Error Count**: 4,726 (18.72% of total)

  * Above acceptable threshold (15%)
  * High priority for investigation

Key Visualizations:

1. **Discrepancy Distribution**

   * Horizontal stacked bars by error type
   * Shows relative proportions of each error
   * Matched: 81.81%
   * Missing in Processor: 6.65%
   * Amount Discrepancies: 4.34%
   * Decimal Shifts: 7.19%
2. **Error Type Composition**

   * Pie chart showing error breakdown
   * Excludes matched transactions
   * Hover for detailed percentages
   * Color-coded by severity
3. **Amount Range Analysis**

   * Bar chart grouping by amount brackets
   * Shows error concentration in each range
   * Identifies high-risk transaction amounts
   * Highlights decimal shift patterns
4. **Error Heatmap**

   * Shows error frequency by day/hour
   * Darker colors = more errors
   * Helps identify timing patterns

Interactivity:

- Date range filter (Last 30 days default)
- Error type filtering
- Cross-filtering between charts
- Hover tooltips with details

### Dashboard 2: Detailed Analysis

Primary audience: Analysts and investigation teams

- **Error Impact Scorecard**

  * Detailed breakdown by error type
  * Financial impact quantification
  * Volume and percentage analysis
- **Transaction Type Analysis (Treemap)**

  * Hierarchical view of transaction categories
  * Size represents transaction volume
  * Color intensity shows error rate
  * Interactive tooltips with detailed metrics
- **Hourly Error Distribution**

  * Time-based pattern visualization
  * Day of week vs hour of day analysis
  * Heat map showing error concentrations
  * Helps identify systematic timing issues

The two-dashboard approach separates strategic overview from tactical analysis, improving both user experience and system performance.

## Project Background & Problem Statement

This case study addresses a common challenge in payment systems: reconciling gift card transactions between Point-of-Sale (POS) systems and payment processors. Key issues include:

- Missing transactions between systems
- Amount discrepancies and decimal shift errors
- Timing mismatches in transaction recording
- Double-charge scenarios
- Complex matching requirements

## Key Achievements

1. **Error Detection Success**

   - Identified $4,807.16 in net discrepancies
   - Detected 464 decimal shift errors (saving $4,640 in potential losses)
   - Reduced investigation time through pattern recognition
2. **Performance Metrics**

   - 25,984 transactions processed in under 5 seconds
   - 81.81% automated match rate
   - 18.72% error rate with clear categorization
3. **Technical Implementation**

   - Built scalable Python reconciliation engine
   - Implemented cloud-ready AWS architecture
   - Created dual-dashboard visualization strategy

## Use Case Scenarios

1. **Daily Reconciliation**

   - Morning review of previous day's transactions
   - Immediate flagging of critical discrepancies
   - Automated pattern detection
2. **Error Investigation**

   - Drill-down capability for analysts
   - Pattern identification across terminals
   - Root cause analysis tools
3. **Management Reporting**

   - Executive dashboard for KPIs
   - Trend analysis and pattern detection
   - Financial impact quantification

## Design Philosophy

The project follows these core principles:

1. **Data Quality First**: Rigorous validation and error detection
2. **User-Centric Design**: Separate views for different user needs
3. **Actionable Insights**: Focus on patterns that drive improvements
4. **Performance Optimized**: Fast processing for large transaction volumes

## License

MIT License

---

*This project demonstrates payment reconciliation and data quality techniques for financial transaction systems.*
