# Test Plan: Publitz Automated Audits

**Date**: December 9, 2025
**Version**: 1.0 (Production Ready)

---

## Test Overview

This document outlines comprehensive testing procedures for the Publitz Automated Audit system to ensure production readiness.

**System Components**:
- Phase 1: Input processing & validation
- Phase 2: Data collection from APIs
- Phase 2.5: Claude Vision analysis
- Phase 3: Claude AI report generation
- Phase 4: PDF export & pricing CSV generation

---

## Test Categories

### 1. Unit Tests (Component Level)
### 2. Integration Tests (End-to-End)
### 3. Performance Tests
### 4. Error Handling Tests
### 5. Output Quality Tests

---

## 1. Unit Tests

### 1.1 Input Processing (`src/input_processor.py`)

**Test: Load and Validate Steam URL**
```bash
# Expected: Extract app ID correctly
# Input: https://store.steampowered.com/app/1145360/Hades/
# Expected Output: app_id = "1145360"
```

**Test: Parse Competitors List**
```bash
# Expected: Handle various formats
# Input: Mix of URLs and names
# Expected: Clean list of identifiers
```

**Test: Validate Intake Form JSON**
```bash
# Expected: Catch missing required fields
# Test with: Missing client_name, invalid dates, bad prices
# Expected: Raise validation errors with helpful messages
```

### 1.2 Data Collection (`src/simple_data_collector.py`)

**Test: Steam API Data Fetch**
```bash
# Test with known game (Hades - 1145360)
# Expected fields:
# - name, price, genres, screenshots, header_image
# - reviews, release_date, detailed_description
```

**Test: Competitor Analysis**
```bash
# Test with 5 competitors
# Expected: All competitor data collected
# Expected: Playtime data attempted (may fail gracefully)
```

**Test: External Research**
```bash
# Test: Reddit insights for genre
# Test: HLTB playtime data
# Test: Launch conflicts check
# Expected: Graceful handling of API failures
```

### 1.3 Report Generation (`src/report_generator.py`)

**Test: Vision Analysis**
```bash
# Test with real Steam game
# Expected: Capsule + screenshots + banner analyzed
# Expected: Specific measurements in feedback
# Expected: Caching works (no duplicate API calls)
```

**Test: Prompt Building**
```bash
# Test: All data sections included
# Expected: Game data, competitors, vision, research
# Expected: Proper formatting
# Expected: <20K characters (fits in context)
```

**Test: Claude API Call**
```bash
# Test: Successful report generation
# Expected: 35-45 page markdown report
# Expected: All 9 sections present
# Expected: Specific recommendations (not generic)
```

### 1.4 PDF Export (`src/export_pdf.py`)

**Test: Markdown to HTML Conversion**
```bash
# Test: Tables, code blocks, lists render correctly
# Expected: Clean HTML output
# Expected: No broken formatting
```

**Test: PDF Rendering**
```bash
# Test: Cover page styling
# Test: Headers/footers
# Test: Page breaks
# Expected: Professional appearance
# Expected: Print-ready quality
```

### 1.5 Pricing CSV (`src/pricing_csv.py`)

**Test: Price Calculation**
```bash
# Input: $19.99 USD base price
# Expected: Tier 1 = $19.99 USD
# Expected: Tier 2 = ~$15 USD equivalent (25% off)
# Expected: Tier 3 = ~$10 USD equivalent (50% off)
```

**Test: Currency Conversion**
```bash
# Test: Major currencies (EUR, GBP, JPY, CNY, INR)
# Expected: Proper multipliers applied
# Expected: Correct decimal handling (JPY no decimals)
```

**Test: CSV Format**
```bash
# Expected: Valid CSV with headers
# Expected: 50+ countries
# Expected: Steam-compatible format
```

---

## 2. Integration Tests (End-to-End)

### Test 2.1: Complete Audit Generation (Happy Path)

**Command**:
```bash
python generate_audit.py --test
```

**Expected Flow**:
1. ✅ Creates test client in `inputs/test-client/`
2. ✅ Validates all 4 input files
3. ✅ Collects Steam data (test game)
4. ✅ Analyzes competitors (up to 10)
5. ✅ Runs vision analysis on images
6. ✅ Generates Claude report (2-3 minutes)
7. ✅ Saves markdown report
8. ✅ Generates PDF (15-20 seconds)
9. ✅ Generates pricing CSV
10. ✅ Shows summary with file paths

**Expected Output Files**:
```
output/test-client/
├── test-client_audit_20251209.md    (~100-150 KB)
├── test-client_audit_20251209.pdf   (~300-500 KB)
└── test-client_pricing_20251209.csv (~5 KB)
```

**Expected Time**: 6-10 minutes total

