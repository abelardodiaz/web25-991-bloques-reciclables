"use client";

import { Admin, Resource, ListGuesser, EditGuesser, ShowGuesser } from "react-admin";
import { BloqueClient } from "@ulfblk/api-client";
import { createDataProvider } from "@ulfblk/admin";

const client = new BloqueClient({ baseUrl: "http://localhost:8000" });
const dataProvider = createDataProvider(client);

export default function AdminApp() {
  return (
    <Admin dataProvider={dataProvider} basename="/admin">
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
