"use client";

import dynamic from "next/dynamic";

const LocationsMapNoSSR = dynamic(() => import("../../components/LocationsMap"), {
  ssr: false,
});

export default function LocationsClient() {
  return <LocationsMapNoSSR />;
}

