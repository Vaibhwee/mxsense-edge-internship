import { notFound } from "next/navigation";

import EdgeConsoleShell from "../../../../../components/EdgeConsoleShell";
import { getPlatformBlueprint, getPlatformOverview } from "../../../../../lib/api";

export default async function DeviceManagementActionPage({ params }) {
  const { action } = await params;

  const [blueprint, overview] = await Promise.all([
    getPlatformBlueprint(),
    getPlatformOverview(),
  ]);

  const deviceModule = blueprint.modules.find((module) => module.slug === "device-management");
  if (!deviceModule) notFound();

  const actionConfig = deviceModule.actionForms?.[action];
  if (!actionConfig) notFound();

  const activeModule = {
    ...deviceModule,
    focusTab: actionConfig.subTab || deviceModule.focusTab,
  };

  return (
    <EdgeConsoleShell
      activeModule={activeModule}
      brand={blueprint.brand}
      modules={blueprint.modules}
      overview={overview}
      services={blueprint.services}
      deviceManagementAction={{ ...actionConfig, slug: action }}
    />
  );
}

