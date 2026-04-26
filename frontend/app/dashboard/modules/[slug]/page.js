import { notFound } from "next/navigation";

import EdgeConsoleShell from "../../../../components/EdgeConsoleShell";
import { getPlatformBlueprint, getPlatformOverview } from "../../../../lib/api";


export default async function DashboardModulePage({ params, searchParams }) {
  const { slug } = await params;
  const [blueprint, overview] = await Promise.all([
    getPlatformBlueprint(),
    getPlatformOverview(),
  ]);

  const activeModule = blueprint.modules.find((module) => module.slug === slug);
  const selectedTab = (await searchParams)?.tab || null;

  if (!activeModule) {
    notFound();
  }

  return (
    <EdgeConsoleShell
      activeModule={activeModule}
      brand={blueprint.brand}
      modules={blueprint.modules}
      overview={overview}
      services={blueprint.services}
      selectedTab={selectedTab}
    />
  );
}
