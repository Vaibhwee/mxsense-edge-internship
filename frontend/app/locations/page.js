import { getPlatformBlueprint } from "../../lib/api";
import MainLayout from "../../components/layout/MainLayout";
import LocationsClient from "./LocationsClient";

export default async function LocationsPage() {
  const blueprint = await getPlatformBlueprint();
  return (
    <MainLayout
      brand={blueprint.brand}
      modules={blueprint.modules}
      activeModuleSlug={"locations"}
      activeModuleTitle={"Locations"}
    >
      <LocationsClient />
    </MainLayout>
  );
}

