#!/bin/bash

# 🗂️ Navi_Gym Workspace Reorganization Script
# Execute with: bash reorganize_workspace.sh

set -e  # Exit on any error

echo "🎌✨ Navi_Gym Workspace Reorganization ✨🎌"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "ichika_vrm_final_display.py" ]; then
    echo "❌ Error: ichika_vrm_final_display.py not found!"
    echo "   Please run this script from the Navi_Gym root directory"
    exit 1
fi

echo "✅ Found ichika_vrm_final_display.py - proceeding with reorganization"
echo ""

# Create backup
echo "📦 Creating backup..."
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_dir="backup_before_reorganization_${timestamp}"
mkdir -p "$backup_dir"

# Backup essential files and directories (just in case)
cp ichika_vrm_final_display.py "$backup_dir/"
cp -r ichika_body_primitives_FIXED "$backup_dir/" 2>/dev/null || echo "   (ichika_body_primitives_FIXED not found - skipping)"
cp -r ichika_face_primitives_correct "$backup_dir/" 2>/dev/null || echo "   (ichika_face_primitives_correct not found - skipping)"
cp -r ichika_meshes_with_uvs "$backup_dir/" 2>/dev/null || echo "   (ichika_meshes_with_uvs not found - skipping)"
cp -r vrm_textures "$backup_dir/" 2>/dev/null || echo "   (vrm_textures not found - skipping)"

echo "✅ Backup created in $backup_dir"
echo ""

# Step 1: Create directory structure
echo "🏗️  Creating new directory structure..."

mkdir -p archive/{experimental_viewers,orientation_experiments,texture_analysis,uv_experiments,mesh_analysis,color_experiments,assembly_tests,legacy_viewers,development_iterations}
mkdir -p demos/{avatar_demos,performance_tests,simple_tests}
mkdir -p rigging/{skeleton_extraction,locomotion_experiments,weight_mapping,animation_conversion,integration_tests}
mkdir -p tools/{extractors,generators,testing,debug}
mkdir -p training
mkdir -p legacy_data
mkdir -p logs
mkdir -p outputs/{images,results}

echo "✅ Directory structure created"
echo ""

# Step 2: Move files to archive/experimental_viewers
echo "📁 Moving experimental viewer files..."

# Pattern-based moves for experimental viewers
for file in *ichika*viewer*.py *textured_ichika*.py ichika_vrm_showcase*.py textured_ichika_viewer.py complete_textured_ichika.py proper_textured_ichika.py real_textured_ichika_viewer.py advanced_textured_ichika.py fixed_textured_ichika.py; do
    [ -f "$file" ] && mv "$file" archive/experimental_viewers/ && echo "  ✅ Moved $file"
done

# Step 3: Move orientation experiments
echo "📁 Moving orientation experiment files..."

for file in *orientation*.py verify_ichika_orientation.py test_*rotation*.py test_ichika_orientations.py test_ultimate_orientations.py quick_orientation_test.py; do
    [ -f "$file" ] && mv "$file" archive/orientation_experiments/ && echo "  ✅ Moved $file"
done

# Step 4: Move texture analysis files
echo "📁 Moving texture analysis files..."

for file in *texture*.py analyze_*texture*.py investigate_texture*.py texture_mapping_audit.py texture_explorer.py vrm_texture_explorer.py test_texture_16.py texture_body_test.py ichika_texture_debug.py ichika_texture_mapping_reference.py debug_texture_application.py find_white_textures.py comprehensive_texture_analysis.py detailed_texture_analysis.py body_texture_diagnostic.py; do
    [ -f "$file" ] && mv "$file" archive/texture_analysis/ && echo "  ✅ Moved $file"
done

# Step 5: Move UV experiments
echo "📁 Moving UV experiment files..."

for file in *uv*.py check_uv_orientations.py test_uv_orientations.py quick_uv_test.py simple_uv_test.py ichika_simple_uv_test.py ichika_uv_diagnostic.py ichika_uv_mapped_textures.py ichika_uv_orientation_test.py; do
    [ -f "$file" ] && mv "$file" archive/uv_experiments/ && echo "  ✅ Moved $file"
done

# Step 6: Move mesh analysis files
echo "📁 Moving mesh analysis files..."

