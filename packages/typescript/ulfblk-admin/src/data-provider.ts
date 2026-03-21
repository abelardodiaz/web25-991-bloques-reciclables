/**
 * React Admin DataProvider using BloqueClient as HTTP transport.
 *
 * Translates react-admin CRUD calls to REST endpoints.
 * Uses `qs` for query string serialization (FastAPI-compatible).
 *
 * Tenant context is handled automatically via BloqueClient's
 * tenant interceptor (call client.setTenantId() to switch tenants).
 */

import type { DataProvider } from "react-admin";
import { HttpError } from "react-admin";
import { stringify } from "qs";
import type { BloqueClient } from "@ulfblk/api-client";
import type { DataProviderOptions, ListResponse } from "./types.js";

const BATCH_SIZE = 5;

function defaultSerializer(params: Record<string, unknown>): string {
  return stringify(params, { arrayFormat: "repeat", skipNulls: true });
}

async function batchExecute<T>(
  ids: (string | number)[],
  fn: (id: string | number) => Promise<T>,
): Promise<T[]> {
  const results: T[] = [];
  for (let i = 0; i < ids.length; i += BATCH_SIZE) {
    const batch = ids.slice(i, i + BATCH_SIZE);
    const batchResults = await Promise.all(batch.map(fn));
    results.push(...batchResults);
  }
  return results;
}

export function createDataProvider(
  client: BloqueClient,
  options?: DataProviderOptions,
): DataProvider {
  const base = (options?.basePath ?? "/api").replace(/\/+$/, "");
  const serialize = options?.querySerializer ?? defaultSerializer;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- react-admin generics are complex
  type AnyRecord = any;

  async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
    try {
      switch (method) {
        case "GET":
          return await client.get<T>(path);
        case "POST":
          return await client.post<T>(path, body);
        case "PUT":
          return await client.put<T>(path, body);
        case "DELETE":
          return await client.delete<T>(path);
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
    } catch (error: unknown) {
      if (error instanceof Error && "status" in error) {
        const e = error as Error & { status: number; body?: unknown };
        throw new HttpError(e.message, e.status, e.body);
      }
      throw error;
    }
  }

  return {
    getList: async (resource: string, params: any) => {
      const { page, perPage } = params.pagination ?? { page: 1, perPage: 20 };
      const { field, order } = params.sort ?? { field: "id", order: "ASC" };
      const query = serialize({
        page,
        size: perPage,
        sort: field,
        order,
        ...params.filter,
      });
      const url = `${base}/${resource}?${query}`;
      const response = await request<AnyRecord>("GET", url);
      return { data: response.items, total: response.total };
    },

    getOne: async (resource: string, params: any) => {
      const data = await request<AnyRecord>("GET", `${base}/${resource}/${params.id}`);
      return { data };
    },

    getMany: async (resource: string, params: any) => {
      const query = serialize({ id: params.ids });
      const response = await request<AnyRecord>("GET", `${base}/${resource}?${query}`);
      return { data: response.items };
    },

    getManyReference: async (resource: string, params: any) => {
      const { page, perPage } = params.pagination ?? { page: 1, perPage: 20 };
      const { field, order } = params.sort ?? { field: "id", order: "ASC" };
      const query = serialize({
        page,
        size: perPage,
        sort: field,
        order,
        [params.target]: params.id,
        ...params.filter,
      });
      const response = await request<AnyRecord>("GET", `${base}/${resource}?${query}`);
      return { data: response.items, total: response.total };
    },

    create: async (resource: string, params: any) => {
      const data = await request<AnyRecord>("POST", `${base}/${resource}`, params.data);
      return { data };
    },

    update: async (resource: string, params: any) => {
      const data = await request<AnyRecord>("PUT", `${base}/${resource}/${params.id}`, params.data);
      return { data };
    },

    delete: async (resource: string, params: any) => {
      const data = await request<AnyRecord>("DELETE", `${base}/${resource}/${params.id}`);
      return { data };
    },

    deleteMany: async (resource: string, params: any) => {
      await batchExecute(params.ids, (id) =>
        request("DELETE", `${base}/${resource}/${id}`),
      );
      return { data: params.ids };
    },

    updateMany: async (resource: string, params: any) => {
      await batchExecute(params.ids, (id) =>
        request("PUT", `${base}/${resource}/${id}`, params.data),
      );
      return { data: params.ids };
    },
  };
}
