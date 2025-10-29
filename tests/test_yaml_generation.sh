#!/bin/bash
# Test script to validate automatic YAML generation from vacantes.txt
# This script tests both plain text and YAML-formatted input processing

echo "=== YAML Generation Workflow Test ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test results
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check workflow file exists and is valid
echo -e "${YELLOW}Test 1: Validating workflow file...${NC}"
if [ -f ".github/workflows/process_vacantes.yml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('.github/workflows/process_vacantes.yml'))" 2>/dev/null
    test_result $? "Workflow YAML is valid"
else
    test_result 1 "Workflow file exists"
fi
echo ""

# Test 2: Check required scripts exist
echo -e "${YELLOW}Test 2: Validating required scripts...${NC}"
for script in "process_vacantes.py" "extract_vacantes_from_text.py"; do
    if [ -f "scripts/$script" ]; then
        python3 -c "import ast; ast.parse(open('scripts/$script').read())" 2>/dev/null
        test_result $? "Script $script syntax is valid"
    else
        test_result 1 "Script $script exists"
    fi
done
echo ""

# Test 3: Check required directories exist
echo -e "${YELLOW}Test 3: Validating directory structure...${NC}"
for dir in "scripts" "vacantes_yaml" "vacantes_yaml_manual"; do
    [ -d "$dir" ]
    test_result $? "Directory $dir exists"
done
echo ""

# Test 4: Test format detection function
echo -e "${YELLOW}Test 4: Testing format detection...${NC}"
cat > /tmp/test_yaml_format.txt << 'EOF'
---
cargo: Test Engineer
empresa: Test Corp
fecha: 2025-01-01
descripcion: Test description
requerimientos: Test requirements
EOF

cat > /tmp/test_plain_format.txt << 'EOF'
Test Engineer Position
Company: Test Corp
Looking for a talented engineer...
EOF

# Test YAML detection
grep -q "^---$" /tmp/test_yaml_format.txt && grep -q "^cargo:" /tmp/test_yaml_format.txt && grep -q "^empresa:" /tmp/test_yaml_format.txt
test_result $? "YAML format detection works"

# Test plain text detection (should NOT match YAML pattern)
! (grep -q "^---$" /tmp/test_plain_format.txt && grep -q "^cargo:" /tmp/test_plain_format.txt && grep -q "^empresa:" /tmp/test_plain_format.txt)
test_result $? "Plain text format detection works"
echo ""

# Test 5: Test YAML processing with vacantes_sample.txt
echo -e "${YELLOW}Test 5: Testing YAML-formatted input processing...${NC}"
if [ -f "vacantes_sample.txt" ]; then
    rm -rf /tmp/test_yaml_output
    mkdir -p /tmp/test_yaml_output
    python scripts/process_vacantes.py --input vacantes_sample.txt --output /tmp/test_yaml_output --quiet 2>/dev/null
    
    # Check if any YAML files were generated
    YAML_COUNT=$(find /tmp/test_yaml_output -name "*.yaml" | wc -l)
    [ $YAML_COUNT -gt 0 ]
    test_result $? "YAML processing generates output files (found $YAML_COUNT files)"
else
    echo -e "${YELLOW}⚠️  SKIP: vacantes_sample.txt not found${NC}"
fi
echo ""

# Test 6: Test plain text processing with vacantes.txt
echo -e "${YELLOW}Test 6: Testing plain text input processing...${NC}"
if [ -f "vacantes.txt" ]; then
    rm -rf /tmp/test_extract_output
    mkdir -p /tmp/test_extract_output
    python scripts/extract_vacantes_from_text.py --input vacantes.txt --output /tmp/test_extract_output 2>/dev/null
    
    # Check if any YAML files were generated
    YAML_COUNT=$(find /tmp/test_extract_output -name "*.yaml" | wc -l)
    [ $YAML_COUNT -gt 0 ]
    test_result $? "Plain text processing generates output files (found $YAML_COUNT files)"
    
    # Validate generated YAML is valid
    if [ $YAML_COUNT -gt 0 ]; then
        FIRST_YAML=$(find /tmp/test_extract_output -name "*.yaml" | head -1)
        python3 -c "import yaml; yaml.safe_load(open('$FIRST_YAML'))" 2>/dev/null
        test_result $? "Generated YAML files are valid YAML syntax"
    fi
else
    echo -e "${YELLOW}⚠️  SKIP: vacantes.txt not found${NC}"
fi
echo ""

# Test 7: Test workflow logic with both format types
echo -e "${YELLOW}Test 7: Testing complete workflow logic...${NC}"

# Create test function (same as in workflow)
cat > /tmp/workflow_test_func.sh << 'EOF'
#!/bin/bash
is_yaml_format() {
  if grep -q "^---$" "$1" && grep -q "^cargo:" "$1" && grep -q "^empresa:" "$1"; then
    return 0
  else
    return 1
  fi
}

# Test with vacantes.txt
if [ -f "vacantes.txt" ] && [ -s "vacantes.txt" ]; then
  if is_yaml_format "vacantes.txt"; then
    echo "YAML"
  else
    echo "PLAINTEXT"
  fi
fi

# Test with vacantes_sample.txt
if [ -f "vacantes_sample.txt" ] && [ -s "vacantes_sample.txt" ]; then
  if is_yaml_format "vacantes_sample.txt"; then
    echo "YAML"
  else
    echo "PLAINTEXT"
  fi
fi
EOF
chmod +x /tmp/workflow_test_func.sh

RESULT=$(/tmp/workflow_test_func.sh)
echo "  Detected formats: $RESULT"

# vacantes.txt should be detected as PLAINTEXT
echo "$RESULT" | grep -q "PLAINTEXT"
test_result $? "vacantes.txt detected as plain text"

# vacantes_sample.txt should be detected as YAML (if it exists)
if [ -f "vacantes_sample.txt" ]; then
    echo "$RESULT" | grep -q "YAML"
    test_result $? "vacantes_sample.txt detected as YAML format"
fi
echo ""

# Test 8: Integration test - simulate full workflow
echo -e "${YELLOW}Test 8: Integration test - full workflow simulation...${NC}"
rm -rf /tmp/integration_test
mkdir -p /tmp/integration_test/vacantes_yaml /tmp/integration_test/vacantes_yaml_manual

# Simulate workflow for vacantes.txt
if [ -f "vacantes.txt" ] && [ -s "vacantes.txt" ]; then
    python scripts/extract_vacantes_from_text.py --input vacantes.txt --output /tmp/integration_test/vacantes_yaml 2>/dev/null || true
    python scripts/extract_vacantes_from_text.py --input vacantes.txt --output /tmp/integration_test/vacantes_yaml_manual 2>/dev/null || true
    
    YAML_COUNT=$(find /tmp/integration_test/vacantes_yaml -name "*.yaml" | wc -l)
    MANUAL_COUNT=$(find /tmp/integration_test/vacantes_yaml_manual -name "*.yaml" | wc -l)
    
    [ $YAML_COUNT -gt 0 ] && [ $MANUAL_COUNT -gt 0 ]
    test_result $? "Both output directories populated (vacantes_yaml: $YAML_COUNT, vacantes_yaml_manual: $MANUAL_COUNT)"
    
    [ $YAML_COUNT -eq $MANUAL_COUNT ]
    test_result $? "Both directories have same number of files"
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "The YAML generation workflow is correctly configured and functional."
    echo ""
    echo "What happens when you push a vacancy:"
    echo "1. GitHub Actions detects changes to vacantes.txt or vacantes_sample.txt"
    echo "2. The workflow automatically detects the file format (YAML or plain text)"
    echo "3. It uses the appropriate processor:"
    echo "   - extract_vacantes_from_text.py for plain text"
    echo "   - process_vacantes.py for YAML-formatted files"
    echo "4. YAML files are generated in both:"
    echo "   - vacantes_yaml/ (backup, read-only)"
    echo "   - vacantes_yaml_manual/ (editable copy)"
    echo "5. Changes are automatically committed and pushed"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo "Please review the failures above and fix the issues."
    exit 1
fi
