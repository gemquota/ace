#!/usr/bin/env bash

# setup_gemini_skills.sh
# Ensures ACE-specific Gemini CLI skills are present in ~/.gemini/skills/

GEMINI_SKILLS_DIR="${HOME}/.gemini/skills"
mkdir -p "${GEMINI_SKILLS_DIR}"

# 1. ace-intent
if [ ! -d "${GEMINI_SKILLS_DIR}/ace-intent" ]; then
    echo "[*] Creating ace-intent skill..."
    mkdir -p "${GEMINI_SKILLS_DIR}/ace-intent"
    cat <<EOF > "${GEMINI_SKILLS_DIR}/ace-intent/SKILL.md"
# 🎯 SKILL: ACE_INTENT
Passes an intent or goal to the ACE Suite Swarm Grid via the CLIDE interface.

## Usage
Use this skill when the user asks to "send a goal", "start a task", or "pass an intent to ACE".

## Protocol
1. Adopt the CLIDE persona.
2. Validate the intent against the current project context.
3. Use 'run_shell_command' to execute: 'python cap/core/clide/cli.py "[INTENT]"'
EOF
fi

# 2. ace-bootstrap
if [ ! -d "${GEMINI_SKILLS_DIR}/ace-bootstrap" ]; then
    echo "[*] Creating ace-bootstrap skill..."
    mkdir -p "${GEMINI_SKILLS_DIR}/ace-bootstrap"
    cat <<EOF > "${GEMINI_SKILLS_DIR}/ace-bootstrap/SKILL.md"
# 🚀 SKILL: ACE_BOOTSTRAP
Initializes the ACE Suite Swarm Grid.

## Usage
Use this when starting a session or when the user wants to ensure the ACE environment (Redis, Mesh State, Dashboard, and Workers) is active.

## Protocol
1. Verify the 'redis-server' is running.
2. Execute the mesh state build: 'python cap/scripts/build_mesh_state.py'
3. Start the dashboard in the background: 'python cap/scripts/startup_dashboard.py' (is_background=true)
EOF
fi

# 3. ace-arm
if [ ! -d "${GEMINI_SKILLS_DIR}/ace-arm" ]; then
    echo "[*] Creating ace-arm skill..."
    mkdir -p "${GEMINI_SKILLS_DIR}/ace-arm"
    cat <<EOF > "${GEMINI_SKILLS_DIR}/ace-arm/SKILL.md"
# 🦾 SKILL: ACE_ARM
Operates as the "Automated Resource Manager" (ARM) worker for ACE.

## Usage
Use this to poll the CLIDE task queue and execute deterministic code using Gemini CLI tools.

## Protocol
1. Run the ARM worker: 'python cap/scripts/arm_worker.py'
2. Monitor output for task interceptions and successful handoffs to the APC executor.
EOF
fi

# 4. ace-rrp (Placeholder for user's actual RRP prompt)
if [ ! -d "${GEMINI_SKILLS_DIR}/ace-rrp" ]; then
    echo "[*] Creating ace-rrp skill..."
    mkdir -p "${GEMINI_SKILLS_DIR}/ace-rrp"
    cat <<EOF > "${GEMINI_SKILLS_DIR}/ace-rrp/SKILL.md"
# 🌀 SKILL: ACE_RRP
Executes the Recursive Refinement Protocol (RRP) for complex architectural decisions.

## Usage
Use this skill when the user asks to "run RRP", "refine a goal", or "validate a major change".

## Protocol
(Wait for user to provide specific RRP prompt/logic)
EOF
fi

echo "[✓] Gemini ACE skills are synchronized."
