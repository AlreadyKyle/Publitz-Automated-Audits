# 🏗️ BUILD ORDER - Implementation Sequence

## Why This Order?

**Principle**: Fix data quality FIRST, then improve AI, then polish UX.

**Reason**: The multi-pass AI system depends on good input data. If competitors are wrong and revenue is off, even the best AI prompts won't help.

---

## PHASE 1: Data Quality Foundations (3 hours)

**Why First**: These fixes improve EVERYTHING else downstream.

### 1.1 Fix Competitor Matching (1.5 hours)
**Priority**: CRITICAL - Wrong competitors ruin entire report
**Location**: `src/game_search.py`

**Tasks**:
- [ ] Add genre-based scoring system
- [ ] Filter out wrong types (F2P vs paid, multiplayer vs single-player)
- [ ] Weight factors: Genre (40pts) > Tags (5pts each) > Price (20pts) > Release window (10pts)
- [ ] Add exclusion rules (F2P shooters shouldn't match paid roguelikes)

**Test**: Run Hades 2 again, verify competitors are all roguelikes/action games, not shooters

**Files to modify**:
```
src/game_search.py:
- find_competitors() - add scoring
- _find_by_tag() - add filtering
- _find_by_genre() - improve weighting
```

**Validation**:
```python
# Test cases
test_hades_2()  # Should get: Hades, Dead Cells, Risk of Rain
test_stardew()  # Should get: Terraria, farming sims
test_among_us() # Should get: social deduction games
```

---

### 1.2 Improve Revenue Calculations (1 hour)
**Priority**: HIGH - Revenue is key metric
**Location**: `src/steamdb_scraper.py`

**Tasks**:
- [ ] Add review-count method (1 review ≈ 50-100 sales)
- [ ] Add confidence ranges (low, mid, high)
- [ ] Add multiplier for highly-rated games (>90% = 1.5x)
- [ ] Combine SteamSpy + review estimates

**Test**: Hades 2 with 50k reviews should show $5M-$20M range, not $500k

**Files to modify**:
```
src/steamdb_scraper.py:
- get_sales_data() - add enhanced calculation
- _calculate_review_based_estimate() - NEW method
- _get_confidence_range() - NEW method
```

---

### 1.3 Add Success Detection (30 min)
**Priority**: HIGH - Context for AI prompts
**Location**: `src/game_search.py` (new utility)

**Tasks**:
- [ ] Create success scoring function
- [ ] Detect: reviews > 10k = strong engagement
- [ ] Detect: review_score > 85% = very successful
- [ ] Detect: owners > 1M = hit game

**Test**: Hades 2 should be flagged as "highly successful"

**Files to create**:
```
src/game_analyzer.py:
- analyze_success_level(game_data) - NEW
- get_performance_context(game_data) - NEW
```

---

## PHASE 2: UX Polish (1 hour)

**Why Second**: Independent of data quality, quick wins.

### 2.1 Disable Button During Generation (10 min)
**Priority**: HIGH - Prevents user errors
**Location**: `app.py`

**Tasks**:
- [ ] Add `st.session_state.generating` flag
- [ ] Disable button when generating
- [ ] Re-enable after completion

**Files to modify**:
```
app.py:
- Line 84: Add disabled parameter to button
- Line 95: Set generating=True
- Line 193: Set generating=False
```

---

### 2.2 Add Loading Spinners (15 min)
**Priority**: MEDIUM - Better UX feedback
**Location**: `app.py`

**Tasks**:
- [ ] Replace progress_bar with st.spinner for each step
- [ ] Add descriptive messages
- [ ] Keep progress bar but add spinners too

**Files to modify**:
```
app.py:
- Lines 111-151: Wrap each step with st.spinner()
```

---

### 2.3 Move Download Button to Top (10 min)
**Priority**: MEDIUM - Better accessibility
**Location**: `app.py`

**Tasks**:
- [ ] Add download section at top of results
- [ ] Keep download at bottom too
- [ ] Make top one more prominent

**Files to modify**:
```
app.py:
- Line 205: Add download section after metrics
```

---

### 2.4 Add "Generating" State to Button (5 min)
**Priority**: LOW - Visual feedback
**Location**: `app.py`

**Tasks**:
- [ ] Change button text while generating
- [ ] Show "Generating..." instead of "Generate Audit Report"

**Files to modify**:
```
app.py:
- Line 84: Dynamic button text based on state
```

---

## PHASE 3: Multi-Pass AI System (2 hours)

**Why Third**: Now data is clean, AI can analyze accurately.

### 3.1 Implement Draft Generator (30 min)
**Priority**: CRITICAL - Foundation of multi-pass
**Location**: `src/ai_generator.py`

**Tasks**:
- [ ] Create `_generate_initial_draft()` method
- [ ] Use 5k tokens, temperature 0.5
- [ ] Focus on speed
- [ ] Basic analysis only

**Files to modify**:
```
src/ai_generator.py:
- _generate_initial_draft() - NEW method
- Simplified prompt for first pass
```

---

### 3.2 Implement Self-Audit (45 min)
**Priority**: CRITICAL - The innovation
**Location**: `src/ai_generator.py`

**Tasks**:
- [ ] Create `_audit_report()` method
- [ ] Check for wrong competitors
- [ ] Check revenue accuracy
- [ ] Check success recognition
- [ ] Output JSON with issues
- [ ] Parse audit results

**Files to modify**:
```
src/ai_generator.py:
- _audit_report() - NEW method
- Audit prompt with checklist
- JSON parsing
```

---

### 3.3 Implement Enhanced Final Report (30 min)
**Priority**: CRITICAL - Final pass
**Location**: `src/ai_generator.py`

**Tasks**:
- [ ] Create `_generate_enhanced_report()` method
- [ ] Apply audit corrections
- [ ] Add success context
- [ ] Use 16k tokens for full detail
- [ ] Better prompts with guidelines

**Files to modify**:
```
src/ai_generator.py:
- _generate_enhanced_report() - NEW method
- Enhanced prompt with corrections
```

---

### 3.4 Wire Up 3-Pass System (15 min)
**Priority**: CRITICAL - Integration
**Location**: `src/ai_generator.py` and `app.py`

**Tasks**:
- [ ] Create `generate_report_with_audit()` method
- [ ] Orchestrate 3 passes
- [ ] Return final report + audit results
- [ ] Update app.py to use new method

**Files to modify**:
```
src/ai_generator.py:
- generate_report_with_audit() - NEW orchestrator

app.py:
- Line 164: Call new method instead of old
- Show 3 progress steps
```

---

## PHASE 4: PDF Export (1 hour)

**Why Fourth**: Independent feature, nice to have.

### 4.1 Add PDF Generation (45 min)
**Priority**: MEDIUM - User request
**Location**: `src/pdf_generator.py` (NEW)

**Tasks**:
- [ ] Create PDF generation module
- [ ] Use reportlab or markdown-pdf
- [ ] Professional styling
- [ ] Add Publitz branding

**Files to create**:
```
src/pdf_generator.py:
- generate_pdf(markdown_content, game_name) - NEW
```

**Files to modify**:
```
requirements.txt:
- Add: reportlab>=4.0.0 or markdown-pdf>=2.0.0

app.py:
- Add PDF download button next to Markdown
```

---

### 4.2 Test PDF Export (15 min)
**Priority**: MEDIUM
**Location**: Test locally

**Tasks**:
- [ ] Generate PDF for test report
- [ ] Verify formatting
- [ ] Check file size
- [ ] Test download

---

## PHASE 5: Testing & Validation (2 hours)

**Why Last**: Validate all improvements work together.

### 5.1 Create Test Suite (30 min)
**Priority**: HIGH - Ensure quality
**Location**: `test_report_quality.py` (NEW)

**Tasks**:
- [ ] Test 5 diverse games
- [ ] Compare old vs new quality
- [ ] Validate competitor accuracy
- [ ] Check revenue ranges
- [ ] Verify no false negatives

**Files to create**:
```
test_report_quality.py:
- test_hades_2() - roguelike
- test_stardew_valley() - farming sim
- test_baldurs_gate_3() - CRPG
- test_among_us() - social deduction
- test_elden_ring() - souls-like
```

---

### 5.2 Quality Comparison (30 min)
**Priority**: HIGH - Measure improvement
**Location**: Manual testing

**Tasks**:
- [ ] Generate report for Hades 2 (before improvements)
- [ ] Generate report for Hades 2 (after improvements)
- [ ] Compare accuracy scores
- [ ] Document improvements

**Metrics to track**:
```
- Competitor accuracy: X/10 correct
- Revenue accuracy: Within Y% of actual
- False negatives: Count
- Generation time: Seconds
- User satisfaction: Rating
```

---

### 5.3 Edge Case Testing (30 min)
**Priority**: MEDIUM - Robustness
**Location**: Various games

**Tasks**:
- [ ] Test F2P game
- [ ] Test early access game
- [ ] Test brand new release
- [ ] Test old classic game
- [ ] Test indie vs AAA

---

### 5.4 Deploy to Production (30 min)
**Priority**: HIGH - Go live
**Location**: Streamlit Cloud

**Tasks**:
- [ ] Commit all changes
- [ ] Push to branch
- [ ] Test on Streamlit Cloud
- [ ] Monitor logs
- [ ] Verify working

---

## SUMMARY: Complete Implementation Timeline

| Phase | Time | Priority | Dependencies |
|-------|------|----------|--------------|
| **Phase 1: Data Quality** | 3 hours | CRITICAL | None |
| 1.1 Competitor Matching | 1.5 hr | Critical | None |
| 1.2 Revenue Calculations | 1 hr | High | None |
| 1.3 Success Detection | 0.5 hr | High | None |
| **Phase 2: UX Polish** | 1 hour | HIGH | None |
| 2.1 Disable Button | 0.2 hr | High | None |
| 2.2 Loading Spinners | 0.25 hr | Medium | None |
| 2.3 Download Position | 0.2 hr | Medium | None |
| 2.4 Button State | 0.1 hr | Low | None |
| **Phase 3: Multi-Pass AI** | 2 hours | CRITICAL | Phase 1 |
| 3.1 Draft Generator | 0.5 hr | Critical | None |
| 3.2 Self-Audit | 0.75 hr | Critical | 3.1 |
| 3.3 Enhanced Final | 0.5 hr | Critical | 3.2 |
| 3.4 Integration | 0.25 hr | Critical | 3.1-3.3 |
| **Phase 4: PDF Export** | 1 hour | MEDIUM | None |
| 4.1 PDF Generation | 0.75 hr | Medium | None |
| 4.2 PDF Testing | 0.25 hr | Medium | 4.1 |
| **Phase 5: Validation** | 2 hours | HIGH | All above |
| 5.1 Test Suite | 0.5 hr | High | All |
| 5.2 Quality Check | 0.5 hr | High | All |
| 5.3 Edge Cases | 0.5 hr | Medium | All |
| 5.4 Deploy | 0.5 hr | High | All |
| **TOTAL** | **9 hours** | | |

---

## Recommended Schedule

### Day 1 (4 hours): Data Quality + UX
- ✅ Morning: Phase 1 - Data Quality (3 hours)
- ✅ Afternoon: Phase 2 - UX Polish (1 hour)
- **Deliverable**: Better data, better UX

### Day 2 (3 hours): Multi-Pass AI
- ✅ Morning: Phase 3 - Multi-Pass System (2 hours)
- ✅ Afternoon: Quick testing (1 hour)
- **Deliverable**: Self-correcting AI reports

### Day 3 (2 hours): Export + Validation
- ✅ Morning: Phase 4 - PDF Export (1 hour)
- ✅ Afternoon: Phase 5 - Full validation (1 hour)
- **Deliverable**: Production-ready system

---

## Critical Path

**Must do in order**:
1. Phase 1 (Data Quality) → BLOCKS Phase 3
2. Phase 3 (Multi-Pass AI) → DEPENDS ON Phase 1
3. Phase 5 (Validation) → DEPENDS ON All

**Can do anytime** (independent):
- Phase 2 (UX Polish)
- Phase 4 (PDF Export)

---

## Next Action: START PHASE 1.1

Should I begin with **Phase 1.1: Fix Competitor Matching**?

This is the foundation that makes everything else better. I'll implement the genre-based scoring system and filtering rules.

Ready to start? 🚀