for file in analyze_ichika_mesh.py analyze_collar_primitive.py ichika_mesh_parts_debug.py comprehensive_vrm_analyzer.py debug_ichika.py check_materials.py; do
    [ -f "$file" ] && mv "$file" archive/mesh_analysis/ && echo "  ✅ Moved $file"
done

# Step 7: Move color experiments
echo "📁 Moving color experiment files..."

for file in ichika_colors.py extract_colors.py ichika_corrected_textures.py clothing_texture_tester.py; do
    [ -f "$file" ] && mv "$file" archive/color_experiments/ && echo "  ✅ Moved $file"
done

# Step 8: Move assembly tests
echo "📁 Moving assembly test files..."

for file in ichika_complete_assembly_test.py ichika_immediate_test.py ichika_quick_test.py test_face_loading.py validate_ichika_fixes.py; do
    [ -f "$file" ] && mv "$file" archive/assembly_tests/ && echo "  ✅ Moved $file"
done

# Step 9: Move legacy viewers
echo "📁 Moving legacy viewer files..."

for file in ichika_vrm_final_display_FIXED.py ichika_vrm_fixed_display.py ichika_enhanced_viewer.py ichika_character_viewer.py ichika_perfect_solution.py ichika_success_summary.py ultimate_ichika_viewer.py; do
    [ -f "$file" ] && mv "$file" archive/legacy_viewers/ && echo "  ✅ Moved $file"
done

# Step 10: Move development iterations
echo "📁 Moving development iteration files..."

for file in ichika_proper_mesh_viewer.py ichika_verbose_display.py ichika_visual_debug.py ichika_vrm_skeleton_viewer.py super_bright_ichika_viewer.py ichika_ground_camera_test.py; do
    [ -f "$file" ] && mv "$file" archive/development_iterations/ && echo "  ✅ Moved $file"
done

# Step 11: Move demo files
echo "📁 Moving demo files..."

for file in demo_genesis_avatar_integration.py demo_working_system.py demo_visualization.py demo_visualization_headless.py advanced_features_demo.py genesis_performance_demo.py quick_performance_demo.py; do
    [ -f "$file" ] && mv "$file" demos/avatar_demos/ && echo "  ✅ Moved $file"
done

# Step 11.5: Move rigging and locomotion files  
echo "📁 Moving rigging and locomotion files..."

for file in ichika_locomotion_rig.py ichika_complete_locomotion.py ichika_advanced_locomotion.py vrm_locomotion_demo.py vrm_humanoid_locomotion.py; do
    [ -f "$file" ] && mv "$file" rigging/locomotion_experiments/ && echo "  ✅ Moved $file to rigging/locomotion_experiments/"
done

for file in ichika_vrm_skeleton_viewer.py; do
    [ -f "$file" ] && mv "$file" rigging/skeleton_extraction/ && echo "  ✅ Moved $file to rigging/skeleton_extraction/"
done

for file in simple_performance_test.py fixed_performance_test.py performance_test_final.py gpu_optimization_test.py optimized_rendering_test.py; do
    [ -f "$file" ] && mv "$file" demos/performance_tests/ && echo "  ✅ Moved $file"
done

for file in simple_genesis_test.py simple_gpu_test.py simple_mesh_viewer.py simple_texture_test.py simple_vrm_texture_test.py simple_vrm_viewer.py minimal_test.py ultra_simple_viewer.py; do
    [ -f "$file" ] && mv "$file" demos/simple_tests/ && echo "  ✅ Moved $file"
done

# Step 12: Move tool files
echo "📁 Moving tool files..."

for file in extract_eye_meshes.py create_collar_only.py vrm_real_converter.py; do
    [ -f "$file" ] && mv "$file" tools/extractors/ && echo "  ✅ Moved $file"
done

for file in generate_avatar_visualization.py visualize_avatar.py; do
    [ -f "$file" ] && mv "$file" tools/generators/ && echo "  ✅ Moved $file"
done

for file in test_basic_components.py test_basic_visibility.py test_lighting_simple.py test_physics_floor.py validate_system.py; do
    [ -f "$file" ] && mv "$file" tools/testing/ && echo "  ✅ Moved $file"
done

