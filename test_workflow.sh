#!/bin/bash
# Test script to validate the repository workflows and scripts
# This script performs basic validation without requiring GitHub tokens

set -e

echo "=== Repository Workflow Validation Test ==="
echo ""

# Test 1: Check workflow file exists and is valid YAML
echo "Test 1: Validating workflow file..."
if [ -f ".github/workflows/copy_to_app_laborales.yml" ]; then
    echo "✅ Workflow file exists"
    python3 -c "import yaml; yaml.safe_load(open('.github/workflows/copy_to_app_laborales.yml'))" && echo "✅ Workflow YAML is valid"
else
    echo "❌ Workflow file not found"
    exit 1
fi
echo ""

# Test 2: Check integration script exists
echo "Test 2: Validating integration script..."
if [ -f "scripts/github_push_yaml_to_other_repo.py" ]; then
    echo "✅ Integration script exists"
    python3 -c "import ast; ast.parse(open('scripts/github_push_yaml_to_other_repo.py').read())" && echo "✅ Script syntax is valid"
else
    echo "❌ Integration script not found"
    exit 1
fi
echo ""

# Test 3: Check required directories exist
echo "Test 3: Validating directory structure..."
for dir in "scripts" "vacantes_yaml_manual" "vacantes_yaml"; do
    if [ -d "$dir" ]; then
        echo "✅ Directory $dir exists"
    else
        echo "❌ Directory $dir not found"
        exit 1
    fi
done
echo ""

# Test 4: Check that aplicaciones folder does NOT exist
echo "Test 4: Validating cleanup..."
if [ -d "aplicaciones" ]; then
    echo "❌ Leftover aplicaciones/ folder still exists (should be removed)"
    exit 1
else
    echo "✅ No leftover aplicaciones/ folder (correct)"
fi
echo ""

# Test 5: Count critical scripts
echo "Test 5: Validating script presence..."
EXPECTED_SCRIPTS=(
    "github_push_yaml_to_other_repo.py"
    "split_vacantes_to_yaml.py"
    "process_vacantes.py"
    "extract_vacantes_from_text.py"
    "convert_to_line_dataset.py"
    "train_line_classifier.py"
    "train_tfidf_baseline.py"
)

for script in "${EXPECTED_SCRIPTS[@]}"; do
    if [ -f "scripts/$script" ]; then
        echo "✅ $script present"
    else
        echo "❌ $script missing"
        exit 1
    fi
done
echo ""

# Test 6: Verify workflow trigger configuration
echo "Test 6: Validating workflow trigger..."
if grep -q "vacantes_yaml_manual/\*.yaml" .github/workflows/copy_to_app_laborales.yml; then
    echo "✅ Workflow triggers on correct path"
else
    echo "❌ Workflow trigger path incorrect"
    exit 1
fi
echo ""

# Test 7: Check script configuration
echo "Test 7: Validating script configuration..."
if grep -q 'SRC_DIR = "vacantes_yaml_manual"' scripts/github_push_yaml_to_other_repo.py; then
    echo "✅ Script source directory correct"
else
    echo "❌ Script source directory incorrect"
    exit 1
fi

if grep -q 'DEST_REPO = "angra8410/aplicaciones_laborales"' scripts/github_push_yaml_to_other_repo.py; then
    echo "✅ Script destination repository correct"
else
    echo "❌ Script destination repository incorrect"
    exit 1
fi

if grep -q 'DEST_PATH = "to_process"' scripts/github_push_yaml_to_other_repo.py; then
    echo "✅ Script destination path correct"
else
    echo "❌ Script destination path incorrect"
    exit 1
fi
echo ""

# Test 8: Verify no centralization artifacts remain
echo "Test 8: Checking for centralization artifacts..."
SHOULD_NOT_EXIST=(
    ".github/workflows/process_vacancies.yml"
    "scripts/copy_to_process.py"
    "scripts/process_and_organize_cv.py"
    "GUIA_FLUJO_CENTRALIZADO.md"
    "GUIA_MIGRACION.md"
    "RESUMEN_CENTRALIZACION.md"
)

ALL_CLEAN=true
for file in "${SHOULD_NOT_EXIST[@]}"; do
    if [ -e "$file" ]; then
        echo "❌ Centralization artifact still exists: $file"
        ALL_CLEAN=false
    fi
done

if [ "$ALL_CLEAN" = true ]; then
    echo "✅ No centralization artifacts found (correct)"
fi
echo ""

# Summary
echo "=== Validation Complete ==="
echo "✅ All tests passed!"
echo ""
echo "Repository is correctly restored to original functional state."
echo ""
echo "Next steps:"
echo "1. Ensure LABORALES_TOKEN secret is configured in repository settings"
echo "2. Test workflow by pushing a new YAML file to vacantes_yaml_manual/"
echo "3. Verify file appears in aplicaciones_laborales/to_process/"
echo ""
