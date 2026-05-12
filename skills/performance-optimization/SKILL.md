---
name: performance-optimization
description: 性能优化工作流，先测量再优化。Use when performance requirements exist, when you suspect performance regressions, or when Core Web Vitals or load times need improvement. 触发场景：「这个接口太慢了」「页面加载慢」「性能优化」「N+1 查询」「Core Web Vitals」「LCP/INP/CLS 不达标」「响应时间超标」「内存泄漏」。核心原则：Measure first（没有数据不优化），识别真正瓶颈后再修复。
---

# Performance Optimization

## Overview

Measure before optimizing. Performance work without measurement is guessing — and guessing leads to premature optimization that adds complexity without improving what matters. Profile first, identify the actual bottleneck, fix it, measure again.

## When to Use

- Performance requirements exist in the spec (load time budgets, response time SLAs)
- Users or monitoring report slow behavior
- Core Web Vitals scores are below thresholds
- You suspect a change introduced a regression
- Building features that handle large datasets or high traffic

**When NOT to use:** Don't optimize before you have evidence of a problem. Premature optimization adds complexity that costs more than the performance it gains.

## Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## The Optimization Workflow

```
1. MEASURE  → Establish baseline with real data
2. IDENTIFY → Find the actual bottleneck (not assumed)
3. FIX      → Address the specific bottleneck
4. VERIFY   → Measure again, confirm improvement
5. GUARD    → Add monitoring or tests to prevent regression
```

## Step 1: Measure

**Frontend:**
```bash
# Synthetic: Lighthouse in Chrome DevTools
# Chrome DevTools → Performance tab → Record

# RUM: Web Vitals library
import { onLCP, onINP, onCLS } from 'web-vitals';
onLCP(console.log);
onINP(console.log);
onCLS(console.log);
```

**Backend:**
```bash
# Response time logging / APM
# Database query logging with timing
console.time('db-query');
const result = await db.query(...);
console.timeEnd('db-query');
```

## Step 2: Identify the Bottleneck

**症状 → 诊断路径：**

```
What is slow?
├── First page load
│   ├── Large bundle? → Measure bundle size, check code splitting
│   ├── Slow server response? → Measure TTFB, profile backend queries
│   └── Render-blocking resources? → Check network waterfall
├── Interaction feels sluggish
│   ├── UI freezes on click? → Profile main thread, look for long tasks (>50ms)
│   └── Animation jank? → Check layout thrashing, forced reflows
├── Page after navigation
│   └── Data loading? → Measure API response times, check for N+1 fetches
└── Backend / API
    ├── Single endpoint slow? → Profile database queries, check indexes
    ├── All endpoints slow? → Check connection pool, memory, CPU
    └── Intermittent slowness? → Check lock contention, GC pauses
```

**常见瓶颈分类：**

| Symptom | Likely Cause | Investigation |
|---------|-------------|---------------|
| Slow LCP | Large images, render-blocking resources | Check network waterfall, image sizes |
| Poor INP | Heavy JavaScript on main thread | Check long tasks in Performance trace |
| Slow API responses | N+1 queries, missing indexes | Check database query log |
| Memory growth | Leaked references, unbounded caches | Heap snapshot analysis |

## Step 3: Fix Common Anti-Patterns

### N+1 Queries（最常见的后端性能问题）

```typescript
// BAD: N+1 — one query per task for the owner
const tasks = await db.tasks.findMany();
for (const task of tasks) {
  task.owner = await db.users.findUnique({ where: { id: task.ownerId } });
}

// GOOD: Single query with join/include
const tasks = await db.tasks.findMany({
  include: { owner: true },
});
```

### Unbounded Data Fetching

```typescript
// BAD: Fetching all records
const allTasks = await db.tasks.findMany();

// GOOD: Paginated with limits
const tasks = await db.tasks.findMany({
  take: 20,
  skip: (page - 1) * 20,
  orderBy: { createdAt: 'desc' },
});
```

### Missing Caching (Backend)

```typescript
// Cache frequently-read, rarely-changed data
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
let cachedConfig: AppConfig | null = null;
let cacheExpiry = 0;

async function getAppConfig(): Promise<AppConfig> {
  if (cachedConfig && Date.now() < cacheExpiry) {
    return cachedConfig;
  }
  cachedConfig = await db.config.findFirst();
  cacheExpiry = Date.now() + CACHE_TTL;
  return cachedConfig;
}
```

### Unnecessary Re-renders (React)

```tsx
// BAD: Creates new object on every render
function TaskList() {
  return <TaskFilters options={{ sortBy: 'date', order: 'desc' }} />;
}

// GOOD: Stable reference
const DEFAULT_OPTIONS = { sortBy: 'date', order: 'desc' } as const;
function TaskList() {
  return <TaskFilters options={DEFAULT_OPTIONS} />;
}
```

### Large Bundle Size

```typescript
// GOOD: Dynamic import for heavy, rarely-used features
const ChartLibrary = lazy(() => import('./ChartLibrary'));

// GOOD: Route-level code splitting
const SettingsPage = lazy(() => import('./pages/Settings'));
```

## Performance Budget

```
JavaScript bundle: < 200KB gzipped (initial load)
CSS: < 50KB gzipped
Images: < 200KB per image (above the fold)
API response time: < 200ms (p95)
Time to Interactive: < 3.5s on 4G
Lighthouse Performance score: ≥ 90
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll optimize later" | Performance debt compounds. Fix obvious anti-patterns now. |
| "It's fast on my machine" | Your machine isn't the user's. Profile on representative hardware. |
| "This optimization is obvious" | If you didn't measure, you don't know. Profile first. |
| "The framework handles performance" | Frameworks can't fix N+1 queries or oversized bundles. |

## Red Flags

- Optimization without profiling data to justify it
- N+1 query patterns in data fetching
- List endpoints without pagination
- Bundle size growing without review
- No performance monitoring in production
- `React.memo` and `useMemo` everywhere (overusing is as bad as underusing)

## Verification

- [ ] Before and after measurements exist (specific numbers)
- [ ] The specific bottleneck is identified and addressed
- [ ] Core Web Vitals are within "Good" thresholds (if frontend)
- [ ] No N+1 queries in new data fetching code
- [ ] Existing tests still pass