for file in debug_genesis.py debug_genesis_cpu.py debug_genesis_fixed.py debug_viewer.py debug_import.py genesis_diagnostic.py; do
    [ -f "$file" ] && mv "$file" tools/debug/ && echo "  ✅ Moved $file"
done

# Step 13: Move training files
echo "📁 Moving training files..."

for file in train_avatar_rl.py complete_avatar_training.py trained_avatar_agent.pth training_summary.txt training_progress_*.png; do
    [ -f "$file" ] && mv "$file" training/ && echo "  ✅ Moved $file"
done

# Note: vrm_animation_trainer.py may be integrated with rigging later - keeping in training for now
for file in vrm_animation_trainer.py; do
    [ -f "$file" ] && mv "$file" training/ && echo "  ✅ Moved $file (may integrate with rigging later)"
done

# Step 14: Move logs
echo "📁 Moving log files..."

for file in *.log *_log.txt deployment_output.log quick_start_output.log; do
    [ -f "$file" ] && mv "$file" logs/ && echo "  ✅ Moved $file"
done

# Step 15: Move output images and results
echo "📁 Moving output files..."

for file in *.png *.jpg *.jpeg; do
    [ -f "$file" ] && mv "$file" outputs/images/ && echo "  ✅ Moved $file"
done

for file in *.json; do
    [ -f "$file" ] && mv "$file" outputs/results/ && echo "  ✅ Moved $file"
done

# Step 16: Move legacy data directories
echo "📁 Moving legacy data directories..."

for dir in ichika_body_primitives_correct ichika_eye_meshes uv_test_outputs recordings; do
    [ -d "$dir" ] && mv "$dir" legacy_data/ && echo "  ✅ Moved $dir/"
done

echo ""
echo "🧹 Cleaning up remaining development files..."

# Move any remaining experimental files
for file in *ichika*.py *test*.py *simple*.py *debug*.py *demo*.py; do
    # Skip files we want to keep in root
    if [[ "$file" != "ichika_vrm_final_display.py" && "$file" != "extract_"* && "$file" != "test_env.py" && "$file" != "test_full_environment.py" && "$file" != "test_environment_final.py" ]]; then
        if [ -f "$file" ]; then
            mv "$file" archive/development_iterations/ && echo "  ✅ Moved remaining file: $file"
        fi
    fi
done

echo ""
echo "✅ Reorganization complete!"
echo ""

# Final verification
echo "🔍 Verifying essential files are still in root..."

essential_files=(
    "ichika_vrm_final_display.py"
    "extract_body_primitives_FIXED.py"
    "extract_face_primitives_correct.py"
    "extract_vrm_mesh_with_uvs.py"
    "extract_vrm_textures.py"
    "vrm_to_genesis_converter.py"
    "vrm_to_obj_converter.py"
)

essential_dirs=(
    "ichika_body_primitives_FIXED"
    "ichika_face_primitives_correct"
    "ichika_meshes_with_uvs"
    "vrm_textures"
)

all_good=true

for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ⚠️  $file - NOT FOUND!"
        all_good=false
    fi
done

for dir in "${essential_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ⚠️  $dir/ - NOT FOUND!"
        all_good=false
    fi
done

echo ""
if [ "$all_good" = true ]; then
    echo "🎉 SUCCESS! All essential files are preserved in root directory"
    echo ""
    echo "📊 Reorganization Summary:"
    echo "   📁 Created organized directory structure"
    echo "   🗄️  Archived experimental development files"
    echo "   � Set up rigging workspace for character animation"
    echo "   �🧹 Cleaned up workspace while preserving functionality"
    echo "   💾 Created backup in: $backup_dir"
    echo ""
    echo "🧪 Next steps:"
    echo "   1. Test ichika_vrm_final_display.py still works"
    echo "   2. Run: python ichika_vrm_final_display.py"
    echo "   3. Begin character rigging development in rigging/ directory"
    echo "   4. Create ichika_vrm_rigged_display.py when rigging is ready"
    echo ""
    echo "🎌✨ Navi_Gym workspace is now clean and organized for rigging development! ✨🎌"
else
    echo "❌ WARNING: Some essential files are missing!"
    echo "   Please check the backup directory: $backup_dir"
    echo "   You may need to restore files from backup"
fi
