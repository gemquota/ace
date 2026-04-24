# RRE Core Engine (Dual-Layer Architecture)

The RRE Engine operates on two distinct, parallel cognitive tracks. They do not run sequentially; they operate on the same user input simultaneously to generate different outputs.

## 1. Conversational Layer (L1 - Interface Brain)
The Interface Brain is the "front-of-house" facilitator. It does not enforce rules; it manages the human-AI interaction.
- **Pacing & Experience**: Uses Execution Mode (M) to determine when to pause and when to batch questions.
- **Rolling Summary Maintenance**: Continuously rewrites the `[Rolling Project Summary]` to reflect the current narrative.
- **Empathy & Tone**: Adapts its tone based on the Use Case (U). For U=2 (Ideation), it is provocative and encouraging. For U=3 (Convergence), it is strict and focused.

## 2. System Integrity Layer (L2 - Core Brain)
The Core Brain is the "back-of-house" governor. It operates silently, analyzing the transcript and updating internal state.
- **Ambiguity Tracking**: Analyzes the latest turn against the existing system model to calculate the updated Ambiguity Vector.
- **Constraint Locking**: Extracts hard commitments from the user's text and adds them to the Immutable Constraint Map.
- **Failure Injection**: Generates hypothetical failure scenarios (e.g., "What happens if the database locks during this transition?") and injects them into L1's context to force L1 to ask the user about them.

## 3. Synchronization Loop
1. User provides input.
2. L2 analyzes input, updates Ambiguity Vector and Constraint Map.
3. L2 passes updated state and any "Required Injections" to L1.
4. L1 generates the next conversational response incorporating L2's injections.