"use client";

import { Admin, Resource, ListGuesser, EditGuesser, ShowGuesser } from "react-admin";
import { BloqueClient } from "@ulfblk/api-client";
import { createDataProvider } from "@ulfblk/admin";

// Use relative URL so requests go through Next.js (same origin) then proxy to backend
const client = new BloqueClient({ baseUrl: "" });
const dataProvider = createDataProvider(client);

export default function AdminApp() {
  return (
    <Admin dataProvider={dataProvider}>
      <Resource
        name="appointments"
        list={ListGuesser}
        show={ShowGuesser}
        edit={EditGuesser}
      />
      <Resource name="availabilities" list={ListGuesser} />
    </Admin>
  );
}
