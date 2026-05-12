---
name: code-simplification
description: 代码简化工作流，在不改变行为的前提下降低复杂度、提升可读性。Use when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. 触发场景：「这段代码太复杂了」「帮我简化」「重构一下」「代码可读性差」「函数太长了」「嵌套太深」。核心原则：Chesterton's Fence（先理解再改）、保持行为完全不变、Rule of 500。
---

# Code Simplification

## Overview

Simplify code by reducing complexity while preserving exact behavior. The goal is not fewer lines — it's code that is easier to read, understand, modify, and debug. Every simplification must pass a simple test: "Would a new team member understand this faster than the original?"

## When to Use

- After a feature is working and tests pass, but the implementation feels heavier than it needs to be
- During code review when readability or complexity issues are flagged
- When you encounter deeply nested logic, long functions, or unclear names
- When refactoring code written under time pressure

**When NOT to use:**

- Code is already clean and readable — don't simplify for the sake of it
- You don't understand what the code does yet — comprehend before you simplify
- The code is performance-critical and the "simpler" version would be measurably slower
- You're about to rewrite the module entirely

## The Five Principles

### 1. Preserve Behavior Exactly

Don't change what the code does — only how it expresses it.

```
ASK BEFORE EVERY CHANGE:
→ Does this produce the same output for every input?
→ Does this maintain the same error behavior?
→ Does this preserve the same side effects and ordering?
→ Do all existing tests still pass without modification?
```

### 2. Follow Project Conventions

Simplification means making code more consistent with the codebase, not imposing external preferences. Before simplifying, study how neighboring code handles similar patterns.

### 3. Prefer Clarity Over Cleverness

Explicit code is better than compact code when the compact version requires a mental pause to parse.

### 4. Maintain Balance

Watch for over-simplification traps:
- Inlining too aggressively — removing a helper that gave a concept a name
- Combining unrelated logic — two simple functions merged into one complex function
- Removing "unnecessary" abstraction that exists for extensibility or testability
- Optimizing for line count instead of comprehension

### 5. Scope to What Changed

Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code unless explicitly asked.

## The Simplification Process

### Step 1: Understand Before Touching (Chesterton's Fence)

Before changing or removing anything, understand why it exists.

```
BEFORE SIMPLIFYING, ANSWER:
- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that define the expected behavior?
- Why might it have been written this way?
- Check git blame: what was the original context?
```

**If you can't answer these, you're not ready to simplify. Read more context first.**

### Step 2: Identify Simplification Opportunities

**Structural complexity:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Deep nesting (3+ levels) | Hard to follow control flow | Extract conditions into guard clauses |
| Long functions (50+ lines) | Multiple responsibilities | Split into focused functions |
| Nested ternaries | Requires mental stack to parse | Replace with if/else chains |
| Boolean parameter flags | `doThing(true, false, true)` | Replace with options objects |
| Repeated conditionals | Same `if` check in multiple places | Extract to a predicate function |

**Naming and readability:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Generic names | `data`, `result`, `temp`, `val` | Rename to describe content |
| Abbreviated names | `usr`, `cfg`, `btn` | Use full words |
| Comments explaining "what" | `// increment counter` above `count++` | Delete the comment |
| Comments explaining "why" | `// Retry because the API is flaky` | Keep these |

**Redundancy:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Duplicated logic | Same 5+ lines in multiple places | Extract to a shared function |
| Dead code | Unreachable branches, unused variables | Remove (after confirming it's truly dead) |
| Unnecessary abstractions | Wrapper that adds no value | Inline the wrapper |
| Over-engineered patterns | Factory-for-a-factory | Replace with the simple direct approach |

### Step 3: Apply Changes Incrementally

Make one simplification at a time. Run tests after each change.

```
FOR EACH SIMPLIFICATION:
1. Make the change
2. Run the test suite
3. If tests pass → commit (or continue)
4. If tests fail → revert and reconsider
```

**The Rule of 500:** If a refactoring would touch more than 500 lines, invest in automation (codemods, AST transforms) rather than making changes by hand.

**Submit refactoring changes separately from feature or bug fix changes.**

### Step 4: Verify the Result

```
COMPARE BEFORE AND AFTER:
- Is the simplified version genuinely easier to understand?
- Did you introduce any new patterns inconsistent with the codebase?
- Is the diff clean and reviewable?
- Would a teammate approve this change?
```

If the "simplified" version is harder to understand, revert.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's working, no need to touch it" | Working code that's hard to read will be hard to fix when it breaks. |
| "Fewer lines is always simpler" | A 1-line nested ternary is not simpler than a 5-line if/else. |
| "I'll just quickly simplify this unrelated code too" | Unscoped simplification creates noisy diffs and risks regressions. |
| "The original author must have had a reason" | Maybe. Check git blame — apply Chesterton's Fence. But accumulated complexity often has no reason. |
| "I'll refactor while adding this feature" | Separate refactoring from feature work. Mixed changes are harder to review and revert. |

## Red Flags

- Simplification that requires modifying tests to pass (you likely changed behavior)
- "Simplified" code that is longer and harder to follow than the original
- Renaming things to match your preferences rather than project conventions
- Removing error handling because "it makes the code cleaner"
- Simplifying code you don't fully understand
- Batching many simplifications into one large, hard-to-review commit

## Verification

- [ ] All existing tests pass without modification
- [ ] Build succeeds with no new warnings
- [ ] Linter/formatter passes
- [ ] Each simplification is a reviewable, incremental change
- [ ] The diff is clean — no unrelated changes mixed in
- [ ] Simplified code follows project conventions
- [ ] No error handling was removed or weakened
- [ ] No dead code was left behind
- [ ] A teammate or review agent would approve the change as a net improvement
