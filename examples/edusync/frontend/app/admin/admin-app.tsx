"use client";

import { Admin, Resource, ListGuesser, EditGuesser, ShowGuesser } from "react-admin";
import { BloqueClient } from "@ulfblk/api-client";
import { createDataProvider } from "@ulfblk/admin";

const client = new BloqueClient({ baseUrl: "" });
const dataProvider = createDataProvider(client);

export default function AdminApp() {
  return (
    <Admin dataProvider={dataProvider}>
      <Resource
        name="courses"
        list={ListGuesser}
        show={ShowGuesser}
        edit={EditGuesser}
      />
      <Resource
        name="enrollments"
        list={ListGuesser}
        show={ShowGuesser}
      />
      <Resource
        name="availabilities"
        list={ListGuesser}
      />
    </Admin>
  );
}