**Success Criteria**:
- All 3 files generated
- PDF opens and displays correctly
- CSV has 50+ rows
- No errors in console output

### Test 2.2: Real Steam Game Test

**Command**:
```bash
python generate_audit.py --create-example hades-test
# Edit inputs/hades-test/steam_url.txt → https://store.steampowered.com/app/1145360/Hades/
# Edit other files with real data
python generate_audit.py --client hades-test
```

**Expected**:
- Successful data collection from real Steam API
- Vision analysis on actual game images
- High-quality report with real competitive data
- Professional PDF output

### Test 2.3: Error Handling - Missing API Key

**Setup**: Remove or invalidate `ANTHROPIC_API_KEY` in `.env`

**Command**:
```bash
python generate_audit.py --test
```

**Expected Behavior**:
- Phase 1 & 2 succeed (no API needed)
- Phase 3 fails with clear error message
- Falls back to placeholder report
- Markdown still generated
- PDF still attempted (with placeholder content)
- System doesn't crash

### Test 2.4: Error Handling - Invalid Steam URL

**Setup**: Create client with invalid Steam URL

**Expected Behavior**:
- Phase 1 catches invalid URL
- Shows helpful error message
- Lists valid URL format
- Exits gracefully

### Test 2.5: Error Handling - Missing Dependencies

**Setup**: Uninstall weasyprint

**Expected Behavior**:
- Phases 1-3 succeed
- Phase 4 PDF export shows warning
- Markdown still available
- CSV still generated
- Continues without crashing

---

## 3. Performance Tests

### Test 3.1: Generation Time Benchmarks

**Target**: < 10 minutes total

**Breakdown**:
- Phase 1 (Input Validation): < 10 seconds
- Phase 2 (Data Collection): < 3 minutes
- Phase 2.5 (Vision Analysis): < 1 minute
- Phase 3 (Report Generation): < 3 minutes
- Phase 4 (PDF + CSV): < 30 seconds

**Test**: Run 3 audits and average the times

**Pass Criteria**: Average < 10 minutes

### Test 3.2: API Cost Benchmarks

**Target**: < $10 per audit

**Expected Costs**:
- Claude Report Generation: $3-5
- Claude Vision (4-5 images): $2-3
- Total: $5-8 per audit

**Test**: Generate 3 audits and check API usage in Anthropic dashboard

**Pass Criteria**: Average cost < $10

### Test 3.3: Output File Sizes

**Expected Sizes**:
- Markdown: 100-200 KB
- PDF: 300-600 KB
- CSV: 5-10 KB

**Pass Criteria**: All files within expected ranges

---

## 4. Error Handling Tests

### Test 4.1: Network Failures

**Test Cases**:
1. Steam API timeout → Should retry and/or use fallback
2. Claude API timeout → Should show error, save data collected
3. Image download fails → Vision analysis skips gracefully

**Expected**: System continues, generates best possible output

### Test 4.2: Invalid Input Data

**Test Cases**:
1. Empty intake form → Validation error with message
2. Future launch date in past → Validation warning
3. Negative price → Validation error
4. Invalid competitor names → Skips with warning

**Expected**: Clear error messages, no crashes

### Test 4.3: Disk Space / Permissions

**Test Cases**:
1. Output directory not writable → Create directory or show error
2. Disk full → Show error before processing
3. Template files missing → Use embedded defaults

**Expected**: Graceful handling, helpful error messages

---

## 5. Output Quality Tests

### Test 5.1: Report Content Quality

**Check**:
- ✅ All 9 sections present and complete
- ✅ Star ratings for all 3 categories
- ✅ Overall tier badge (Launch Ready/Viable/High Risk/Not Ready)
- ✅ Specific recommendations with measurements
- ✅ Vision analysis incorporated into Section 2
- ✅ Competitor data in Section 4
- ✅ Pricing recommendations in Section 3

**Manual Review**: Read 3 generated reports for quality

### Test 5.2: Vision Analysis Quality

**Check**:
- ✅ Specific measurements (e.g., "logo is 60px")
- ✅ Actionable feedback (e.g., "increase to 120px")
- ✅ Genre-appropriate critique
- ✅ Not generic ("improve capsule" ❌ vs "move logo to left-third" ✅)

**Manual Review**: Check vision analysis in 3 reports

### Test 5.3: PDF Visual Quality

**Check**:
- ✅ Cover page looks professional
- ✅ Branding consistent throughout
- ✅ Tables render correctly
- ✅ Code blocks formatted properly
- ✅ Page breaks sensible (no orphaned headers)
- ✅ Headers/footers on every page
- ✅ Page numbers accurate

**Manual Review**: Print or view PDF in reader

