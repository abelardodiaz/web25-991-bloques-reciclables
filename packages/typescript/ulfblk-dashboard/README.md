# @bloque/dashboard

React dashboard layout components - sidebar, header, data tables, navigation. Zero external UI deps (only React + Tailwind classes + `cn()` from `@bloque/ui`).

## Install

```bash
pnpm add @bloque/dashboard @bloque/ui @bloque/types
```

## Quick Start

```tsx
import {
  DashboardLayout,
  Sidebar,
  Header,
  NavItem,
  NavSection,
  PageContainer,
  Breadcrumb,
} from "@bloque/dashboard";

function App() {
  return (
    <DashboardLayout
      sidebar={
        <Sidebar header={<span>My App</span>}>
          <NavSection heading="Main">
            <NavItem label="Dashboard" href="/" active />
            <NavItem label="Users" href="/users" badge={3} />
          </NavSection>
        </Sidebar>
      }
      header={
        <Header
          breadcrumbs={
            <Breadcrumb items={[{ label: "Home", href: "/" }, { label: "Dashboard" }]} />
          }
        />
      }
    >
      <PageContainer>
        <h1>Hello Dashboard</h1>
      </PageContainer>
    </DashboardLayout>
  );
}
```

## Components

### Layout

| Component | Description |
|-----------|-------------|
| `DashboardLayout` | Shell: sidebar + header + content area |
| `Sidebar` | Collapsible sidebar with header/footer slots |
| `Header` | Top bar with breadcrumbs + actions slot |
| `PageContainer` | Content wrapper with max-width + padding |

### Navigation

| Component | Description |
|-----------|-------------|
| `NavItem` | Icon + label + badge. Renders `<a>` or `<button>` |
| `NavSection` | Group with heading, optionally collapsible |
| `Breadcrumb` | Breadcrumb trail |

### Data Display

| Component | Description |
|-----------|-------------|
| `StatCard` | Metric card: value, label, trend, icon |
| `DataTable<T>` | Generic table with sorting + pagination |
| `EmptyState` | Placeholder for empty lists |

### User

| Component | Description |
|-----------|-------------|
| `UserMenu` | Dropdown with user info + logout |
| `TenantSelector` | Dropdown to switch tenant |

### Hooks

| Hook | Description |
|------|-------------|
| `useSidebar()` | Sidebar collapsed state + toggle |
| `useClickOutside(handler)` | Dismiss on click outside ref |
| `useEscapeKey(handler)` | Dismiss on Escape key |

## Auth Integration (Optional)

`UserMenu` and `TenantSelector` optionally integrate with `@bloque/auth-react`. If `AuthProvider`/`TenantProvider` are in the tree, they auto-detect the user/tenant. Otherwise, pass props directly.

## DataTable

```tsx
import { DataTable, type ColumnDef } from "@bloque/dashboard";

interface User {
  id: string;
  name: string;
  email: string;
}

const columns: ColumnDef<User>[] = [
  { key: "name", header: "Name", sortable: true },
  { key: "email", header: "Email" },
];

// Simple array
<DataTable columns={columns} data={users} />

// PaginatedResponse (auto-pagination)
<DataTable
  columns={columns}
  data={paginatedResponse}
  onSort={(key, dir) => fetchSorted(key, dir)}
  onPageChange={(page) => fetchPage(page)}
/>
```
