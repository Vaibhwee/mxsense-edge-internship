import EdgeConsoleShell from "../../components/EdgeConsoleShell";
import { getPlatformBlueprint, getPlatformOverview } from "../../lib/api";

export default async function DashboardPage({ searchParams }) {
  const [blueprint, overview] = await Promise.all([
    getPlatformBlueprint(),
    getPlatformOverview(),
  ]);

  const activeModule =
    blueprint.modules.find((module) => module.slug === "dashboard") ||
    blueprint.modules[0];

  return (
    <EdgeConsoleShell
      activeModule={activeModule}
      brand={blueprint.brand}
      isHome={true}
      modules={blueprint.modules}
      overview={overview}
      services={blueprint.services}
    />
  );
}
