import type { UserRole } from "@/types";

// Routes with role restrictions. Order matters: first match wins.
const ROUTE_RULES: Array<{ test: (path: string) => boolean; roles: UserRole[] }> = [
  {
    test: (p) => p.startsWith("/admin"),
    roles: ["admin"],
  },
  {
    test: (p) => /\/finance(\/|$)/.test(p),
    roles: ["admin", "receptionist"],
  },
  {
    test: (p) => /\/medical(\/|$)/.test(p),
    roles: ["admin", "medical", "counselor"],
  },
  {
    test: (p) => /\/therapeutic(\/|$)/.test(p),
    roles: ["admin", "counselor"],
  },
  {
    test: (p) => /\/social-work(\/|$)/.test(p),
    roles: ["admin", "social_worker"],
  },
  {
    test: (p) => /\/psychology(\/|$)/.test(p),
    roles: ["admin", "psychologist"],
  },
  {
    test: (p) => /\/occupational-therapy(\/|$)/.test(p),
    roles: ["admin", "occupational_therapist"],
  },
];

export function canAccess(path: string, role: string): boolean {
  for (const rule of ROUTE_RULES) {
    if (rule.test(path)) {
      return (rule.roles as string[]).includes(role);
    }
  }
  return true;
}