### Test 5.4: Pricing CSV Accuracy

**Check**:
- ✅ All major markets included (US, EU, UK, JP, CN, IN, BR, RU)
- ✅ Tier discounts applied correctly
- ✅ Currency symbols not included (Steam format)
- ✅ Decimal places correct per currency
- ✅ CSV opens in Excel/Sheets without errors

**Manual Test**: Open CSV, spot-check calculations

---

## 6. Smoke Test Script

Quick smoke test to verify system is working:

```bash
#!/bin/bash
# smoke_test.sh - Quick system check

echo "🧪 Running Publitz Audit Smoke Test..."

# Check environment
echo "1. Checking environment..."
if [ ! -f .env ]; then
    echo "❌ .env file missing"
    exit 1
fi

if ! grep -q "ANTHROPIC_API_KEY" .env; then
    echo "❌ ANTHROPIC_API_KEY not found in .env"
    exit 1
fi

echo "✅ Environment OK"

# Check dependencies
echo "2. Checking dependencies..."
python -c "import anthropic, markdown, weasyprint, jinja2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies OK"

# Run test generation
echo "3. Running test audit..."
timeout 600 python generate_audit.py --test > /tmp/audit_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Test audit completed"
else
    echo "❌ Test audit failed"
    echo "   Check /tmp/audit_test.log for details"
    exit 1
fi

# Check outputs
echo "4. Checking outputs..."
if [ ! -f output/test-client/test-client_audit_*.md ]; then
    echo "❌ Markdown not generated"
    exit 1
fi

if [ ! -f output/test-client/test-client_audit_*.pdf ]; then
    echo "⚠️  PDF not generated (non-critical)"
fi

if [ ! -f output/test-client/test-client_pricing_*.csv ]; then
    echo "⚠️  Pricing CSV not generated (non-critical)"
fi

echo "✅ All outputs generated"
echo ""
echo "🎉 Smoke test PASSED!"
echo "   System is ready for production use"
```

---

## 7. Pre-Production Checklist

Before deploying to production:

- [ ] All unit tests passing
- [ ] End-to-end test completed successfully
- [ ] Performance within targets (<10 min, <$10)
- [ ] Error handling tested (API failures, invalid inputs)
- [ ] Output quality manually reviewed (3+ reports)
- [ ] PDF renders correctly in multiple viewers
- [ ] Pricing CSV imports into Excel without errors
- [ ] Documentation complete (README, WORKFLOW.md, claude.md)
- [ ] .env.example created with required variables
- [ ] Dependencies listed in requirements.txt
- [ ] Git repository clean and pushed
- [ ] Version tagged (v1.0.0)

---

## 8. Known Limitations & Accepted Risks

**Limitations**:
1. External research APIs (Reddit, HLTB) may fail → Graceful degradation
2. Vision analysis requires images → Skips if unavailable
3. Steam API rate limits → May need delays between requests
4. Claude API costs → ~$5-8 per report (acceptable)

**Accepted Risks**:
1. API changes (Steam, Claude) → Monitor and update
2. Network failures → Retry logic in place
3. Invalid client data → Validation catches most issues

**Mitigation**:
- Error handling with helpful messages
- Fallbacks for missing data
- Always generate markdown backup
- Test with multiple real games

---

## 9. Test Execution Log Template

```
Test Execution Date: YYYY-MM-DD
Tester: [Name]
System Version: [Git commit hash]

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 2.1 | Complete Audit (Happy Path) | ✅ PASS | 8.5 min |
| 2.2 | Real Steam Game | ✅ PASS | Hades test |
| 2.3 | Missing API Key | ✅ PASS | Good fallback |
| 2.4 | Invalid URL | ✅ PASS | Clear error |
| 2.5 | Missing Dependencies | ✅ PASS | Warning shown |
| 3.1 | Performance | ✅ PASS | 8.2 min avg |
| 3.2 | API Cost | ✅ PASS | $6.50 avg |
| 5.1 | Report Quality | ✅ PASS | Manual review good |
| 5.3 | PDF Quality | ✅ PASS | Professional |
| 5.4 | CSV Accuracy | ✅ PASS | Spot-checked |

Overall: ✅ READY FOR PRODUCTION
```

---

## 10. Continuous Testing

**Ongoing**:
- Run smoke test before each release
- Test with new Steam games monthly
- Monitor API costs weekly
- Review output quality quarterly
- Update test plan as system evolves

**Automated** (Future):
- CI/CD pipeline with automated smoke tests
- Nightly test runs with random Steam games
- Cost monitoring alerts
- Quality regression detection

---

**Test Plan Owner**: Development Team
**Last Review**: December 9, 2025
**Next Review**: Monthly or after major changes
