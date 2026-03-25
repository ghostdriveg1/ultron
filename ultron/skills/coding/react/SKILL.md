---
name: React Development
description: Build modern React applications with TypeScript, hooks, and best practices
---

# React Development Skill

## Trigger Patterns
- "build React app"
- "create React component"
- "React page"
- "React website"
- "frontend with React"

## Steps
1. **Project setup** — Vite + React + TypeScript (`npm create vite@latest`)
2. **Component design** — Break UI into atomic components (atoms, molecules, organisms)
3. **State management** — React Query for server state, useState/useReducer for UI state
4. **Routing** — React Router v6 with lazy loading
5. **Styling** — Tailwind CSS or CSS Modules (no inline styles)
6. **API integration** — React Query `useQuery`/`useMutation` with proper error boundaries
7. **Accessibility** — Semantic HTML, ARIA labels, keyboard navigation
8. **Testing** — Vitest + React Testing Library
9. **Build** — `npm run build`, deploy to Cloudflare Pages

## Example
```tsx
import { useQuery } from '@tanstack/react-query';

function StatusCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['status'],
    queryFn: () => fetch('/api/status').then(r => r.json()),
    refetchInterval: 30000,
  });

  if (isLoading) return <div>Loading...</div>;
  return <div>{data.brain_healthy ? '🟢' : '🔴'} Brain</div>;
}
```

## Common Pitfalls
- Not memoizing expensive computations (`useMemo`/`useCallback`)
- Prop drilling instead of context or composition
- Missing dependency arrays in `useEffect`
- Not handling loading/error states
