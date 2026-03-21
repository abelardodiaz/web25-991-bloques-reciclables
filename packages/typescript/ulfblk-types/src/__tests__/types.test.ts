import { describe, it, expect } from "vitest";
import type {
  BaseEntity,
  SoftDeletableEntity,
  AuditableEntity,
  PaginatedResponse,
  ErrorResponse,
  SuccessResponse,
  HealthResponse,
  LoginRequest,
  LoginResponse,
  TokenPair,
  TokenPayload,
  TokenData,
  User,
  LoginAttemptState,
  Tenant,
  TenantContext,
  TenantConfig,
} from "../index.js";

describe("@ulfblk/types", () => {
  describe("entity types", () => {
    it("BaseEntity has required fields", () => {
      const entity: BaseEntity = {
        id: "123",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
      };
      expect(entity.id).toBe("123");
    });

    it("SoftDeletableEntity extends BaseEntity with deletedAt", () => {
      const entity: SoftDeletableEntity = {
        id: "123",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
        deletedAt: null,
      };
      expect(entity.deletedAt).toBeNull();
    });

    it("AuditableEntity extends BaseEntity with audit fields", () => {
      const entity: AuditableEntity = {
        id: "123",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
        createdBy: "user-1",
        updatedBy: "user-2",
      };
      expect(entity.createdBy).toBe("user-1");
      expect(entity.updatedBy).toBe("user-2");
    });
  });

  describe("api types", () => {
    it("PaginatedResponse holds items with metadata", () => {
      const response: PaginatedResponse<{ name: string }> = {
        items: [{ name: "test" }],
        total: 1,
        page: 1,
        pageSize: 10,
        pages: 1,
      };
      expect(response.items).toHaveLength(1);
      expect(response.pages).toBe(1);
    });

    it("ErrorResponse has detail and optional fields", () => {
      const err: ErrorResponse = {
        detail: "Not found",
        code: "NOT_FOUND",
      };
      expect(err.detail).toBe("Not found");
      expect(err.code).toBe("NOT_FOUND");
    });

    it("SuccessResponse wraps data", () => {
      const res: SuccessResponse<string> = {
        data: "hello",
        message: "OK",
      };
      expect(res.data).toBe("hello");
    });

    it("HealthResponse has status enum", () => {
      const health: HealthResponse = {
        status: "healthy",
        service: "api",
        version: "1.0.0",
        timestamp: "2026-01-01T00:00:00Z",
      };
      expect(health.status).toBe("healthy");
    });
  });

  describe("auth types", () => {
    it("LoginRequest has email and password", () => {
      const req: LoginRequest = { email: "a@b.com", password: "secret" };
      expect(req.email).toBe("a@b.com");
    });

    it("LoginResponse has tokens", () => {
      const res: LoginResponse = {
        accessToken: "at",
        refreshToken: "rt",
        tokenType: "bearer",
      };
      expect(res.tokenType).toBe("bearer");
    });

    it("TokenPair holds both tokens", () => {
      const pair: TokenPair = { accessToken: "at", refreshToken: "rt" };
      expect(pair.accessToken).toBe("at");
    });

    it("TokenPayload has JWT claims", () => {
      const payload: TokenPayload = {
        sub: "user-1",
        tenantId: "t-1",
        roles: ["admin"],
        permissions: ["read"],
        tokenType: "access",
        exp: 9999999999,
        iat: 1000000000,
      };
      expect(payload.sub).toBe("user-1");
      expect(payload.tokenType).toBe("access");
    });

    it("TokenData has runtime fields", () => {
      const data: TokenData = {
        userId: "u-1",
        tenantId: "t-1",
        roles: ["admin"],
        permissions: [],
        tokenType: "access",
      };
      expect(data.userId).toBe("u-1");
    });

    it("User extends BaseEntity", () => {
      const user: User = {
        id: "u-1",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
        email: "a@b.com",
        tenantId: "t-1",
        roles: ["user"],
        isActive: true,
      };
      expect(user.email).toBe("a@b.com");
      expect(user.isActive).toBe(true);
    });

    it("LoginAttemptState tracks brute force", () => {
      const state: LoginAttemptState = {
        attempts: 3,
        lastAttempt: "2026-01-01T00:00:00Z",
        lockedUntil: null,
      };
      expect(state.attempts).toBe(3);
      expect(state.lockedUntil).toBeNull();
    });
  });

  describe("tenant types", () => {
    it("Tenant extends BaseEntity", () => {
      const tenant: Tenant = {
        id: "t-1",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
        slug: "acme",
        name: "Acme Corp",
        isActive: true,
      };
      expect(tenant.slug).toBe("acme");
    });

    it("TenantContext has minimal fields", () => {
      const ctx: TenantContext = {
        tenantId: "t-1",
        tenantSlug: "acme",
      };
      expect(ctx.tenantId).toBe("t-1");
    });

    it("TenantConfig holds feature flags and settings", () => {
      const config: TenantConfig = {
        tenantId: "t-1",
        features: { darkMode: true },
        settings: { maxUsers: 100 },
      };
      expect(config.features.darkMode).toBe(true);
    });
  });
});
