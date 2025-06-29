# Navi_Gym Migration Plan

## Overview
Migrate existing infrastructure from `migrate_projects` into `navi_gym` to create a unified RL development environment that integrates with your customer-facing systems.

## Current Infrastructure Analysis

### Source Structure (`migrate_projects/`)
```
migrate_projects/
├── assets/          # 3D models, animations, MMD assets
├── chat/           # Chat system (psyche, server, webapp)  
├── engine/         # Core engine (a2navi, render, tts, driver)
└── studio/         # Development tools and workspace
```

### Target Structure (`navi_gym/`)
```
navi_gym/
├── core/                    # Core RL infrastructure
│   ├── __init__.py
│   ├── environments/        # RL environments
│   ├── agents/             # RL agents
│   ├── training/           # Training pipelines
│   └── inference/          # Inference engine
├── assets/                 # Migrated 3D assets
│   ├── avatars/           # Character models
│   ├── animations/        # Motion data
│   ├── scenes/            # Environment scenes
│   └── shared/            # Common assets
├── engine/                 # Migrated engine components
│   ├── render/            # Rendering system
│   ├── audio/             # TTS and audio
│   ├── physics/           # Physics integration
│   └── avatar/            # Avatar system (a2navi)
├── studio/                 # Development tools
│   ├── viewer/            # Asset viewer
│   ├── editor/            # Scene editor
│   └── training_monitor/   # RL training dashboard
├── integration/            # Customer system integration
│   ├── api/               # API adapters
│   ├── chat/              # Chat system bridge
│   └── deployment/        # Production deployment
├── config/                 # Configuration files
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## Migration Strategy

### Phase 1: Core Structure Setup ✅
- [x] Create `navi_gym` directory structure
- [ ] Set up package configuration
- [ ] Create base modules

### Phase 2: Asset Migration 🔄
- [ ] Migrate 3D models and avatars
- [ ] Port animation data
- [ ] Integrate scene assets
- [ ] Set up asset loading pipeline

### Phase 3: Engine Integration 🔄
- [ ] Port rendering system
- [ ] Integrate avatar system (a2navi)
- [ ] Migrate TTS/audio components
- [ ] Connect physics engine

### Phase 4: Development Tools 🔄
- [ ] Port studio components
- [ ] Create RL training dashboard
- [ ] Set up asset viewer
- [ ] Build debugging tools

### Phase 5: Customer Integration 🔄
- [ ] Create API bridges
- [ ] Port chat system components
- [ ] Set up deployment pipeline
- [ ] Create inference adapters

## Detailed Migration Steps

### 1. Asset Migration (`migrate_projects/assets/` → `navi_gym/assets/`)

**Priority Assets:**
- `mumumu/` → `navi_gym/assets/avatars/mumumu/`
- `animations/` → `navi_gym/assets/animations/`
- `scenes/` → `navi_gym/assets/scenes/`
- `mmd_misc/` → `navi_gym/assets/shared/mmd/`

**Actions:**
1. Copy asset files preserving directory structure
2. Convert formats if needed (MMD → URDF/MJCF)
3. Create asset registry/database
4. Set up loading utilities

### 2. Engine Migration (`migrate_projects/engine/` → `navi_gym/engine/`)

**Components to Migrate:**
- `a2navi/` → `navi_gym/engine/avatar/` (Avatar system)
- `render/` → `navi_gym/engine/render/` (Rendering)
- `tts/` → `navi_gym/engine/audio/` (Text-to-speech)
- `driver/` → `navi_gym/engine/drivers/` (Hardware drivers)
- `common/` → `navi_gym/engine/common/` (Shared utilities)

**Actions:**
1. Copy source code
2. Update import paths
3. Integrate with Genesis physics engine
4. Create unified API layer

### 3. Studio Migration (`migrate_projects/studio/` → `navi_gym/studio/`)

**Components:**
- Web-based studio → Desktop/web hybrid
- Asset viewer integration
- RL training monitoring
- Real-time debugging

### 4. Chat System Integration (`migrate_projects/chat/` → `navi_gym/integration/chat/`)

**Purpose:** Bridge between RL models and customer chat system
**Components:**
- `psyche/` → Personality/behavior models
- `server/` → Chat server integration
- `webapp/` → Web interface for testing

## Implementation Plan

### Week 1: Foundation
```bash
# Day 1-2: Create directory structure
# Day 3-4: Set up package configuration
# Day 5: Create base modules and utilities
```

### Week 2: Asset Pipeline
```bash
# Day 1-3: Migrate avatar assets
# Day 4-5: Set up asset loading system
```

### Week 3: Engine Integration
```bash
# Day 1-2: Port rendering system
# Day 3-4: Integrate avatar system
# Day 5: Connect Genesis physics
```

### Week 4: RL Foundation
```bash
# Day 1-3: Create RL environment base classes
# Day 4-5: Set up training infrastructure
```

## Key Integration Points

### 1. Genesis Physics Engine
- Use Genesis for physics simulation
- Integrate avatar physics with existing render system
- Create bridge between Genesis entities and avatar system

### 2. Customer System APIs
- Create adapter layer for existing customer APIs
- Maintain compatibility with current inference system
- Enable seamless RL model deployment

### 3. Asset Pipeline
- Support existing asset formats
- Create conversion utilities
- Unified asset management system

## Success Criteria

### Phase 1 Complete:
- [ ] All directory structures created
- [ ] Base package configuration working
- [ ] Import system functional

### Phase 2 Complete:
- [ ] Avatar assets accessible in navi_gym
- [ ] Asset loading pipeline functional
- [ ] Basic viewer working

### Phase 3 Complete:
- [ ] Rendering system integrated
- [ ] Avatar system functional
- [ ] Genesis physics connected

### Phase 4 Complete:
- [ ] RL environment base classes ready
- [ ] Training infrastructure set up
- [ ] Ready for RL model development

## Risk Mitigation

### Dependency Conflicts
- Use virtual environments
- Document exact version requirements
- Test compatibility systematically

### Asset Format Issues
- Create conversion utilities
- Maintain backup of original assets
- Document format requirements

### Integration Complexity
- Start with minimal viable integration
- Add features incrementally
- Maintain clear separation of concerns

## Next Steps

1. **Execute Phase 1**: Create the basic structure
2. **Test Integration**: Verify Genesis compatibility
3. **Asset Pipeline**: Get basic asset loading working
4. **RL Prep**: Set up training environment structure

This migration will create a unified development environment where you can build RL models while maintaining compatibility with your existing customer-facing infrastructure.

## Quick Start

### Virtual Environment Setup

First, activate the virtual environment:

```bash
cd /home/barberb/Navi_Gym
source navi_gym_env/bin/activate
```

### Install Dependencies

Install the minimal requirements:

```bash
pip install -r requirements-minimal.txt
```

For full development features, install all dependencies:

```bash
pip install -r requirements.txt
```

### Test the Installation

```bash
python examples/quick_start.py
```
